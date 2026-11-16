"""EduLingua AI — LinguaBot Foreign Language Learning Handler.

Orchestrates vocabulary retention (SM-2), grammar exercises, interactive AI speaking scenarios,
text writing reviews, and CEFR level tests.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import LinguaCallback, MenuCallback
from app.bot.keyboards.lingua_kb import (
    get_learning_languages_keyboard,
    get_lingua_sections_keyboard,
    get_speaking_scenarios_keyboard,
    get_vocabulary_actions_keyboard,
)
from app.bot.states.states import LinguaStates
from app.config import get_settings
from app.database.models.user import User
from app.database.repositories.user_repo import UserRepository
from app.i18n import get_language_name, t
from app.services.ai.gemini_provider import GeminiProvider
from app.services.language.language_tutor_service import LanguageTutorService

logger = logging.getLogger(__name__)

router = Router(name="lingua")


@router.callback_query(MenuCallback.filter(F.action == "lingua"))
async def open_lingua_menu(
    callback: CallbackQuery,
    lang: str,
    state: FSMContext,
) -> None:
    """Show target language selection for LinguaBot."""
    await state.set_state(LinguaStates.selecting_language)
    await callback.message.edit_text(  # type: ignore[union-attr]
        text=t("select_learning_lang", lang=lang),
        reply_markup=get_learning_languages_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(LinguaCallback.filter(F.action == "select_lang"))
async def select_learning_language(
    callback: CallbackQuery,
    callback_data: LinguaCallback,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Handle language selection, display sections."""
    learning_code = callback_data.language
    user_repo = UserRepository(session)
    await user_repo.update_learning_language(user.id, learning_code)

    await state.update_data(learning_language=learning_code)

    tutor = LanguageTutorService(session, GeminiProvider(get_settings()))
    level = await tutor.get_user_level(user.id, learning_code)
    lang_name = get_language_name(learning_code, interface_lang=lang)

    text = t("lingua_sections", lang=lang, language=lang_name, level=level)
    markup = get_lingua_sections_keyboard(lang=lang, language_code=learning_code)

    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()


# ── SECTION: VOCABULARY ───────────────────────────────────────────────────

@router.callback_query(LinguaCallback.filter(F.action == "section", F.section == "vocab"))
async def start_vocabulary(
    callback: CallbackQuery,
    callback_data: LinguaCallback,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Generate and display vocabulary flashcard."""
    data = await state.get_data()
    learning_code = data.get("learning_language", callback_data.language or "en")

    await callback.answer(t("processing", lang=lang))
    tutor = LanguageTutorService(session, GeminiProvider(get_settings()))
    card = await tutor.generate_vocabulary_card(user.id, learning_code, interface_lang=lang)

    await state.update_data(current_word=card.get("word", ""))
    await state.set_state(LinguaStates.vocabulary)

    text = (
        f"📝 <b>Новое слово ({learning_code.upper()})</b>\n\n"
        f"🔤 <b>{card.get('word')}</b>  <i>{card.get('pronunciation', '')}</i>\n"
        f"📖 <b>Перевод:</b> {card.get('translation')}\n\n"
        f"💬 <b>Пример:</b>\n"
        f"• {card.get('example_target')}\n"
        f"• <i>{card.get('example_translation')}</i>\n\n"
        f"🏷 <i>Тема: {card.get('topic', 'General')}</i>"
    )

    markup = get_vocabulary_actions_keyboard(lang=lang, language_code=learning_code)
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]


@router.callback_query(LinguaCallback.filter(F.action == "vocab_rating"))
async def evaluate_vocabulary_recall(
    callback: CallbackQuery,
    callback_data: LinguaCallback,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Record SM-2 recall rating (know / don't know)."""
    rating = int(callback_data.scenario or 4)  # 5 = know, 1 = don't know
    tutor = LanguageTutorService(session, GeminiProvider(get_settings()))

    # Record review with dummy UUID or word ID
    await tutor.record_word_review(user.id, uuid.uuid4(), quality=rating)

    await callback.answer(t("xp_earned", lang=lang, xp=5))
    # Fetch next word
    await start_vocabulary(callback, callback_data, user, session, lang, state)


# ── SECTION: SPEAKING PRACTICE ────────────────────────────────────────────

@router.callback_query(LinguaCallback.filter(F.action == "section", F.section == "speaking"))
async def open_speaking_scenarios(
    callback: CallbackQuery,
    callback_data: LinguaCallback,
    lang: str,
) -> None:
    """Show available speaking scenarios."""
    learning_code = callback_data.language or "en"
    markup = get_speaking_scenarios_keyboard(lang=lang, language_code=learning_code)
    text = (
        "🗣 <b>Разговорная практика с ИИ-собеседником</b>\n\n"
        "Выберите ситуацию для живого диалога. ИИ будет общаться с вами как носитель языка, "
        "а также деликатно исправлять грамматические неточности и предлагать более естественные фразы:"
    )
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(LinguaCallback.filter(F.action == "scenario"))
async def start_speaking_scenario(
    callback: CallbackQuery,
    callback_data: LinguaCallback,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Initiate selected conversational roleplay."""
    scenario = callback_data.scenario
    learning_code = callback_data.language or "en"

    await state.update_data(
        speaking_scenario=scenario,
        learning_language=learning_code,
        conversation_history=[],
    )
    await state.set_state(LinguaStates.speaking)

    await callback.answer(t("processing", lang=lang))
    tutor = LanguageTutorService(session, GeminiProvider(get_settings()))
    intro_message = await tutor.start_speaking_session(
        language_code=learning_code,
        scenario=scenario,
        level="B1",
        interface_lang=lang,
    )

    await callback.message.edit_text(  # type: ignore[union-attr]
        text=(
            f"🗣 <b>Сценарий: {scenario.capitalize()} ({learning_code.upper()})</b>\n\n"
            f"{intro_message}\n\n"
            f"<i>(Ответьте текстом или голосовым сообщением на изучаемом языке)</i>"
        ),
    )


@router.message(LinguaStates.speaking, F.text)
async def handle_speaking_reply(
    message: Message,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Process user's conversational reply and generate next turn with feedback."""
    data = await state.get_data()
    scenario = data.get("speaking_scenario", "daily")
    learning_code = data.get("learning_language", "en")
    history = data.get("conversation_history", [])

    status_msg = await message.answer(t("processing", lang=lang))

    tutor = LanguageTutorService(session, GeminiProvider(get_settings()))
    ai_reply = await tutor.reply_speaking_session(
        user_id=user.id,
        language_code=learning_code,
        scenario=scenario,
        conversation_history=history,
        student_message=message.text or "",
        level="B1",
        interface_lang=lang,
    )

    # Update conversation history
    history.append({"role": "user", "content": message.text or ""})
    history.append({"role": "assistant", "content": ai_reply})
    if len(history) > 10:
        history = history[-10:]
    await state.update_data(conversation_history=history)

    await status_msg.edit_text(text=ai_reply)


# ── SECTION: WRITING ──────────────────────────────────────────────────────

@router.callback_query(LinguaCallback.filter(F.action == "section", F.section == "writing"))
async def prompt_writing(
    callback: CallbackQuery,
    callback_data: LinguaCallback,
    lang: str,
    state: FSMContext,
) -> None:
    """Prompt user to submit text for writing analysis."""
    learning_code = callback_data.language or "en"
    await state.update_data(learning_language=learning_code)
    await state.set_state(LinguaStates.writing)

    text = (
        f"✍️ <b>Проверка письменных текстов ({learning_code.upper()})</b>\n\n"
        "Отправьте мне любой текст на изучаемом языке (эссе, письмо, рассказ о себе).\n"
        "ИИ проверит орфографию, пунктуацию, грамматику и предложит улучшенные формулировки."
    )
    await callback.message.edit_text(text=text)  # type: ignore[union-attr]
    await callback.answer()


@router.message(LinguaStates.writing, F.text)
async def analyze_writing_submission(
    message: Message,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Review submitted writing essay."""
    data = await state.get_data()
    learning_code = data.get("learning_language", "en")

    status_msg = await message.answer(t("processing", lang=lang))
    tutor = LanguageTutorService(session, GeminiProvider(get_settings()))

    result = await tutor.check_writing(
        user_id=user.id,
        language_code=learning_code,
        text=message.text or "",
        interface_lang=lang,
    )
    await status_msg.edit_text(text=result)
