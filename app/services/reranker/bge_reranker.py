"""BGE Reranker —— 通过 OpenAI-compatible API 调用。"""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.reranker.base import RerankerService


class BGEReranker(RerankerService):
    def __init__(
        self, base_url: str | None = None, api_key: str | None = None, model: str | None = None
    ) -> None:
        self.base_url = (base_url or settings.RERANKER_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.RERANKER_API_KEY
        self.model = model or settings.RERANKER_MODEL

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def rerank(self, query: str, chunks: list[dict], top_k: int = 8) -> list[dict]:
        documents = [ch.get("content", "") for ch in chunks]

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/rerank",
                json={"model": self.model, "query": query, "documents": documents, "top_n": top_k},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("results", []):
                idx = item.get("index", 0)
                if idx < len(chunks):
                    ch = dict(chunks[idx])
                    ch["rerank_score"] = item.get("relevance_score", 0)
                    results.append(ch)
            return results
