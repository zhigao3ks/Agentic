"""测试 LLM 服务。"""

import pytest

from app.services.llm.base import LLMService


class TestLLMServiceABC:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            LLMService()  # type: ignore


@pytest.mark.asyncio
class TestFakeLLMService:
    async def test_generate_returns_string(self):
        from app.services.llm.fake import FakeLLMService
        svc = FakeLLMService()
        result = await svc.generate("test prompt")
        assert isinstance(result, str)
        assert len(result) > 0

    async def test_generate_with_fixed_response(self):
        from app.services.llm.fake import FakeLLMService
        svc = FakeLLMService(fixed_response="固定回答")
        result = await svc.generate("anything")
        assert result == "固定回答"

    async def test_generate_stream_yields_chars(self):
        from app.services.llm.fake import FakeLLMService
        svc = FakeLLMService(fixed_response="ABC")
        chars = []
        async for c in svc.generate_stream("prompt"):
            chars.append(c)
        assert "".join(chars) == "ABC"
