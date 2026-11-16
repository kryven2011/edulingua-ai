"""EduLingua AI — Language Repository.

Handles foreign languages, vocabulary, spaced repetition, grammar lessons, and level tests.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.language import (
    GrammarLesson,
    Language,
    LanguageLevel,
    UserVocabulary,
    VocabularyWord,
)
from app.database.repositories.base import BaseRepository


class LanguageRepository(BaseRepository[Language]):
    """Repository for LinguaBot entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Language, session)

    async def get_active_languages(self) -> Sequence[Language]:
        """Fetch all enabled target languages."""
        stmt = (
            select(Language)
            .where(Language.is_active == True)  # noqa: E712
            .order_by(Language.code.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_code(self, code: str) -> Language | None:
        """Find language by code (e.g. 'en', 'de', 'es')."""
        stmt = select(Language).where(Language.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_level(
        self,
        user_id: uuid.UUID,
        language_id: uuid.UUID,
    ) -> LanguageLevel | None:
        """Retrieve user's assessed level in language."""
        stmt = select(LanguageLevel).where(
            LanguageLevel.user_id == user_id,
            LanguageLevel.language_id == language_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_user_level(
        self,
        user_id: uuid.UUID,
        language_id: uuid.UUID,
        level: str,
        score: int = 0,
    ) -> LanguageLevel:
        """Create or update user language level."""
        current = await self.get_user_level(user_id, language_id)
        if current:
            current.level = level
            current.assessment_score = score
            current.assessed_at = datetime.utcnow()
            await self.session.flush()
            return current

        new_level = LanguageLevel(
            user_id=user_id,
            language_id=language_id,
            level=level,
            assessment_score=score,
            assessed_at=datetime.utcnow(),
        )
        self.session.add(new_level)
        await self.session.flush()
        return new_level

    async def get_words_for_review(
        self,
        user_id: uuid.UUID,
        language_id: uuid.UUID,
        limit: int = 10,
    ) -> Sequence[UserVocabulary]:
        """Fetch vocabulary items due for spaced repetition review."""
        now = datetime.utcnow()
        stmt = (
            select(UserVocabulary)
            .options(selectinload(UserVocabulary.word))
            .join(VocabularyWord, UserVocabulary.word_id == VocabularyWord.id)
            .where(
                UserVocabulary.user_id == user_id,
                VocabularyWord.language_id == language_id,
                UserVocabulary.next_review_at <= now,
            )
            .order_by(UserVocabulary.next_review_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_new_words(
        self,
        user_id: uuid.UUID,
        language_id: uuid.UUID,
        limit: int = 5,
    ) -> Sequence[VocabularyWord]:
        """Find words not yet in user's vocabulary list."""
        subquery = (
            select(UserVocabulary.word_id)
            .where(UserVocabulary.user_id == user_id)
        )
        stmt = (
            select(VocabularyWord)
            .where(
                VocabularyWord.language_id == language_id,
                VocabularyWord.id.not_in(subquery),
            )
            .order_by(VocabularyWord.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_or_update_word_review(
        self,
        user_id: uuid.UUID,
        word_id: uuid.UUID,
        next_review_at: datetime,
        ease_factor: float,
        review_count: int,
        status: str,
    ) -> UserVocabulary:
        """Upsert spaced repetition state for a word."""
        stmt = select(UserVocabulary).where(
            UserVocabulary.user_id == user_id,
            UserVocabulary.word_id == word_id,
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        if item:
            item.next_review_at = next_review_at
            item.ease_factor = ease_factor
            item.review_count = review_count
            item.status = status
            await self.session.flush()
            return item

        item = UserVocabulary(
            user_id=user_id,
            word_id=word_id,
            next_review_at=next_review_at,
            ease_factor=ease_factor,
            review_count=review_count,
            status=status,
            learned_at=datetime.utcnow(),
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_grammar_lessons(
        self,
        language_id: uuid.UUID,
        level: str | None = None,
    ) -> Sequence[GrammarLesson]:
        """Fetch grammar lessons, optionally filtered by level."""
        stmt = (
            select(GrammarLesson)
            .where(
                GrammarLesson.language_id == language_id,
                GrammarLesson.is_active == True,  # noqa: E712
            )
            .order_by(GrammarLesson.sort_order.asc())
        )
        if level:
            stmt = stmt.where(GrammarLesson.level == level)
        result = await self.session.execute(stmt)
        return result.scalars().all()
