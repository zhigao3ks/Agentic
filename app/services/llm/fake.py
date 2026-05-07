"""Fake LLM 服务 —— 用于测试。"""

from collections.abc import AsyncGenerator

from app.services.llm.base import LLMService


class FakeLLMService(LLMService):
    def __init__(self, fixed_response: str | None = None) -> None:
        self._fixed = fixed_response

    async def generate(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7
    ) -> str:
        if self._fixed:
            return self._fixed

        # 基于 prompt 中的关键词生成模拟回答
        if "RAG" in prompt or "检索" in prompt:
            return "根据提供的文档资料，RAG 检索增强生成技术结合了信息检索与文本生成。"
        if "问题" in prompt or "question" in prompt.lower():
            return "这是一个基于检索证据的回答，引用了相关文档中的内容 [1]。"
        return f"这是对您问题的回答。基于上下文中的信息，相关结论如上所述。"

    async def generate_stream(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt, system_prompt, temperature)
        # 逐字输出模拟流式
        for i, char in enumerate(text):
            yield char
