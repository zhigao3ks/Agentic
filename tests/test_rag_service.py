"""测试 RAG 问答服务。"""

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
async def setup_kb(s):
    from app.models.chunk import Chunk
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase
    from app.models.user import User

    u = User(username="raguser", email="rag@x.com", password_hash="h")
    s.add(u)
    await s.flush()

    kb = KnowledgeBase(name="RAG KB", owner_id=u.id)
    s.add(kb)
    await s.flush()

    doc = Document(kb_id=kb.id, filename="d.txt", file_type="txt", file_path="/p", file_size=10)
    s.add(doc)
    await s.flush()

    chunks = [
        Chunk(document_id=doc.id, kb_id=kb.id, content="Python 是一种高级编程语言，广泛用于数据科学和 Web 开发。", chunk_index=0),
        Chunk(document_id=doc.id, kb_id=kb.id, content="FastAPI 是一个现代 Python Web 框架，支持异步处理和自动 API 文档生成。", chunk_index=1),
        Chunk(document_id=doc.id, kb_id=kb.id, content="RAG 是检索增强生成技术，结合了信息检索和文本生成来提高回答准确性。", chunk_index=2),
    ]
    for c in chunks:
        s.add(c)
    await s.flush()

    # 索引 chunks
    from app.services.dependencies import set_embedding_service, set_vector_store
    from app.services.embedding.fake import FakeEmbeddingService
    from app.services.indexing import index_chunks
    from app.services.vector_store.chroma_store import ChromaVectorStore

    tmp = tempfile.mkdtemp()
    store = ChromaVectorStore(persist_dir=tmp)
    emb = FakeEmbeddingService(dimension=128)
    set_embedding_service(emb)
    set_vector_store(store)

    await index_chunks(s, kb.id, emb, store)

    return kb.id


@pytest.mark.asyncio
class TestRAGServiceAsk:
    async def test_ask_returns_answer_and_citations(self, s, setup_kb):
        from app.services.rag_service import ask

        result = await ask("什么是 FastAPI？", setup_kb, db=s)
        assert "answer" in result
        assert "citations" in result
        assert len(result["answer"]) > 0

    async def test_ask_empty_kb(self, s):
        from app.services.rag_service import ask
        import uuid

        result = await ask("nothing", uuid.uuid4(), db=s)
        assert "没有找到相关信息" in result["answer"]

    async def test_enrich_chunks_returns_empty_for_empty(self, s):
        from app.services.rag_service import _enrich_chunks
        result = await _enrich_chunks(s, [])
        assert result == []
