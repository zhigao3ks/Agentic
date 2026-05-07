"""向量检索服务。"""

import uuid

from app.services.embedding.base import EmbeddingService
from app.services.vector_store.base import VectorStore


class VectorRetriever:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore) -> None:
        self._emb = embedding_service
        self._store = vector_store

    async def retrieve(
        self, query: str, kb_id: uuid.UUID, top_k: int = 10
    ) -> list[dict]:
        """执行向量检索，返回 [{id, chunk_id, document_id, score, content, ...}]。"""
        query_vector = await self._emb.embed_query(query)
        results = await self._store.search(
            query_vector, top_k=top_k, filter_dict={"kb_id": str(kb_id)}
        )
        return results
