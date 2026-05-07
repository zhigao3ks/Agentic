"""索引流水线：Embedding 向量化 + 向量库写入。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.chunk import Chunk
from app.models.document import DocumentStatus
from app.services.embedding.base import EmbeddingService
from app.services.vector_store.base import VectorStore

logger = get_logger(__name__)

BATCH_SIZE = 32


async def index_chunks(
    db: AsyncSession,
    kb_id: uuid.UUID,
    embedding_service: EmbeddingService,
    vector_store: VectorStore,
) -> None:
    """将知识库中所有未索引的 chunk 向量化并写入向量库。"""
    result = await db.execute(
        select(Chunk).where(Chunk.kb_id == kb_id, Chunk.embedding_id.is_(None))
    )
    unindexed = result.scalars().all()

    if not unindexed:
        return

    texts = [chunk.content for chunk in unindexed]
    kb_id_str = str(kb_id)

    all_ids = []
    all_vectors = []
    all_metadatas = []

    # 批量向量化
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i : i + BATCH_SIZE]
        batch_chunks = unindexed[i : i + BATCH_SIZE]

        vectors = await embedding_service.embed_texts(batch_texts)

        for chunk, vector in zip(batch_chunks, vectors):
            embedding_id = f"{chunk.id}_{kb_id_str}"
            all_ids.append(embedding_id)
            all_vectors.append(vector)
            all_metadatas.append({
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "kb_id": kb_id_str,
                "page": chunk.page or 0,
                "section_title": chunk.section_title or "",
            })
            chunk.embedding_id = embedding_id

        await db.flush()

    # 写入向量库
    await vector_store.add_vectors(all_ids, all_vectors, all_metadatas)

    # 更新文档状态为 embedding 完成
    from app.models.document import Document
    doc_result = await db.execute(
        select(Document).where(Document.kb_id == kb_id)
    )
    for doc in doc_result.scalars().all():
        doc.status = DocumentStatus.EMBEDDING

    await db.flush()
    logger.info("indexing complete", kb_id=kb_id_str, chunks=len(unindexed))
