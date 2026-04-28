import os
import json
import re
from groq import Groq
from core.document_processor import process_file_bytes

# -----------------------------------------------------------------------------
# 🔐 API Key – Loaded from Environment (.env)
# -----------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def update_resume_keys():
    global client, GROQ_API_KEY
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    print("📄 Resume Service Hot-Reloaded with new Groq Key.")

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
    Uses local text extraction then calls Groq to parse JSON.
    """
    if not client:
        return {"error": "Groq API key missing"}

    try:
        # 1. Local Text Extraction (No AI needed for raw text)
        chunks = process_file_bytes(file_bytes, filename)
        full_text = "\n".join(chunks)

        if not full_text.strip():
            print("❌ No text could be extracted from file.")
            return None

        # 2. Call Groq for JSON extraction
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional recruitment AI. Extract details from resume text into the requested JSON format."},
                {"role": "user", "content": f"{EXTRACT_PROMPT}\n\nRESUME TEXT:\n{full_text[:6000]}"}
            ],
            response_format={"type": "json_object"}
        )
        
        if not response or not response.choices:
            print("❌ Groq API returned an empty response.")
            return None

        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        return data
        
    except Exception as e:
        print(f"⚠️ Groq Extraction Error: {str(e)}")
        return {"error": f"Groq Extraction Error: {str(e)}"}

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
