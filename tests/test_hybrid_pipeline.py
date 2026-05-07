"""测试混合检索流水线。"""

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

    u = User(username="hybuser", email="hyb@x.com", password_hash="h")
    s.add(u)
    await s.flush()

    kb = KnowledgeBase(name="Hybrid KB", owner_id=u.id)
    s.add(kb)
    await s.flush()

    doc = Document(kb_id=kb.id, filename="d.txt", file_type="txt", file_path="/p", file_size=10)
    s.add(doc)
    await s.flush()

    chunks_data = [
        "Python 是一种高级编程语言，广泛用于数据科学和 Web 开发。",
        "FastAPI 是一个现代 Python Web 框架，支持异步处理和自动 API 文档生成。",
        "RAG 是检索增强生成技术，结合了信息检索和文本生成来提高回答准确性。",
        "BM25 是一种基于概率检索模型的关键词匹配算法，常用于信息检索中。",
        "ChromaDB 是一个开源的向量数据库，支持高效的语义检索。",
    ]
    for i, content in enumerate(chunks_data):
        s.add(Chunk(document_id=doc.id, kb_id=kb.id, content=content, chunk_index=i))
    await s.flush()

    # 索引到向量库
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
class TestHybridSearch:
    async def test_hybrid_returns_results(self, s, setup_kb):
        from app.services.retrieval.hybrid_pipeline import hybrid_search

        results = await hybrid_search("Python 编程", setup_kb, s, top_k=5)
        assert len(results) >= 1

    async def test_hybrid_without_bm25(self, s, setup_kb):
        from app.services.retrieval.hybrid_pipeline import hybrid_search

        results = await hybrid_search("Python 编程", setup_kb, s, top_k=5, use_bm25=False)
        assert len(results) >= 1

    async def test_hybrid_without_reranker(self, s, setup_kb):
        from app.services.retrieval.hybrid_pipeline import hybrid_search

        results = await hybrid_search("Python 编程", setup_kb, s, top_k=5, use_reranker=False)
        assert len(results) >= 1
