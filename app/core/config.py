from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_a8f5f167f44f4964e6c998dee827110c"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS - frontend origins allowed to call this API
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Seeding
    SEED_ON_STARTUP: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
