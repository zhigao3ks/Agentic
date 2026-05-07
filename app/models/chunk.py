"""文档切片模型。"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    kb_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int | None] = mapped_column(Integer, default=None)
    section_title: Mapped[str | None] = mapped_column(String(500), default="")
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    chunk_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, default=dict)
    embedding_id: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["Document"] = relationship("Document", lazy="selectin")  # noqa: F821
    knowledge_base: Mapped["KnowledgeBase"] = relationship("KnowledgeBase", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Chunk {self.document_id}#{self.chunk_index}>"
