"""Fake Embedding 服务 —— 用于测试，基于文本哈希生成确定性向量。"""

import hashlib

from app.services.embedding.base import EmbeddingService


class FakeEmbeddingService(EmbeddingService):
    def __init__(self, dimension: int = 1024) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_to_vector(t) for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        return self._hash_to_vector(text)

    def _hash_to_vector(self, text: str) -> list[float]:
        """基于 SHA-256 哈希生成确定性向量。"""
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(self._dimension):
            byte_val = h[i % len(h)]
            vec.append((byte_val / 255.0) * 2 - 1)  # 归一化到 [-1, 1]
        return vec
