"""Tests for the SQL agent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from text2sql.agent.sql_agent import SQLAgent
from text2sql.core.config import LLMConfig
from text2sql.core.schema import Column, Table, DatabaseSchema


@pytest.fixture
def sample_schema():
    """Create a sample database schema for testing."""
    users_table = Table(
        name="users",
        columns=[
            Column(name="id", data_type="INTEGER", is_primary=True),
            Column(name="name", data_type="TEXT", is_nullable=False),
            Column(name="email", data_type="TEXT", is_nullable=True),
            Column(name="created_at", data_type="TIMESTAMP", is_nullable=True)
        ],
        primary_keys=["id"],
        description="User information"
    )
    
    posts_table = Table(
        name="posts",
        columns=[
            Column(name="id", data_type="INTEGER", is_primary=True),
            Column(name="user_id", data_type="INTEGER", is_nullable=False, is_foreign=True, references="users.id"),
            Column(name="title", data_type="TEXT", is_nullable=False),
            Column(name="content", data_type="TEXT", is_nullable=True),
            Column(name="created_at", data_type="TIMESTAMP", is_nullable=True)
        ],
        primary_keys=["id"],
        foreign_keys=["user_id"],
        description="User posts"
    )
    
    return DatabaseSchema(
        tables=[users_table, posts_table],
        relationships=[
            {
                "from_table": "posts",
                "to_table": "users",
                "from_column": "user_id",
                "to_column": "id",
                "type": "many_to_one"
            }
        ]
    )


@pytest.fixture
def llm_config():
    """Create a sample LLM configuration."""
    return LLMConfig(
        model_name="gpt-3.5-turbo",
        api_key="test-api-key",
        temperature=0.0,
        max_tokens=1000,
        timeout=30
    )


@pytest.mark.asyncio
async def test_sql_agent_initialization(llm_config):
    """Test SQL agent initialization."""
    with patch("langchain.chat_models.ChatOpenAI") as mock_chat:
        mock_chat.return_value = MagicMock()
        agent = SQLAgent(llm_config)
        
        assert agent.llm_config == llm_config
        assert len(agent.examples) == 4  # We have 4 examples


@pytest.mark.asyncio
async def test_generate_sql(llm_config, sample_schema):
    """Test SQL generation."""
    expected_sql = "SELECT name FROM users"
    
    with patch("langchain.chat_models.ChatOpenAI") as mock_chat:
        mock_response = MagicMock()
        mock_response.content = expected_sql
        mock_chat.return_value.ainvoke = AsyncMock(return_value=mock_response)
        
        agent = SQLAgent(llm_config)
        
        # Mock the validate_sql method to always return True
        agent.validate_sql = AsyncMock(return_value=True)
        
        result = await agent.generate_sql(
            natural_query="What are the names of all users?",
            schema=sample_schema
        )
        
        assert result == expected_sql


@pytest.mark.asyncio
async def test_validate_sql(llm_config, sample_schema):
    """Test SQL validation."""
    agent = SQLAgent(llm_config)
    
    # Valid SQL
    valid_sql = "SELECT name FROM users"
    assert await agent.validate_sql(valid_sql, sample_schema) is True
    
    # Invalid SQL - table doesn't exist
    invalid_sql = "SELECT name FROM nonexistent_table"
    assert await agent.validate_sql(invalid_sql, sample_schema) is False
    
    # Valid SQL with JOIN
    valid_join_sql = """
    SELECT p.title, u.name
    FROM posts p
    JOIN users u ON p.user_id = u.id
    """
    assert await agent.validate_sql(valid_join_sql, sample_schema) is True


@pytest.mark.asyncio
async def test_generate_sql_error_handling(llm_config, sample_schema):
    """Test error handling in SQL generation."""
    with patch("langchain.chat_models.ChatOpenAI") as mock_chat:
        mock_chat.return_value.ainvoke = AsyncMock(side_effect=Exception("LLM error"))
        
        agent = SQLAgent(llm_config)
        
        with pytest.raises(Exception) as excinfo:
            await agent.generate_sql(
                natural_query="What are the names of all users?",
                schema=sample_schema
            )
        
        assert "Failed to generate SQL" in str(excinfo.value) 