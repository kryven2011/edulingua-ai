"""EduLingua AI — Repositories Registry."""

from app.database.repositories.base import BaseRepository
from app.database.repositories.education_repo import EducationRepository
from app.database.repositories.gamification_repo import GamificationRepository
from app.database.repositories.language_repo import LanguageRepository
from app.database.repositories.subscription_repo import SubscriptionRepository
from app.database.repositories.user_repo import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "EducationRepository",
    "LanguageRepository",
    "GamificationRepository",
    "SubscriptionRepository",
]
