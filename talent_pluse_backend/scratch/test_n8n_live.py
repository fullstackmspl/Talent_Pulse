"""
TalentPulse n8n Live Test Script
Run this AFTER clicking 'Execute Workflow' in n8n editor.
"""

import requests
import json

WEBHOOK_URL = "https://admin18.app.n8n.cloud/webhook-test/webhook/candidate-update"


def send_event(payload, label):
    print("\n" + "="*50)
    print("Testing: " + label)
    print("Payload:")
    print(json.dumps(payload, indent=2))
    print("="*50)
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print("SUCCESS! Status: " + str(response.status_code))
            print("  -> The '" + payload["event"] + "' branch should be GREEN in n8n!")
        elif response.status_code == 404:
            print("404 - n8n Test URL is ASLEEP.")
            print("  -> Click 'Execute Workflow' in n8n first, then re-run!")
        else:
            print("Response: " + str(response.status_code) + " - " + response.text)
    except Exception as e:
        print("Connection Error: " + str(e))


# Test 1: TICKET
send_event({
    "event":       "NEW_TICKET",
    "id":          10,
    "title":       "Auto-Ticket: Login page is crashing",
    "issue":       "My account is locked and the login page is crashing",
    "status":      "open",
    "priority":    "medium",
    "description": "AI-Generated ticket from user message"
}, label="Ticket -> NEW_TICKET")


# Test 2: CANDIDATE
send_event({
    "event":            "CANDIDATE_UPDATE",
    "id":               2,
    "name":             "Rahul Sharma",
    "email":            "rahul@example.com",
    "position_applied": "Python Developer",
    "status":           "applied",
    "notes":            "AI-registered candidate"
}, label="Candidate -> CANDIDATE_UPDATE")


# Test 3: INTERVIEW
send_event({
    "event":            "INTERVIEW_SCHEDULED",
    "id":               2,
    "name":             "Rahul Sharma",
    "email":            "rahul@example.com",
    "position_applied": "Python Developer",
    "status":           "interview",
    "notes":            "Candidate moved to interview round"
}, label="Interview -> INTERVIEW_SCHEDULED")


# Test 4: LEAD
send_event({
    "event":   "NEW_LEAD",
    "id":      6,
    "name":    "Alice",
    "email":   "alice@abc.com",
    "status":  "new",
    "company": "ABC Corp",
    "notes":   "Auto-captured via TalentPulse AI Chat"
}, label="Lead -> NEW_LEAD")


# Test 5: REMINDER
send_event({
    "event":       "REMINDER_DUE",
    "id":          1,
    "title":       "Call the client",
    "description": "Remind me to call the client tomorrow at 10am",
    "due_date":    "2026-04-19T09:00:00",
    "is_done":     False
}, label="Reminder -> REMINDER_DUE")


print("\n" + "="*50)
print("All 5 tests sent! Check n8n Executions tab.")
print("="*50)
