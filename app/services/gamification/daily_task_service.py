"""EduLingua AI — Daily Quests Service.

Generates and tracks daily study tasks for motivation and continuous engagement.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.daily import DailyTask
from app.database.repositories.gamification_repo import GamificationRepository

logger = logging.getLogger(__name__)


class DailyTaskService:
    """Service managing daily study missions."""

    DEFAULT_DAILY_TASKS = [
        {
            "task_type": "quiz",
            "title_ru": "Решить 3 учебные задачи",
            "title_uz": "3 ta o'quv masalasini yechish",
            "title_en": "Solve 3 study problems",
            "description_ru": "Задайте вопросы или решите задачи с помощью EduAI",
            "description_uz": "EduAI orqali savollar bering yoki masalalar yeching",
            "description_en": "Ask questions or solve problems using EduAI",
            "xp_reward": 50,
            "target_value": 3,
        },
        {
            "task_type": "vocabulary",
            "title_ru": "Выучить 5 новых слов",
            "title_uz": "5 ta yangi so'z o'rganish",
            "title_en": "Learn 5 new vocabulary words",
            "description_ru": "Потренируйте словарный запас в LinguaBot",
            "description_uz": "LinguaBotda lug'at boyligini mashq qiling",
            "description_en": "Practice vocabulary cards in LinguaBot",
            "xp_reward": 40,
            "target_value": 5,
        },
        {
            "task_type": "speaking",
            "title_ru": "Пройти диалог в LinguaBot",
            "title_uz": "LinguaBotda suhbat o'tkazish",
            "title_en": "Complete a conversation in LinguaBot",
            "description_ru": "Потренируйте разговорную речь на иностранном языке",
            "description_uz": "Xorijiy tilda muloqotni mashq qiling",
            "description_en": "Practice conversational speaking with the AI partner",
            "xp_reward": 60,
            "target_value": 1,
        },
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = GamificationRepository(session)

    async def ensure_daily_tasks(self) -> None:
        """Seed standard daily templates if empty."""
        stmt = select(DailyTask)
        existing = (await self.session.execute(stmt)).scalars().all()
        if not existing:
            for item in self.DEFAULT_DAILY_TASKS:
                task = DailyTask(
                    task_type=item["task_type"],
                    title_ru=item["title_ru"],
                    title_uz=item["title_uz"],
                    title_en=item["title_en"],
                    description_ru=item["description_ru"],
                    description_uz=item["description_uz"],
                    description_en=item["description_en"],
                    xp_reward=item["xp_reward"],
                    target_value=item["target_value"],
                    is_active=True,
                )
                self.session.add(task)
            await self.session.flush()

    async def get_today_tasks_for_user(self, user_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return today's active tasks and progress for a user."""
        await self.ensure_daily_tasks()
        return await self.repo.get_daily_tasks(user_id)

    async def increment_task_progress(
        self, user_id: uuid.UUID, task_type: str, increment: int = 1
    ) -> list[DailyTask]:
        """Record progress towards daily task."""
        await self.ensure_daily_tasks()
        return await self.repo.update_daily_task_progress(user_id, task_type, increment)
