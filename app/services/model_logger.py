"""模型调用日志服务 —— 记录每次 LLM/Embedding 调用的耗时、token 用量和异常。"""

import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_call_log import ModelCallLog


async def log_llm_call(
    db: AsyncSession,
    model_name: str,
    prompt_preview: str = "",
    response_preview: str = "",
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    latency_ms: int = 0,
    status: str = "success",
    error_message: str | None = None,
    request_meta: dict | None = None,
) -> ModelCallLog:
    """记录一次 LLM 调用。"""
    log = ModelCallLog(
        model_name=model_name,
        call_type="llm",
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message,
        prompt_preview=prompt_preview[:500] if prompt_preview else None,
        response_preview=response_preview[:500] if response_preview else None,
        request_meta=request_meta,
    )
    db.add(log)
    await db.flush()
    return log


async def log_embedding_call(
    db: AsyncSession,
    model_name: str,
    text_count: int = 0,
    total_tokens: int | None = None,
    latency_ms: int = 0,
    status: str = "success",
    error_message: str | None = None,
) -> ModelCallLog:
    """记录一次 Embedding 调用。"""
    log = ModelCallLog(
        model_name=model_name,
        call_type="embedding",
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message,
        request_meta={"text_count": text_count},
    )
    db.add(log)
    await db.flush()
    return log
