from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import requests
import config
from database import get_db, User
from utils.token_utils import encrypt_token, decrypt_token

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth 2.0 scopes needed for Gmail and user info
# Note: 'openid' is automatically added by Google when using userinfo scopes
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Create OAuth flow
def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [config.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=config.GOOGLE_REDIRECT_URI
    )


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to get refresh token
    )
    
    # Store state in session (for production, use proper session storage)
    # For now, we'll include it in the redirect
    return RedirectResponse(url=authorization_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        flow = get_flow()
        # Fetch token - handle scope mismatch (Google automatically adds 'openid')
        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
        except ValueError as scope_error:
            # Google automatically adds 'openid' scope, causing a mismatch
            # But the credentials are usually still valid
            error_str = str(scope_error)
            if 'Scope has changed' in error_str:
                print(f"Scope mismatch warning (Google added 'openid' automatically) - continuing anyway")
                # Check if credentials are still available despite the error
                if hasattr(flow, 'credentials') and flow.credentials:
                    credentials = flow.credentials
                    print("Credentials available despite scope mismatch - using them")
                else:
                    # If not, manually exchange the token
                    print("Manually exchanging token due to scope mismatch...")
                    token_data = {
                        'code': code,
                        'client_id': config.GOOGLE_CLIENT_ID,
                        'client_secret': config.GOOGLE_CLIENT_SECRET,
                        'redirect_uri': config.GOOGLE_REDIRECT_URI,
                        'grant_type': 'authorization_code'
                    }
                    token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
                    if token_response.status_code != 200:
                        raise HTTPException(
                            status_code=token_response.status_code,
                            detail=f"Token exchange failed: {token_response.text}"
                        )
                    token_json = token_response.json()
                    # Create credentials manually
                    credentials = Credentials(
                        token=token_json.get('access_token'),
                        refresh_token=token_json.get('refresh_token'),
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=config.GOOGLE_CLIENT_ID,
                        client_secret=config.GOOGLE_CLIENT_SECRET,
                        scopes=SCOPES + ['openid']  # Include openid since Google adds it
                    )
                    if token_json.get('expires_in'):
                        credentials.expiry = datetime.utcnow() + timedelta(seconds=token_json['expires_in'])
            else:
                raise  # Re-raise if it's a different error
        
        # Get user info from Google using direct HTTP request (most reliable)
        email = None
        
        if not credentials.token:
            raise HTTPException(status_code=400, detail="No access token received from Google")
        
        # Use direct HTTP request to get user info
        try:
            headers = {'Authorization': f'Bearer {credentials.token}'}
            response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                email = user_info.get('email')
                print(f"Successfully got email from Google: {email}")
            else:
                print(f"Failed to get user info. Status: {response.status_code}, Response: {response.text}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Failed to get user info from Google: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            print(f"Request exception when getting user info: {e}")
            raise HTTPException(status_code=500, detail=f"Error contacting Google API: {str(e)}")
        
        if not email:
            raise HTTPException(status_code=400, detail="Could not get user email from Google")
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        # Calculate token expiration
        if credentials.expiry:
            expires_at = credentials.expiry
        else:
            expires_at = datetime.utcnow() + timedelta(hours=1)  # Default 1 hour
        
        if user:
            # Update existing user
            user.access_token = credentials.token
            user.refresh_token = encrypt_token(credentials.refresh_token) if credentials.refresh_token else user.refresh_token
            user.token_expires_at = expires_at
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = User(
                email=email,
                access_token=credentials.token,
                refresh_token=encrypt_token(credentials.refresh_token) if credentials.refresh_token else "",
                token_expires_at=expires_at
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        print(f"OAuth callback successful for user: {email}")
        print(f"User ID: {user.id}")
        
        # Redirect to frontend with success
        # In production, you'd set a session cookie here
        frontend_url = f"{config.FRONTEND_URL}/auth/callback?success=true&email={email}"
        print(f"Redirecting to: {frontend_url}")
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        import traceback
        print(f"OAuth callback error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        frontend_url = f"{config.FRONTEND_URL}/auth/callback?success=false&error={str(e)}"
        return RedirectResponse(url=frontend_url)


def get_user_credentials(user: User) -> Credentials:
    """Get Google credentials object from user"""
    creds = Credentials(
        token=user.access_token,
        refresh_token=decrypt_token(user.refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.GOOGLE_CLIENT_ID,
        client_secret=config.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    return creds


def refresh_user_token(user: User, db: Session):
    """Refresh user's access token if expired"""
    if not user.token_expires_at or user.token_expires_at > datetime.utcnow():
        return  # Token still valid
    
    try:
        creds = get_user_credentials(user)
        creds.refresh(GoogleRequest())
        
        # Update user with new token
        user.access_token = creds.token
        expires_at = creds.expiry if creds.expiry else datetime.utcnow() + timedelta(hours=1)
        user.token_expires_at = expires_at
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return creds
    except Exception as e:
        print(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to refresh token")


@router.get("/me")
async def get_current_user(
    email: str,  # For now, pass email as query param. In production, use session/JWT
    db: Session = Depends(get_db)
):
    """Get current user info"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


@router.post("/logout")
async def logout():
    """Logout user (clear session)"""
    # In production, clear session cookie
    return {"message": "Logged out successfully"}

