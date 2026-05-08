"""OpenAI-compatible LLM 服务 —— 含调用日志记录。"""

import time
import json as _json
from collections.abc import AsyncGenerator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.llm.base import LLMService


class OpenAILLMService(LLMService):
    def __init__(
        self, base_url: str | None = None, api_key: str | None = None, model: str | None = None
    ) -> None:
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        self.last_usage: dict | None = None
        self.last_latency_ms: int = 0

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def generate(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={"model": self.model, "messages": messages, "temperature": temperature},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                self.last_latency_ms = int((time.monotonic() - start) * 1000)
                usage = data.get("usage", {})
                self.last_usage = {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
                return data["choices"][0]["message"]["content"]
        except Exception:
            self.last_latency_ms = int((time.monotonic() - start) * 1000)
            self.last_usage = None
            raise

    async def generate_stream(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.monotonic()
        self.last_usage = None
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json={"model": self.model, "messages": messages, "temperature": temperature, "stream": True},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = _json.loads(data)
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                                # 最后一个 chunk 可能包含 usage
                                if "usage" in chunk:
                                    usage = chunk["usage"]
                                    self.last_usage = {
                                        "prompt_tokens": usage.get("prompt_tokens"),
                                        "completion_tokens": usage.get("completion_tokens"),
                                        "total_tokens": usage.get("total_tokens"),
                                    }
                            except (_json.JSONDecodeError, KeyError, IndexError):
                                continue
            self.last_latency_ms = int((time.monotonic() - start) * 1000)
        except Exception:
            self.last_latency_ms = int((time.monotonic() - start) * 1000)
            self.last_usage = None
            raise
