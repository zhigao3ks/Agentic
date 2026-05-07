"""检索 API 路由。"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services import rag_service
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/retrieval", tags=["retrieval"])


@router.post("/search")
async def search(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """检索知识库，返回相关 chunk 及分数。"""
    query = body.get("query", "")
    kb_id = uuid.UUID(body.get("kb_id", ""))
    top_k = body.get("top_k", 10)

    retriever = rag_service._get_retriever()
    results = await retriever.retrieve(query, kb_id, top_k)
    enriched = await rag_service._enrich_chunks(db, results)
    return {"query": query, "results": enriched, "total": len(enriched)}
