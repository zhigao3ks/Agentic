"""模型调用日志 API。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.model_call_log import ModelCallLog
from app.models.user import User
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/model", tags=["model_logs"])


@router.get("/calls")
async def list_model_calls(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """列出最近的模型调用日志。"""
    total = await db.scalar(select(func.count(ModelCallLog.id)))
    result = await db.execute(
        select(ModelCallLog).order_by(desc(ModelCallLog.created_at)).limit(limit).offset(offset)
    )
    logs = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": str(log.id),
                "model": log.model_name,
                "type": log.call_type,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "total_tokens": log.total_tokens,
                "latency_ms": log.latency_ms,
                "status": log.status,
                "error": log.error_message,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.get("/stats")
async def model_call_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """模型调用统计。"""
    total = await db.scalar(select(func.count(ModelCallLog.id)))
    total_tokens = await db.scalar(select(func.sum(ModelCallLog.total_tokens)))
    total_errors = await db.scalar(
        select(func.count(ModelCallLog.id)).where(ModelCallLog.status == "error")
    )
    avg_latency = await db.scalar(select(func.avg(ModelCallLog.latency_ms)))

    return {
        "total_calls": total or 0,
        "total_tokens": total_tokens or 0,
        "error_count": total_errors or 0,
        "avg_latency_ms": round(avg_latency, 1) if avg_latency else 0,
    }
