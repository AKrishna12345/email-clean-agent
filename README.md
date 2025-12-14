# Email Clean Agent

Messy Inbox??? We got the fix. Login with your email address, give a range of emails, and watch the magic happen!

An AI-powered tool to help you clean and organize your Gmail inbox. Simply log in with your Google account, specify how many emails to process, and let AI classify and clean them automatically.

## Features

- 🔐 **Secure OAuth Login** - Sign in with your Google account
- 🤖 **AI-Powered Classification** - Uses OpenAI to intelligently classify emails
- 🧹 **Automated Cleanup** - Delete, archive, mark as read, or draft responses
- 📊 **Summary Dashboard** - See what actions were taken on your emails
- 🎨 **Beautiful UI** - Modern, Gmail-inspired interface

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy (SQLite)
- **Frontend**: React, Vite, React Router
- **APIs**: Gmail API, OpenAI API
- **Authentication**: Google OAuth 2.0

## Setup

See [SETUP.md](./SETUP.md) for detailed setup instructions.

### Quick Start

1. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Generate Encryption Key:**
   ```bash
   python generate_key.py
   ```

3. **Create `.env` file** in `backend/` with your credentials (see SETUP.md)

4. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

5. **Run:**
   - Backend: `uvicorn main:app --reload` (from backend/)
   - Frontend: `npm run dev` (from frontend/)

## Project Status

✅ **Step 1: OAuth Authentication** - Complete
- User can log in with Google
- Tokens stored securely in database
- Beautiful Gmail-themed UI

🚧 **Step 2: Email Range Input** - Ready (UI complete, backend pending)
🚧 **Step 3: Gmail API Integration** - Pending
🚧 **Step 4: LLM Classification** - Pending
🚧 **Step 5: Action Execution** - Pending
🚧 **Step 6: Summary Screen** - Pending

## License

MIT
