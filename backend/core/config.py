# backend/core/config.py

from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Database paths
    FINANCE_DB_PATH: Path = DATA_DIR / "finance.db"
    TEMPLATES_DB_PATH: Path = DATA_DIR / "templates.db"
    
    # API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # WebSocket settings
    WS_HEALTH_CHECK_INTERVAL: int = 30  # seconds
    WS_PING_TIMEOUT: int = 10  # seconds
    
    # Scheduler settings
    SCHEDULER_INTERVAL: int = 60  # seconds
    MAX_RESULTS_AGE: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings