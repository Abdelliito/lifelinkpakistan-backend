import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.exceptions import APIError, api_error_handler, generic_error_handler, validation_error_handler
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.db.seed import seed
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Import models so they're registered on Base's metadata before create_all runs.
from app.models import BloodRequest, Donor, User  # noqa: F401

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")
    init_db()
    if settings.SEED_ON_STARTUP:
        logger.warning("SEED_ON_STARTUP is enabled - seeding database with demo data")
        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()
    yield
    logger.info("Shutting down application")


is_prod = settings.ENVIRONMENT.lower() == "production"

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for LifeLink Pakistan — AI-Assisted Blood Donor Network.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
)

# Add custom exception handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middlewares (order matters - should be near the top)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {"status": "ok", "service": settings.APP_NAME, "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

