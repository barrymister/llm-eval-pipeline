import time
import httpx
from api.providers.base import BaseProvider
from api.config import settings


class OllamaProvider(BaseProvider):
    """
    Local Ollama inference provider.
    Connects to Ollama running on appfactory (or any Ollama endpoint).
    Default: http://10.0.1.1:11434 (Docker host gateway on appfactory).
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(self, model: str, prompt: str) -> tuple[str, float]:
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = (time.perf_counter() - start) * 1000
        return data.get("response", ""), latency_ms

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
        return [m["name"] for m in data.get("models", [])]
