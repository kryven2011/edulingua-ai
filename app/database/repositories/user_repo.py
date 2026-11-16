"""EduLingua AI — User Repository.

Handles user creation, profile statistics, settings, and queries.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.user import User, UserProfile, UserSettings
from app.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User and related entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Find user by telegram ID with settings and profile preloaded."""
        stmt = (
            select(User)
            .options(
                selectinload(User.settings),
                selectinload(User.profile),
            )
            .where(User.telegram_id == telegram_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        default_language: str = "ru",
    ) -> tuple[User, bool]:
        """Fetch existing user or create a new user with default settings & profile.
        
        Returns:
            Tuple of (User, created: bool)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            # Update names/username if changed
            changed = False
            if user.username != username:
                user.username = username
                changed = True
            if user.first_name != first_name:
                user.first_name = first_name
                changed = True
            if user.last_name != last_name:
                user.last_name = last_name
                changed = True
            if changed:
                await self.session.flush()
            return user, False

        # Create new user
        new_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            interface_language=default_language,
            is_blocked=False,
            is_admin=False,
            is_registered=False,
        )
        self.session.add(new_user)
        await self.session.flush()

        # Create settings
        settings = UserSettings(
            user_id=new_user.id,
            learning_language="en",
            notifications_enabled=True,
        )
        self.session.add(settings)

        # Create profile
        today = date.today()
        profile = UserProfile(
            user_id=new_user.id,
            xp=0,
            level=1,
            streak_days=1,
            last_active_date=today,
            tasks_solved=0,
            correct_answers=0,
            lessons_completed=0,
            words_learned=0,
            total_study_time_minutes=0,
        )
        self.session.add(profile)
        await self.session.flush()

        # Preload relationships
        new_user.settings = settings
        new_user.profile = profile

        return new_user, True

    async def complete_registration(
        self,
        user_id: uuid.UUID,
        name: str | None = None,
        interface_language: str | None = None,
        study_goal: str | None = None,
        learning_language: str | None = None,
        target_level: str | None = None,
    ) -> User:
        """Mark user as fully registered and store initial preferences."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        user.is_registered = True
        if name:
            user.first_name = name
        if interface_language:
            user.interface_language = interface_language

        if user.settings:
            if study_goal:
                user.settings.study_goal = study_goal
            if learning_language:
                user.settings.learning_language = learning_language
            if target_level:
                user.settings.target_level = target_level

        await self.session.flush()
        return user

    async def update_interface_language(self, user_id: uuid.UUID, language: str) -> None:
        """Update interface language for a user."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(interface_language=language)
        )
        await self.session.execute(stmt)

    async def update_activity_streak(self, user_id: uuid.UUID) -> int:
        """Update active day streak. Returns current streak."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        if not profile:
            return 1

        today = date.today()
        if profile.last_active_date == today:
            return profile.streak_days

        if profile.last_active_date:
            days_diff = (today - profile.last_active_date).days
            if days_diff == 1:
                profile.streak_days += 1
            elif days_diff > 1:
                profile.streak_days = 1
        else:
            profile.streak_days = 1

        profile.last_active_date = today
        await self.session.flush()
        return profile.streak_days

    async def update_learning_language(self, user_id: uuid.UUID, language_code: str) -> None:
        """Update selected target learning language."""
        stmt = (
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(learning_language=language_code)
        )
        await self.session.execute(stmt)

    async def set_current_subject(self, user_id: uuid.UUID, subject_code: str) -> None:
        """Update user's active subject."""
        stmt = (
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(current_subject=subject_code)
        )
        await self.session.execute(stmt)

    async def get_profile(self, user_id: uuid.UUID) -> UserProfile | None:
        """Retrieve user profile."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_total_users(self) -> int:
        """Total user count."""
        return await self.count()

    async def count_active_today(self) -> int:
        """Active users today."""
        today = date.today()
        stmt = (
            select(func.count())
            .select_from(UserProfile)
            .where(UserProfile.last_active_date == today)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def block_user(self, user_id: uuid.UUID, blocked: bool = True) -> bool:
        """Block or unblock user."""
        stmt = update(User).where(User.id == user_id).values(is_blocked=blocked)
        result = await self.session.execute(stmt)
        return (result.rowcount or 0) > 0
