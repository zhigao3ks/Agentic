"""测试上下文构造器。"""

from app.services.context_builder import build_context


class TestBuildContext:
    def test_empty_chunks(self):
        result = build_context([])
        assert "未找到" in result

    def test_single_chunk(self):
        chunks = [{"id": "c1", "score": 0.9, "content": "这是第一段内容。", "metadata": {"section_title": "简介"}}]
        result = build_context(chunks)
        assert "[1]" in result
        assert "简介" in result
        assert "这是第一段内容" in result

    def test_multiple_chunks(self):
        chunks = [
            {"id": "c1", "score": 0.9, "content": "内容A", "metadata": {}},
            {"id": "c2", "score": 0.7, "content": "内容B", "metadata": {"section_title": "方法"}},
        ]
        result = build_context(chunks)
        assert "[1]" in result
        assert "[2]" in result
        assert "内容A" in result
        assert "内容B" in result

    def test_truncates_long_context(self):
        chunks = [{"id": f"c{i}", "score": 0.9, "content": "X" * 3000, "metadata": {}} for i in range(5)]
        result = build_context(chunks, max_chars=5000)
        assert len(result) < 15000  # 不会包含全部 5 个超大 chunk
