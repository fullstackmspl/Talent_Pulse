import os
import json
import re
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 🔐 API Key – Loaded from Environment (.env)
# -----------------------------------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

def update_resume_keys():
    global client, API_KEY
    API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=API_KEY)
    print("📄 Resume Service Hot-Reloaded with new Gemini Key.")

# -----------------------------------------------------------------------------
# 📋 Extraction Prompt
# -----------------------------------------------------------------------------
EXTRACT_PROMPT = """
Extract the following details from this resume and return ONLY a valid JSON object:

{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "linkedin": "",
  "github": "",
  "summary": "",
  "coding_languages": [],
  "frameworks_libraries": [],
  "tools_technologies": [],
  "education": [
    {
      "degree": "",
      "institution": "",
      "year": ""
    }
  ],
  "experience": [
    {
      "role": "",
      "company": "",
      "duration": "",
      "description": ""
    }
  ],
  "projects": [
    {
      "name": "",
      "description": "",
      "technologies": []
    }
  ],
  "certifications": []
}

If any field is not found, leave it as empty string or empty list.
Return ONLY the JSON, no extra text, no markdown formatting.
"""

# -----------------------------------------------------------------------------
# 🚀 Extraction Logic
# -----------------------------------------------------------------------------
async def extract_resume_data(file_bytes: bytes, filename: str):
    """
    Calls Gemini API to extract JSON from resume bytes.
    """
    # Determine MIME type
    mime_type = "application/pdf"
    lower_path = filename.lower()
    if lower_path.endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"
    elif lower_path.endswith(".png"):
        mime_type = "image/png"

    try:
        # Using gemini-2.5-flash for high-accuracy resume extraction
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                EXTRACT_PROMPT
            ]
        )
        
        if not response or not response.text:
            print("❌ Gemini API returned an empty response.")
            return None

        raw = response.text.strip()
        # Clean markdown formatting if present
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        
        data = json.loads(raw)
        return data
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Gemini 2.0 Error: {error_msg}")
        
        # Aggressive Fallback: Try 1.5-flash-latest for ANY error (Quota 429, 404, etc.)
        print("🔄 Attempting automatic fallback to gemini-1.5-flash-latest...")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash-latest", 
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    EXTRACT_PROMPT
                ]
            )
            
            if not response or not response.text:
                return {"error": "Gemini 1.5 also returned an empty response."}

            raw = response.text.strip()
            raw = re.sub(r"```json\s*", "", raw)
            raw = re.sub(r"```\s*", "", raw)
            return json.loads(raw)
            
        except Exception as e2:
            print(f"❌ Critical Failure: Both models failed. Error: {str(e2)}")
            return {"error": f"Quota Exhausted or API Error. (Details: {str(e2)})"}

def format_resume_details(data: dict):
    """
    Formats the complex JSON into a readable string for the database 'notes' field.
    """
    lines = []
    lines.append(f"Location: {data.get('location', 'N/A')}")
    lines.append(f"Summary: {data.get('summary', 'N/A')}")
    
    if data.get('coding_languages'):
        lines.append(f"Languages: {', '.join(data['coding_languages'])}")
        
    if data.get('frameworks_libraries'):
        lines.append(f"Frameworks: {', '.join(data['frameworks_libraries'])}")

    lines.append("\n--- EDUCATION ---")
    for edu in data.get("education", []):
        lines.append(f"• {edu.get('degree')} @ {edu.get('institution')} ({edu.get('year')})")

    lines.append("\n--- EXPERIENCE ---")
    for exp in data.get("experience", []):
        lines.append(f"• {exp.get('role')} at {exp.get('company')} [{exp.get('duration')}]")

    return "\n".join(lines)
