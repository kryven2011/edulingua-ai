"""EduLingua AI — Main Menu Keyboard."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import MenuCallback
from app.i18n import t


def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Build the 9-button main menu inline keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=t("btn_eduai", lang),
            callback_data=MenuCallback(action="eduai").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_lingua", lang),
            callback_data=MenuCallback(action="lingua").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_progress", lang),
            callback_data=MenuCallback(action="progress").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_daily", lang),
            callback_data=MenuCallback(action="daily").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_leaderboard", lang),
            callback_data=MenuCallback(action="leaderboard").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_premium", lang),
            callback_data=MenuCallback(action="premium").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_profile", lang),
            callback_data=MenuCallback(action="profile").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_settings", lang),
            callback_data=MenuCallback(action="settings").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_help", lang),
            callback_data=MenuCallback(action="help").pack(),
        ),
    )

    return builder.as_markup()
