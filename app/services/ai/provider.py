"""EduLingua AI — Abstract AI Provider Interface.

Defines the contract for all AI provider implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AIResponse:
    """Response from an AI provider."""

    text: str
    tokens_used: int
    model: str
    finish_reason: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


class AIProvider(ABC):
    """Abstract base for AI text/vision generation providers."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 60,
    ) -> AIResponse:
        """Generate a text response from a conversation history.

        Args:
            messages: List of ``{"role": "user"|"assistant", "content": "..."}`` dicts.
            system_prompt: System-level instruction for the model.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.

        Returns:
            AIResponse with generated text and metadata.
        """

    @abstractmethod
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.4,
        timeout: int = 90,
    ) -> AIResponse:
        """Analyze an image and return a text response.

        Args:
            image_data: Raw image bytes (JPEG/PNG).
            prompt: Text prompt accompanying the image.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.

        Returns:
            AIResponse with analysis text.
        """

    @abstractmethod
    async def is_available(self) -> bool:
        """Check whether the provider is configured and reachable."""
