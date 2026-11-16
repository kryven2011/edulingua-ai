"""EduLingua AI — Leaderboard Keyboard."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import LeaderboardCallback, MenuCallback
from app.i18n import t


def get_leaderboard_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Leaderboard period-switching keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_daily_board", lang),
            callback_data=LeaderboardCallback(period="daily").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_weekly_board", lang),
            callback_data=LeaderboardCallback(period="weekly").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_alltime_board", lang),
            callback_data=LeaderboardCallback(period="alltime").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()
