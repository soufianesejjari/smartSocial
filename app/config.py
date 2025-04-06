from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    # API Keys
    FACEBOOK_PAGE_ACCESS_TOKEN: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # LLM Settings
    MODEL_NAME: str = "qwen-2.5-32b"
    MAX_TOKENS: int = 4048
    TEMPERATURE: float = 0.5
    
    # App Settings
    MONGODB_URI: str = "mongodb://localhost:27017/smartsocial"
    
    # MongoDB settings
    MONGODB_DB: str = "smartsocial"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USERNAME: str = ""  # Add if authentication is required
    MONGODB_PASSWORD: str = ""  # Add if authentication is required
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        validate_assignment = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
