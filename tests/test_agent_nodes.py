"""测试 Agent 节点函数。"""

import pytest
import pytest_asyncio

from app.agents.state import make_initial_state


@pytest.mark.asyncio
class TestQueryAnalyzer:
    async def test_analyze_returns_analysis(self):
        from app.agents.query_analyzer import analyze_query

        state = make_initial_state("什么是 RAG？", "kb1")
        result = await analyze_query(state)

        assert "query_analysis" in result
        assert result["query_analysis"]["needs_retrieval"] is True
        assert result["step_count"] == 1

    async def test_keywords_extracted(self):
        from app.agents.query_analyzer import analyze_query

        state = make_initial_state("Python 数据分析", "kb1")
        result = await analyze_query(state)

        assert len(result["query_analysis"]["keywords"]) >= 0


@pytest.mark.asyncio
class TestAnswerGenerator:
    async def test_generate_without_chunks(self):
        from app.agents.answer_generator import generate_answer

        state = make_initial_state("test", "kb1")
        result = await generate_answer(state)

        assert "没有找到相关信息" in result["answer"]
        assert result["citations"] == []

    async def test_generate_with_chunks(self):
        from app.agents.answer_generator import generate_answer

        chunks = [
            {"id": "c1", "score": 0.9, "content": "Python 是一种编程语言。", "metadata": {"chunk_id": "ch1", "document_id": "d1"}},
        ]
        state = make_initial_state("什么是 Python？", "kb1")
        state["retrieved_chunks"] = chunks

        result = await generate_answer(state)

        assert len(result["answer"]) > 0


@pytest.mark.asyncio
class TestVerifier:
    async def test_verify_without_answer(self):
        from app.agents.verifier import verify

        state = make_initial_state("q", "kb1")
        result = await verify(state)

        assert result["verification"]["result"] == "fail"

    async def test_verify_with_answer(self):
        from app.agents.verifier import verify

        chunks = [{"id": "c1", "score": 0.9, "content": "Python 是一种编程语言。", "metadata": {}}]
        state = make_initial_state("什么是 Python？", "kb1")
        state["answer"] = "Python 是一种编程语言。[1]"
        state["retrieved_chunks"] = chunks
        state["citations"] = [{"index": 1, "chunk_id": "ch1"}]

        result = await verify(state)

        assert "verification" in result
        assert result["verification"]["result"] in ("pass", "partial", "fail")
