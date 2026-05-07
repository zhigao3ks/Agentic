"""BM25 关键词检索器 —— 按知识库维护独立索引。"""

import re
from collections import defaultdict

from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self) -> None:
        self._indexes: dict[str, dict] = {}  # kb_id → {"bm25": BM25Okapi, "chunks": list[dict]}

    def _tokenize(self, text: str) -> list[str]:
        """中文按单字+词切分，英文按空格分词。"""
        # 简单分词：中文字符单独切分，英文按空格
        tokens = []
        for char in text:
            if char.isalpha() and ord(char) < 128:
                tokens.append(char.lower())
            elif char.strip():
                tokens.append(char)
        # 同时按空格分词获取英文单词
        for word in re.findall(r"[a-zA-Z]+", text.lower()):
            tokens.append(word)
        return tokens

    def build_index(self, kb_id: str, chunks: list[dict]) -> None:
        """为指定知识库构建 BM25 索引。"""
        corpus = [self._tokenize(ch["content"]) for ch in chunks]
        self._indexes[kb_id] = {
            "bm25": BM25Okapi(corpus),
            "chunks": chunks,
        }

    def retrieve(self, query: str, kb_id: str, top_k: int = 20) -> list[dict]:
        """BM25 关键词检索。"""
        if kb_id not in self._indexes:
            return []

        idx = self._indexes[kb_id]
        tokens = self._tokenize(query)
        scores = idx["bm25"].get_scores(tokens)

        scored = sorted(
            zip(idx["chunks"], scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        return [
            {"id": ch.get("id", ""), "score": float(max(s, 0)), "content": ch.get("content", ""), "metadata": ch.get("metadata", {})}
            for ch, s in scored
        ]
