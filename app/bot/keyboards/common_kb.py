"""EduLingua AI — Common Keyboards.

Reusable keyboard builders shared across multiple handlers.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import MenuCallback, SettingsCallback
from app.i18n import t


def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard for first launch (no lang yet)."""
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


def get_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Single "Back" button."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=MenuCallback(action="back").pack(),
        ),
    )
    return builder.as_markup()


def get_back_to_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Single "Back to Main Menu" button."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()


def get_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Yes / No confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_confirm_reset", lang),
            callback_data=SettingsCallback(action="confirm_reset", value="yes").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_cancel", lang),
            callback_data=SettingsCallback(action="confirm_reset", value="no").pack(),
        ),
    )
    return builder.as_markup()


def get_pagination_keyboard(
    lang: str,
    current_page: int,
    total_pages: int,
    callback_prefix: str,
) -> list[InlineKeyboardButton]:
    """Build pagination row buttons.

    Returns a list of buttons (not a markup) so the caller can append them
    to their own InlineKeyboardBuilder.
    """
    buttons: list[InlineKeyboardButton] = []

    if current_page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"{callback_prefix}:page:{current_page - 1}",
            )
        )

    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}",
            callback_data="noop",
        )
    )

    if current_page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"{callback_prefix}:page:{current_page + 1}",
            )
        )

    return buttons
