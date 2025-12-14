# How to Start the Backend

## Quick Start

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

## Step-by-Step Instructions

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Activate virtual environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file (if not already done)

Create a file named `.env` in the `backend/` directory with:
```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=any-random-string
ENCRYPTION_KEY=4-zjMU68apddxVmdkZCH11BrzCFm4XFHrA5L5mo1Qs8=
DATABASE_URL=sqlite:///./email_clean_agent.db
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### 5. Start the server
```bash
uvicorn main:app --reload
```

The `--reload` flag enables auto-reload when you change code.

## ✅ Success Indicators

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Test It's Working

1. **Visit http://localhost:8000**
   - Should see: `{"message":"Email Clean Agent API","status":"running"}`

2. **Visit http://localhost:8000/health**
   - Should see: `{"status":"healthy"}`

3. **Visit http://localhost:8000/docs**
   - Should see FastAPI automatic API documentation (Swagger UI)

## Common Issues

### "ModuleNotFoundError" or import errors
```bash
pip install -r requirements.txt
```

### "GOOGLE_CLIENT_ID must be set"
- Create `.env` file in `backend/` directory
- Add all required environment variables

### "Port already in use"
- Another process is using port 8000
- Kill it or change port: `uvicorn main:app --reload --port 8001`

### Virtual environment not found
```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Stop the Server

Press `CTRL+C` in the terminal where it's running.

