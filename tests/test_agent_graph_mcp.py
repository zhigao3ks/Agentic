"""测试集成 MCP 的 Agent 工作流。"""

import tempfile

import pytest
import pytest_asyncio

from app.db.session import _get_session_factory, init_db


@pytest_asyncio.fixture
async def s():
    await init_db()
    async with _get_session_factory()() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def setup_kb(s):
    from app.models.chunk import Chunk
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase
    from app.models.user import User

    u = User(username="mcpagent", email="mcpagent@x.com", password_hash="h")
    s.add(u)
    await s.flush()

    kb = KnowledgeBase(name="MCP Agent KB", owner_id=u.id)
    s.add(kb)
    await s.flush()

    doc = Document(kb_id=kb.id, filename="d.txt", file_type="txt", file_path="/p", file_size=10)
    s.add(doc)
    await s.flush()

    for i, content in enumerate([
        "Python 是一种高级编程语言。",
        "FastAPI 是一个现代 Python Web 框架。",
    ]):
        s.add(Chunk(document_id=doc.id, kb_id=kb.id, content=content, chunk_index=i))
    await s.flush()
    await s.commit()

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
    await s.commit()

    return kb.id


@pytest.mark.asyncio
class TestAgentGraphWithMCP:
    async def test_run_agent_with_tools_enabled(self, s, setup_kb):
        from app.agents.graph import run_agent

        state = await run_agent(
            query="什么是 Python？",
            kb_id=str(setup_kb),
            db=s,
            enable_tools=True,
            enable_verifier=False,
        )

        assert "answer" in state
        assert len(state.get("answer", "")) > 0
        assert "tool_calls" in state

    async def test_run_agent_with_tools_disabled(self, s, setup_kb):
        from app.agents.graph import run_agent

        state = await run_agent(
            query="什么是 Python？",
            kb_id=str(setup_kb),
            db=s,
            enable_tools=False,
            enable_verifier=False,
        )

        assert len(state.get("answer", "")) > 0

    async def test_needs_tools_routing(self):
        """测试条件路由函数。"""
        from app.agents.graph import _needs_tools
        from app.agents.state import make_initial_state

        state = make_initial_state("q", "kb1")
        state["query_analysis"] = {"needs_tools": True}
        assert _needs_tools(state) == "tool_planner"

        state["query_analysis"] = {"needs_tools": False}
        assert _needs_tools(state) == "retriever"

    async def test_has_tool_calls_routing(self):
        """测试工具调用条件路由。"""
        from app.agents.graph import _has_tool_calls
        from app.agents.state import make_initial_state

        state = make_initial_state("q", "kb1")
        state["tool_calls"] = [{"tool": "search"}]
        assert _has_tool_calls(state) == "mcp_tool_agent"

        state["tool_calls"] = []
        assert _has_tool_calls(state) == "retriever"
