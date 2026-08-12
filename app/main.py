from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.rate_limit import limiter
from app.db.seed import seed

# Import models so they're registered on Base's metadata before create_all runs.
from app.models import BloodRequest, Donor, User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.SEED_ON_STARTUP:
        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()
    yield


is_prod = settings.ENVIRONMENT.lower() == "production"

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for LifeLink Pakistan — AI-Assisted Blood Donor Network.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "healthy"}

