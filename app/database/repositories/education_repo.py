"""EduLingua AI — Education Repository.

Handles subjects, study sessions, and conversation messages for EduAI tutor.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.education import (
    ConversationMessage,
    StudySession,
    Subject,
)
from app.database.repositories.base import BaseRepository


class EducationRepository(BaseRepository[Subject]):
    """Repository for Subjects and StudySessions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Subject, session)

    async def get_active_subjects(self) -> Sequence[Subject]:
        """Fetch all enabled subjects ordered by sort_order."""
        stmt = (
            select(Subject)
            .where(Subject.is_active == True)  # noqa: E712
            .order_by(Subject.sort_order.asc(), Subject.code.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_subject_by_code(self, code: str) -> Subject | None:
        """Find subject by code."""
        stmt = select(Subject).where(Subject.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_study_session(
        self,
        user_id: uuid.UUID,
        subject_id: uuid.UUID,
        session_type: str = "question",
    ) -> StudySession:
        """Start a new study session."""
        session = StudySession(
            user_id=user_id,
            subject_id=subject_id,
            session_type=session_type,
            status="active",
            started_at=datetime.utcnow(),
        )
        self.session.add(session)
        await self.session.flush()
        return session

    async def get_active_session(
        self,
        user_id: uuid.UUID,
        subject_id: uuid.UUID | None = None,
    ) -> StudySession | None:
        """Get user's latest active session."""
        stmt = (
            select(StudySession)
            .where(
                StudySession.user_id == user_id,
                StudySession.status == "active",
            )
            .order_by(StudySession.started_at.desc())
        )
        if subject_id:
            stmt = stmt.where(StudySession.subject_id == subject_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def end_study_session(self, session_id: uuid.UUID) -> None:
        """Mark study session as completed."""
        stmt = (
            update(StudySession)
            .where(StudySession.id == session_id)
            .values(status="completed", ended_at=datetime.utcnow())
        )
        await self.session.execute(stmt)

    async def save_message(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        content: str,
        message_type: str = "text",
        tokens_used: int = 0,
    ) -> ConversationMessage:
        """Record message in conversation history."""
        msg = ConversationMessage(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            message_type=message_type,
            tokens_used=tokens_used,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def get_recent_messages(
        self,
        session_id: uuid.UUID,
        limit: int = 10,
    ) -> list[ConversationMessage]:
        """Fetch latest messages for conversation context (oldest first)."""
        stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()
        return messages
