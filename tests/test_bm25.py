"""测试 BM25 检索器。"""

from app.services.retrieval.bm25_retriever import BM25Retriever


class TestBM25Retriever:
    def test_build_and_retrieve(self):
        bm25 = BM25Retriever()
        chunks = [
            {"id": "c1", "content": "Python 是一种高级编程语言", "metadata": {}},
            {"id": "c2", "content": "FastAPI 是一个 Python Web 框架", "metadata": {}},
            {"id": "c3", "content": "机器学习是人工智能的一个分支", "metadata": {}},
        ]
        bm25.build_index("kb1", chunks)

        results = bm25.retrieve("Python 编程", "kb1", top_k=2)
        assert len(results) >= 1
        assert any("Python" in r["content"] for r in results)

    def test_retrieve_unknown_kb(self):
        bm25 = BM25Retriever()
        results = bm25.retrieve("query", "nonexistent")
        assert results == []

    def test_chinese_tokenization(self):
        bm25 = BM25Retriever()
        chunks = [
            {"id": "c1", "content": "企业知识库问答系统基于大语言模型构建", "metadata": {}},
        ]
        bm25.build_index("kb1", chunks)
        results = bm25.retrieve("知识库问答", "kb1")
        assert len(results) >= 1

    def test_score_in_result(self):
        bm25 = BM25Retriever()
        chunks = [
            {"id": "c1", "content": "test document content here", "metadata": {}},
            {"id": "c2", "content": "another unrelated document", "metadata": {}},
        ]
        bm25.build_index("kb1", chunks)
        results = bm25.retrieve("document content", "kb1")
        assert len(results) >= 1
        assert "score" in results[0]
        assert results[0]["score"] >= 0
