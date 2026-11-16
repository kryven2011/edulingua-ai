"""EduLingua AI — Google Gemini AI Provider.

Implements the AIProvider interface using the ``google-generativeai`` library.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import Settings
from app.services.ai.provider import AIProvider, AIResponse

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Google Gemini AI provider with retry logic and timeout handling."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._configured = False
        if settings.has_gemini_key:
            genai.configure(api_key=settings.gemini_api_key.get_secret_value())  # type: ignore[union-attr]
            self._configured = True
            logger.info(
                "Gemini provider initialised (model=%s, vision_model=%s)",
                settings.gemini_model,
                settings.gemini_vision_model,
            )
        else:
            logger.warning("Gemini provider: API key not configured")

    # ── helpers ──────────────────────────────────────────────────

    def _build_text_model(
        self,
        system_prompt: str,
        *,
        max_tokens: int,
        temperature: float,
    ) -> genai.GenerativeModel:
        """Create a ``GenerativeModel`` for text generation."""
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        return genai.GenerativeModel(
            model_name=self._settings.gemini_model,
            generation_config=generation_config,
            system_instruction=system_prompt,
        )

    def _build_vision_model(
        self,
        *,
        max_tokens: int,
        temperature: float,
    ) -> genai.GenerativeModel:
        """Create a ``GenerativeModel`` for image analysis."""
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        return genai.GenerativeModel(
            model_name=self._settings.gemini_vision_model,
            generation_config=generation_config,
        )

    @staticmethod
    def _format_messages(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Convert generic messages to Gemini content format."""
        contents: list[dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role", "user")
            gemini_role = "model" if role == "assistant" else "user"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": msg["content"]}],
            })
        return contents

    @staticmethod
    def _extract_token_count(response: Any) -> int:
        """Safely extract total token count from a Gemini response."""
        try:
            usage = getattr(response, "usage_metadata", None)
            if usage is not None:
                return int(getattr(usage, "total_token_count", 0))
        except (TypeError, ValueError):
            pass
        return 0

    @staticmethod
    def _extract_finish_reason(response: Any) -> str | None:
        """Extract finish reason from the first candidate."""
        try:
            candidates = getattr(response, "candidates", [])
            if candidates:
                reason = getattr(candidates[0], "finish_reason", None)
                return str(reason) if reason is not None else None
        except (IndexError, TypeError):
            pass
        return None

    # ── public API ───────────────────────────────────────────────

    @retry(
        retry=retry_if_exception_type((
            google_exceptions.ServiceUnavailable,
            google_exceptions.DeadlineExceeded,
            google_exceptions.ResourceExhausted,
        )),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 60,
    ) -> AIResponse:
        """Generate a text response using Gemini."""
        if not self._configured:
            raise RuntimeError("Gemini API key is not configured")

        model = self._build_text_model(
            system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        contents = self._format_messages(messages)

        logger.debug(
            "Gemini generate: %d messages, max_tokens=%d",
            len(messages),
            max_tokens,
        )

        try:
            response = await asyncio.wait_for(
                model.generate_content_async(contents),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Gemini request timed out after %ds", timeout)
            raise

        text = response.text or ""
        tokens = self._extract_token_count(response)
        finish_reason = self._extract_finish_reason(response)

        logger.info(
            "Gemini response: %d chars, %d tokens, finish=%s",
            len(text),
            tokens,
            finish_reason,
        )

        return AIResponse(
            text=text,
            tokens_used=tokens,
            model=self._settings.gemini_model,
            finish_reason=finish_reason,
        )

    @retry(
        retry=retry_if_exception_type((
            google_exceptions.ServiceUnavailable,
            google_exceptions.DeadlineExceeded,
            google_exceptions.ResourceExhausted,
        )),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.4,
        timeout: int = 90,
    ) -> AIResponse:
        """Analyze an image using Gemini vision model."""
        if not self._configured:
            raise RuntimeError("Gemini API key is not configured")

        model = self._build_vision_model(
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Build multimodal content
        image_part = {"mime_type": "image/jpeg", "data": image_data}
        contents = [prompt, image_part]

        logger.debug(
            "Gemini analyze_image: prompt=%d chars, image=%d bytes",
            len(prompt),
            len(image_data),
        )

        try:
            response = await asyncio.wait_for(
                model.generate_content_async(contents),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Gemini image analysis timed out after %ds", timeout)
            raise

        text = response.text or ""
        tokens = self._extract_token_count(response)
        finish_reason = self._extract_finish_reason(response)

        logger.info(
            "Gemini vision response: %d chars, %d tokens",
            len(text),
            tokens,
        )

        return AIResponse(
            text=text,
            tokens_used=tokens,
            model=self._settings.gemini_vision_model,
            finish_reason=finish_reason,
        )

    async def is_available(self) -> bool:
        """Check if Gemini is configured."""
        return self._configured
