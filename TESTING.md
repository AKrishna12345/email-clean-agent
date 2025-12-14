# Testing Step 1: OAuth Authentication

## Prerequisites

Before testing, you need:

1. **Google OAuth Credentials** (Client ID & Secret)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8000/auth/google/callback`

2. **OpenAI API Key** (for later steps, but required now for config validation)

3. **Encryption Key** (32 characters)

## Setup Steps

### 1. Generate Encryption Key

```bash
cd backend
python generate_key.py
```

Copy the generated key.

### 2. Create `.env` File

Create `backend/.env` with:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=any-random-string-here
ENCRYPTION_KEY=the-32-char-key-from-step-1
DATABASE_URL=sqlite:///./email_clean_agent.db
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Running the Servers

### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

## Testing the Login Flow

### ✅ Signs Everything is Working:

1. **Frontend loads successfully**
   - Go to `http://localhost:5173`
   - You should see the beautiful login page with "Sign in with Google" button
   - No console errors in browser DevTools

2. **Backend is running**
   - Go to `http://localhost:8000`
   - Should see: `{"message":"Email Clean Agent API","status":"running"}`
   - Go to `http://localhost:8000/health`
   - Should see: `{"status":"healthy"}`

3. **Click "Sign in with Google"**
   - Should redirect to Google login page
   - After login, Google asks for permissions
   - After granting, redirects back to your app

4. **OAuth callback works**
   - Should see "Completing sign in..." briefly
   - Then redirects to dashboard
   - Dashboard shows your email address

5. **Database created**
   - Check `backend/email_clean_agent.db` exists
   - User record should be created with your email

6. **User info endpoint works**
   - Dashboard should display your email
   - No errors in browser console

### ❌ Common Issues:

1. **"GOOGLE_CLIENT_ID must be set" error**
   - Missing or incorrect `.env` file
   - Check file is in `backend/` directory
   - Check all required variables are set

2. **"ENCRYPTION_KEY must be exactly 32 characters"**
   - Run `python generate_key.py` again
   - Copy the full key (it's base64, longer than 32 chars - that's OK, use the full string)

3. **CORS errors in browser**
   - Check `FRONTEND_URL` in `.env` matches your frontend URL
   - Check backend CORS settings in `main.py`

4. **"Redirect URI mismatch" from Google**
   - Check redirect URI in Google Cloud Console matches exactly:
     `http://localhost:8000/auth/google/callback`
   - No trailing slashes!

5. **Database errors**
   - Make sure SQLite can create files in `backend/` directory
   - Check file permissions

6. **Frontend can't connect to backend**
   - Check backend is running on port 8000
   - Check `VITE_API_URL` in frontend `.env` (optional, defaults to localhost:8000)
   - Check browser console for network errors

## What to Check After Successful Login:

1. ✅ **Database has user record**
   ```bash
   # You can check with SQLite:
   sqlite3 backend/email_clean_agent.db "SELECT email, created_at FROM users;"
   ```

2. ✅ **Tokens are encrypted**
   - Refresh token should be encrypted (not plain text)
   - Access token should be stored

3. ✅ **Dashboard displays correctly**
   - Shows your email in header
   - "Sign out" button works
   - Input field for email count is visible

4. ✅ **Logout works**
   - Click "Sign out"
   - Should redirect to login page
   - User data cleared from localStorage

## Next Steps After Testing:

Once login works, you're ready for:
- ✅ Step 2: Email range input (UI already there!)
- ✅ Step 3: Gmail API integration
- ✅ Step 4: LLM classification
- ✅ Step 5: Action execution
- ✅ Step 6: Summary screen

