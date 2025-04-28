# backend/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    database_path: str   = "path/to/your/database.db"
    openai_api_key: str  = Field(..., env='OPENAI_API_KEY')
    openai_model: str    = Field('gpt-4o-mini', env='OPENAI_MODEL')
    openai_api_base: str = Field('https://api.openai.com/v1', env='OPENAI_API_BASE')

    class Config:
        env_file = ".env"

    def __hash__(self):
        return hash((self.database_path, self.openai_api_key))

@lru_cache()
def get_settings() -> Settings:
    return Settings()