from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.models import SQLTemplate
from ...core.schemas import SQLTemplateCreate, SQLTemplate as SQLTemplateSchema

router = APIRouter(
    prefix="/api/templates",
    tags=["templates"]
)

@router.post("/", response_model=SQLTemplateSchema)
def create_template(template: SQLTemplateCreate, db: Session = Depends(get_db)):
    """Create a new SQL template"""
    db_template = SQLTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/", response_model=List[SQLTemplateSchema])
def list_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all SQL templates with pagination"""
    templates = db.query(SQLTemplate).offset(skip).limit(limit).all()
    return templates

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a SQL template by ID"""
    template = db.query(SQLTemplate).filter(SQLTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"} 