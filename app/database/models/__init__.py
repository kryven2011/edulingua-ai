"""EduLingua AI — Database Models Registry.

Exports all SQLAlchemy models so that Alembic and repositories
can discover them easily.
"""

from app.database.models.admin import Admin, UsageLog
from app.database.models.base import Base
from app.database.models.daily import DailyProgress, DailyTask
from app.database.models.education import (
    ConversationMessage,
    StudySession,
    Subject,
)
from app.database.models.gamification import (
    Achievement,
    UserAchievement,
    XPTransaction,
)
from app.database.models.language import (
    GrammarLesson,
    Language,
    LanguageLevel,
    UserVocabulary,
    VocabularyWord,
)
from app.database.models.quiz import QuizAttempt, QuizQuestion
from app.database.models.referral import Referral
from app.database.models.subscription import Subscription, Transaction
from app.database.models.telegram import TelegramUpdate
from app.database.models.user import User, UserProfile, UserSettings

__all__ = [
    "Base",
    "User",
    "UserSettings",
    "UserProfile",
    "Subject",
    "StudySession",
    "ConversationMessage",
    "Language",
    "LanguageLevel",
    "VocabularyWord",
    "UserVocabulary",
    "GrammarLesson",
    "QuizQuestion",
    "QuizAttempt",
    "Achievement",
    "UserAchievement",
    "XPTransaction",
    "Subscription",
    "Transaction",
    "DailyTask",
    "DailyProgress",
    "Referral",
    "Admin",
    "UsageLog",
    "TelegramUpdate",
]
