"""EduLingua AI — Registration Flow Keyboards.

Interactive keyboards for onboarding, language selection, study goals,
and level assessment.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import RegistrationCallback
from app.i18n import t


def get_reg_language_keyboard() -> InlineKeyboardMarkup:
    """Step 1: Choose interface language."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🇷🇺 Русский",
            callback_data=RegistrationCallback(step="lang", value="ru").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🇺🇿 Oʻzbekcha",
            callback_data=RegistrationCallback(step="lang", value="uz").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🇬🇧 English",
            callback_data=RegistrationCallback(step="lang", value="en").pack(),
        ),
    )
    return builder.as_markup()


def get_reg_name_confirm_keyboard(suggested_name: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Step 2: Confirm Telegram name or type a custom one."""
    builder = InlineKeyboardBuilder()

    confirm_text = {
        "ru": f"✅ Да, я {suggested_name}",
        "uz": f"✅ Ha, men {suggested_name}",
        "en": f"✅ Yes, call me {suggested_name}",
    }.get(lang, f"✅ Use {suggested_name}")

    change_text = {
        "ru": "✏️ Ввести другое имя",
        "uz": "✏️ Boshqa ism kiritish",
        "en": "✏️ Enter different name",
    }.get(lang, "✏️ Change name")

    builder.row(
        InlineKeyboardButton(
            text=confirm_text,
            callback_data=RegistrationCallback(step="confirm_name", value="yes").pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=change_text,
            callback_data=RegistrationCallback(step="confirm_name", value="no").pack(),
        )
    )
    return builder.as_markup()


def get_reg_goal_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Step 3: Choose primary educational path."""
    builder = InlineKeyboardBuilder()

    goals = [
        ("eduai", {
            "ru": "🎓 EduAI — Школьные предметы",
            "uz": "🎓 EduAI — Maktab fanlari",
            "en": "🎓 EduAI — School & Academic subjects",
        }),
        ("lingua", {
            "ru": "🌍 LinguaBot — Изучение языков",
            "uz": "🌍 LinguaBot — Til o'rganish",
            "en": "🌍 LinguaBot — Foreign languages",
        }),
        ("both", {
            "ru": "🌟 Всё вместе (EduAI + LinguaBot)",
            "uz": "🌟 Hammasi birga (EduAI + LinguaBot)",
            "en": "🌟 All-in-one (EduAI + LinguaBot)",
        }),
    ]

    for code, titles in goals:
        text = titles.get(lang, titles["ru"])
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=RegistrationCallback(step="goal", value=code).pack(),
            )
        )
    return builder.as_markup()


def get_reg_learning_lang_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Step 4: Select foreign language to study."""
    builder = InlineKeyboardBuilder()

    langs = [
        ("en", "🇬🇧 English"),
        ("ru", "🇷🇺 Русский"),
        ("uz", "🇺🇿 Oʻzbekcha"),
        ("de", "🇩🇪 Deutsch"),
        ("fr", "🇫🇷 Français"),
        ("es", "🇪🇸 Español"),
    ]

    for code, title in langs:
        builder.button(
            text=title,
            callback_data=RegistrationCallback(step="learn_lang", value=code).pack(),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_reg_level_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Step 5: Select current estimated proficiency level."""
    builder = InlineKeyboardBuilder()

    levels = [
        ("A1", "🟢 A1 — Beginner (С нуля)"),
        ("A2", "🟡 A2 — Elementary (Базовый)"),
        ("B1", "🟠 B1 — Intermediate (Средний)"),
        ("B2", "🔵 B2 — Upper Intermediate (Уверенный)"),
        ("C1", "🟣 C1 — Advanced (Продвинутый)"),
    ]

    for code, title in levels:
        builder.row(
            InlineKeyboardButton(
                text=title,
                callback_data=RegistrationCallback(step="level", value=code).pack(),
            )
        )
    return builder.as_markup()
