"""检索结果融合 —— RRF（Reciprocal Rank Fusion）算法。"""


def rrf_fusion(
    vector_results: list[dict],
    bm25_results: list[dict],
    k: int = 60,
    vector_weight: float = 0.6,
    bm25_weight: float = 0.4,
    top_k: int = 20,
) -> list[dict]:
    """RRF 融合向量检索和 BM25 结果。"""
    scores: dict[str, float] = {}
    chunks: dict[str, dict] = {}

    def _score(results, weight, prefix):
        for rank, item in enumerate(results):
            chunk_id = item.get("id", item.get("metadata", {}).get("chunk_id", ""))
            if not chunk_id:
                continue
            rrf = weight / (k + rank + 1)
            if chunk_id in scores:
                scores[chunk_id] += rrf
            else:
                scores[chunk_id] = rrf
                chunks[chunk_id] = item

    _score(vector_results, vector_weight, "vec")
    _score(bm25_results, bm25_weight, "bm25")

    # 按融合分数排序
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    result = []
    for chunk_id, score in ranked:
        item = dict(chunks.get(chunk_id, {}))
        item["fusion_score"] = score
        result.append(item)

    return result
