import os
import httpx
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ----------------------------------------------------
# Config
# ----------------------------------------------------
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
USE_SMTP = os.getenv("USE_SMTP", "false").lower() == "true"

SMTP_HOST = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
DEFAULT_EMAIL_TO = os.getenv("DEFAULT_EMAIL_RECIPIENT", SMTP_USER)


# ----------------------------------------------------
# Webhook Sender
# ----------------------------------------------------
async def send_webhook(path: str, payload: dict):
    # If path is already a full URL, use it
    if path.startswith("http"):
        url = path
    else:
        url = f"{N8N_BASE_URL.rstrip('/')}/{path.lstrip('/')}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json=payload)
        return True
    except Exception:
        return False

# ----------------------------------------------------
# SMTP Sender
# ----------------------------------------------------
def send_email(to_email: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASS:
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, to_email, msg.as_string())
        server.quit()

        return True

    except Exception:
        return False


# ----------------------------------------------------
# Combined Notify
# ----------------------------------------------------
async def notify(
    event_name: str,
    payload: dict,
    webhook_path: str
):
    from datetime import datetime
    
    # Create a structured wrapper for the payload
    full_payload = {
        "event": event_name,
        "timestamp": datetime.now().isoformat(),
        "source": "TalentPulse AI",
        "details": payload
    }

    await send_webhook(webhook_path, full_payload)

    if USE_SMTP:
        # Create a beautiful readable body for emails
        lines = [f"EVENT: {event_name}", f"TIME: {full_payload['timestamp']}", "---"]
        for k, v in payload.items():
            lines.append(f"{k.upper()}: {v}")
        
        send_email(
            DEFAULT_EMAIL_TO,
            f"TalentPulse Alert: {event_name}",
            "\n".join(lines)
        )


# ----------------------------------------------------
# Public Functions
# ----------------------------------------------------
async def notify_new_lead(data: dict):
    path = os.getenv("N8N_LEAD_WEBHOOK", "webhook/new-lead")
    await notify("NEW_LEAD", data, path)


async def notify_new_ticket(data: dict):
    path = os.getenv("N8N_TICKET_WEBHOOK", "webhook/new-ticket")
    await notify("NEW_TICKET", data, path)


async def notify_candidate_update(data: dict):
    path = os.getenv("N8N_CANDIDATE_WEBHOOK", "webhook/candidate-update")
    await notify("CANDIDATE_UPDATE", data, path)


async def notify_reminder(data: dict):
    path = os.getenv("N8N_REMINDER_WEBHOOK", "webhook/reminder-due")
    await notify("REMINDER_DUE", data, path)

