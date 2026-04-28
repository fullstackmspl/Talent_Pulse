from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
import os
import requests
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .models import Lead, Ticket, Candidate, Reminder
from .serializers import (
    LeadSerializer,
    TicketSerializer,
    CandidateSerializer,
    ReminderSerializer,
)

USE_SMTP = os.getenv("USE_SMTP", "true").lower() in ("true", "1", "yes")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
DEFAULT_EMAIL_RECIPIENT = os.getenv("DEFAULT_EMAIL_RECIPIENT")


def _send_smtp_email(to, subject, body):
    if not SMTP_USER or not SMTP_PASS:
        print("❌ [SMTP] SMTP_USER and SMTP_PASS must be set to send email.")
        return False
    if not to:
        print("❌ [SMTP] No recipient provided for email.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, to, msg.as_string())
        server.quit()
        print(f"[SMTP] Email sent to {to}")
        return True
    except Exception as e:
        print(f"❌ [SMTP] Email send error: {e}")
        return False


def _notify_event(payload):
    if USE_SMTP:
        recipient = DEFAULT_EMAIL_RECIPIENT or payload.get("email") or SMTP_USER
        subject = f"TalentPulse Notification"
        body = json.dumps(payload, indent=2)
        return _send_smtp_email(recipient, subject, body)

    try:
        base = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        webhook_path = payload.get("webhook_path")
        requests.post(f"{base}/{webhook_path}", json=payload, timeout=5)
        return True
    except Exception as e:
        print(f"[n8n] Failed: {e}")
        return False


# ---------------------------------------------------
# Lead
# ---------------------------------------------------
class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-created_at")
    serializer_class = LeadSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email", "company"]

    def perform_create(self, serializer):
        lead = serializer.save()
        _notify_event({
            "event": "new_lead",
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "status": lead.status,
            "webhook_path": "webhook/new-lead"
        })


# ---------------------------------------------------
# Ticket
# ---------------------------------------------------
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by("-created_at")
    serializer_class = TicketSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "issue"]

    def perform_create(self, serializer):
        ticket = serializer.save()
        _notify_event({
            "event": "new_ticket",
            "id": ticket.id,
            "title": ticket.title,
            "issue": ticket.issue,
            "status": ticket.status,
            "priority": ticket.priority,
            "webhook_path": "webhook/new-ticket"
        })


# ---------------------------------------------------
# Candidate
# ---------------------------------------------------
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all().order_by("-created_at")
    serializer_class = CandidateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email", "position_applied"]

    def perform_create(self, serializer):
        candidate = serializer.save()
        _notify_event({
            "event": "new_candidate",
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "position": candidate.position_applied,
            "status": candidate.status,
            "webhook_path": "webhook/new-resume"
        })

    def perform_update(self, serializer):
        candidate = serializer.save()
        _notify_event({
            "event": "candidate_update",
            "id": candidate.id,
            "name": candidate.name,
            "status": candidate.status,
            "position": candidate.position_applied,
            "webhook_path": "webhook/candidate-update"
        })


# ---------------------------------------------------
# Reminder
# ---------------------------------------------------
class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all().order_by("due_date")
    serializer_class = ReminderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        done = self.request.query_params.get("done")
        if done == "true":
            qs = qs.filter(is_done=True)
        elif done == "false":
            qs = qs.filter(is_done=False)
        return qs

    @action(detail=False, methods=["get"])
    def pending(self, request):
        qs = Reminder.objects.filter(is_done=False).order_by("due_date")
        data = ReminderSerializer(qs, many=True).data
        return Response(data)