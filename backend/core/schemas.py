from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import WidgetType

class SQLTemplateBase(BaseModel):
    query: str
    source_question: str
    widget_type: WidgetType
    refresh_rate: int = Field(gt=0)  # must be positive

class SQLTemplateCreate(SQLTemplateBase):
    pass

class SQLTemplate(SQLTemplateBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 