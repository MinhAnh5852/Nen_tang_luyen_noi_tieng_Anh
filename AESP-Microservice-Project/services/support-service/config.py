import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Support Service"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    PORT: int = int(os.getenv("PORT", 8002))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/support_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "support-secret-key")
    
    class Config:
        env_file = ".env"

settings = Settings()