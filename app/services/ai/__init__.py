"""EduLingua AI — AI Services and Providers."""

from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.prompts import (
    EDUAI_SYSTEM_PROMPT,
    GRAMMAR_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    LEVEL_TEST_PROMPT,
    LINGUA_SYSTEM_PROMPT,
    VOCABULARY_PROMPT,
)
from app.services.ai.provider import AIProvider, AIResponse
from app.services.ai.usage_tracker import AIUsageTracker

__all__ = [
    "AIProvider",
    "AIResponse",
    "GeminiProvider",
    "AIUsageTracker",
    "EDUAI_SYSTEM_PROMPT",
    "LINGUA_SYSTEM_PROMPT",
    "IMAGE_ANALYSIS_PROMPT",
    "LEVEL_TEST_PROMPT",
    "VOCABULARY_PROMPT",
    "GRAMMAR_PROMPT",
]
