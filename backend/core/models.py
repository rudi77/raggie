from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from .database import Base

import enum

class WidgetType(str, enum.Enum):
    table = "table"
    line_chart = "line_chart"
    bar_chart = "bar_chart"

class SQLTemplate(Base):
    __tablename__ = "sql_templates"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    source_question = Column(String, nullable=False)
    widget_type = Column(Enum(WidgetType), nullable=False)
    refresh_rate = Column(Integer, nullable=False)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_execution = Column(DateTime(timezone=True), nullable=True)
    
    class Config:
        orm_mode = True 