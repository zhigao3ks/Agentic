"""混合检索流水线：向量检索 + BM25 + 融合 + Reranker 精排。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.services import dependencies
from app.services.embedding.base import EmbeddingService
from app.services.reranker.base import RerankerService
from app.services.retrieval.bm25_retriever import BM25Retriever
from app.services.retrieval.fusion import rrf_fusion
from app.services.retrieval.vector_retriever import VectorRetriever
from app.services.vector_store.base import VectorStore

# 全局 BM25 索引缓存
_bm25_cache: dict[str, BM25Retriever] = {}


def _ensure_bm25_index(kb_id: str, chunks: list[dict]) -> BM25Retriever:
    """确保 BM25 索引存在，不存在则构建。"""
    if kb_id not in _bm25_cache:
        bm25 = BM25Retriever()
        bm25.build_index(kb_id, chunks)
        _bm25_cache[kb_id] = bm25
    return _bm25_cache[kb_id]


async def _load_kb_chunks(db: AsyncSession, kb_id: uuid.UUID) -> list[dict]:
    """从数据库加载知识库的全部 chunk。"""
    result = await db.execute(select(Chunk).where(Chunk.kb_id == kb_id))
    return [
        {
            "id": str(ch.id),
            "content": ch.content,
            "metadata": {
                "chunk_id": str(ch.id),
                "document_id": str(ch.document_id),
                "page": ch.page,
                "section_title": ch.section_title,
            },
        }
        for ch in result.scalars().all()
    ]


async def hybrid_search(
    query: str,
    kb_id: uuid.UUID,
    db: AsyncSession,
    top_k: int = 8,
    use_bm25: bool = True,
    use_reranker: bool = True,
    embedding_service: EmbeddingService | None = None,
    vector_store: VectorStore | None = None,
    reranker: RerankerService | None = None,
) -> list[dict]:
    """执行混合检索流水线。"""
    emb = embedding_service or dependencies.get_embedding_service()
    store = vector_store or dependencies.get_vector_store()

    # 1. 向量检索
    vec_retriever = VectorRetriever(emb, store)
    vector_results = await vec_retriever.retrieve(query, kb_id, top_k=20)

    if not use_bm25:
        return vector_results[:top_k]

    # 2. BM25 检索
    all_chunks = await _load_kb_chunks(db, kb_id)
    bm25 = _ensure_bm25_index(str(kb_id), all_chunks)
    bm25_results = bm25.retrieve(query, str(kb_id), top_k=20)

    # 3. RRF 融合
    fused = rrf_fusion(vector_results, bm25_results, top_k=20)

    # 4. Reranker 精排
    if use_reranker and fused:
        reranker_svc = reranker
        if reranker_svc is None:
            from app.services.reranker.fake import FakeReranker
            reranker_svc = FakeReranker()
        fused = await reranker_svc.rerank(query, fused, top_k=top_k)

    return fused[:top_k]
