"""测试 RRF 融合策略。"""

from app.services.retrieval.fusion import rrf_fusion


class TestRRFFusion:
    def test_dedup_across_sources(self):
        vec = [{"id": "c1", "score": 0.9, "content": "A"}]
        bm25 = [{"id": "c1", "score": 0.8, "content": "A"}]

        result = rrf_fusion(vec, bm25, top_k=5)
        # 同 id 应去重
        assert len(result) == 1

    def test_combines_results(self):
        vec = [{"id": "c1", "score": 0.9, "content": "A"}]
        bm25 = [{"id": "c2", "score": 0.8, "content": "B"}]

        result = rrf_fusion(vec, bm25, top_k=5)
        assert len(result) == 2

    def test_fusion_score_present(self):
        vec = [{"id": "c1", "score": 0.9, "content": "A"}]
        bm25 = [{"id": "c2", "score": 0.7, "content": "B"}]

        result = rrf_fusion(vec, bm25, top_k=5)
        assert "fusion_score" in result[0]

    def test_respects_top_k(self):
        vec = [{"id": f"v{i}", "score": 0.9, "content": f"V{i}"} for i in range(10)]
        bm25 = [{"id": f"b{i}", "score": 0.8, "content": f"B{i}"} for i in range(10)]

        result = rrf_fusion(vec, bm25, top_k=5)
        assert len(result) == 5
