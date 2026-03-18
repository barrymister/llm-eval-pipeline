from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g. 'ollama', 'claude')."""
        ...

    @abstractmethod
    async def generate(self, model: str, prompt: str) -> tuple[str, float]:
        """
        Generate a response for the given prompt.

        Returns:
            Tuple of (response_text, latency_ms)
        """
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        """List available models for this provider."""
        ...
