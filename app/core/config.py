from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Tender Intel"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str
    DATABASE_NAME: str = "tender_intel"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email (Gmail)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Tender Intel"

    # Scraping
    SCRAPING_TIMEOUT: int = 30
    MAX_CONCURRENT_SCRAPES: int = 5
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    # Notifications
    ENABLE_DESKTOP_NOTIFICATIONS: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True

    # Scheduler
    SCHEDULER_TIMEZONE: str = "US/Eastern"
    DEFAULT_FETCH_INTERVAL_HOURS: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()