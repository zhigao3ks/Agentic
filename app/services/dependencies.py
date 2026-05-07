"""服务依赖注入 —— 根据配置返回对应的服务实例。"""

from app.core.config import settings
from app.services.embedding.base import EmbeddingService
from app.services.embedding.fake import FakeEmbeddingService
from app.services.vector_store.base import VectorStore
from app.services.vector_store.chroma_store import ChromaVectorStore

_embedding_service: EmbeddingService | None = None
_vector_store: VectorStore | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        if settings.APP_ENV == "development":
            _embedding_service = FakeEmbeddingService()
        else:
            from app.services.embedding.bge import BGEEmbeddingService
            _embedding_service = BGEEmbeddingService()
    return _embedding_service


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        if settings.APP_ENV == "development":
            import tempfile
            import os
            tmp = os.path.join(tempfile.gettempdir(), "chroma_test")
            _vector_store = ChromaVectorStore(persist_dir=tmp)
        else:
            _vector_store = ChromaVectorStore()
    return _vector_store


def set_embedding_service(svc: EmbeddingService) -> None:
    global _embedding_service
    _embedding_service = svc


def set_vector_store(store: VectorStore) -> None:
    global _vector_store
    _vector_store = store
