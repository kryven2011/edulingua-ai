"""EduLingua AI — Daily Quests Handler.

Displays active daily tasks and completion states.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import MenuCallback
from app.bot.keyboards.daily_kb import get_daily_tasks_keyboard
from app.database.models.user import User
from app.i18n import t
from app.services.gamification.daily_task_service import DailyTaskService

router = Router(name="daily")


@router.callback_query(MenuCallback.filter(F.action == "daily"))
async def show_daily_tasks(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Render daily quests screen."""
    daily_service = DailyTaskService(session)
    tasks_data = await daily_service.get_today_tasks_for_user(user.id)

    task_lines = []
    for item in tasks_data:
        task = item["task"]
        cur = item["current_value"]
        target = task.target_value
        done = item["is_completed"]
        status_icon = "✅" if done else f"({cur}/{target})"
        title = getattr(task, f"title_{lang}", task.title_ru)
        task_lines.append(f"• <b>{title}</b> — +{task.xp_reward} XP {status_icon}")

    tasks_str = "\n".join(task_lines) if task_lines else "Нет активных заданий на сегодня."
    text = t("daily_title", lang=lang, tasks=tasks_str)

    markup = get_daily_tasks_keyboard(lang=lang, tasks=[item["task"] for item in tasks_data])
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()
