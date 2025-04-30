from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_templates_db
from ...core.models import SQLTemplate, WidgetType
from ...core.schemas import SQLTemplateCreate, SQLTemplateResponse
from datetime import datetime
from sqlalchemy import select

router = APIRouter(
    prefix="/api",
    tags=["templates"]
)

@router.post("/templates", response_model=SQLTemplateResponse)
async def create_template(template: SQLTemplateCreate, db: AsyncSession = Depends(get_templates_db)):
    """Create a new SQL template"""
    db_template = SQLTemplate(
        name=template.name,
        description=template.description,
        query=template.query,
        source_question=template.source_question,
        widget_type=template.widget_type,
        refresh_rate=template.refresh_rate,
        created_at=datetime.utcnow()
    )
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get("/templates", response_model=List[SQLTemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_templates_db)):
    """List all SQL templates"""
    result = await db.execute(select(SQLTemplate))
    return result.scalars().all()

@router.get("/templates/{template_id}", response_model=SQLTemplateResponse)
async def get_template(template_id: int, db: AsyncSession = Depends(get_templates_db)):
    """Get a specific SQL template by ID"""
    result = await db.execute(select(SQLTemplate).where(SQLTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=SQLTemplateResponse)
async def update_template(template_id: int, template: SQLTemplateCreate, db: AsyncSession = Depends(get_templates_db)):
    """Update a SQL template"""
    result = await db.execute(select(SQLTemplate).where(SQLTemplate.id == template_id))
    db_template = result.scalar_one_or_none()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in template.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
    
    db_template.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, db: AsyncSession = Depends(get_templates_db)):
    """Delete a SQL template"""
    result = await db.execute(select(SQLTemplate).where(SQLTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.delete(template)
    await db.commit()
    return {"message": "Template deleted successfully"} 