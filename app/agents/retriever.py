"""Retriever Agent —— 执行知识库检索并补充 chunk 内容。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.models.chunk import Chunk
from app.services.retrieval.hybrid_pipeline import hybrid_search


async def retrieve(
    state: AgentState,
    db: AsyncSession | None = None,
) -> dict:
    """执行混合检索，从 DB 回填 chunk 内容，返回状态更新。"""
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

    # 从 DB 回填 chunk 内容
    enriched = await _enrich_chunks(db, chunks)

    return {
        "retrieved_chunks": enriched,
        "messages": [{"role": "retriever", "content": f"retrieved {len(enriched)} chunks"}],
        "step_count": state["step_count"] + 1,
    }


async def _enrich_chunks(db: AsyncSession, results: list[dict]) -> list[dict]:
    """从数据库加载 chunk 内容，补充到检索结果中。"""
    chunk_ids = []
    for r in results:
        cid = r.get("metadata", {}).get("chunk_id", "")
        if cid:
            try:
                chunk_ids.append(uuid.UUID(cid))
            except ValueError:
                pass

    if not chunk_ids:
        return results

    db_result = await db.execute(select(Chunk).where(Chunk.id.in_(chunk_ids)))
    chunk_map = {str(c.id): c for c in db_result.scalars().all()}

    enriched = []
    for r in results:
        cid = r.get("metadata", {}).get("chunk_id", "")
        ch = chunk_map.get(cid)
        enriched.append({
            "id": r.get("id", ""),
            "score": r.get("score", 0),
            "content": ch.content if ch else r.get("content", ""),
            "metadata": {
                "chunk_id": cid,
                "document_id": r.get("metadata", {}).get("document_id", str(ch.document_id) if ch else ""),
                "page": ch.page if ch else r.get("metadata", {}).get("page"),
                "section_title": ch.section_title if ch else r.get("metadata", {}).get("section_title", ""),
            },
        })
    return enriched
