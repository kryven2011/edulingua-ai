"""EduLingua AI — Language Services (LinguaBot)."""

from app.services.language.language_tutor_service import LanguageTutorService
from app.services.language.spaced_repetition import SpacedRepetitionService

__all__ = ["LanguageTutorService", "SpacedRepetitionService"]
