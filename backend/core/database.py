from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path
from .config import settings
import asyncio

# Ensure the data directory exists
if not settings.DATA_DIR.exists():
    os.makedirs(settings.DATA_DIR, exist_ok=True)

# Get the absolute path to the database files
FINANCE_DB_PATH = os.path.abspath(os.path.join("data", "finance.db"))
TEMPLATES_DB_PATH = os.path.abspath(os.path.join("data", "templates.db"))

# Create async engines
finance_engine = create_async_engine(
    f"sqlite+aiosqlite:///{FINANCE_DB_PATH}",
    echo=False,
    future=True
)

templates_engine = create_async_engine(
    f"sqlite+aiosqlite:///{TEMPLATES_DB_PATH}",
    echo=False,
    future=True
)

# Create async session factories
AsyncFinanceSessionLocal = sessionmaker(
    finance_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

AsyncTemplatesSessionLocal = sessionmaker(
    templates_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create Base class for models
Base = declarative_base()

# Dependencies
async def get_templates_db():
    async with AsyncTemplatesSessionLocal() as db:
        yield db

async def get_finance_db():
    async with AsyncFinanceSessionLocal() as db:
        yield db

async def create_tables():
    """Create all tables in the templates database."""
    async with templates_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def recreate_tables():
    """Drop all tables and recreate them in the templates database."""
    async with templates_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all) 