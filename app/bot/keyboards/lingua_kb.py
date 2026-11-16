"""EduLingua AI — LinguaBot Keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.filters.callback_filters import LinguaCallback, MenuCallback
from app.i18n import t

# Languages available for learning
LEARNING_LANGUAGES: list[tuple[str, str]] = [
    ("en", "btn_lang_en"),
    ("ru", "btn_lang_ru"),
    ("uz", "btn_lang_uz"),
    ("de", "btn_lang_de"),
    ("fr", "btn_lang_fr"),
    ("es", "btn_lang_es"),
]

# Speaking practice scenarios
SPEAKING_SCENARIOS: list[tuple[str, str]] = [
    ("intro", "btn_scenario_intro"),
    ("travel", "btn_scenario_travel"),
    ("restaurant", "btn_scenario_restaurant"),
    ("shop", "btn_scenario_shop"),
    ("work", "btn_scenario_work"),
    ("study", "btn_scenario_study"),
    ("daily", "btn_scenario_daily"),
]


def get_learning_languages_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Language selection keyboard for LinguaBot."""
    builder = InlineKeyboardBuilder()

    for i in range(0, len(LEARNING_LANGUAGES), 2):
        row: list[InlineKeyboardButton] = []
        for code, i18n_key in LEARNING_LANGUAGES[i : i + 2]:
            row.append(
                InlineKeyboardButton(
                    text=t(i18n_key, lang),
                    callback_data=LinguaCallback(
                        action="select_lang", language=code
                    ).pack(),
                )
            )
        builder.row(*row)

    builder.row(
        InlineKeyboardButton(
            text=t("btn_main_menu", lang),
            callback_data=MenuCallback(action="main").pack(),
        ),
    )
    return builder.as_markup()


def get_lingua_sections_keyboard(
    lang: str, language_code: str
) -> InlineKeyboardMarkup:
    """Sections keyboard once a learning language is selected."""
    builder = InlineKeyboardBuilder()

    sections: list[tuple[str, str]] = [
        ("vocabulary", "btn_vocabulary"),
        ("grammar", "btn_grammar"),
        ("speaking", "btn_speaking"),
        ("writing", "btn_writing"),
        ("listening", "btn_listening"),
        ("level_test", "btn_level_test"),
    ]

    for i in range(0, len(sections), 2):
        row: list[InlineKeyboardButton] = []
        for section_key, i18n_key in sections[i : i + 2]:
            row.append(
                InlineKeyboardButton(
                    text=t(i18n_key, lang),
                    callback_data=LinguaCallback(
                        action="section",
                        language=language_code,
                        section=section_key,
                    ).pack(),
                )
            )
        builder.row(*row)

    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=LinguaCallback(action="back").pack(),
        ),
    )
    return builder.as_markup()


def get_speaking_scenarios_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Scenario selection keyboard for speaking practice."""
    builder = InlineKeyboardBuilder()

    for i in range(0, len(SPEAKING_SCENARIOS), 2):
        row: list[InlineKeyboardButton] = []
        for key, i18n_key in SPEAKING_SCENARIOS[i : i + 2]:
            row.append(
                InlineKeyboardButton(
                    text=t(i18n_key, lang),
                    callback_data=LinguaCallback(
                        action="scenario", scenario=key
                    ).pack(),
                )
            )
        builder.row(*row)

    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=LinguaCallback(action="back_sections").pack(),
        ),
    )
    return builder.as_markup()


def get_vocabulary_actions_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Vocabulary card action buttons."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ " + t("btn_vocabulary", lang),
            callback_data=LinguaCallback(action="vocab_know").pack(),
        ),
        InlineKeyboardButton(
            text="❌",
            callback_data=LinguaCallback(action="vocab_dont_know").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="➡️",
            callback_data=LinguaCallback(action="vocab_next").pack(),
        ),
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=LinguaCallback(action="back_sections").pack(),
        ),
    )
    return builder.as_markup()
