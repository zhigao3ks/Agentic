"""Agent 执行日志模型。"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AgentRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chat_sessions.id", ondelete="SET NULL"), default=None)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    final_answer: Mapped[str | None] = mapped_column(Text, default="")
    status: Mapped[AgentRunStatus] = mapped_column(Enum(AgentRunStatus), default=AgentRunStatus.PENDING, nullable=False)
    steps: Mapped[dict | None] = mapped_column(JSON, default=list)
    latency_ms: Mapped[int | None] = mapped_column(Integer, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["ChatSession | None"] = relationship("ChatSession", lazy="selectin")  # noqa: F821

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("status", AgentRunStatus.PENDING)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<AgentRun {self.status.value} ({self.latency_ms}ms)>"
