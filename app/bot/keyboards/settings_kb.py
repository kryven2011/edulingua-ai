"""EduLingua AI — Settings Keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import MenuCallback, SettingsCallback
from app.i18n import t


def get_settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=t("btn_change_lang", lang),
            callback_data=SettingsCallback(action="change_lang").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_change_learning_lang", lang),
            callback_data=SettingsCallback(action="change_learning_lang").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_reset_progress", lang),
            callback_data=SettingsCallback(action="reset_progress").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )

    return builder.as_markup()


def get_language_change_keyboard() -> InlineKeyboardMarkup:
    """Language change keyboard (same as initial selection but with settings callback)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🇷🇺 Русский",
            callback_data=SettingsCallback(action="set_lang", value="ru").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🇺🇿 Oʻzbekcha",
            callback_data=SettingsCallback(action="set_lang", value="uz").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🇬🇧 English",
            callback_data=SettingsCallback(action="set_lang", value="en").pack(),
        ),
    )
    return builder.as_markup()
