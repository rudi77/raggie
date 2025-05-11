import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    chroma_db_path: str = "C:/Users/rudi/source/gpt-o4-mini/data/chroma"
    database_path: str = "C:/Users/rudi/source/repos/raggie/test.db"  # Hinzugefügt

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Erlaubt zusätzliche Felder