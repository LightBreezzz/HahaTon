from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hahaton"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Admin
    ADMIN_EMAIL: str = "admin@hahaton.ru"
    ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"


settings = Settings()
