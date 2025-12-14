# Setup Instructions

## Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   Create a `.env` file in the `backend/` directory with the following:
   ```env
   # Google OAuth Credentials
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

   # OpenAI API
   OPENAI_API_KEY=your_openai_api_key_here

   # App Configuration
   SECRET_KEY=your_secret_key_here_change_in_production
   ENCRYPTION_KEY=your_32_character_encryption_key_here

   # Database
   DATABASE_URL=sqlite:///./email_clean_agent.db

   # Server
   BACKEND_URL=http://localhost:8000
   FRONTEND_URL=http://localhost:5173
   ```

5. **Generate encryption key (32 characters):**
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```
   Use the output as your `ENCRYPTION_KEY`

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file (optional):**
   Create a `.env` file in the `frontend/` directory if you need to configure API URLs:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

## Getting API Credentials

### Google OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Set application type to "Web application"
6. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
7. Copy Client ID and Client Secret to your `.env` file

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

## Running the Application

### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend
```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

## Project Structure

```
email-clean-agent/
├── backend/
│   ├── venv/           # Python virtual environment
│   ├── requirements.txt
│   ├── config.py       # Configuration file
│   ├── .env            # Environment variables (create this)
│   └── main.py         # FastAPI app (to be created)
├── frontend/
│   ├── node_modules/
│   ├── src/
│   ├── package.json
│   └── .env            # Frontend env vars (optional)
├── .gitignore
└── README.md

