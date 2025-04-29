from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_templates_db
from ...core.models import SQLTemplate
from ...core.schemas import SQLTemplateCreate, SQLTemplateResponse

router = APIRouter(
    prefix="/api/templates",
    tags=["templates"]
)

@router.post("/", response_model=SQLTemplateResponse)
def create_template(template: SQLTemplateCreate, db: Session = Depends(get_templates_db)):
    """Create a new SQL template"""
    db_template = SQLTemplate(
        name=template.name,
        description=template.description,
        query=template.query,
        source_question=template.source_question,
        widget_type=template.widget_type,
        refresh_rate=template.refresh_rate
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/", response_model=List[SQLTemplateResponse])
def list_templates(db: Session = Depends(get_templates_db)):
    """List all SQL templates"""
    return db.query(SQLTemplate).all()

@router.get("/{template_id}", response_model=SQLTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_templates_db)):
    """Get a specific SQL template by ID"""
    template = db.query(SQLTemplate).filter(SQLTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_templates_db)):
    """Delete a SQL template"""
    template = db.query(SQLTemplate).filter(SQLTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"} 