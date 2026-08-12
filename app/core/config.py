import logging
import secrets
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_INSECURE_DEFAULT_KEY = "CHANGE_ME_IN_PRODUCTION_a8f5f167f44f4964e6c998dee827110c"


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are read from environment variables / a `.env` file at the
    project root. See `.env.example` for the full list of supported keys.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "LifeLink Pakistan API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./lifelink.db"

    # Auth / JWT
    SECRET_KEY: str = _INSECURE_DEFAULT_KEY
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS - frontend origins allowed to call this API.
    # In production, set CORS_ORIGINS as a comma-separated string:
    #   CORS_ORIGINS=https://lifelinkpakistan.com,https://www.lifelinkpakistan.com
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Seeding — disabled by default; set SEED_ON_STARTUP=true for local dev
    SEED_ON_STARTUP: bool = False

    # AI / Gemini
    GEMINI_API_KEY: str = ""
    AI_MAX_INPUT_LENGTH: int = 2000  # max chars for AI parse input

    # Rate limiting (requests per minute for AI endpoint)
    RATE_LIMIT: str = "10/minute"

    @model_validator(mode="after")
    def _validate_production_settings(self) -> "Settings":
        is_prod = self.ENVIRONMENT.lower() == "production"

        if is_prod and self.SECRET_KEY == _INSECURE_DEFAULT_KEY:
            raise ValueError(
                "FATAL: SECRET_KEY must be set to a secure random value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        if not is_prod and self.SECRET_KEY == _INSECURE_DEFAULT_KEY:
            logger.warning(
                "Using default SECRET_KEY — this is fine for development but MUST be "
                "changed before deploying to production."
            )

        if is_prod and self.DATABASE_URL.startswith("sqlite"):
            logger.warning(
                "SQLite is not recommended for production. "
                "Set DATABASE_URL to a PostgreSQL connection string."
            )

        if is_prod and self.SEED_ON_STARTUP:
            logger.warning(
                "SEED_ON_STARTUP is enabled in production — demo accounts with "
                "known passwords will be created. Consider disabling this."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
