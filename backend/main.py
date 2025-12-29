from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import config
from database import init_db
from auth import router as auth_router
from clean import router as clean_router

# Rate limiting (optional - only if slowapi is installed)
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    print("⚠️  slowapi not installed - rate limiting disabled")

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Email Clean Agent API",
    description="API for cleaning Gmail inboxes with AI",
    version="1.0.0"
)

# Initialize rate limiter (if available)
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
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
    return {
        "status": "healthy",
        "environment": config.ENVIRONMENT,
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if config.IS_PRODUCTION:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "status": "error"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body}
        )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    if config.IS_PRODUCTION:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "status": "error"}
        )
    else:
        import traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "traceback": traceback.format_exc()}
        )
