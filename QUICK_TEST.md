# Quick Testing Guide - Step 1

## ✅ Yes, you should be able to login!

Here's what you need and what to look for:

## Setup Checklist

### 1. Create `.env` file in `backend/` directory

Copy this template and fill in your credentials:

```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=any-random-string-here
ENCRYPTION_KEY=4-zjMU68apddxVmdkZCH11BrzCFm4XFHrA5L5mo1Qs8=
DATABASE_URL=sqlite:///./email_clean_agent.db
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

**To get Google OAuth credentials:**
1. Go to https://console.cloud.google.com/
2. Create/select project
3. Enable "Gmail API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URI: `http://localhost:8000/auth/google/callback`
7. Copy Client ID and Secret

### 2. Install dependencies (if not done)

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Running & Testing

### Start Backend (Terminal 1):
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**✅ Good signs:**
- See: `INFO: Uvicorn running on http://127.0.0.1:8000`
- Visit http://localhost:8000 → see `{"message":"Email Clean Agent API","status":"running"}`
- Visit http://localhost:8000/health → see `{"status":"healthy"}`

**❌ Bad signs:**
- Error about missing `.env` file
- Error about missing GOOGLE_CLIENT_ID
- Import errors (run `pip install -r requirements.txt`)

### Start Frontend (Terminal 2):
```bash
cd frontend
npm run dev
```

**✅ Good signs:**
- See: `Local: http://localhost:5173/`
- Visit http://localhost:5173 → see beautiful login page
- No errors in browser console (F12)

## Testing Login Flow

### Step-by-Step:

1. **Visit http://localhost:5173**
   - ✅ Should see login page with Gmail logo
   - ✅ "Sign in with Google" button visible
   - ✅ No console errors

2. **Click "Sign in with Google"**
   - ✅ Redirects to Google login page
   - ✅ You can log in with your Google account

3. **Grant permissions**
   - ✅ Google asks for Gmail access permissions
   - ✅ Click "Allow"

4. **OAuth callback**
   - ✅ Brief "Completing sign in..." screen
   - ✅ Redirects to dashboard
   - ✅ Dashboard shows your email address

5. **Check database**
   ```bash
   # Should see your email
   sqlite3 backend/email_clean_agent.db "SELECT email FROM users;"
   ```

## ✅ Signs Everything is Working:

1. ✅ **Backend starts without errors**
2. ✅ **Frontend loads login page** (beautiful Gmail-themed UI)
3. ✅ **Click login → Google login page appears**
4. ✅ **After login → Dashboard shows your email**
5. ✅ **Database file created** (`backend/email_clean_agent.db`)
6. ✅ **User record in database** with your email
7. ✅ **No errors in browser console**
8. ✅ **"Sign out" button works** (returns to login)

## ❌ Common Issues:

| Issue | Solution |
|-------|----------|
| "GOOGLE_CLIENT_ID must be set" | Create `.env` file in `backend/` |
| "Redirect URI mismatch" | Check redirect URI in Google Console matches exactly: `http://localhost:8000/auth/google/callback` |
| CORS errors | Check `FRONTEND_URL` in `.env` |
| Database errors | Check file permissions in `backend/` directory |
| Frontend can't connect | Make sure backend is running on port 8000 |

## What Success Looks Like:

After clicking "Sign in with Google" and completing the flow:

1. **Dashboard appears** with:
   - Your email in the top right
   - "Email Clean Agent" title
   - Input field for number of emails (1-200)
   - "Test with 5 emails" button
   - "Start Cleaning" button (red, Gmail-style)

2. **Database has your user:**
   - File: `backend/email_clean_agent.db` exists
   - Contains your email and encrypted tokens

3. **You can logout:**
   - Click "Sign out"
   - Returns to login page
   - Can log in again

## Next Steps After Login Works:

Once login is working, you're ready for:
- ✅ Step 2: Connect the email count input to backend
- ✅ Step 3: Fetch emails from Gmail API
- ✅ Step 4: Send to LLM for classification
- ✅ Step 5: Execute actions
- ✅ Step 6: Show summary

---

**TL;DR:** Yes, you should be able to login! If backend and frontend start without errors, and you have Google OAuth credentials in `.env`, the login flow should work end-to-end.

