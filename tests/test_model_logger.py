"""测试模型调用日志。"""

import pytest
import pytest_asyncio

from app.db.session import _get_session_factory, init_db


@pytest_asyncio.fixture
async def s():
    await init_db()
    async with _get_session_factory()() as session:
        async with session.begin():
            yield session


@pytest.mark.asyncio
class TestModelLogger:
    async def test_log_llm_call(self, s):
        from app.services.model_logger import log_llm_call

        log = await log_llm_call(s, model_name="qwen-plus", prompt_preview="test prompt",
                                  response_preview="test response", prompt_tokens=10,
                                  completion_tokens=20, total_tokens=30, latency_ms=500,
                                  status="success")
        assert log.id is not None
        assert log.model_name == "qwen-plus"
        assert log.total_tokens == 30
        assert log.latency_ms == 500
        assert log.status == "success"

    async def test_log_llm_call_error(self, s):
        from app.services.model_logger import log_llm_call

        log = await log_llm_call(s, model_name="qwen-plus", status="error",
                                  error_message="Connection timeout", latency_ms=0)
        assert log.status == "error"
        assert log.error_message == "Connection timeout"

    async def test_log_embedding_call(self, s):
        from app.services.model_logger import log_embedding_call

        log = await log_embedding_call(s, model_name="text-embedding-v4",
                                        text_count=5, total_tokens=500, latency_ms=300)
        assert log.call_type == "embedding"
        assert log.model_name == "text-embedding-v4"


@pytest.mark.asyncio
class TestModelCallLogModel:
    async def test_create_log(self, s):
        from app.models.model_call_log import ModelCallLog

        log = ModelCallLog(model_name="test-model", call_type="llm",
                            prompt_tokens=5, completion_tokens=10, total_tokens=15,
                            latency_ms=200, status="success")
        s.add(log)
        await s.flush()
        assert log.id is not None
