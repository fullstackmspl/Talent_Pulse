import requests
import json
import os

BASE_URL = "http://localhost:8028/api"

def test_flow(message, label):
    print(f"\n--- Testing {label} ---")
    payload = {
        "message": message
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 1. Test Ticket Creation (The one that was failing)
    test_flow("My login is crashing again", "Ticket Creation")
    
    # 2. Test Lead Creation (Verify n8n trigger)
    test_flow("Save lead Rahul Sharma, email rahul.test@example.com", "Lead Creation")
