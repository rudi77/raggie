"""Tests for SQLite implementations."""
import os
import pytest
import aiosqlite
from text2sql.core.sqlite import SQLiteConnector, SQLiteExecutor


@pytest.fixture
async def test_db_path(tmp_path):
    """Create a test database with sample tables."""
    db_path = tmp_path / "test.db"
    
    async with aiosqlite.connect(db_path) as conn:
        # Create test tables
        await conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insert sample data
        await conn.execute("""
            INSERT INTO users (name, email) VALUES
            ('Alice', 'alice@example.com'),
            ('Bob', 'bob@example.com')
        """)
        
        await conn.execute("""
            INSERT INTO posts (user_id, title, content) VALUES
            (1, 'First Post', 'Hello World'),
            (1, 'Second Post', 'More content'),
            (2, 'Bob''s Post', 'My first post')
        """)
        
        await conn.commit()
    
    return str(db_path)


@pytest.mark.asyncio
async def test_sqlite_connector(test_db_path):
    """Test SQLite connector functionality."""
    connector = SQLiteConnector()
    
    # Test connection
    await connector.connect(test_db_path)
    assert await connector.is_connected()
    
    # Test schema loading
    schema = await connector.get_schema()
    assert len(schema.tables) == 2
    assert schema.tables[0].name in ['users', 'posts']
    assert schema.tables[1].name in ['users', 'posts']
    
    # Verify relationships
    assert len(schema.relationships) == 1
    rel = schema.relationships[0]
    assert rel['from_table'] == 'posts'
    assert rel['to_table'] == 'users'
    assert rel['from_column'] == 'user_id'
    assert rel['to_column'] == 'id'
    
    # Test disconnection
    await connector.disconnect()
    assert not await connector.is_connected()


@pytest.mark.asyncio
async def test_sqlite_executor(test_db_path):
    """Test SQLite executor functionality."""
    connector = SQLiteConnector()
    await connector.connect(test_db_path)
    executor = SQLiteExecutor(connector)
    
    # Test SELECT query
    result = await executor.execute_query(
        "SELECT name, email FROM users ORDER BY name"
    )
    assert result.columns == ['name', 'email']
    assert len(result.rows) == 2
    assert result.rows[0][0] == 'Alice'
    assert result.rows[1][0] == 'Bob'
    
    # Test INSERT query
    result = await executor.execute_query(
        "INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')"
    )
    assert result.affected_rows == 1
    
    # Test UPDATE query
    result = await executor.execute_query(
        "UPDATE users SET email = 'alice.new@example.com' WHERE name = 'Alice'"
    )
    assert result.affected_rows == 1
    
    # Test batch execution
    results = await executor.execute_batch([
        "SELECT COUNT(*) FROM users",
        "SELECT COUNT(*) FROM posts"
    ])
    assert len(results) == 2
    assert results[0].rows[0][0] == 3  # 3 users
    assert results[1].rows[0][0] == 3  # 3 posts
    
    await connector.disconnect()


@pytest.mark.asyncio
async def test_error_handling(test_db_path):
    """Test error handling in SQLite implementations."""
    connector = SQLiteConnector()
    await connector.connect(test_db_path)
    executor = SQLiteExecutor(connector)
    
    # Test invalid SQL
    with pytest.raises(Exception):
        await executor.execute_query("SELECT * FROM nonexistent_table")
    
    # Test disconnected state
    await connector.disconnect()
    with pytest.raises(Exception):
        await executor.execute_query("SELECT * FROM users") 