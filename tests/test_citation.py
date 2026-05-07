"""测试引用溯源。"""

from app.services.citation import extract_citations


class TestExtractCitations:
    def test_single_citation(self):
        chunks = [{"id": "c1", "score": 0.9, "metadata": {"chunk_id": "ch1", "document_id": "d1"}}]
        answer = "根据文档，结果如下 [1]。"
        citations = extract_citations(answer, chunks)
        assert len(citations) == 1
        assert citations[0]["index"] == 1
        assert citations[0]["chunk_id"] == "ch1"

    def test_multiple_citations(self):
        chunks = [
            {"id": "c1", "metadata": {"chunk_id": "ch1"}},
            {"id": "c2", "metadata": {"chunk_id": "ch2"}},
            {"id": "c3", "metadata": {"chunk_id": "ch3"}},
        ]
        answer = "如 [1] 和 [3] 所述。"
        citations = extract_citations(answer, chunks)
        assert len(citations) == 2
        assert citations[0]["index"] == 1
        assert citations[1]["index"] == 3

    def test_out_of_range_citation(self):
        chunks = [{"id": "c1", "metadata": {"chunk_id": "ch1"}}]
        answer = "引用 [5] 不存在。"
        citations = extract_citations(answer, chunks)
        assert len(citations) == 0

    def test_no_citations(self):
        chunks = [{"id": "c1", "metadata": {"chunk_id": "ch1"}}]
        answer = "没有引用标记。"
        citations = extract_citations(answer, chunks)
        assert len(citations) == 0

    def test_includes_content_preview(self):
        chunks = [{"id": "c1", "score": 0.8, "metadata": {"chunk_id": "ch1", "document_id": "d1", "page": 3, "section_title": "方法"}}]
        answer = "参见 [1]。"
        citations = extract_citations(answer, chunks)
        assert citations[0]["score"] == 0.8
        assert citations[0]["document_id"] == "d1"
        assert citations[0]["page"] == 3
