# backend/api/dependencies.py

from smolagents import LiteLLMModel, CodeAgent
from fastapi import Depends
from ..services.text2sql_service import Text2SQLService
from ..core.config import get_settings, Settings
from ..agents import create_manager_agent, create_text2sql_agent

def get_text2sql_service(settings: Settings = Depends(get_settings)) -> Text2SQLService:
    return Text2SQLService(
        db_path=settings.DATABASE_PATH,
        openai_api_key=settings.OPENAI_API_KEY
    )

def get_manager_agent(settings: Settings = Depends(get_settings)) -> CodeAgent:
    model = LiteLLMModel(
        model_id=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        api_base=settings.OPENAI_API_BASE
    )

    text2sql_agent = create_text2sql_agent(
        model=model,
        db_path=settings.DATABASE_PATH,
        api_key=settings.OPENAI_API_KEY
    )
    
    # agent = create_manager_agent(model, [text2sql_agent])
    # return agent
    return text2sql_agent