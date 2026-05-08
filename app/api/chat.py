"""对话 API 路由。"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.chat import ChatMessage, ChatSession, MessageRole
from app.models.user import User
from app.services import rag_service
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """同步问答接口。"""
    query = body.get("query", "")
    kb_id = uuid.UUID(body.get("kb_id", ""))
    session_id = body.get("session_id")

    # 加载对话历史
    history = []
    if session_id:
        history = await rag_service.load_conversation_history(db, uuid.UUID(str(session_id)))

    result = await rag_service.ask(query, kb_id, db, history=history)

    # 保存会话和消息
    if not session_id:
        session = ChatSession(user_id=user.id, kb_id=kb_id, title=query[:50])
        db.add(session)
        await db.flush()
        session_id = str(session.id)
    else:
        session_id = str(session_id)

    user_msg = ChatMessage(session_id=uuid.UUID(session_id), role=MessageRole.USER, content=query)
    db.add(user_msg)

    assistant_msg = ChatMessage(
        session_id=uuid.UUID(session_id),
        role=MessageRole.ASSISTANT,
        content=result["answer"],
        citations=result["citations"],
    )
    db.add(assistant_msg)
    await db.flush()

    return {
        "session_id": session_id,
        "answer": result["answer"],
        "citations": result["citations"],
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """获取会话历史和消息。"""
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalars().first()
    if not session:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(detail="Session not found")

    msg_result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = msg_result.scalars().all()

    return {
        "id": str(session.id),
        "title": session.title,
        "kb_id": str(session.kb_id) if session.kb_id else None,
        "messages": [
            {"role": m.role.value, "content": m.content, "citations": m.citations, "created_at": m.created_at.isoformat()}
            for m in messages
        ],
    }
