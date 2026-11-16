"""EduLingua AI — Gamification Repository.

Handles XP transactions (with strict idempotency), achievements, daily tasks, and leaderboards.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Sequence

from sqlalchemy import desc, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.gamification import (
    Achievement,
    UserAchievement,
    XPTransaction,
)
from app.database.models.daily import DailyProgress, DailyTask
from app.database.models.user import User, UserProfile
from app.database.repositories.base import BaseRepository


class GamificationRepository(BaseRepository[Achievement]):
    """Repository for XP, achievements, daily quests, and leaderboards."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Achievement, session)

    async def award_xp(
        self,
        user_id: uuid.UUID,
        amount: int,
        source: str,
        idempotency_key: str,
        description: str | None = None,
        source_id: uuid.UUID | None = None,
    ) -> tuple[int, bool]:
        """Award XP with strict idempotency protection against duplicate rewards.
        
        Returns:
            Tuple of (new_total_xp, awarded: bool). If duplicate key, returns (current_xp, False).
        """
        # Check if idempotency key was already processed
        stmt_check = select(XPTransaction).where(
            XPTransaction.idempotency_key == idempotency_key
        )
        existing = (await self.session.execute(stmt_check)).scalar_one_or_none()
        if existing:
            # Already awarded
            profile_stmt = select(UserProfile.xp).where(UserProfile.user_id == user_id)
            current_xp = (await self.session.execute(profile_stmt)).scalar_one() or 0
            return current_xp, False

        # Insert XP Transaction
        tx = XPTransaction(
            user_id=user_id,
            amount=amount,
            source=source,
            source_id=source_id,
            description=description,
            idempotency_key=idempotency_key,
        )
        self.session.add(tx)

        # Update UserProfile total XP
        update_stmt = (
            update(UserProfile)
            .where(UserProfile.user_id == user_id)
            .values(xp=UserProfile.xp + amount)
            .returning(UserProfile.xp)
        )
        result = await self.session.execute(update_stmt)
        new_xp = result.scalar_one() or amount
        await self.session.flush()

        return new_xp, True

    async def get_user_achievements(
        self, user_id: uuid.UUID
    ) -> Sequence[UserAchievement]:
        """Fetch all achievements unlocked by user."""
        stmt = (
            select(UserAchievement)
            .options(selectinload(UserAchievement.achievement))
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def unlock_achievement(
        self, user_id: uuid.UUID, achievement_code: str
    ) -> UserAchievement | None:
        """Unlock an achievement if not already owned."""
        ach_stmt = select(Achievement).where(Achievement.code == achievement_code)
        achievement = (await self.session.execute(ach_stmt)).scalar_one_or_none()
        if not achievement:
            return None

        # Check existing
        existing_stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id,
        )
        if (await self.session.execute(existing_stmt)).scalar_one_or_none():
            return None

        user_ach = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id,
            unlocked_at=datetime.utcnow(),
        )
        self.session.add(user_ach)
        await self.session.flush()

        # Award XP for achievement
        idem_key = f"ach:{user_id}:{achievement.id}"
        await self.award_xp(
            user_id=user_id,
            amount=achievement.xp_reward,
            source="achievement",
            idempotency_key=idem_key,
            description=f"Unlocked: {achievement.title_ru}",
            source_id=achievement.id,
        )
        return user_ach

    async def get_daily_tasks(
        self, user_id: uuid.UUID, target_date: date | None = None
    ) -> list[dict[str, Any]]:
        """Fetch active daily tasks with user completion status."""
        today = target_date or date.today()
        # Active tasks
        stmt_tasks = (
            select(DailyTask)
            .where(DailyTask.is_active == True)  # noqa: E712
            .order_by(DailyTask.created_at.asc())
        )
        tasks = (await self.session.execute(stmt_tasks)).scalars().all()

        # User progress
        stmt_prog = select(DailyProgress).where(
            DailyProgress.user_id == user_id,
            DailyProgress.date == today,
        )
        progress_map = {
            p.task_id: p
            for p in (await self.session.execute(stmt_prog)).scalars().all()
        }

        output = []
        for task in tasks:
            prog = progress_map.get(task.id)
            current_val = prog.current_value if prog else 0
            is_done = prog.is_completed if prog else False
            output.append({
                "task": task,
                "current_value": current_val,
                "is_completed": is_done,
            })
        return output

    async def update_daily_task_progress(
        self,
        user_id: uuid.UUID,
        task_type: str,
        increment: int = 1,
    ) -> list[DailyTask]:
        """Increment progress for daily tasks matching task_type.
        
        Returns newly completed tasks.
        """
        today = date.today()
        tasks_stmt = select(DailyTask).where(
            DailyTask.task_type == task_type,
            DailyTask.is_active == True,  # noqa: E712
        )
        matching_tasks = (await self.session.execute(tasks_stmt)).scalars().all()
        newly_completed = []

        for task in matching_tasks:
            stmt = select(DailyProgress).where(
                DailyProgress.user_id == user_id,
                DailyProgress.task_id == task.id,
                DailyProgress.date == today,
            )
            prog = (await self.session.execute(stmt)).scalar_one_or_none()

            if not prog:
                prog = DailyProgress(
                    user_id=user_id,
                    task_id=task.id,
                    date=today,
                    current_value=0,
                    is_completed=False,
                )
                self.session.add(prog)

            if not prog.is_completed:
                prog.current_value += increment
                if prog.current_value >= task.target_value:
                    prog.is_completed = True
                    prog.completed_at = datetime.utcnow()
                    prog.xp_awarded = task.xp_reward
                    newly_completed.append(task)

                    # Award XP
                    idem = f"daily:{user_id}:{task.id}:{today.isoformat()}"
                    await self.award_xp(
                        user_id=user_id,
                        amount=task.xp_reward,
                        source="daily_task",
                        idempotency_key=idem,
                        description=f"Daily quest: {task.title_ru}",
                        source_id=task.id,
                    )
        await self.session.flush()
        return newly_completed

    async def get_leaderboard(
        self, period: str = "daily", limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get leaderboard entries for the specified period ('daily', 'weekly', 'all')."""
        if period == "all":
            # All time based on UserProfile
            stmt = (
                select(User, UserProfile)
                .join(UserProfile, User.id == UserProfile.user_id)
                .where(User.is_blocked == False)  # noqa: E712
                .order_by(UserProfile.xp.desc())
                .limit(limit)
            )
            rows = (await self.session.execute(stmt)).all()
            return [
                {
                    "rank": idx + 1,
                    "user_id": u.id,
                    "name": u.first_name or u.username or f"User #{u.telegram_id}",
                    "xp": p.xp,
                    "level": p.level,
                }
                for idx, (u, p) in enumerate(rows)
            ]

        # For daily or weekly, aggregate from XPTransaction
        if period == "daily":
            cutoff = datetime.utcnow() - timedelta(days=1)
        else:  # weekly
            cutoff = datetime.utcnow() - timedelta(days=7)

        stmt = (
            select(
                User.id,
                User.first_name,
                User.username,
                User.telegram_id,
                func.sum(XPTransaction.amount).label("period_xp"),
            )
            .join(XPTransaction, User.id == XPTransaction.user_id)
            .where(
                User.is_blocked == False,  # noqa: E712
                XPTransaction.created_at >= cutoff,
            )
            .group_by(User.id, User.first_name, User.username, User.telegram_id)
            .order_by(desc("period_xp"))
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            {
                "rank": idx + 1,
                "user_id": r.id,
                "name": r.first_name or r.username or f"User #{r.telegram_id}",
                "xp": int(r.period_xp or 0),
            }
            for idx, r in enumerate(rows)
        ]
