"""EduLingua AI — Education Models.

Subject, StudySession, and ConversationMessage models.
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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class SessionType(str, enum.Enum):
    """Type of study session."""

    QUESTION = "question"
    PHOTO_TASK = "photo_task"
    TEST = "test"
    EXERCISE = "exercise"


class SessionStatus(str, enum.Enum):
    """Status of a study session."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageRole(str, enum.Enum):
    """Role of a conversation participant."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, enum.Enum):
    """Type of message content."""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"


class Subject(Base):
    """Educational subject (Math, Physics, etc.)."""

    __tablename__ = "subjects"
    __table_args__ = (
        Index("ix_subjects_code", "code", unique=True),
    )

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False,
    )
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )

    # --- Relationships ---
    study_sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="subject", lazy="noload",
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="subject", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Subject(code={self.code!r})>"


class StudySession(Base):
    """A single study session between user and AI."""

    __tablename__ = "study_sessions"
    __table_args__ = (
        Index("ix_study_sessions_user_id", "user_id"),
        Index("ix_study_sessions_subject_id", "subject_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True,
    )
    session_type: Mapped[SessionType] = mapped_column(
        Enum(SessionType, name="session_type_enum", native_enum=False),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status_enum", native_enum=False),
        nullable=False,
        server_default=SessionStatus.ACTIVE.value,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()",
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="study_sessions")
    subject: Mapped["Subject | None"] = relationship(back_populates="study_sessions")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="session", lazy="noload", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<StudySession(id={self.id!r}, user_id={self.user_id!r}, "
            f"type={self.session_type})>"
        )


class ConversationMessage(Base):
    """Single message in a study conversation."""

    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index("ix_conversation_messages_user_id", "user_id"),
        Index("ix_conversation_messages_session_id", "session_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role_enum", native_enum=False),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type_enum", native_enum=False),
        nullable=False,
        server_default=MessageType.TEXT.value,
    )
    tokens_used: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="conversation_messages")
    session: Mapped["StudySession | None"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return (
            f"<ConversationMessage(id={self.id!r}, role={self.role}, "
            f"tokens={self.tokens_used})>"
        )


# String-based forward references resolved by SQLAlchemy registry
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.quiz import QuizQuestion
    from app.database.models.user import User
