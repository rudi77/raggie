# backend/api/dependencies.py

from smolagents import LiteLLMModel, CodeAgent
from fastapi import Depends
from ..services.text2sql_service import Text2SQLService
from ..core.config import get_settings, Settings
from ..agents import create_manager_agent, create_text2sql_agent

def get_text2sql_service(settings: Settings = Depends(get_settings)) -> Text2SQLService:
    return Text2SQLService(
        db_path=settings.database_path,
        openai_api_key=settings.openai_api_key
    )

def get_manager_agent(settings: Settings = Depends(get_settings)) -> CodeAgent:

    model = LiteLLMModel(
        model_id=settings.openai_model,
        api_key=settings.openai_api_key,
        api_base=settings.openai_api_base
    )

    text2sql_agent = create_text2sql_agent(
        model=model,
        db_path=settings.database_path,
        api_key=settings.openai_api_key
    )
    
    # agent = create_manager_agent(model, [text2sql_agent])
    # return agent
    return text2sql_agent