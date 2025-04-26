# backend/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_path: str = "path/to/your/database.db"
    openai_api_key: str

    class Config:
        env_file = ".env"

    def __hash__(self):
        return hash((self.database_path, self.openai_api_key))

@lru_cache()
def get_settings() -> Settings:
    return Settings()