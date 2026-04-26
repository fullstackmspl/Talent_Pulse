import asyncio
import os
import sys
import django

# Setup path for django_backend
sys.path.append(os.path.join(os.getcwd(), "django_backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_backend.settings")
django.setup()

from core.router import route_intent
from ai.intent import predict_intent_with_confidence

async def test_scenarios():
    scenarios = [
        "Create candidate Rahul for Python developer, email rahul@gmail.com",
        "Add lead Amit at Google, email amit@google.com",
        "Create candidate Sonia", # Should ask for email/position
        "Remind me to call Rahul tomorrow",
    ]
    
    for text in scenarios:
        print(f"\n[USER]: {text}")
        intent, conf = predict_intent_with_confidence(text)
        print(f"[AI INTENT]: {intent} ({conf:.2f})")
        
        result = await route_intent(intent, text)
        if result:
            print(f"[AI RESPONSE]: {result['message']}")
        else:
            print("[AI RESPONSE]: Fallback to RAG")

if __name__ == "__main__":
    asyncio.run(test_scenarios())
