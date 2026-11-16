"""EduLingua AI — EduAI Handler.

Manages subject selection, question processing, photo problem analysis,
and pedagogical interaction modes (explain simpler, another method, hints, check answer, similar task).
"""

from __future__ import annotations

import io
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import EduAICallback, MenuCallback
from app.bot.keyboards.eduai_kb import (
    get_eduai_actions_keyboard,
    get_subjects_keyboard,
)
from app.bot.states.states import EduAIStates
from app.config import get_settings
from app.database.models.user import User
from app.database.repositories.subscription_repo import SubscriptionRepository
from app.database.repositories.user_repo import UserRepository
from app.i18n import t
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.usage_tracker import AIUsageTracker
from app.services.education.tutor_service import AITutorService

logger = logging.getLogger(__name__)

router = Router(name="eduai")


@router.callback_query(MenuCallback.filter(F.action == "eduai"))
async def open_eduai_menu(
    callback: CallbackQuery,
    lang: str,
    state: FSMContext,
) -> None:
    """Show EduAI subjects menu."""
    await state.set_state(EduAIStates.selecting_subject)
    await callback.message.edit_text(  # type: ignore[union-attr]
        text=t("eduai_menu", lang=lang),
        reply_markup=get_subjects_keyboard(lang=lang, page=0),
    )
    await callback.answer()


@router.callback_query(EduAICallback.filter(F.action == "page"))
async def paginate_subjects(
    callback: CallbackQuery,
    callback_data: EduAICallback,
    lang: str,
) -> None:
    """Handle subject pagination."""
    await callback.message.edit_reply_markup(  # type: ignore[union-attr]
        reply_markup=get_subjects_keyboard(lang=lang, page=callback_data.page),
    )
    await callback.answer()


@router.callback_query(EduAICallback.filter(F.action == "subject"))
async def select_subject(
    callback: CallbackQuery,
    callback_data: EduAICallback,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Handle subject choice, prompt for student question or photo."""
    subject_code = callback_data.subject
    user_repo = UserRepository(session)
    await user_repo.set_current_subject(user.id, subject_code)

    await state.update_data(current_subject=subject_code)
    await state.set_state(EduAIStates.asking_question)

    msg = t("subject_selected", lang=lang, subject=subject_code.capitalize())
    await callback.message.edit_text(  # type: ignore[union-attr]
        text=msg,
        reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
    )
    await callback.answer()


@router.message(EduAIStates.asking_question, F.text)
async def handle_text_question(
    message: Message,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Process user's written academic inquiry."""
    data = await state.get_data()
    subject_code = data.get("current_subject", "math")

    # Check daily AI limits
    sub_repo = SubscriptionRepository(session)
    tier = await sub_repo.get_user_tier(user.id)
    settings = get_settings()
    daily_limit = settings.get_ai_daily_limit(tier)

    status_msg = await message.answer(t("processing", lang=lang))

    ai_provider = GeminiProvider(settings)
    tutor = AITutorService(session=session, ai_provider=ai_provider)

    try:
        reply_text = await tutor.ask_question(
            user_id=user.id,
            subject_code=subject_code,
            question_text=message.text or "",
            lang=lang,
        )
        await status_msg.edit_text(
            text=reply_text,
            reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
        )
    except Exception as e:
        logger.error("AI tutor error: %s", e)
        await status_msg.edit_text(t("ai_error", lang=lang))


@router.message(EduAIStates.asking_question, F.photo)
async def handle_photo_problem(
    message: Message,
    user: User,
    session: AsyncSession,
    lang: str,
    state: FSMContext,
) -> None:
    """Process user's photo of a problem or textbook task."""
    data = await state.get_data()
    subject_code = data.get("current_subject", "math")

    status_msg = await message.answer(t("processing", lang=lang))

    # Download largest photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_bytes_io = io.BytesIO()
    await message.bot.download_file(file.file_path, destination=file_bytes_io)
    image_bytes = file_bytes_io.getvalue()

    settings = get_settings()
    ai_provider = GeminiProvider(settings)
    tutor = AITutorService(session=session, ai_provider=ai_provider)

    try:
        reply_text = await tutor.analyze_photo_problem(
            user_id=user.id,
            subject_code=subject_code,
            image_bytes=image_bytes,
            mime_type="image/jpeg",
            lang=lang,
        )
        await status_msg.edit_text(
            text=reply_text,
            reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
        )
    except Exception as e:
        logger.error("AI photo problem analysis error: %s", e)
        await status_msg.edit_text(t("ai_error", lang=lang))


# ── Pedagogical Action Modes ──────────────────────────────────────────────

@router.callback_query(EduAICallback.filter(F.action == "simpler"))
async def explain_simpler_mode(
    callback: CallbackQuery,
    callback_data: EduAICallback,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Mode: Explain simpler."""
    subject_code = callback_data.subject or "math"
    await callback.answer(t("processing", lang=lang))

    settings = get_settings()
    tutor = AITutorService(session=session, ai_provider=GeminiProvider(settings))
    result = await tutor.explain_simpler(user.id, subject_code, lang=lang)

    await callback.message.reply(  # type: ignore[union-attr]
        text=result,
        reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
    )


@router.callback_query(EduAICallback.filter(F.action == "method"))
async def another_method_mode(
    callback: CallbackQuery,
    callback_data: EduAICallback,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Mode: Show alternative solving method."""
    subject_code = callback_data.subject or "math"
    await callback.answer(t("processing", lang=lang))

    settings = get_settings()
    tutor = AITutorService(session=session, ai_provider=GeminiProvider(settings))
    result = await tutor.show_another_method(user.id, subject_code, lang=lang)

    await callback.message.reply(  # type: ignore[union-attr]
        text=result,
        reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
    )


@router.callback_query(EduAICallback.filter(F.action == "hint"))
async def hint_mode(
    callback: CallbackQuery,
    callback_data: EduAICallback,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Mode: Give a hint without revealing full answer."""
    subject_code = callback_data.subject or "math"
    await callback.answer(t("processing", lang=lang))

    settings = get_settings()
    tutor = AITutorService(session=session, ai_provider=GeminiProvider(settings))
    result = await tutor.give_hint(user.id, subject_code, lang=lang)

    await callback.message.reply(  # type: ignore[union-attr]
        text=result,
        reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
    )


@router.callback_query(EduAICallback.filter(F.action == "similar"))
async def similar_task_mode(
    callback: CallbackQuery,
    callback_data: EduAICallback,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Mode: Generate a similar task for practice."""
    subject_code = callback_data.subject or "math"
    await callback.answer(t("processing", lang=lang))

    settings = get_settings()
    tutor = AITutorService(session=session, ai_provider=GeminiProvider(settings))
    result = await tutor.generate_similar_task(user.id, subject_code, lang=lang)

    await callback.message.reply(  # type: ignore[union-attr]
        text=result,
        reply_markup=get_eduai_actions_keyboard(lang=lang, session_id=subject_code),
    )
