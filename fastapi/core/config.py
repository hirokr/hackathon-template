# core/config.py — Pydantic settings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/template_dev"
    SESSION_SECRET: str = "change_me"
    SESSION_MAX_AGE: int = 86400

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    META_CLIENT_ID: str = ""
    META_CLIENT_SECRET: str = ""
    META_REDIRECT_URI: str = "http://localhost:8000/auth/facebook/callback"

    CLIENT_URL: str = "http://localhost:3000"


settings = Settings()
