"""Agent API 路由。"""

import time
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_agent
from app.db.session import get_db
from app.models.user import User
from app.services import agent_logger
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat")
async def agent_chat(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """Agent 工作流问答接口。"""
    query = body.get("query", "")
    kb_id = body.get("kb_id", "")
    session_id = body.get("session_id")
    enable_verifier = body.get("enable_verifier", True)

    start_time = time.monotonic()

    state = await run_agent(
        query=query,
        kb_id=kb_id,
        session_id=session_id,
        db=db,
        enable_verifier=enable_verifier,
    )

    # 记录日志
    run = await agent_logger.log_agent_run(db, state, start_time)

    return {
        "agent_run_id": str(run.id),
        "query": state["query"],
        "answer": state.get("answer", ""),
        "citations": state.get("citations", []),
        "status": state.get("status", "completed"),
        "verification": state.get("verification", {}),
        "latency_ms": run.latency_ms,
    }
