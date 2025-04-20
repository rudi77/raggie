from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    openai_api_key: str
    chroma_db_path: str = "C:/Users/rudi/source/gpt-o4-mini/data/chroma"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8" 