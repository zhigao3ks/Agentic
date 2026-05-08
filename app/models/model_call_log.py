"""模型调用日志模型。"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelCallLog(Base):
    __tablename__ = "model_call_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    call_type: Mapped[str] = mapped_column(String(50), nullable=False)  # llm / embedding / reranker
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    total_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="success")  # success / error
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    prompt_preview: Mapped[str | None] = mapped_column(Text, default=None)
    response_preview: Mapped[str | None] = mapped_column(Text, default=None)
    request_meta: Mapped[dict | None] = mapped_column(JSON, default=None)  # 额外元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<ModelCallLog {self.model_name} {self.call_type} ({self.status})>"
