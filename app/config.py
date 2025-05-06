import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    APP_NAME: str = "Conference Registration System"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "sqlite:///./conference.db"
    )
    
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()