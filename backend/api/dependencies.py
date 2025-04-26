# backend/api/dependencies.py

from functools import lru_cache
from ..services.text2sql_service import Text2SQLService
from ..core.config import Settings

@lru_cache()
def get_text2sql_service(settings: Settings = Depends(get_settings)) -> Text2SQLService:
    return Text2SQLService(
        db_path=settings.database_path,
        openai_api_key=settings.openai_api_key
    )