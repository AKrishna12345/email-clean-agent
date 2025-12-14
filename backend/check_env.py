#!/usr/bin/env python3
"""
Helper script to check and validate .env file
"""
import os
from pathlib import Path

env_file = Path(__file__).parent / '.env'

print("=" * 60)
print("Checking .env file...")
print("=" * 60)
print(f"File path: {env_file}")
print(f"File exists: {env_file.exists()}")
print(f"File size: {env_file.stat().st_size if env_file.exists() else 0} bytes")
print()

if env_file.exists() and env_file.stat().st_size > 0:
    print("File content:")
    print("-" * 60)
    with open(env_file, 'r') as f:
        content = f.read()
        if content.strip():
            # Hide actual values for security
            lines = content.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if '=' in line and not line.strip().startswith('#'):
                    key = line.split('=')[0].strip()
                    value = line.split('=', 1)[1].strip() if len(line.split('=')) > 1 else ''
                    if value:
                        # Show first 10 chars and last 3 chars if long
                        if len(value) > 15:
                            masked = value[:10] + "..." + value[-3:]
                        else:
                            masked = "***" if value != "your_*_here" else value
                        print(f"{key}={masked}")
                    else:
                        print(f"{key}=")
                else:
                    print(line)
        else:
            print("(file is empty)")
    print("-" * 60)
else:
    print("⚠️  .env file is empty or doesn't exist!")
    print()
    print("Please add the following to your .env file:")
    print()
    print("GOOGLE_CLIENT_ID=your_google_client_id_here")
    print("GOOGLE_CLIENT_SECRET=your_google_client_secret_here")
    print("GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback")
    print("OPENAI_API_KEY=your_openai_api_key_here")
    print("SECRET_KEY=any-random-string-here")
    print("ENCRYPTION_KEY=sMgJOh7vj35Aqp6sky7Zd4Ppa-kfIvVkC3b5paL6FOw=")
    print("DATABASE_URL=sqlite:///./email_clean_agent.db")
    print("BACKEND_URL=http://localhost:8000")
    print("FRONTEND_URL=http://localhost:5173")

print()
print("=" * 60)
print("Testing if values can be loaded...")
print("=" * 60)

from dotenv import load_dotenv
load_dotenv(env_file)

required_vars = {
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'ENCRYPTION_KEY': os.getenv('ENCRYPTION_KEY'),
}

all_set = True
for var_name, var_value in required_vars.items():
    status = "✅ SET" if var_value and var_value not in ['', 'your_*_here', 'your_google_client_id_here', 'your_openai_api_key_here'] else "❌ NOT SET"
    print(f"{var_name}: {status}")
    if not var_value or var_value in ['', 'your_*_here', 'your_google_client_id_here', 'your_openai_api_key_here']:
        all_set = False

print()
if all_set:
    print("✅ All required variables are set!")
else:
    print("❌ Some variables are missing. Please update your .env file.")

