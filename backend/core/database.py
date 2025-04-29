from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from .config import settings

# Ensure the data directory exists
if not settings.DATA_DIR.exists():
    os.makedirs(settings.DATA_DIR, exist_ok=True)

# Create engine for templates database
templates_engine = create_engine(
    f"sqlite:///{settings.TEMPLATES_DB_PATH}",
    connect_args={"check_same_thread": False}
)
TemplatesSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=templates_engine)

# Create engine for finance database
finance_engine = create_engine(
    f"sqlite:///{settings.FINANCE_DB_PATH}",
    connect_args={"check_same_thread": False}
)
FinanceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=finance_engine)

# Base for models
Base = declarative_base()

# Dependencies
def get_templates_db():
    db = TemplatesSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_finance_db():
    db = FinanceSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the templates database."""
    Base.metadata.create_all(bind=templates_engine)

def recreate_tables():
    """Drop all tables and recreate them in the templates database."""
    Base.metadata.drop_all(bind=templates_engine)
    Base.metadata.create_all(bind=templates_engine) 