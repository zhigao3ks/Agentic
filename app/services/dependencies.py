"""服务依赖注入 —— 根据配置自动选择 Fake 或真实服务。"""

from app.core.config import settings
from app.services.embedding.base import EmbeddingService
from app.services.llm.base import LLMService
from app.services.vector_store.base import VectorStore
from app.services.vector_store.chroma_store import ChromaVectorStore

_embedding_service: EmbeddingService | None = None
_vector_store: VectorStore | None = None
_llm_service: LLMService | None = None


def _is_real_api_configured() -> bool:
    """检测是否配置了真实 API Key（非默认占位值）。"""
    key = settings.LLM_API_KEY
    if not key:
        return False
    # 排除明显的占位/默认值
    placeholders = {"ollama", "not-needed", "change-me", "sk-your-", "your-key"}
    key_lower = key.lower()
    return not any(p in key_lower for p in placeholders)


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        if _is_real_api_configured():
            from app.services.embedding.bge import BGEEmbeddingService
            _embedding_service = BGEEmbeddingService()
        else:
            from app.services.embedding.fake import FakeEmbeddingService
            _embedding_service = FakeEmbeddingService()
    return _embedding_service


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        if _is_real_api_configured():
            from app.services.llm.openai_llm import OpenAILLMService
            _llm_service = OpenAILLMService()
        else:
            from app.services.llm.fake import FakeLLMService
            _llm_service = FakeLLMService()
    return _llm_service


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    return _vector_store


def set_embedding_service(svc: EmbeddingService) -> None:
    global _embedding_service
    _embedding_service = svc


def set_llm_service(svc: LLMService) -> None:
    global _llm_service
    _llm_service = svc


def set_vector_store(store: VectorStore) -> None:
    global _vector_store
    _vector_store = store
