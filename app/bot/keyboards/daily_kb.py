"""EduLingua AI — Daily Tasks Keyboard."""

from __future__ import annotations

from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import DailyCallback, MenuCallback
from app.i18n import t


def get_daily_tasks_keyboard(
    lang: str,
    tasks: list[dict[str, Any]],
) -> InlineKeyboardMarkup:
    """Build keyboard with a button per incomplete daily task.

    Each task dict is expected to have at minimum:
        - "id": str
        - "title": str
        - "completed": bool
    """
    builder = InlineKeyboardBuilder()

    for task in tasks:
        if not task.get("completed", False):
            builder.row(
                InlineKeyboardButton(
                    text=f"▶️ {task['title']}",
                    callback_data=DailyCallback(
                        action="start", task_id=str(task["id"])
                    ).pack(),
                ),
            )

    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()
