import time
import anthropic
from api.providers.base import BaseProvider
from api.config import settings


class ClaudeProvider(BaseProvider):
    """
    Anthropic Claude API provider.
    Optional — only active when ANTHROPIC_API_KEY is set.
    Useful for comparing local Ollama models against Claude as a quality baseline.
    """

    SUPPORTED_MODELS = [
        "claude-haiku-4-5-20251001",
        "claude-sonnet-4-6",
    ]

    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Claude provider requires an API key in .env"
            )
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    @property
    def name(self) -> str:
        return "claude"

    async def generate(self, model: str, prompt: str) -> tuple[str, float]:
        start = time.perf_counter()
        message = self.client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.perf_counter() - start) * 1000
        return message.content[0].text, latency_ms

    async def list_models(self) -> list[str]:
        return self.SUPPORTED_MODELS
