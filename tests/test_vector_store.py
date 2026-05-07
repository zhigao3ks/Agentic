"""测试向量存储。"""

import os
import tempfile

import pytest

from app.services.vector_store.base import VectorStore


class TestVectorStoreABC:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            VectorStore()  # type: ignore


@pytest.mark.asyncio
class TestChromaVectorStore:
    @pytest.fixture
    def store(self):
        from app.services.vector_store.chroma_store import ChromaVectorStore
        tmp = tempfile.mkdtemp()
        yield ChromaVectorStore(persist_dir=tmp)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    async def test_add_and_search(self, store):
        await store.add_vectors(
            ids=["chunk_1", "chunk_2"],
            vectors=[[0.1] * 128, [0.9] * 128],
            metadatas=[
                {"kb_id": "kb1", "chunk_id": "c1"},
                {"kb_id": "kb1", "chunk_id": "c2"},
            ],
        )

        query = [0.15] * 128
        results = await store.search(query, top_k=2, filter_dict={"kb_id": "kb1"})
        assert len(results) == 2
        assert results[0]["id"] in ("chunk_1", "chunk_2")
        assert "score" in results[0]

    async def test_search_returns_empty_for_no_match(self, store):
        results = await store.search([0.5] * 128, top_k=5, filter_dict={"kb_id": "nonexistent"})
        assert results == []

    async def test_delete_by_ids(self, store):
        await store.add_vectors(
            ids=["del_1"],
            vectors=[[0.5] * 128],
            metadatas=[{"kb_id": "kb1"}],
        )
        await store.delete(["del_1"])
        results = await store.search([0.5] * 128, top_k=1, filter_dict={"kb_id": "kb1"})
        assert len(results) == 0

    async def test_kb_isolation(self, store):
        """不同 kb_id 的数据应隔离。"""
        await store.add_vectors(
            ids=["a1"],
            vectors=[[0.1] * 128],
            metadatas=[{"kb_id": "kb_a"}],
        )
        await store.add_vectors(
            ids=["b1"],
            vectors=[[0.9] * 128],
            metadatas=[{"kb_id": "kb_b"}],
        )

        # 从 kb_a 检索，不应返回 kb_b 的数据
        results = await store.search([0.1] * 128, top_k=2, filter_dict={"kb_id": "kb_a"})
        assert len(results) == 1
        assert results[0]["id"] == "a1"
