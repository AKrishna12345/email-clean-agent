from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import config
from database import init_db
from auth import router as auth_router
from clean import router as clean_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Email Clean Agent API",
    description="API for cleaning Gmail inboxes with AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(clean_router)


@app.get("/")
async def root():
    return {"message": "Email Clean Agent API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

