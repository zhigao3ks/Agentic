"""测试 Embedding 服务。"""

import pytest

from app.services.embedding.base import EmbeddingService
from app.services.embedding.fake import FakeEmbeddingService


class TestEmbeddingServiceABC:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            EmbeddingService()  # type: ignore


@pytest.mark.asyncio
class TestFakeEmbeddingService:
    @pytest.fixture
    def svc(self):
        return FakeEmbeddingService(dimension=128)

    async def test_embed_texts_returns_correct_dimension(self, svc):
        vectors = await svc.embed_texts(["hello", "world"])
        assert len(vectors) == 2
        assert len(vectors[0]) == 128

    async def test_embed_query_returns_correct_dimension(self, svc):
        vector = await svc.embed_query("test query")
        assert len(vector) == 128

    async def test_embed_is_deterministic(self, svc):
        v1 = await svc.embed_query("same text")
        v2 = await svc.embed_query("same text")
        assert v1 == v2

    async def test_embed_different_texts_different_vectors(self, svc):
        v1 = await svc.embed_query("text A")
        v2 = await svc.embed_query("text B")
        assert v1 != v2

    async def test_embed_texts_empty_list(self, svc):
        vectors = await svc.embed_texts([])
        assert vectors == []

    async def test_default_dimension(self):
        svc = FakeEmbeddingService()
        assert svc.dimension == 1024
