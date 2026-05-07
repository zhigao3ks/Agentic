"""测试 LangGraph 工作流。"""

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

    u = User(username="agentuser", email="agent@x.com", password_hash="h")
    s.add(u)
    await s.flush()

    kb = KnowledgeBase(name="Agent KB", owner_id=u.id)
    s.add(kb)
    await s.flush()

    doc = Document(kb_id=kb.id, filename="d.txt", file_type="txt", file_path="/p", file_size=10)
    s.add(doc)
    await s.flush()

    for i, content in enumerate([
        "Python 是一种高级编程语言，广泛用于数据科学和 Web 开发。",
        "FastAPI 是一个现代 Python Web 框架，支持异步处理。",
        "RAG 是检索增强生成技术，结合了信息检索和文本生成。",
    ]):
        s.add(Chunk(document_id=doc.id, kb_id=kb.id, content=content, chunk_index=i))
    await s.flush()

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
class TestAgentGraph:
    async def test_run_agent_completes(self, s, setup_kb):
        from app.agents.graph import run_agent

        state = await run_agent(
            query="什么是 Python？",
            kb_id=str(setup_kb),
            db=s,
            enable_verifier=True,
        )

        assert state["status"] in ("running", "completed")
        assert len(state.get("answer", "")) > 0
        assert state["step_count"] > 0

    async def test_run_agent_without_verifier(self, s, setup_kb):
        from app.agents.graph import run_agent

        state = await run_agent(
            query="什么是 Python？",
            kb_id=str(setup_kb),
            db=s,
            enable_verifier=False,
        )

        assert len(state.get("answer", "")) > 0

    async def test_run_agent_empty_kb(self, s):
        from app.agents.graph import run_agent
        import uuid

        state = await run_agent(
            query="nothing",
            kb_id=str(uuid.uuid4()),
            db=s,
        )

        assert "answer" in state
