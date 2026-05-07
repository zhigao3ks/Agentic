"""测试检索服务。"""

import tempfile

import pytest
import pytest_asyncio

from app.db.session import _get_session_factory, init_db


@pytest_asyncio.fixture
async def s():
    await init_db()
    async with _get_session_factory()() as session:
        async with session.begin():
            yield session


@pytest.fixture
def retriever():
    from app.services.embedding.fake import FakeEmbeddingService
    from app.services.retrieval.vector_retriever import VectorRetriever
    from app.services.vector_store.chroma_store import ChromaVectorStore

    tmp = tempfile.mkdtemp()
    store = ChromaVectorStore(persist_dir=tmp)
    emb = FakeEmbeddingService(dimension=128)
    yield VectorRetriever(emb, store)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.mark.asyncio
class TestVectorRetriever:
    async def test_retrieve_returns_results(self, retriever):
        import uuid
        # 先添加向量
        from app.services.vector_store.chroma_store import ChromaVectorStore
        store = retriever._store
        await store.add_vectors(
            ids=["r1", "r2"],
            vectors=[[0.1] * 128, [0.5] * 128],
            metadatas=[
                {"kb_id": "test-kb", "chunk_id": "c1"},
                {"kb_id": "test-kb", "chunk_id": "c2"},
            ],
        )

        results = await retriever.retrieve("test query", "test-kb", top_k=2)
        assert len(results) == 2

    async def test_retrieve_empty_kb(self, retriever):
        results = await retriever.retrieve("nothing", "empty-kb")
        assert results == []
