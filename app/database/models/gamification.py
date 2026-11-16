"""EduLingua AI — Gamification Models.

Achievement, UserAchievement, and XPTransaction models.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class XPSource(str, enum.Enum):
    """Source of an XP transaction."""

    LESSON = "lesson"
    QUIZ = "quiz"
    DAILY_TASK = "daily_task"
    ACHIEVEMENT = "achievement"
    WORD_LEARNED = "word_learned"
    STREAK_BONUS = "streak_bonus"


class Achievement(Base):
    """An unlockable achievement."""

    __tablename__ = "achievements"
    __table_args__ = (
        Index("ix_achievements_code", "code", unique=True),
    )

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False)
    description_uz: Mapped[str] = mapped_column(Text, nullable=False)
    description_en: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    xp_reward: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    condition_type: Mapped[str] = mapped_column(String(100), nullable=False)
    condition_value: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )

    # --- Relationships ---
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="achievement", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Achievement(code={self.code!r})>"


class UserAchievement(Base):
    """Record of a user unlocking an achievement."""

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
        Index("ix_user_achievements_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False,
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship(
        back_populates="user_achievements",
    )

    def __repr__(self) -> str:
        return (
            f"<UserAchievement(user_id={self.user_id!r}, "
            f"achievement_id={self.achievement_id!r})>"
        )


class XPTransaction(Base):
    """XP award or deduction with idempotency protection."""

    __tablename__ = "xp_transactions"
    __table_args__ = (
        Index("ix_xp_transactions_user_id", "user_id"),
        Index(
            "ix_xp_transactions_idempotency_key",
            "idempotency_key",
            unique=True,
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[XPSource] = mapped_column(
        Enum(XPSource, name="xp_source_enum", native_enum=False),
        nullable=False,
    )
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="xp_transactions")

    def __repr__(self) -> str:
        return (
            f"<XPTransaction(user_id={self.user_id!r}, amount={self.amount}, "
            f"source={self.source})>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.user import User
