from typing import Dict, Any, List
from smolagents import (
    CodeAgent,
    LiteLLMModel,
    ToolCallingAgent
)

from .tools import Text2SQLTool
def create_manager_agent(model: LiteLLMModel, managed_agents: List[ToolCallingAgent]) -> CodeAgent:
    return CodeAgent(
        tools=[],
        model=model,
        managed_agents=managed_agents,
        planning_interval=2
    )

def create_text2sql_agent(model: LiteLLMModel, db_path: str, api_key: str) -> ToolCallingAgent:
    text2sql_agent = ToolCallingAgent(
        model=model,
        tools=[Text2SQLTool(db_path=db_path, openai_api_key=api_key)],
        name="Text2SQLAgent",
        description="This agent converts natural language questions into SQL queries and executes them on a database.",
        planning_interval=0,        
    )

    text2sql_agent.prompt_templates["system_prompt"] = """
    You are a helpful assistant that converts natural language questions into SQL queries and executes them on a database.
    Therefore you have a single tool to use: Text2SQLTool.

    Do not use any other tools.
    Do not plan, just use the tool.

    Return the result as a JSON string and nothing else.
    """

    text2sql_agent.prompt_templates["planning"] = "Do not plan, just use the tool."
    text2sql_agent.prompt_templates["task"] = "{{question}}"

    print(text2sql_agent.prompt_templates)

    return text2sql_agent


