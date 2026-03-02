"""
Application Configuration
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "InsightGenius"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/insightgenius"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/insightgenius"
    
    # Redis (for caching & Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Email (for automated reports)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "InsightGenius <reports@insightgenius.com>"
    
    # AI/ML APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # ML Model Paths
    MODEL_CACHE_DIR: str = "./models"
    
    # Feature Flags
    ENABLE_ANOMALY_DETECTION: bool = True
    ENABLE_NLP_QUERIES: bool = True
    ENABLE_AUTO_REPORTS: bool = True
    ENABLE_REALTIME_ALERTS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
