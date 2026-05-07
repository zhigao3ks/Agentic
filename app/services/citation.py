"""引用溯源服务。"""

import re


def extract_citations(answer: str, chunks: list[dict]) -> list[dict]:
    """从回答中提取引用标记 [N]，并关联回检索结果。"""
    cited_indices = set()
    for match in re.finditer(r"\[(\d+)\]", answer):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(chunks):
            cited_indices.add(idx)

    citations = []
    for idx in sorted(cited_indices):
        ch = chunks[idx]
        meta = ch.get("metadata", {})
        citations.append({
            "index": idx + 1,
            "chunk_id": meta.get("chunk_id", ch.get("id", "")),
            "document_id": meta.get("document_id", ""),
            "score": ch.get("score", 0),
            "content_preview": (meta.get("content", "") or ch.get("content", ""))[:200],
            "page": meta.get("page"),
            "section_title": meta.get("section_title", ""),
        })

    return citations
