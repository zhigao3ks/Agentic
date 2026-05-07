"""测试 Reranker 服务。"""

import pytest

from app.services.reranker.base import RerankerService


class TestRerankerABC:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            RerankerService()  # type: ignore


@pytest.mark.asyncio
class TestFakeReranker:
    async def test_returns_top_k(self):
        from app.services.reranker.fake import FakeReranker
        reranker = FakeReranker()
        chunks = [{"id": f"c{i}", "content": f"C{i}"} for i in range(10)]
        result = await reranker.rerank("query", chunks, top_k=3)
        assert len(result) == 3

    async def test_preserves_order(self):
        from app.services.reranker.fake import FakeReranker
        reranker = FakeReranker()
        chunks = [{"id": "c1", "content": "A"}, {"id": "c2", "content": "B"}]
        result = await reranker.rerank("query", chunks, top_k=5)
        assert result[0]["id"] == "c1"
