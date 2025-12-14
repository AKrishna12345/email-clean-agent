#!/usr/bin/env python3
"""
Interactive script to update .env file with Google OAuth credentials
"""
import os
from pathlib import Path

env_file = Path(__file__).parent / '.env'

print("=" * 60)
print("Google OAuth Credentials Setup")
print("=" * 60)
print()
print("To get your credentials:")
print("1. Go to: https://console.cloud.google.com/")
print("2. Create/select a project")
print("3. Enable Gmail API")
print("4. Go to Credentials → Create OAuth 2.0 Client ID")
print("5. Application type: Web application")
print("6. Add redirect URI: http://localhost:8000/auth/google/callback")
print()
print("=" * 60)
print()

# Read current .env
current_values = {}
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                current_values[key.strip()] = value.strip()

# Get new values
print("Enter your Google OAuth credentials:")
print("(Press Enter to keep current value or skip)")
print()

client_id = input(f"GOOGLE_CLIENT_ID [{current_values.get('GOOGLE_CLIENT_ID', 'not set')[:30]}...]: ").strip()
if not client_id and 'GOOGLE_CLIENT_ID' in current_values:
    client_id = current_values['GOOGLE_CLIENT_ID']

client_secret = input(f"GOOGLE_CLIENT_SECRET [{current_values.get('GOOGLE_CLIENT_SECRET', 'not set')[:30]}...]: ").strip()
if not client_secret and 'GOOGLE_CLIENT_SECRET' in current_values:
    client_secret = current_values['GOOGLE_CLIENT_SECRET']

openai_key = input(f"OPENAI_API_KEY [{current_values.get('OPENAI_API_KEY', 'not set')[:30]}...]: ").strip()
if not openai_key and 'OPENAI_API_KEY' in current_values:
    openai_key = current_values['OPENAI_API_KEY']

# Update values
if client_id:
    current_values['GOOGLE_CLIENT_ID'] = client_id
if client_secret:
    current_values['GOOGLE_CLIENT_SECRET'] = client_secret
if openai_key:
    current_values['OPENAI_API_KEY'] = openai_key

# Write back to .env
env_template = """# Google OAuth Credentials
GOOGLE_CLIENT_ID={GOOGLE_CLIENT_ID}
GOOGLE_CLIENT_SECRET={GOOGLE_CLIENT_SECRET}
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# OpenAI API Key
OPENAI_API_KEY={OPENAI_API_KEY}

# App Configuration
SECRET_KEY={SECRET_KEY}
ENCRYPTION_KEY={ENCRYPTION_KEY}

# Database
DATABASE_URL=sqlite:///./email_clean_agent.db

# Server URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
"""

# Use current values or defaults
final_values = {
    'GOOGLE_CLIENT_ID': current_values.get('GOOGLE_CLIENT_ID', 'your_google_client_id_here'),
    'GOOGLE_CLIENT_SECRET': current_values.get('GOOGLE_CLIENT_SECRET', 'your_google_client_secret_here'),
    'OPENAI_API_KEY': current_values.get('OPENAI_API_KEY', 'sk-placeholder-for-now'),
    'SECRET_KEY': current_values.get('SECRET_KEY', 'change-this-to-any-random-string'),
    'ENCRYPTION_KEY': current_values.get('ENCRYPTION_KEY', 'sMgJOh7vj35Aqp6sky7Zd4Ppa-kfIvVkC3b5paL6FOw='),
}

with open(env_file, 'w') as f:
    f.write(env_template.format(**final_values))

print()
print("✅ .env file updated!")
print()
print("Next steps:")
print("1. Make sure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set correctly")
print("2. Run: python3 check_env.py to verify")
print("3. Start server: python3 -m uvicorn main:app --reload")

