# Quick Guide: Get Google OAuth Credentials

## Step-by-Step Instructions

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Create or Select a Project
- Click the project dropdown at the top
- Click "New Project" or select an existing one
- Give it a name like "Email Clean Agent"

### 3. Enable Gmail API
- Go to "APIs & Services" → "Library"
- Search for "Gmail API"
- Click on it and click "Enable"

### 4. Create OAuth 2.0 Credentials
- Go to "APIs & Services" → "Credentials"
- Click "+ CREATE CREDENTIALS" → "OAuth client ID"
- If prompted, configure OAuth consent screen first:
  - User Type: "External" (for personal/testing)
  - App name: "Email Clean Agent"
  - User support email: Your email
  - Developer contact: Your email
  - Click "Save and Continue" through the steps
- Back to creating OAuth client ID:
  - Application type: **"Web application"**
  - Name: "Email Clean Agent Web Client"
  - Authorized redirect URIs: Click "ADD URI"
  - Add: `http://localhost:8000/auth/google/callback`
  - Click "CREATE"

### 5. Copy Your Credentials
- You'll see a popup with:
  - **Your Client ID** (long string ending in `.apps.googleusercontent.com`)
  - **Your Client Secret** (starts with `GOCSPX-`)
- Copy both of these

### 6. Update .env File
Open `backend/.env` and replace:
```
GOOGLE_CLIENT_ID=paste_your_client_id_here
GOOGLE_CLIENT_SECRET=paste_your_client_secret_here
```

## Quick Links
- Google Cloud Console: https://console.cloud.google.com/
- APIs & Services: https://console.cloud.google.com/apis
- Credentials: https://console.cloud.google.com/apis/credentials

