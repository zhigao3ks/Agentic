"""Retriever Agent —— 执行知识库检索。"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.services.retrieval.hybrid_pipeline import hybrid_search


async def retrieve(
    state: AgentState,
    db: AsyncSession | None = None,
) -> dict:
    """执行混合检索，返回状态更新。"""
    if db is None:
        return {
            "retrieved_chunks": [],
            "messages": [{"role": "retriever", "content": "no database session"}],
            "step_count": state["step_count"] + 1,
        }

    try:
        kb_id = uuid.UUID(state["kb_id"])
    except ValueError:
        return {
            "retrieved_chunks": [],
            "messages": [{"role": "retriever", "content": "invalid kb_id"}],
            "step_count": state["step_count"] + 1,
        }

    chunks = await hybrid_search(
        query=state["query"],
        kb_id=kb_id,
        db=db,
        top_k=8,
    )

    return {
        "retrieved_chunks": chunks,
        "messages": [{"role": "retriever", "content": f"retrieved {len(chunks)} chunks"}],
        "step_count": state["step_count"] + 1,
    }
