# Email Clean Agent

AI-powered Gmail inbox cleanup. Sign in with Google, choose how many emails to process, and let the app classify + take cleanup actions.

## Access (Test Users)

To be added to the test users list (so you can use the app), email **aryankrishna0404@gmail.com**.

## Features

- **Google OAuth**: Sign in securely with your Google account
- **Gmail cleanup**: Archive / delete / mark as read (depending on configured actions)
- **Dashboard + summary**: See what actions were taken

## Tech Stack

- **Backend**: FastAPI (Python), SQLAlchemy
- **Frontend**: React + Vite
- **Integrations**: Gmail API, OpenAI (optional depending on features enabled)

## Running Locally (Full Directions)

### Prerequisites

- **Node.js**: 18+
- **Python**: 3.9+ (local dev)

### 1) Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Create backend `.env`

Create `backend/.env` with:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# App configuration
SECRET_KEY=any-random-string
ENCRYPTION_KEY=your-44-character-base64-key

# Optional (only required for LLM features)
OPENAI_API_KEY=your_openai_api_key_here

# URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=sqlite:///./email_clean_agent.db

ENVIRONMENT=development
```

Generate an encryption key:

```bash
cd backend
python generate_key.py
```

### 3) Start backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Backend should be available at:
- `http://localhost:8000`
- `http://localhost:8000/docs` (Swagger UI)

### 4) Frontend setup + start

```bash
cd frontend
npm install
npm run dev
```

Frontend should be available at `http://localhost:5173`.

### 5) Google OAuth setup (local)

In Google Cloud Console:
- **Authorized redirect URI**: `http://localhost:8000/auth/google/callback`
- **JavaScript origin**: `http://localhost:5173`

Then put the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` into `backend/.env`.

## Deployment

- **Backend**: Railway
- **Frontend**: Vercel

See `DEPLOYMENT.md` for the full checklist and required environment variables.

## Troubleshooting

- **Frontend “VITE_API_URL” issues**: set `VITE_API_URL` in Vercel project settings to your Railway backend URL (no trailing slash recommended).
- **OAuth redirect issues**: ensure `GOOGLE_REDIRECT_URI` matches exactly what’s configured in Google Cloud Console and your deployed backend URL.
- **CORS issues**: ensure Railway `FRONTEND_URL` matches your Vercel URL (including `https://`).

## License

MIT
