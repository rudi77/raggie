from typing import Dict, Any
from smolagents import (
    CodeAgent,
    LiteLLMModel,
    ToolCallingAgent
)

from .tools import Text2SQLTool
def create_manager_agent(model: str = "gpt-4o-mini", api_key: str = None) -> CodeAgent:
    return CodeAgent(
        tools=[],
        model=LiteLLMModel(model=model, api_key=api_key),
        managed_agents=[create_text2sql_agent(model=LiteLLMModel(model=model, api_key=api_key), api_key=api_key)]
    )

def create_text2sql_agent(model: LiteLLMModel, db_path: str, api_key: str) -> ToolCallingAgent:
    return ToolCallingAgent(
        model=model,
        tools=[Text2SQLTool(db_path=db_path, openai_api_key=api_key)],
        name="Text2SQLAgent",
        description="This agent converts natural language questions into SQL queries and executes them on a database."
    )


