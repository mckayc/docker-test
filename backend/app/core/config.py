from pydantic_settings import BaseSettings
from typing import List
import secrets
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Donegeon"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js frontend in development
        "http://localhost:5485",  # Production frontend
    ]
    
    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = "sqlite:///./task_donegeon.db"
    
    # File Storage
    BASE_PATH: str = "/data"
    UPLOAD_FOLDER: str = f"{BASE_PATH}/uploads"
    MAX_UPLOAD_SIZE: int = 16 * 1024 * 1024  # 16MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s"
    LOG_FILE: str = f"{BASE_PATH}/config/app.log"
    AUDIT_LOG_FILE: str = f"{BASE_PATH}/config/audit.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 