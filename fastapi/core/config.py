# core/config.py — Pydantic settings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/template_dev"
    SESSION_SECRET: str = "change_me"
    SESSION_MAX_AGE: int = 86400
    SESSION_COOKIE_SECURE: bool = False

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    META_CLIENT_ID: str = ""
    META_CLIENT_SECRET: str = ""
    META_REDIRECT_URI: str = "http://localhost:8000/auth/facebook/callback"

    CLIENT_URL: str = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"

    JWT_SECRET: str = "change_me_access_secret"
    REFRESH_JWT_SECRET: str = "change_me_refresh_secret"
    JWT_EXPIRES_IN: str = "5m"
    REFRESH_JWT_EXPIRES_IN: str = "15d"

    ACCESS_TOKEN_COOKIE_NAME: str = "accessToken"
    REFRESH_TOKEN_COOKIE_NAME: str = "refreshToken"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "strict"
    COOKIE_DOMAIN: str | None = None

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    EMAIL_HOST: str = "smtp.example.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "no-reply@example.com"
    SUPPORT_EMAIL: str = "support@example.com"


settings = Settings()
