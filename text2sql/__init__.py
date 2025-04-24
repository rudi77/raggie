"""Text2SQL - Convert natural language to SQL queries."""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .agent.sql_agent import SQLAgent
from .core.config import DatabaseConfig, LLMConfig, Text2SQLConfig
from .core.exceptions import (
    ConnectionError,
    QueryExecutionError,
    QueryGenerationError,
    SchemaError,
    Text2SQLError,
)
from .core.sqlite import SQLiteConnector, SQLiteExecutor, SQLiteSchemaLoader
from .formatters.factory import FormatterFactory

# Global configuration
_config_path = Path.home() / ".text2sql" / "config.json"
_config: Optional[Text2SQLConfig] = None


def _load_config() -> Text2SQLConfig:
    """Load configuration from file or create default."""
    global _config
    
    if _config is not None:
        return _config
        
    if _config_path.exists():
        try:
            with open(_config_path, "r") as f:
                config_data = json.load(f)
                _config = Text2SQLConfig(**config_data)
                return _config
        except Exception as e:
            raise Text2SQLError(f"Error loading config: {str(e)}")
    
    # Create default config
    _config = Text2SQLConfig(
        database=DatabaseConfig(
            type="sqlite",
            path=":memory:",
            username="",
            password="",
            host="",
            port=0,
        ),
        llm=LLMConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            max_tokens=1000,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            timeout=30,
        ),
        output_format="text",
    )
    
    # Save default config
    _config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(_config_path, "w") as f:
            json.dump(_config.dict(), f, indent=2)
    except Exception as e:
        # Just log the warning, don't fail
        print(f"Warning: Could not save default config: {str(e)}")
    
    return _config


def _save_config() -> None:
    """Save current configuration to file."""
    global _config
    
    if _config is None:
        return
        
    _config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(_config_path, "w") as f:
            json.dump(_config.dict(), f, indent=2)
    except Exception as e:
        raise Text2SQLError(f"Error saving config: {str(e)}")


async def _initialize_components():
    """Initialize database and agent components."""
    cfg = _load_config()
    
    # Initialize database components
    if cfg.database.type == "sqlite":
        connector = SQLiteConnector(cfg.database)
        executor = SQLiteExecutor(connector)
    else:
        raise ConnectionError(f"Unsupported database type: {cfg.database.type}")
    
    # Get database URL
    db_url = connector.get_connection_string()
    
    # Initialize agent with database URL
    agent = SQLAgent(db_url=db_url, llm=cfg.llm)
    
    return agent, executor


class QueryResult:
    """Result of a query execution."""
    
    def __init__(self, sql: str, result: Any, formatted_result: str):
        """Initialize the query result.
        
        Args:
            sql: The SQL query that was executed.
            result: The raw query result.
            formatted_result: The formatted query result.
        """
        self.sql = sql
        self.result = result
        self.formatted_result = formatted_result


async def query(nl: str, format_type: Optional[str] = None) -> QueryResult:
    """Convert a natural language question to SQL and execute it.
    
    Args:
        nl: The natural language question.
        format_type: The output format (text, json, csv). If None, uses the configured format.
        
    Returns:
        A QueryResult object containing the SQL, raw result, and formatted result.
        
    Raises:
        QueryGenerationError: If SQL generation fails.
        QueryExecutionError: If SQL execution fails.
        Text2SQLError: For other errors.
    """
    try:
        # Load config and override format if specified
        cfg = _load_config()
        if format_type:
            cfg.output_format = format_type
            
        # Initialize components
        agent, executor = await _initialize_components()
        
        # Generate SQL
        sql = await agent.generate_sql(nl)
        
        # Execute SQL
        result = await executor.execute(sql)
        
        # Format result
        formatter = FormatterFactory.create(cfg.output_format)
        formatted_result = await formatter.format(result)
        
        return QueryResult(sql, result, formatted_result)
        
    except QueryGenerationError as e:
        raise QueryGenerationError(f"Error generating SQL: {str(e)}")
    except QueryExecutionError as e:
        raise QueryExecutionError(f"Error executing SQL: {str(e)}")
    except Text2SQLError as e:
        raise Text2SQLError(f"Error: {str(e)}")


async def explain(nl: str) -> str:
    """Show the SQL that would be generated for a question without executing it.
    
    Args:
        nl: The natural language question.
        
    Returns:
        The generated SQL query.
        
    Raises:
        QueryGenerationError: If SQL generation fails.
        Text2SQLError: For other errors.
    """
    try:
        # Initialize components
        agent, _ = await _initialize_components()
        
        # Generate SQL
        sql = await agent.generate_sql(nl)
        
        return sql
        
    except QueryGenerationError as e:
        raise QueryGenerationError(f"Error generating SQL: {str(e)}")
    except Text2SQLError as e:
        raise Text2SQLError(f"Error: {str(e)}")


def configure(config: Union[Text2SQLConfig, Dict[str, Any]]) -> None:
    """Configure Text2SQL settings.
    
    Args:
        config: A Text2SQLConfig object or a dictionary with configuration values.
        
    Raises:
        Text2SQLError: If configuration fails.
    """
    global _config
    
    try:
        if isinstance(config, dict):
            # Update existing config with new values
            current_config = _load_config()
            for key, value in config.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            _config = current_config
        else:
            # Use the provided config
            _config = config
            
        # Save the updated config
        _save_config()
        
    except Exception as e:
        raise Text2SQLError(f"Error configuring Text2SQL: {str(e)}")


# For convenience, provide synchronous versions of the async functions
def query_sync(nl: str, format_type: Optional[str] = None) -> QueryResult:
    """Synchronous version of query."""
    return asyncio.run(query(nl, format_type))


def explain_sync(nl: str) -> str:
    """Synchronous version of explain."""
    return asyncio.run(explain(nl))


__all__ = [
    "query",
    "query_sync",
    "explain",
    "explain_sync",
    "configure",
    "QueryResult",
    "Text2SQLConfig",
    "DatabaseConfig",
    "LLMConfig",
]
