"""RAG 问答服务 —— 串联检索→上下文→LLM→引用溯源的完整流程。"""

import uuid as _uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.services import citation, context_builder, dependencies
from app.services.llm.base import LLMService
from app.services.retrieval.vector_retriever import VectorRetriever

uuid = _uuid  # 兼容外部调用

RAG_SYSTEM_PROMPT = (
    "你是一个基于企业知识库的智能问答助手。"
    "请严格根据提供的上下文信息回答用户问题。"
    "如果上下文中没有相关信息，请明确告知用户'当前知识库中没有找到相关信息'，不要编造答案。"
    "回答时请引用相关上下文编号，例如 [1]、[2]。"
)


def _get_retriever() -> VectorRetriever:
    emb = dependencies.get_embedding_service()
    store = dependencies.get_vector_store()
    return VectorRetriever(emb, store)


async def ask(
    query: str,
    kb_id: _uuid.UUID,
    db: AsyncSession | None = None,
    top_k: int = 8,
    llm: LLMService | None = None,
) -> dict:
    """执行 RAG 问答流程，返回 {answer, citations, chunks}。"""
    retriever = _get_retriever()

    # 1. 检索
    results = await retriever.retrieve(query, kb_id, top_k)

    # 2. 从数据库获取 chunk content（向量库只存了元数据）
    enriched = await _enrich_chunks(db, results) if db else results

    if not enriched:
        return {"answer": "当前知识库中没有找到相关信息，请尝试上传相关文档后再提问。", "citations": [], "chunks": []}

    # 3. 构造上下文
    context = context_builder.build_context(enriched)

    # 4. LLM 生成
    llm_svc = llm or dependencies.get_llm_service()
    prompt = f"上下文信息：\n\n{context}\n\n用户问题：{query}\n\n请基于以上上下文回答问题，并标注引用编号。"
    answer = await llm_svc.generate(prompt, system_prompt=RAG_SYSTEM_PROMPT)

    # 5. 引用溯源
    citations_list = citation.extract_citations(answer, enriched)

    return {"answer": answer, "citations": citations_list, "chunks": enriched}


async def _enrich_chunks(db: AsyncSession, results: list[dict]) -> list[dict]:
    """从数据库加载 chunk 内容，补充到检索结果中。"""
    from sqlalchemy import select

    chunk_ids = []
    for r in results:
        cid = r.get("metadata", {}).get("chunk_id", "")
        if cid:
            try:
                chunk_ids.append(_uuid.UUID(cid))
            except ValueError:
                pass

    if not chunk_ids:
        return []

    result = await db.execute(select(Chunk).where(Chunk.id.in_(chunk_ids)))
    chunk_map = {str(c.id): c for c in result.scalars().all()}

    enriched = []
    for r in results:
        cid = r.get("metadata", {}).get("chunk_id", "")
        ch = chunk_map.get(cid)
        if ch:
            enriched.append({
                "id": r["id"],
                "score": r["score"],
                "content": ch.content,
                "metadata": {
                    "chunk_id": cid,
                    "document_id": str(ch.document_id),
                    "page": ch.page,
                    "section_title": ch.section_title,
                },
            })
    return enriched


