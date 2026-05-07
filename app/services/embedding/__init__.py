"""Embedding 服务。"""

from app.services.embedding.base import EmbeddingService
from app.services.embedding.fake import FakeEmbeddingService

__all__ = ["EmbeddingService", "FakeEmbeddingService"]
