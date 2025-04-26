"""Configuration models for Text2SQL."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    type: str = Field(..., description="Database type")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    schema: str = Field(default="public", description="Database schema")
    ssl_mode: Optional[str] = Field(default=None, description="SSL mode for connection")
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Maximum number of connections")


class LLMConfig(BaseModel):
    """LLM configuration."""
    model_name: str = Field(..., description="Name of the LLM model")
    api_key: str = Field(..., description="API key for LLM service")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    max_tokens: int = Field(default=1000, description="Maximum tokens in response")
    timeout: int = Field(default=30, description="API request timeout in seconds")
    additional_params: Dict[str, Any] = Field(default_factory=dict, description="Additional model parameters")


class Text2SQLConfig(BaseSettings):
    """Main configuration for Text2SQL component."""
    database: DatabaseConfig = Field(..., description="Database configuration")
    llm: LLMConfig = Field(..., description="LLM configuration")
    cache_schema: bool = Field(default=True, description="Whether to cache database schema")
    schema_cache_ttl: int = Field(default=3600, description="Schema cache TTL in seconds")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "TEXT2SQL_"
        case_sensitive = False 