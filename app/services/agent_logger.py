"""Agent 执行日志服务。"""

import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.models.agent_run import AgentRun, AgentRunStatus
from app.models.chat import ChatSession


async def log_agent_run(
    db: AsyncSession,
    state: AgentState,
    start_time: float,
) -> AgentRun:
    """记录 Agent 执行日志到数据库。"""
    latency_ms = int((time.monotonic() - start_time) * 1000)

    session_id = None
    if state.get("session_id"):
        try:
            session_id = uuid.UUID(state["session_id"])
        except (ValueError, TypeError):
            pass

    run = AgentRun(
        session_id=session_id,
        user_query=state["query"],
        final_answer=state.get("answer", ""),
        status=AgentRunStatus.COMPLETED if state.get("status") != "failed" else AgentRunStatus.FAILED,
        steps=[
            {"role": m["role"], "content": str(m.get("content", ""))[:500]}
            for m in state.get("messages", [])
        ],
        latency_ms=latency_ms,
    )
    db.add(run)
    await db.flush()
    return run
