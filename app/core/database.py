import logging
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    pass


def init_db() -> None:
    """Create all tables. Logs a warning in production — prefer Alembic migrations."""
    if settings.ENVIRONMENT.lower() == "production":
        logger.warning(
            "Running Base.metadata.create_all() in production. "
            "Consider using 'alembic upgrade head' for schema migrations instead."
        )
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """FastAPI dependency that yields a database session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

