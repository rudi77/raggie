# backend/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_path: str = "path/to/your/database.db"
    openai_api_key: str

    class Config:
        env_file = ".env"