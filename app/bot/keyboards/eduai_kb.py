"""EduLingua AI — EduAI Keyboards."""

from __future__ import annotations

import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import EduAICallback, MenuCallback
from app.i18n import t

# Subject definitions: (key suffix, i18n key)
SUBJECTS: list[tuple[str, str]] = [
    ("math", "btn_math"),
    ("algebra", "btn_algebra"),
    ("geometry", "btn_geometry"),
    ("physics", "btn_physics"),
    ("chemistry", "btn_chemistry"),
    ("biology", "btn_biology"),
    ("history", "btn_history"),
    ("geography", "btn_geography"),
    ("informatics", "btn_informatics"),
    ("literature", "btn_literature"),
    ("russian_lang", "btn_russian_lang"),
    ("english_lang", "btn_english_lang"),
]

SUBJECTS_PER_PAGE = 6


def get_subjects_keyboard(lang: str, page: int = 0) -> InlineKeyboardMarkup:
    """Paginated subject-selection keyboard (6 per page)."""
    total_pages = math.ceil(len(SUBJECTS) / SUBJECTS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))

    start = page * SUBJECTS_PER_PAGE
    end = start + SUBJECTS_PER_PAGE
    page_subjects = SUBJECTS[start:end]

    builder = InlineKeyboardBuilder()

    # Two subjects per row
    for i in range(0, len(page_subjects), 2):
        row_buttons: list[InlineKeyboardButton] = []
        for key, i18n_key in page_subjects[i : i + 2]:
            row_buttons.append(
                InlineKeyboardButton(
                    text=t(i18n_key, lang),
                    callback_data=EduAICallback(
                        action="subject", subject=key, page=page
                    ).pack(),
                )
            )
        builder.row(*row_buttons)

    # Pagination row
    if total_pages > 1:
        nav_buttons: list[InlineKeyboardButton] = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=EduAICallback(
                        action="page", page=page - 1
                    ).pack(),
                )
            )
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{page + 1}/{total_pages}",
                callback_data="noop",
            )
        )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=EduAICallback(
                        action="page", page=page + 1
                    ).pack(),
                )
            )
        builder.row(*nav_buttons)

    # Back button
    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )

    return builder.as_markup()


def get_eduai_actions_keyboard(
    lang: str, session_id: str
) -> InlineKeyboardMarkup:
    """Action buttons shown after an AI response."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=t("btn_explain_simpler", lang),
            callback_data=EduAICallback(
                action="explain_simpler", session_id=session_id
            ).pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_another_method", lang),
            callback_data=EduAICallback(
                action="another_method", session_id=session_id
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_hint", lang),
            callback_data=EduAICallback(
                action="hint", session_id=session_id
            ).pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_check_answer", lang),
            callback_data=EduAICallback(
                action="check_answer", session_id=session_id
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_similar_task", lang),
            callback_data=EduAICallback(
                action="similar_task", session_id=session_id
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=EduAICallback(action="back").pack(),
        ),
    )

    return builder.as_markup()


def get_back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Back to EduAI subjects / main menu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=EduAICallback(action="back").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()
