"""EduLingua AI — User Models.

User, UserSettings, and UserProfile models for Telegram user management.
"""

from __future__ import annotations

import uuid
from datetime import date, time

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class User(Base):
    """Telegram user account."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_telegram_id", "telegram_id", unique=True),
        Index("ix_users_username", "username"),
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False,
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    interface_language: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="ru",
    )
    is_blocked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )
    is_registered: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )

    # --- Relationships (all use string refs to avoid circular imports) ---
    settings: Mapped[UserSettings | None] = relationship(
        back_populates="user", uselist=False, lazy="selectin",
        cascade="all, delete-orphan",
    )
    profile: Mapped[UserProfile | None] = relationship(
        back_populates="user", uselist=False, lazy="selectin",
        cascade="all, delete-orphan",
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    conversation_messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    language_levels: Mapped[list["LanguageLevel"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    user_vocabulary: Mapped[list["UserVocabulary"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    xp_transactions: Mapped[list["XPTransaction"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    daily_progress: Mapped[list["DailyProgress"]] = relationship(
        back_populates="user", lazy="noload", cascade="all, delete-orphan",
    )
    referrals_made: Mapped[list["Referral"]] = relationship(
        back_populates="referrer",
        foreign_keys="[Referral.referrer_id]",
        lazy="noload",
        cascade="all, delete-orphan",
    )
    referred_by: Mapped["Referral | None"] = relationship(
        back_populates="referred",
        foreign_keys="[Referral.referred_id]",
        uselist=False,
        lazy="noload",
    )
    usage_logs: Mapped[list["UsageLog"]] = relationship(
        back_populates="user", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, telegram_id={self.telegram_id})>"


class UserSettings(Base):
    """Per-user application settings."""

    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    learning_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    current_subject: Mapped[str | None] = mapped_column(String(50), nullable=True)
    study_goal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    daily_reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings(user_id={self.user_id!r})>"


class UserProfile(Base):
    """Gamification / progress profile for a user."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    xp: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    streak_days: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    tasks_solved: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    correct_answers: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    lessons_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    words_learned: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    total_study_time_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id!r}, xp={self.xp})>"
