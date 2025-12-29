import os
from dotenv import load_dotenv

load_dotenv()

from typing import Optional
#helper method to normalize base urls
def _normalize_base_url(url: Optional[str]) -> Optional[str]:
    """Ensure URLs used for redirects have a scheme (https://) and no trailing slash."""
    if not url:
        return url
    url = url.strip().rstrip("/")
    if url.startswith("http://") or url.startswith("https://"):
        return url
    # Vercel/Railway domains are commonly provided without scheme; default to https.
    return f"https://{url}"

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # Should be 32 characters for Fernet

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./email_clean_agent.db")

# Server URLs
BACKEND_URL = _normalize_base_url(os.getenv("BACKEND_URL", "http://localhost:8000"))
FRONTEND_URL = _normalize_base_url(os.getenv("FRONTEND_URL", "http://localhost:5173"))

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# CORS origins - allow both localhost and production URLs
CORS_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
]
# Add production frontend URL if provided
if IS_PRODUCTION and FRONTEND_URL and FRONTEND_URL != "http://localhost:5173":
    CORS_ORIGINS.append(FRONTEND_URL)

# Validate required environment variables
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or GOOGLE_CLIENT_ID == "your_google_client_id_here":
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env file (replace placeholder values)")

# Don't overwrite OPENAI_API_KEY - let it be None or the actual value
# The LLM service will check and provide a clear error if missing
if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-placeholder-for-now" or OPENAI_API_KEY == "placeholder":
    import warnings
    warnings.warn("OPENAI_API_KEY is set to placeholder. Update it before using LLM features.")
    # Keep it as None/placeholder so LLM service can detect it

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY must be set in .env file")
# Fernet keys are base64-encoded and should be 44 characters, but we'll accept any length and handle it

