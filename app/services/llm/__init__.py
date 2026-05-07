"""LLM 服务。"""

from app.services.llm.base import LLMService
from app.services.llm.fake import FakeLLMService

__all__ = ["LLMService", "FakeLLMService"]
