"""Command-line interface for Text2SQL."""
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..agent.sql_agent import SQLAgent
from ..core.config import DatabaseConfig, LLMConfig, Text2SQLConfig
from ..core.exceptions import (
    ConnectionError,
    QueryExecutionError,
    QueryGenerationError,
    SchemaError,
    Text2SQLError,
)
from ..core.schema import DatabaseSchema
from ..core.sqlite import SQLiteConnector, SQLiteExecutor, SQLiteSchemaLoader
from ..formatters.factory import FormatterFactory

# Initialize Typer app
app = typer.Typer(
    name="t2s",
    help="Text2SQL - Convert natural language to SQL queries",
    add_completion=False,
)

# Initialize Rich console
console = Console()

# Global configuration
config_path = Path.home() / ".text2sql" / "config.json"
config: Optional[Text2SQLConfig] = None


def load_config() -> Text2SQLConfig:
    """Load configuration from file or create default."""
    global config
    
    if config is not None:
        return config
        
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
                config = Text2SQLConfig(**config_data)
                return config
        except Exception as e:
            console.print(f"[red]Error loading config: {str(e)}[/red]")
    
    # Create default config
    config = Text2SQLConfig(
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
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_path, "w") as f:
            json.dump(config.dict(), f, indent=2)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save default config: {str(e)}[/yellow]")
    
    return config


def save_config() -> None:
    """Save current configuration to file."""
    global config
    
    if config is None:
        return
        
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_path, "w") as f:
            json.dump(config.dict(), f, indent=2)
        console.print("[green]Configuration saved successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Error saving config: {str(e)}[/red]")


async def initialize_components():
    """Initialize database and agent components."""
    cfg = load_config()
    
    # Initialize database components
    if cfg.database.type == "sqlite":
        connector = SQLiteConnector(cfg.database)
        schema_loader = SQLiteSchemaLoader(connector)
        executor = SQLiteExecutor(connector)
    else:
        raise ConnectionError(f"Unsupported database type: {cfg.database.type}")
    
    # Load schema
    schema = await schema_loader.load_schema()
    
    # Initialize agent
    agent = SQLAgent(cfg.llm)
    
    # Initialize query engine
    sql_database = connector.get_sql_database()
    agent._initialize_query_engine(sql_database)
    
    return agent, executor, schema


@app.command()
def query(
    question: str = typer.Argument(..., help="Natural language question to convert to SQL"),
    format: str = typer.Option(None, "--format", "-f", help="Output format (text, json, csv)"),
):
    """Convert a natural language question to SQL and execute it."""
    try:
        # Load config and override format if specified
        cfg = load_config()
        if format:
            cfg.output_format = format
            
        # Initialize components
        agent, executor, schema = asyncio.run(initialize_components())
        
        # Generate SQL
        sql = asyncio.run(agent.generate_sql(question, schema))
        
        # Execute SQL
        result = asyncio.run(executor.execute(sql))
        
        # Format result
        formatter = FormatterFactory.create(cfg.output_format)
        formatted_result = asyncio.run(formatter.format(result))
        
        # Display result
        console.print(Panel(formatted_result, title="Query Result", border_style="green"))
        
    except QueryGenerationError as e:
        console.print(f"[red]Error generating SQL: {str(e)}[/red]")
    except QueryExecutionError as e:
        console.print(f"[red]Error executing SQL: {str(e)}[/red]")
    except Text2SQLError as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.command()
def explain(
    question: str = typer.Argument(..., help="Natural language question to explain"),
):
    """Show the SQL that would be generated for a question without executing it."""
    try:
        # Initialize components
        agent, _, schema = asyncio.run(initialize_components())
        
        # Generate SQL
        sql = asyncio.run(agent.generate_sql(question, schema))
        
        # Display SQL
        console.print(Panel(sql, title="Generated SQL", border_style="blue"))
        
    except QueryGenerationError as e:
        console.print(f"[red]Error generating SQL: {str(e)}[/red]")
    except Text2SQLError as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.command()
def status():
    """Check database connection and configuration status."""
    try:
        # Load config
        cfg = load_config()
        
        # Create status table
        table = Table(title="Text2SQL Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Check config
        config_exists = config_path.exists()
        table.add_row(
            "Configuration",
            "✓" if config_exists else "✗",
            str(config_path) if config_exists else "Default config will be created",
        )
        
        # Check database
        if cfg.database.type == "sqlite":
            db_path = cfg.database.path
            db_exists = db_path == ":memory:" or Path(db_path).exists()
            table.add_row(
                "Database",
                "✓" if db_exists else "✗",
                f"SQLite: {db_path}",
            )
        else:
            table.add_row(
                "Database",
                "✗",
                f"Unsupported type: {cfg.database.type}",
            )
        
        # Check LLM
        api_key = cfg.llm.api_key
        api_key_set = bool(api_key)
        table.add_row(
            "LLM API Key",
            "✓" if api_key_set else "✗",
            "Set" if api_key_set else "Not set (set OPENAI_API_KEY env var)",
        )
        
        # Display table
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error checking status: {str(e)}[/red]")


@app.command()
def config(
    db_type: Optional[str] = typer.Option(None, "--db-type", help="Database type (sqlite)"),
    db_path: Optional[str] = typer.Option(None, "--db-path", help="Database path (for SQLite)"),
    model: Optional[str] = typer.Option(None, "--model", help="LLM model name"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="LLM API key"),
    format: Optional[str] = typer.Option(None, "--format", help="Output format (text, json, csv)"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
):
    """Configure Text2SQL settings."""
    try:
        # Load current config
        cfg = load_config()
        
        # Show current config if requested
        if show:
            console.print(Panel(json.dumps(cfg.dict(), indent=2), title="Current Configuration"))
            return
        
        # Update config with provided values
        if db_type:
            cfg.database.type = db_type
        if db_path:
            cfg.database.path = db_path
        if model:
            cfg.llm.model_name = model
        if api_key:
            cfg.llm.api_key = api_key
        if format:
            cfg.output_format = format
            
        # Save updated config
        save_config()
        
        # Show updated config
        console.print(Panel(json.dumps(cfg.dict(), indent=2), title="Updated Configuration"))
        
    except Exception as e:
        console.print(f"[red]Error updating configuration: {str(e)}[/red]")


if __name__ == "__main__":
    app()
