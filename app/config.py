import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Conference Registration System"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "sqlite:///./conference.db"
    )
    
    CORS_ORIGINS: List[str] = ["*"]
    
    LOGIN_RATE_LIMIT: int = 5
    
    USE_HTTPS: bool = os.environ.get("USE_HTTPS", "false").lower() == "true"
    
    # Email settings
    EMAIL_HOST: str = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USERNAME: str = os.environ.get("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "noreply@conference.com")
    EMAIL_USE_TLS: bool = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
    
    # Password reset settings
    RESET_TOKEN_EXPIRE_MINUTES: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()