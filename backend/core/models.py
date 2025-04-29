from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class WidgetType(PyEnum):
    TABLE = 'TABLE'
    LINE_CHART = 'LINE_CHART'
    BAR_CHART = 'BAR_CHART'
    PIE_CHART = 'PIE_CHART'
    NUMBER = 'NUMBER'
    TEXT = 'TEXT'

class SQLTemplate(Base):
    __tablename__ = "sql_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    query = Column(Text, nullable=False)
    source_question = Column(Text, nullable=False)
    widget_type = Column(Enum(WidgetType), nullable=False, default=WidgetType.TABLE)
    refresh_rate = Column(Integer, nullable=False, default=0)  # 0 means no refresh
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_execution = Column(DateTime(timezone=True), nullable=True) 