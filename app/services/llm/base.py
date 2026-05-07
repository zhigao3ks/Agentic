"""LLM 服务抽象接口。"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class LLMService(ABC):
    """大语言模型服务抽象基类。"""

    @abstractmethod
    async def generate(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7
    ) -> str:
        """生成完整回答。"""
        ...

    @abstractmethod
    async def generate_stream(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式生成回答。"""
        ...
