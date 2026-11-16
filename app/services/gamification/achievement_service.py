"""EduLingua AI — Achievement Service.

Manages unlockable badges and progress milestones.
"""

from __future__ import annotations

import logging
import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.gamification import Achievement, UserAchievement
from app.database.models.user import UserProfile
from app.database.repositories.gamification_repo import GamificationRepository

logger = logging.getLogger(__name__)


class AchievementService:
    """Service checking milestones and granting achievements."""

    DEFAULT_ACHIEVEMENTS = [
        {
            "code": "first_lesson",
            "title_ru": "Первый урок",
            "title_uz": "Birinchi dars",
            "title_en": "First Lesson",
            "description_ru": "Завершите ваш первый учебный диалог или задачу",
            "description_uz": "Birinchi o'quv darsini yakunlang",
            "description_en": "Complete your first study lesson or task",
            "icon": "🏅",
            "xp_reward": 50,
            "condition_type": "lessons_completed",
            "condition_value": 1,
        },
        {
            "code": "streak_7",
            "title_ru": "Неделя в ударе",
            "title_uz": "7 kun ketma-ket",
            "title_en": "7 Days Streak",
            "description_ru": "Занимайтесь 7 дней подряд без перерыва",
            "description_uz": "Ketma-ket 7 kun davomida ta'lim oling",
            "description_en": "Study 7 consecutive days without missing",
            "icon": "🔥",
            "xp_reward": 200,
            "condition_type": "streak_days",
            "condition_value": 7,
        },
        {
            "code": "word_master_100",
            "title_ru": "Мастер слов",
            "title_uz": "So'z ustasi",
            "title_en": "Word Master",
            "description_ru": "Выучите 100 новых иностранных слов",
            "description_uz": "100 ta yangi xorijiy so'zni o'rganing",
            "description_en": "Master 100 foreign words",
            "icon": "📚",
            "xp_reward": 300,
            "condition_type": "words_learned",
            "condition_value": 100,
        },
        {
            "code": "smart_student_50",
            "title_ru": "Умный ученик",
            "title_uz": "Aqlli o'quvchi",
            "title_en": "Smart Student",
            "description_ru": "Дайте 50 правильных ответов на тесты и задачи",
            "description_uz": "50 ta savolga to'g'ri javob bering",
            "description_en": "Provide 50 correct answers in quizzes",
            "icon": "🧠",
            "xp_reward": 250,
            "condition_type": "correct_answers",
            "condition_value": 50,
        },
        {
            "code": "tasks_solved_25",
            "title_ru": "Решатель задач",
            "title_uz": "Masalalar yechuvchi",
            "title_en": "Problem Solver",
            "description_ru": "Решите 25 практических задач по школьным предметам",
            "description_uz": "25 ta amaliy masalani yeching",
            "description_en": "Solve 25 problems in school subjects",
            "icon": "📐",
            "xp_reward": 200,
            "condition_type": "tasks_solved",
            "condition_value": 25,
        },
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = GamificationRepository(session)

    async def ensure_defaults(self) -> None:
        """Seed default achievements if not present."""
        stmt = select(Achievement)
        existing = (await self.session.execute(stmt)).scalars().all()
        existing_codes = {a.code for a in existing}

        for item in self.DEFAULT_ACHIEVEMENTS:
            if item["code"] not in existing_codes:
                ach = Achievement(
                    code=item["code"],
                    title_ru=item["title_ru"],
                    title_uz=item["title_uz"],
                    title_en=item["title_en"],
                    description_ru=item["description_ru"],
                    description_uz=item["description_uz"],
                    description_en=item["description_en"],
                    icon=item["icon"],
                    xp_reward=item["xp_reward"],
                    condition_type=item["condition_type"],
                    condition_value=item["condition_value"],
                    is_active=True,
                )
                self.session.add(ach)
        await self.session.flush()

    async def check_and_unlock(self, user_id: uuid.UUID) -> list[Achievement]:
        """Check user profile stats against unearned achievements and unlock qualifying ones."""
        await self.ensure_defaults()

        stmt_profile = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = (await self.session.execute(stmt_profile)).scalar_one_or_none()
        if not profile:
            return []

        # Current unlocked
        user_achs = await self.repo.get_user_achievements(user_id)
        unlocked_codes = {ua.achievement.code for ua in user_achs if ua.achievement}

        # Available
        stmt_all = select(Achievement).where(Achievement.is_active == True)  # noqa: E712
        all_achs = (await self.session.execute(stmt_all)).scalars().all()

        newly_unlocked = []
        for ach in all_achs:
            if ach.code in unlocked_codes:
                continue

            cond = ach.condition_type
            val = ach.condition_value
            earned = False

            if cond == "lessons_completed" and profile.lessons_completed >= val:
                earned = True
            elif cond == "streak_days" and profile.streak_days >= val:
                earned = True
            elif cond == "words_learned" and profile.words_learned >= val:
                earned = True
            elif cond == "correct_answers" and profile.correct_answers >= val:
                earned = True
            elif cond == "tasks_solved" and profile.tasks_solved >= val:
                earned = True

            if earned:
                unlocked = await self.repo.unlock_achievement(user_id, ach.code)
                if unlocked:
                    newly_unlocked.append(ach)

        return newly_unlocked
