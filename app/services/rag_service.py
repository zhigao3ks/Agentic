"""RAG 问答服务 —— 串联检索→上下文→LLM→引用溯源的完整流程。"""

import uuid as _uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.services import citation, context_builder, dependencies
from app.services.llm.base import LLMService
from app.services.retrieval.vector_retriever import VectorRetriever

uuid = _uuid

RAG_SYSTEM_PROMPT = (
    "你是一个基于企业知识库的智能问答助手。"
    "请严格根据提供的上下文信息回答用户问题。"
    "如果上下文中没有相关信息，请明确告知用户'当前知识库中没有找到相关信息'，不要编造答案。"
    "回答时请引用相关上下文编号，例如 [1]、[2]。"
)

_MAX_HISTORY_MESSAGES = 10


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
    history: list[dict] | None = None,
) -> dict:
    """执行 RAG 问答流程，返回 {answer, citations, chunks}。

    history 为多轮对话历史，格式: [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
    """
    retriever = _get_retriever()

    # 1. 检索
    results = await retriever.retrieve(query, kb_id, top_k)
    enriched = await _enrich_chunks(db, results) if db else results

    if not enriched:
        return {"answer": "当前知识库中没有找到相关信息，请尝试上传相关文档后再提问。", "citations": [], "chunks": []}

    # 2. 构造上下文（含对话历史）
    context = context_builder.build_context(enriched)
    prompt = _build_prompt_with_history(context, query, history or [])

    # 3. LLM 生成
    llm_svc = llm or dependencies.get_llm_service()
    answer = await llm_svc.generate(prompt, system_prompt=RAG_SYSTEM_PROMPT)

    # 4. 引用溯源
    citations_list = citation.extract_citations(answer, enriched)

    return {"answer": answer, "citations": citations_list, "chunks": enriched}


def _build_prompt_with_history(context: str, query: str, history: list[dict]) -> str:
    """构建带对话历史的 prompt。"""
    parts = ["上下文信息：\n\n" + context]

    if history:
        history_text = _format_history(history)
        parts.insert(0, "对话历史：\n" + history_text)

    parts.append(f"用户问题：{query}\n\n请基于以上上下文回答问题，并标注引用编号。")
    return "\n\n".join(parts)


def _format_history(history: list[dict]) -> str:
    """格式化对话历史为文本。"""
    lines = []
    for msg in history[-_MAX_HISTORY_MESSAGES:]:
        role = "用户" if msg["role"] == "user" else "助手"
        content = msg.get("content", "")[:500]  # 截断过长消息
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


async def load_conversation_history(
    db: AsyncSession,
    session_id: _uuid.UUID,
    limit: int = _MAX_HISTORY_MESSAGES,
) -> list[dict]:
    """加载会话的最近 N 条消息作为对话历史。"""
    from sqlalchemy import select
    from app.models.chat import ChatMessage

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    # 反转为时间正序
    return [
        {"role": m.role.value, "content": m.content}
        for m in reversed(messages)
    ]


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
