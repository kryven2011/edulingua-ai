"""EduLingua AI — Language Learning Models.

Language, LanguageLevel, VocabularyWord, UserVocabulary, GrammarLesson.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class LanguageProficiency(str, enum.Enum):
    """CEFR language proficiency levels."""

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class VocabularyStatus(str, enum.Enum):
    """Spaced-repetition status for a vocabulary word."""

    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    MASTERED = "mastered"


class Language(Base):
    """Supported language for learning."""

    __tablename__ = "languages"
    __table_args__ = (
        Index("ix_languages_code", "code", unique=True),
    )

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )

    # --- Relationships ---
    levels: Mapped[list["LanguageLevel"]] = relationship(
        back_populates="language", lazy="noload",
    )
    vocabulary_words: Mapped[list["VocabularyWord"]] = relationship(
        back_populates="language", lazy="noload",
    )
    grammar_lessons: Mapped[list["GrammarLesson"]] = relationship(
        back_populates="language", lazy="noload",
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="language", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Language(code={self.code!r})>"


class LanguageLevel(Base):
    """Assessed language proficiency level for a user."""

    __tablename__ = "language_levels"
    __table_args__ = (
        UniqueConstraint("language_id", "user_id", name="uq_language_level_user"),
        Index("ix_language_levels_user_id", "user_id"),
    )

    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("languages.id", ondelete="CASCADE"), nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    level: Mapped[LanguageProficiency] = mapped_column(
        Enum(LanguageProficiency, name="language_proficiency_enum", native_enum=False),
        nullable=False,
        server_default=LanguageProficiency.A1.value,
    )
    assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    assessment_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Relationships ---
    language: Mapped["Language"] = relationship(back_populates="levels")
    user: Mapped["User"] = relationship(back_populates="language_levels")

    def __repr__(self) -> str:
        return (
            f"<LanguageLevel(user_id={self.user_id!r}, "
            f"language_id={self.language_id!r}, level={self.level})>"
        )


class VocabularyWord(Base):
    """A vocabulary word in a specific language."""

    __tablename__ = "vocabulary_words"
    __table_args__ = (
        Index("ix_vocabulary_words_language_id", "language_id"),
        Index("ix_vocabulary_words_topic", "topic"),
    )

    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("languages.id", ondelete="CASCADE"), nullable=False,
    )
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    translation_ru: Mapped[str | None] = mapped_column(String(500), nullable=True)
    translation_uz: Mapped[str | None] = mapped_column(String(500), nullable=True)
    translation_en: Mapped[str | None] = mapped_column(String(500), nullable=True)
    example_sentence: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1",
    )
    topic: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # --- Relationships ---
    language: Mapped["Language"] = relationship(back_populates="vocabulary_words")
    user_vocabulary: Mapped[list["UserVocabulary"]] = relationship(
        back_populates="word_entry", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<VocabularyWord(word={self.word!r}, language_id={self.language_id!r})>"


class UserVocabulary(Base):
    """User's personal vocabulary with spaced-repetition data."""

    __tablename__ = "user_vocabulary"
    __table_args__ = (
        UniqueConstraint("user_id", "word_id", name="uq_user_vocabulary"),
        Index("ix_user_vocabulary_user_id", "user_id"),
        Index("ix_user_vocabulary_next_review", "next_review_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    word_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vocabulary_words.id", ondelete="CASCADE"), nullable=False,
    )
    learned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    review_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    ease_factor: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="2.5",
    )
    status: Mapped[VocabularyStatus] = mapped_column(
        Enum(VocabularyStatus, name="vocabulary_status_enum", native_enum=False),
        nullable=False,
        server_default=VocabularyStatus.NEW.value,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="user_vocabulary")
    word_entry: Mapped["VocabularyWord"] = relationship(
        back_populates="user_vocabulary",
    )

    def __repr__(self) -> str:
        return (
            f"<UserVocabulary(user_id={self.user_id!r}, "
            f"word_id={self.word_id!r}, status={self.status})>"
        )


class GrammarLesson(Base):
    """Grammar lesson content for a language."""

    __tablename__ = "grammar_lessons"
    __table_args__ = (
        Index("ix_grammar_lessons_language_id", "language_id"),
    )

    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("languages.id", ondelete="CASCADE"), nullable=False,
    )
    title_ru: Mapped[str] = mapped_column(String(500), nullable=False)
    title_uz: Mapped[str] = mapped_column(String(500), nullable=False)
    title_en: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[LanguageProficiency] = mapped_column(
        Enum(LanguageProficiency, name="language_proficiency_enum", native_enum=False,
             create_constraint=False),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )

    # --- Relationships ---
    language: Mapped["Language"] = relationship(back_populates="grammar_lessons")

    def __repr__(self) -> str:
        return f"<GrammarLesson(id={self.id!r}, level={self.level})>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.quiz import QuizQuestion
    from app.database.models.user import User
