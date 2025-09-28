from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from ...core.database import get_templates_db
from ...core.models import Conversation, Message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/conversations", response_model=dict)
async def create_conversation(
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_templates_db),
):
    conv = Conversation(title=title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return {"id": conv.id, "title": conv.title, "created_at": conv.created_at}


@router.get("/conversations", response_model=List[dict])
async def list_conversations(db: AsyncSession = Depends(get_templates_db)):
    result = await db.execute(select(Conversation).order_by(Conversation.id.desc()))
    conversations = result.scalars().all()
    return [
        {"id": c.id, "title": c.title, "created_at": c.created_at}
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=List[dict])
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_templates_db)):
    result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "text": m.text,
            "meta": m.meta,
            "created_at": m.created_at,
        }
        for m in messages
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=dict)
async def append_message(
    conversation_id: int,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_templates_db),
):
    role = payload.get("role")
    text = payload.get("text")
    meta = payload.get("meta")

    if role not in ("user", "assistant") or not isinstance(text, str) or not text:
        raise HTTPException(status_code=400, detail="Invalid message payload")

    # Ensure conversation exists
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = Message(conversation_id=conversation_id, role=role, text=text, meta=meta)
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return {
        "id": message.id,
        "role": message.role,
        "text": message.text,
        "meta": message.meta,
        "created_at": message.created_at,
    }


