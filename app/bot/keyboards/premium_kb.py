"""EduLingua AI — Premium Keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import MenuCallback, PremiumCallback
from app.i18n import t


def get_premium_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Premium plans overview keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_free_plan", lang),
            callback_data=PremiumCallback(action="select", tier="free").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_pro_plan", lang),
            callback_data=PremiumCallback(action="select", tier="pro").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_ultimate_plan", lang),
            callback_data=PremiumCallback(action="select", tier="ultimate").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()


def get_plan_keyboard(lang: str, tier: str) -> InlineKeyboardMarkup:
    """Keyboard shown after selecting a specific plan."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=PremiumCallback(action="back").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()
