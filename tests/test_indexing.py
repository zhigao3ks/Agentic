"""测试索引流水线。"""

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


@pytest_asyncio.fixture
async def setup_chunks(s):
    from app.models.chunk import Chunk
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase
    from app.models.user import User

    u = User(username="idxuser", email="idx@x.com", password_hash="h")
    s.add(u)
    await s.flush()

    kb = KnowledgeBase(name="Idx KB", owner_id=u.id)
    s.add(kb)
    await s.flush()

    doc = Document(kb_id=kb.id, filename="doc.txt", file_type="txt", file_path="/p", file_size=10)
    s.add(doc)
    await s.flush()

    for i in range(3):
        s.add(Chunk(
            document_id=doc.id, kb_id=kb.id,
            content=f"Chunk {i} 的内容", chunk_index=i,
        ))
    await s.flush()

    return kb.id


@pytest.mark.asyncio
class TestIndexing:
    async def test_index_chunks_embeds_and_stores(self, s, setup_chunks):
        from app.services.embedding.fake import FakeEmbeddingService
        from app.services.indexing import index_chunks
        from app.services.vector_store.chroma_store import ChromaVectorStore

        import tempfile
        tmp = tempfile.mkdtemp()
        store = ChromaVectorStore(persist_dir=tmp)
        emb = FakeEmbeddingService(dimension=128)

        await index_chunks(s, setup_chunks, emb, store)

        # 验证 chunk 的 embedding_id 已设置
        from sqlalchemy import select
        from app.models.chunk import Chunk
        result = await s.execute(select(Chunk).where(Chunk.kb_id == setup_chunks))
        chunks = result.scalars().all()
        for c in chunks:
            assert c.embedding_id is not None

        # 验证可以从向量库检索
        query_vector = await emb.embed_query("Chunk 1")
        results = await store.search(query_vector, top_k=2, filter_dict={"kb_id": str(setup_chunks)})
        assert len(results) >= 1

        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    async def test_index_no_unindexed_chunks(self, s, setup_chunks):
        from app.services.embedding.fake import FakeEmbeddingService
        from app.services.indexing import index_chunks
        from app.services.vector_store.chroma_store import ChromaVectorStore

        import tempfile
        tmp = tempfile.mkdtemp()
        store = ChromaVectorStore(persist_dir=tmp)
        emb = FakeEmbeddingService(dimension=128)

        # 第一次索引
        await index_chunks(s, setup_chunks, emb, store)
        # 第二次索引应无操作（所有 chunk 已有 embedding_id）
        await index_chunks(s, setup_chunks, emb, store)

        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
