from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from ...core.database import get_templates_db
from ...core.models import Conversation, Message
from ...core.config import settings
from ...services.text2sql_service import Text2SQLService
from llama_index.llms.openai import OpenAI
import asyncio

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


async def _classify_intent(llm: OpenAI, history: List[Dict[str, str]], question: str) -> Dict[str, Any]:
    """Use LLM to decide whether to route to text2sql or llm.
    Returns dict with keys: route ('text2sql'|'llm'), confidence (0..1)
    """
    try:
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-10:]])
        prompt = f"""
Du bist ein Router. Entscheide, ob die Anfrage an den Text2SQL-Agent (SQL über strukturierte Unternehmensdaten) oder an den allgemeinen LLM (freie Analyse/Erklärung) gehen soll.

Kriterien Text2SQL:
- Datenbank-/Tabellenbezug, Kennzahlenabfragen, Aggregationen, Zeitreihen über Unternehmensdaten, explizite Datenabfragen
Kriterien LLM:
- Freie Analyse, Erklärung, inhaltliche Zusammenfassung, hypothetische Szenarien ohne konkrete Datenbankabfrage

Gib eine JSON-Antwort zurück, exakt dieses Schema und nichts anderes:
{{"route":"text2sql|llm","confidence":0.0-1.0,"rationale":"kurze Begründung"}}

Verlauf:\n{history_text}\n\nFrage: {question}
"""
        if hasattr(llm, "acomplete"):
            resp = await llm.acomplete(prompt)
        else:
            resp = await asyncio.to_thread(llm.complete, prompt)
        text = getattr(resp, "text", str(resp)).strip()
        # Try to parse JSON
        import json as _json
        data = _json.loads(text)
        route = (data.get("route") or "llm").lower()
        confidence = float(data.get("confidence") or 0.5)
        if route not in ("text2sql", "llm"):
            route = "llm"
        return {"route": route, "confidence": max(0.0, min(1.0, confidence)), "rationale": data.get("rationale")}
    except Exception:
        return {"route": "text2sql", "confidence": 0.5}


async def _generate_llm_answer(llm: OpenAI, history: List[Dict[str, str]], question: str) -> Dict[str, Any]:
    """Generate an LLM answer using chat history. Returns unified payload."""
    history_text = "\n\n".join([f"{m['role'].upper()}:\n{m['content']}" for m in history[-10:]])
    prompt = f"""
Du bist ein Datenanalyse-Assistent. Berücksichtige den bisherigen Verlauf und beantworte die aktuelle Frage prägnant.
- Wenn sinnvoll, antworte als kurzes Markdown.
- Falls eine Darstellung sinnvoll ist, antworte als Widget-Direktive @widgets/<Name> oder als Markdown. KEINE erfundenen Daten.

VERLAUF:\n{history_text}

AKTUELLE FRAGE: {question}
"""
    if hasattr(llm, "acomplete"):
        resp = await llm.acomplete(prompt)
    else:
        resp = await asyncio.to_thread(llm.complete, prompt)
    answer = getattr(resp, "text", str(resp)).strip()
    return {
        "answer": answer,
        "presentation": answer,
    }


@router.post("/route")
async def route_message(payload: Dict[str, Any], db: AsyncSession = Depends(get_templates_db)) -> Dict[str, Any]:
    """LLM-based intent routing: uses chat history to choose Text2SQL vs LLM and returns unified response."""
    conversation_id = payload.get("conversation_id")
    message = payload.get("message")
    if not conversation_id or not isinstance(message, str) or not message.strip():
        raise HTTPException(status_code=400, detail="conversation_id and message are required")

    # Ensure conversation exists
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Persist user message first
    user_msg = Message(conversation_id=conversation_id, role="user", text=message)
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # Load recent history (last 20)
    result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())
    )
    history_rows = result.scalars().all()
    history = [
        {"role": ("user" if r.role == "user" else "assistant"), "content": r.text}
        for r in history_rows[-20:]
    ]

    # Initialize services
    t2s = Text2SQLService(db_path=settings.FINANCE_DB_PATH)
    await t2s.initialize()
    llm = t2s.llm or OpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")

    # Decide
    decision = await _classify_intent(llm, history, message)
    route = decision.get("route", "llm")
    confidence = float(decision.get("confidence", 0.5))
    threshold = 0.6

    if route == "text2sql" and confidence >= threshold:
        # Compose question with minimal context (optional): last assistant line + current question
        try:
            result = await t2s.query(message)
            assistant_text = result.get("answer") or result.get("formatted_result") or ""
            payload_meta = {
                "sql": result.get("sql"),
                "result": result.get("result"),
                "formatted_result": result.get("formatted_result"),
                "presentation": result.get("presentation"),
            }
            assistant = Message(
                conversation_id=conversation_id,
                role="assistant",
                text=payload_meta.get("presentation") or assistant_text or "",
                meta=payload_meta,
            )
            db.add(assistant)
            await db.commit()
            await db.refresh(assistant)
            return {
                "route": "text2sql",
                "confidence": confidence,
                **payload_meta,
                "answer": assistant_text,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Plain LLM analysis path
        try:
            result = await _generate_llm_answer(llm, history, message)
            assistant = Message(
                conversation_id=conversation_id,
                role="assistant",
                text=result.get("presentation") or result.get("answer") or "",
                meta=result,
            )
            db.add(assistant)
            await db.commit()
            await db.refresh(assistant)
            return {
                "route": "llm",
                "confidence": confidence,
                **result,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


