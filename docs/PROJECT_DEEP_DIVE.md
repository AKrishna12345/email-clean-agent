# Email Clean Agent — Project Deep Dive (Build + Learn Guide)

This document is meant to help you understand this project **inside and out**:

- **What we built (end-to-end)** and the **major steps** it took
- For each step: **what’s happening**, **why it was done this way**, and **what to learn next** as you scale up
- For each step: **exact files** to read to go deeper

---

## 1) Define the product + the “happy path”

### What we built
The app’s core user journey (“happy path”) is:

- User opens the web app
- Clicks **Sign in with Google**
- Backend completes Google OAuth and stores tokens
- User chooses how many emails to process (1–100)
- Backend fetches Gmail messages, uses an LLM to classify them, then applies Gmail labels
- Frontend shows a summary of what happened

### What to learn / know for bigger apps
- **Start with a crisp happy path**: you’ll build faster if every component maps to a user step.
- **Keep the contract stable**: define the data exchanged between frontend/backend early (request/response shapes).

### Where to look
- **Frontend routing + pages**: `frontend/src/App.jsx`
- **Login → OAuth redirect**: `frontend/src/context/AuthContext.jsx`
- **Email-clean request**: `frontend/src/pages/Dashboard.jsx`
- **Summary display**: `frontend/src/pages/Summary.jsx`
- **Backend app wiring**: `backend/main.py`

---

## 2) Choose an architecture (split frontend/backend)

### What we did
We used a simple, standard web app split:

- **Frontend** (React + Vite) handles UI, routing, and calls the backend API.
- **Backend** (FastAPI) handles OAuth, Gmail API calls, token storage, and LLM calls.

This keeps secrets (Google client secret, token encryption key, OpenAI key) on the backend only.

### What to learn / know for bigger apps
- **Boundary discipline**: never put OAuth client secrets, DB creds, or API keys in the frontend.
- **API contracts**: consider OpenAPI-first and strong typing (e.g., TS types generated from OpenAPI).
- **State management**: localStorage is okay for a demo; at scale you’ll want real sessions/JWT + refresh patterns.

### Where to look
- **Backend routers**: `backend/main.py`, `backend/auth.py`, `backend/clean.py`
- **Frontend API client**: `frontend/src/services/api.js`

---

## 3) Backend skeleton: FastAPI app + routers + CORS

### What we did
The backend app is created in `backend/main.py`:

- Sets up CORS origins
- Includes `auth` and `clean` routers
- Exposes `/` and `/health`
- Initializes the DB

### What to learn / know for bigger apps
- **CORS**: in production, lock this down to the exact Vercel domain(s).
- **App initialization**: avoid doing heavy work at import time; prefer startup events.
- **Observability**: add structured logging, request IDs, and metrics early.

### Where to look
- `backend/main.py`
- `backend/config.py` (CORS and env config)

---

## 4) Environment configuration + secrets

### What we did
All important runtime configuration comes from environment variables loaded via `.env`:

- Google OAuth credentials and redirect URI
- OpenAI key (optional depending on features)
- DB connection string
- `FRONTEND_URL` / `BACKEND_URL` for correct redirects and CORS
- `ENCRYPTION_KEY` for token encryption

The backend validates required vars at import-time and fails fast if missing.

### What to learn / know for bigger apps
- **Fail fast** is good—but at scale prefer:
  - clear startup validation errors
  - environment-specific defaults
  - “configuration schema” (e.g., Pydantic settings)
- **Secret handling**: never commit `.env`. Use Railway/Vercel env settings for prod.

### Where to look
- `backend/config.py`
- `backend/generate_key.py`
- `SETUP.md`, `DEPLOYMENT.md`

---

## 5) Database: store users + OAuth tokens

### What we did
We store a `User` row with:

- `email`
- `access_token`
- `refresh_token` (encrypted before storing)
- `token_expires_at`

SQLite works locally; Railway can provide Postgres in production via `DATABASE_URL`.

### What to learn / know for bigger apps
- **Token storage** is sensitive data:
  - encrypt at rest (done here)
  - restrict DB access
  - rotate encryption keys carefully
- **Migrations**: move from “create_all” to Alembic migrations for real apps.
- **Data model evolution**: store token scopes, provider IDs, audit fields.

### Where to look
- `backend/database.py` (SQLAlchemy model + session dependency)
- `backend/utils/token_utils.py` (encryption/decryption)

---

## 6) Google OAuth: login + callback + redirect to frontend

### What we did
The OAuth flow is implemented in `backend/auth.py`:

- `/auth/google/login` creates an OAuth flow and redirects to Google
- `/auth/google/callback` exchanges the `code` for tokens
- Fetches the user’s email from Google userinfo endpoint
- Creates/updates the `User` record
- Redirects back to the frontend `FRONTEND_URL/auth/callback?success=true&email=...`

Frontend:
- Clicking login sends the user to `${VITE_API_URL}/auth/google/login`
- The `/auth/callback` route stores the email and optionally fetches `/auth/me`

### What to learn / know for bigger apps
- **State + CSRF**: production OAuth should validate `state` server-side.
- **Sessions**: passing `email` in query params is okay for a demo; at scale:
  - set an HttpOnly session cookie on callback, OR
  - mint a signed JWT for the frontend
- **Scopes & consent**: users can deny permissions; build clear UX for missing scopes.

### Where to look
- Backend OAuth: `backend/auth.py`
- Frontend login redirect: `frontend/src/context/AuthContext.jsx`
- Frontend callback handling: `frontend/src/pages/AuthCallback.jsx`
- OAuth setup notes: `backend/setup_oauth.md`

---

## 7) Gmail integration: fetch messages

### What we did
We fetch emails using the Gmail API:

- Build an authenticated Gmail client
- Fetch message IDs (`list`)
- Fetch full messages (`get`)
- Parse subject/from/snippet/body/labels

### What to learn / know for bigger apps
- **Rate limits & batching**: use Gmail batch endpoints where possible.
- **Partial data**: prefer `snippet` to reduce token usage and speed up LLM calls.
- **Reliability**: Gmail payload parsing is tricky (multipart bodies, HTML vs text).

### Where to look
- `backend/services/gmail_service.py`
- Token refresh: `backend/auth.py` (refresh logic)

---

## 8) LLM classification: prompt + batch strategy

### What we did
We classify emails into categories using OpenAI:

- Build a prompt listing categories + constraints (must return N results)
- Batch emails (default batch size 20)
- Optionally run batches concurrently (ThreadPoolExecutor)
- Parse JSON output with recovery attempts
- Return a list of classifications + a summary count per category

### What to learn / know for bigger apps
- **Prompt contracts**: always validate and guard against malformed outputs.
- **Idempotency**: store classification results if you’ll rerun or debug.
- **Cost/latency**: experiment with smaller models, fewer tokens, caching, and retries.
- **Evaluation**: create labeled test sets and measure accuracy.

### Where to look
- `backend/services/llm_service.py`

---

## 9) Gmail labels: create labels + apply via batchModify

### What we did
We apply labels to emails:

- Ensure each category label exists (create if missing)
- Assign colors from the Gmail-allowed palette
- Group emails by label
- Apply labels using `batchModify` (fast; up to 1000 IDs per call)

### What to learn / know for bigger apps
- **Idempotent label creation**: handle “already exists” vs create races.
- **Bulk operations**: always group and batch API calls.
- **Feature flags**: allow disabling label writes (dry-run mode) for safety.

### Where to look
- `backend/services/gmail_label_service.py`

---

## 10) “Clean emails” endpoint: orchestration pipeline

### What we did
The `/api/clean` endpoint is the orchestrator:

1. Validate user + count
2. Fetch emails from Gmail
3. Send to LLM classifier
4. Apply labels
5. Return classifications + summary + labeling stats

### What to learn / know for bigger apps
- **Long-running work**: at scale, this should move to a background job queue:
  - Celery/RQ/Temporal/Sidekiq-style
  - return a job ID and poll for status
- **Timeouts**: don’t block HTTP requests for minutes in production.
- **Error boundaries**: isolate failures (e.g., “labeling failed but classification succeeded”).

### Where to look
- `backend/clean.py`

---

## 11) Frontend: auth state, protected routes, dashboard, summary

### What we did
Frontend responsibilities:

- Store the user (currently in localStorage)
- Route protection for `/dashboard` and `/summary`
- Call backend endpoints and render results

### What to learn / know for bigger apps
- **Auth correctness**: localStorage-only auth is not secure; use cookies/JWT.
- **API error UX**: show actionable errors (scopes missing, rate-limited, etc.).
- **State shape**: consider React Query / SWR for caching and request state.

### Where to look
- Routing: `frontend/src/App.jsx`
- Protected route: `frontend/src/components/ProtectedRoute.jsx`
- Auth state: `frontend/src/context/AuthContext.jsx`
- Login + consent warning UI: `frontend/src/pages/Login.jsx`
- Dashboard request: `frontend/src/pages/Dashboard.jsx`
- Summary render: `frontend/src/pages/Summary.jsx`
- API client config: `frontend/src/services/api.js`

---

## 12) Deployment: Railway (backend) + Vercel (frontend)

### What we did
Deployment split:

- Backend deployed on Railway (Dockerfile / Nixpacks)
- Frontend deployed on Vercel (Vite)

We fixed common deployment pitfalls:

- Vercel env var referencing a missing Secret (removed `@vite_api_url` usage)
- Trailing slash issues in `VITE_API_URL` causing double slashes
- Missing `https://` scheme in `FRONTEND_URL` causing bad redirects
- Python runtime upgraded to avoid `importlib.metadata.packages_distributions` errors

### What to learn / know for bigger apps
- **Config drift**: keep an “env var reference” table and automate checks.
- **Release process**: add CI (tests + lint), staging environment, and rollback plan.
- **Security**: tighten CORS; set secure cookies; use proper session storage.

### Where to look
- Backend deploy:
  - `backend/Dockerfile`
  - `backend/nixpacks.toml`
  - `backend/start.sh`
  - `backend/README_DEPLOYMENT.md`
- Frontend deploy:
  - `frontend/vercel.json`
  - `frontend/README_DEPLOYMENT.md`
- Full guide:
  - `DEPLOYMENT.md`

---

## 13) “What I should learn next” (roadmap for scaling)

If you want to build larger-scale apps, prioritize these next:

### Authentication & Security
- Proper OAuth `state` validation and CSRF protection
- HttpOnly cookie sessions or JWT auth
- Permissions/scopes auditing and “missing scope” UX

### Backend reliability & scaling
- Background jobs for long tasks (queue + worker)
- Retries, idempotency, and structured logging
- Metrics + tracing (OpenTelemetry)

### Data & migrations
- Alembic migrations
- Better schema design (provider accounts, scopes, refresh rotation)

### Testing
- Unit tests for services (Gmail parsing, LLM output parsing)
- Integration tests for OAuth callback + `/api/clean`
- Mocking external APIs (Google/OpenAI)

### Frontend architecture
- API state management (React Query)
- Better error UX and loading states
- Type safety (TypeScript) + generated API types

---

## 14) Suggested “study order” (fastest way to understand the code)

If you read files in this order, it will click quickly:

1. `backend/main.py` - DONE
2. `backend/config.py` - DONE
3. `backend/database.py` - DONE
4. `backend/auth.py` - don't fully understand but come back to it once looking to change the logic to cookies
5. `backend/services/gmail_service.py` - DONE
6. `backend/services/llm_service.py` - skimmed
7. `backend/services/gmail_label_service.py` - skimmed
8. `backend/clean.py` - DONE
9. `frontend/src/services/api.js` - DONE
10. `frontend/src/context/AuthContext.jsx` - skimmed
11. `frontend/src/pages/Login.jsx` - 
12. `frontend/src/pages/AuthCallback.jsx` - 
13. `frontend/src/pages/Dashboard.jsx` - 
14. `frontend/src/pages/Summary.jsx` - 


