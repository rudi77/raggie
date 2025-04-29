from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import WidgetType

class SQLTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    query: str
    source_question: Optional[str] = None
    widget_type: WidgetType = WidgetType.TABLE
    refresh_rate: int = 0

class SQLTemplateCreate(SQLTemplateBase):
    pass

class SQLTemplateResponse(SQLTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_execution: Optional[datetime] = None

    class Config:
        from_attributes = True 