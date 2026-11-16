"""EduLingua AI — Quiz Models.

QuizQuestion and QuizAttempt models for quizzes and testing.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class QuestionType(str, enum.Enum):
    """Type of quiz question."""

    MULTIPLE_CHOICE = "multiple_choice"
    TEXT_INPUT = "text_input"
    TRUE_FALSE = "true_false"


class QuizQuestion(Base):
    """A quiz / test question."""

    __tablename__ = "quiz_questions"
    __table_args__ = (
        Index("ix_quiz_questions_subject_id", "subject_id"),
        Index("ix_quiz_questions_language_id", "language_id"),
        Index("ix_quiz_questions_difficulty", "difficulty"),
    )

    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True,
    )
    language_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("languages.id", ondelete="SET NULL"), nullable=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, name="question_type_enum", native_enum=False),
        nullable=False,
    )
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(1000), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )

    # --- Relationships ---
    subject: Mapped["Subject | None"] = relationship(back_populates="quiz_questions")
    language: Mapped["Language | None"] = relationship(back_populates="quiz_questions")
    attempts: Mapped[list["QuizAttempt"]] = relationship(
        back_populates="question", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<QuizQuestion(id={self.id!r}, type={self.question_type})>"


class QuizAttempt(Base):
    """A user's attempt at answering a quiz question."""

    __tablename__ = "quiz_attempts"
    __table_args__ = (
        Index("ix_quiz_attempts_user_id", "user_id"),
        Index("ix_quiz_attempts_question_id", "question_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False,
    )
    user_answer: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_taken_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    xp_earned: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    question: Mapped["QuizQuestion"] = relationship(back_populates="attempts")

    def __repr__(self) -> str:
        return (
            f"<QuizAttempt(user_id={self.user_id!r}, "
            f"question_id={self.question_id!r}, correct={self.is_correct})>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.education import Subject
    from app.database.models.language import Language
    from app.database.models.user import User
