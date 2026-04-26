import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Request,
    APIRouter
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

# ---------------------------------------------------
# Load .env first
# ---------------------------------------------------
load_dotenv()

# ---------------------------------------------------
# Django Setup
# ---------------------------------------------------
import sys
import django

# Add the django_backend directory to sys.path so Django can find the settings and apps
django_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "django_backend")
if django_dir not in sys.path:
    sys.path.append(django_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
django.setup()

# ---------------------------------------------------
# File Storage Setup
# ---------------------------------------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_to_registry(name: str):
    import json
    from datetime import datetime
    registry_path = "uploaded_files.json"
    try:
        if os.path.exists(registry_path):
            with open(registry_path, "r") as f:
                data = json.load(f)
        else:
            data = []
        
        # Avoid duplicates
        if not any(f["name"] == name for f in data):
            data.append({
                "name": name,
                "uploaded_at": datetime.now().isoformat()
            })
            with open(registry_path, "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Registry Update Failed: {e}")

def remove_from_registry(name: str):
    import json
    registry_path = "uploaded_files.json"
    try:
        if os.path.exists(registry_path):
            with open(registry_path, "r") as f:
                data = json.load(f)
            
            # Remove the entry
            data = [f for f in data if f["name"] != name]
            
            with open(registry_path, "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Registry Removal Failed: {e}")


# ---------------------------------------------------
# Internal Imports
# ---------------------------------------------------
from auth import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
)

from core.rag_service import (
    startup_rag,
    shutdown_rag,
    add_document_file,
    add_document_url,
    ask_rag,
    list_sources,
    delete_source,
)

from ai.intent import predict_intent_with_confidence
from core.router import route_intent
from core.db_service import (
    db_get_all_leads,
    db_get_all_candidates,
    db_get_all_tickets,
    db_get_all_reminders,
    db_create_candidate, # ADD THIS
)

from core.resume_service import extract_resume_data, format_resume_details
from core.n8n_service import notify


# ---------------------------------------------------
# Config
# ---------------------------------------------------
APP_NAME = os.getenv(
    "APP_NAME",
    "TalentPulse AI"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)

MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "20")
)

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    "developer.mspl@gmail.com"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "Meander@8982"
)

# Gemini Key loaded from .env
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.0-flash"
)

ADMIN_HASH = hash_password(ADMIN_PASSWORD)


# ---------------------------------------------------
# Lifespan
# ---------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_rag()
    yield
    await shutdown_rag()


# ---------------------------------------------------
# App
# ---------------------------------------------------
app = FastAPI(
    title=APP_NAME,
    version="2.0.0",
    lifespan=lifespan
)

# API Router with /api prefix
api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Models
# ---------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


class UrlRequest(BaseModel):
    url: str


class PublicLeadRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: str = Field(...)
    phone: str = Field(...)
    company: str = Field(...)
    service: str = Field(...)
    budget: str = Field(default="")
    message: str = Field(default="")


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def ok(message: str, data=None):
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def fail(message: str, code=400):
    raise HTTPException(
        status_code=code,
        detail=message
    )


# ---------------------------------------------------
# Global Errors
# ---------------------------------------------------
@app.exception_handler(Exception)
async def global_error(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "data": None
        }
    )


# ---------------------------------------------------
# Root
# ---------------------------------------------------
@app.get("/")
async def root():
    return ok(
        f"{APP_NAME} Running",
        {
            "gemini_enabled": bool(GEMINI_API_KEY),
            "gemini_model": GEMINI_MODEL
        }
    )


@app.get("/health")
async def health():
    return ok("Healthy")


# ---------------------------------------------------
# Login
# ---------------------------------------------------
@api_router.post("/login")
async def login(body: LoginRequest):
    if body.email.lower() != ADMIN_EMAIL.lower():
        fail("Invalid credentials", 401)

    if not verify_password(
        body.password,
        ADMIN_HASH
    ):
        fail("Invalid credentials", 401)

    token = create_access_token(
        {"sub": body.email}
    )

    return ok(
        "Login successful",
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": body.email
            }
        }
    )


# ---------------------------------------------------
# Upload File
# ---------------------------------------------------
@api_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(verify_token)
):
    raw = await file.read()

    if not raw:
        fail("Empty file")

    if len(raw) > MAX_UPLOAD_MB * 1024 * 1024:
        fail("File too large")

    ext = os.path.splitext(
        file.filename
    )[1].lower()

    allowed = [
        ".pdf",
        ".txt",
        ".docx",
        ".csv"
    ]

    if ext not in allowed:
        fail("Unsupported file type")

    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(raw)

    count = await add_document_file(
        file.filename,
        raw,
        file_path # Pass the path
    )

    # Add to uploaded_files.json registry
    save_to_registry(file.filename)


    return ok(
        f"Indexed {count} chunks",
        {
            "filename": file.filename
        }
    )


# ---------------------------------------------------
# Automated Resume Parsing (NEW)
# ---------------------------------------------------
@api_router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user=Depends(verify_token)
):
    """
    Unified endpoint for:
    1. Extracting AI details from Resume PDF/Image
    2. Saving as a Candidate in Dataset
    3. Sending Email notification
    """
    raw = await file.read()
    
    if not raw:
        fail("Empty file")

    # Save to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(raw)

    # 1. AI Extraction
    extracted_data = await extract_resume_data(raw, file.filename)
    if not extracted_data:
        fail("AI could not extract details from this resume.")

    # Index in RAG for future retrieval/search
    await add_document_file(file.filename, raw, file_path)
    
    # Add to uploaded_files.json registry
    save_to_registry(file.filename)

    # 2. Map to Database
    # We use 'notes' to store the complex extracted details
    notes = format_resume_details(extracted_data)
    
    exp_list = extracted_data.get("experience") or []
    pos_applied = exp_list[0].get("role") if exp_list and isinstance(exp_list, list) and len(exp_list) > 0 else "Parsed Applicant"

    candidate_data = {
        "name": extracted_data.get("name") or "Unknown Candidate",
        "email": extracted_data.get("email") or "no-email@talentpulse.local",
        "phone": extracted_data.get("phone"),
        "position_applied": pos_applied,
        "status": "applied",
        "notes": notes
    }
    
    try:
        new_candidate = await db_create_candidate(candidate_data)
        
        # 3. Email Notification
        email_payload = {
            "candidate_id": new_candidate["id"],
            "name": new_candidate["name"],
            "email": new_candidate["email"],
            "role": new_candidate["position_applied"],
            "summary": extracted_data.get("summary", "N/A"),
            "details": notes
        }
        
        # Using the existing notify function (sends to n8n and/or SMTP)
        await notify("RESUME_PARSED", email_payload, "webhook/new-resume")
        
        return ok(
            f"Resume parsed and candidate #{new_candidate['id']} created.",
            {
                "candidate": new_candidate,
                "extracted": extracted_data
            }
        )
        
    except Exception as e:
        print(f"❌ Failed to save candidate: {e}")
        fail(f"Database error: {str(e)}")



# ---------------------------------------------------
# Process URL
# ---------------------------------------------------
@api_router.post("/process-link")
async def process_link(
    body: UrlRequest,
    user=Depends(verify_token)
):
    count = await add_document_url(
        body.url
    )

    if count > 0:
        save_to_registry(body.url)

    return ok(
        f"Indexed {count} chunks",
        {"url": body.url}
    )


# ---------------------------------------------------
# Chat
# ---------------------------------------------------
@api_router.post("/chat")
async def chat(
    body: ChatRequest,
    user=Depends(verify_token)
):
    # Use user email as the session ID for stateful conversations
    session_id = user.get("sub", "default")

    # 1. Attempt intent detection and routing
    try:
        intent, conf = predict_intent_with_confidence(body.query)
        route_data = await route_intent(intent, body.query, session_id=session_id)
        
        if route_data:
            return {
                "response": route_data.get("message", "Action completed."),
                "data": route_data.get("data", None),
                "options": route_data.get("options", []), # ADD THIS LINE
                "intent": intent,
                "confidence": conf,
                "source": "database/action"
            }
    except Exception as e:
        print(f"Intent detection or routing failed: {e}")
        # Fallback to RAG if intent model is missing or router fails

    # 2. Fallback to RAG
    result = await ask_rag(
        body.query
    )

    return {
        "response": result["answer"],
        "sources": result["sources"],
        "model": GEMINI_MODEL,
        "source": "rag"
    }


# ---------------------------------------------------
# CRM Data Endpoints
# ---------------------------------------------------
@api_router.get("/leads")
async def get_leads(user=Depends(verify_token)):
    data = await db_get_all_leads()
    return ok("Leads fetched", data)


@api_router.get("/candidates")
async def get_candidates(user=Depends(verify_token)):
    data = await db_get_all_candidates()
    return ok("Candidates fetched", data)


@api_router.get("/tickets")
async def get_tickets(user=Depends(verify_token)):
    data = await db_get_all_tickets()
    return ok("Tickets fetched", data)


@api_router.get("/reminders")
async def get_reminders(user=Depends(verify_token)):
    data = await db_get_all_reminders()
    return ok("Reminders fetched", data)


# ---------------------------------------------------
# Public Leads
# ---------------------------------------------------
@api_router.post("/public/lead")
async def create_public_lead(body: PublicLeadRequest):
    # Public endpoint, no auth
    notes = f"Service: {body.service}\nBudget: {body.budget}\nMessage: {body.message}"
    
    lead_data = {
        "name": body.name,
        "email": body.email,
        "phone": body.phone,
        "company": body.company,
        "status": "new",
        "source": "Website Lead Form",
        "notes": notes.strip()
    }
    
    try:
        from core.db_service import db_create_lead
        new_lead = await db_create_lead(lead_data)
        
        from core.n8n_service import notify_new_lead
        await notify_new_lead(new_lead)
        
        return ok("Thank you! Your request has been submitted successfully.", new_lead)
    except Exception as e:
        print(f"❌ Failed to save public lead: {e}")
        fail(f"Could not submit request: {str(e)}")


# ---------------------------------------------------
# Files
# ---------------------------------------------------
@api_router.get("/files")
async def list_files():
    import json
    try:
        if os.path.exists("uploaded_files.json"):
            with open("uploaded_files.json", "r") as f:
                data = json.load(f)
            # Return wrapped in a 'data' field to match frontend expectation
            return ok("Files fetched", data)
        return ok("No files found", [])
    except Exception as e:
        return fail(str(e))


@api_router.delete("/files/{name:path}")
async def remove_file(
    name: str,
    user=Depends(verify_token)
):
    deleted = await delete_source(
        name
    )

    if not deleted:
        # Still try to remove from registry even if RAG deletion failed
        remove_from_registry(name)
        # Check if it was a 404 in RAG but might still be in registry
        # We'll return OK anyway to be safe
        return ok("Registry cleaned")

    # Remove from registry
    remove_from_registry(name)

    if not deleted:
        fail("File not found", 404)

    return ok("Deleted")


# Register API Router
app.include_router(api_router)


# ---------------------------------------------------
# Run
# ---------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8028,
        reload=True
    )