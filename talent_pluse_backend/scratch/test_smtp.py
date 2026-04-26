import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
TO = os.getenv("DEFAULT_EMAIL_RECIPIENT", SMTP_USER)

def test_smtp():
    if not SMTP_USER or not SMTP_PASS:
        print("Error: SMTP_USER or SMTP_PASS not set.")
        return

    print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
    try:
        msg = MIMEText("TalentPulse SMTP Connection Test Success.")
        msg["Subject"] = "SMTP Test"
        msg["From"] = SMTP_FROM
        msg["To"] = TO

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, [TO], msg.as_string())
        server.quit()
        print("Success: Test email sent!")
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    test_smtp()
