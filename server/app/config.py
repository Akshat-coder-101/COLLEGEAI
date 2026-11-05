import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "HypothesisLab AI"
    API_V1_STR: str = "/api/v1"
    
    # LLM & AI Models
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    # Database
    DATABASE_URL: str = "sqlite:///./hypothesis_lab.db"
    
    # External APIs
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    
    # Storage & Uploads
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Simulation Settings
    MAX_SIMULATION_ITERATIONS: int = 3
    SIMULATION_TIMEOUT: int = 60  # seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure uploads directory exists
upload_path = Path(settings.UPLOAD_DIRECTORY)
upload_path.mkdir(parents=True, exist_ok=True)
