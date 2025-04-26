from typing import Optional, Any
from text2sql import (
    query,
    explain,
    configure,
    Text2SQLConfig,
    DatabaseConfig,
    LLMConfig,
    QueryResult
)

class Text2SQLService:
    def __init__(self, db_path: str, openai_api_key: str):
        """Initialize Text2SQL service with configuration."""
        # Configure Text2SQL with your settings
        config = Text2SQLConfig(
            database=DatabaseConfig(
                type="sqlite",
                path=db_path,
                database=db_path,
                username="",
                password="",
                host="",
                port=0,
            ),
            llm=LLMConfig(
                model_name="gpt-4o-mini",
                temperature=0.0,
                max_tokens=1000,
                api_key=openai_api_key,
                timeout=30,
            )
        )
        configure(config)

    async def query(self, question: str, output_format: Optional[str] = None) -> QueryResult:
        """Execute a natural language query."""
        return await query(question, output_format)

    async def explain(self, question: str) -> str:
        """Get SQL explanation for a question without executing it."""
        return await explain(question)