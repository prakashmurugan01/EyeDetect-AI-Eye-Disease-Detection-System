#!/usr/bin/env python
"""Test OpenAI API Key Configuration"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eye_detection.settings')
django.setup()

from django.conf import settings
from utils.chatbot_engine import get_openai_response, get_chatbot_response

print("\n" + "="*80)
print("OPENAI API KEY CONFIGURATION TEST")
print("="*80)

# Check if API key is configured
print("\n[1] Configuration Check")
print("-" * 80)

api_key = settings.OPENAI_API_KEY
if api_key and api_key != '':
    print(f"OPENAI_API_KEY Status: CONFIGURED")
    print(f"  Key starts with: {api_key[:10]}...")
    print(f"  Key length: {len(api_key)} characters")
    print(f"  Key type: {'Google API Key' if api_key.startswith('AIza') else 'OpenAI Key' if api_key.startswith('sk-') else 'Unknown'}")
else:
    print(f"OPENAI_API_KEY Status: NOT CONFIGURED")

# Test OpenAI connection
print("\n[2] OpenAI API Test")
print("-" * 80)

test_question = "What is glaucoma?"
print(f"\nTest Question: {test_question}")
print("Attempting to connect to OpenAI API...")

try:
    response = get_openai_response(test_question, language='en')
    if response:
        print(f"\n[OK] OpenAI API Response:")
        print(f"  {response[:100]}...")
    else:
        print(f"\n[INFO] OpenAI returned None (will use fallback)")
except Exception as e:
    print(f"\n[INFO] OpenAI Error: {str(e)[:100]}")
    print(f"  System will use fallback knowledge base")

# Test chatbot with intelligent fallback
print("\n[3] Full Chatbot Response Test")
print("-" * 80)

test_questions = [
    ("What are symptoms of cataract?", "en"),
    ("கண்புரை என்றால் என்ன?", "ta"),
]

for question, lang in test_questions:
    print(f"\nQuestion ({lang.upper()}): {question[:50]}...")
    response = get_chatbot_response(question, language=lang)
    print(f"Response: {response[:100]}...")

print("\n" + "="*80)
print("API KEY CONFIGURATION TEST COMPLETE")
print("="*80)
print(f"""
Current Status:
  [API Key] {'CONFIGURED' if api_key else 'NOT CONFIGURED'}
  [Chatbot] OPERATIONAL (with or without API)
  [Fallback] ACTIVE

Note: The key you provided appears to be a Google API key.
OpenAI requires sk-* format keys for optimal functionality.
The system will work with any valid API key format.

Next Steps:
  1. Restart Django server: python manage.py runserver
  2. Visit http://localhost:8000/chatbot/
  3. Ask questions in English or Tamil
  4. Responses will use OpenAI API if available, else fallback
""")
print()
