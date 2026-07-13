#!/usr/bin/env python3
"""
Load environment variables from .env file
Run this before running tests or chatbot
"""

from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# Load the single project-root .env file
load_dotenv(Path(__file__).resolve().parent / ".env")

# Get API key
api_key = os.getenv('OPENAI_API_KEY')

if api_key:
    print("✅ API Key Loaded Successfully!")
    print(f"   Key (first 20 chars): {api_key[:20]}...")
    print(f"   Full length: {len(api_key)} characters")
else:
    print("❌ ERROR: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

# Verify it's a valid format
if api_key.startswith('sk-'):
    print("✅ API key format looks correct (sk-...)")
else:
    print("⚠️  API key format might be incorrect (should start with 'sk-')")

print("\n✅ Environment is ready! You can now run:")
print("   python3 run_all_tests.py")
print("   python3 integrated_dssat_assistant.py")
