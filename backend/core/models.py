from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
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


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # 'user' | 'assistant'
    text = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")