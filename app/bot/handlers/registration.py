"""EduLingua AI — Complete Multi-Step User Registration Flow.

Handles onboarding sequence for new users:
1. Interface Language Selection
2. Name Confirmation / Custom Input
3. Primary Educational Goal (EduAI / LinguaBot / Both)
4. Target Foreign Language Selection
5. Proficiency Level Assessment
6. Finalization in PostgreSQL, Starter XP Award, and Main Menu display.
"""

from __future__ import annotations

import logging
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import RegistrationCallback
from app.bot.keyboards.main_kb import get_main_menu_keyboard
from app.bot.keyboards.registration_kb import (
    get_reg_goal_keyboard,
    get_reg_language_keyboard,
    get_reg_learning_lang_keyboard,
    get_reg_level_keyboard,
    get_reg_name_confirm_keyboard,
)
from app.bot.states.states import RegistrationStates
from app.database.models.user import User
from app.database.repositories.gamification_repo import GamificationRepository
from app.database.repositories.language_repo import LanguageRepository
from app.database.repositories.user_repo import UserRepository
from app.i18n import t

logger = logging.getLogger(__name__)

router = Router(name="registration")


async def start_registration_flow(
    message_or_callback: Message | CallbackQuery,
    state: FSMContext,
) -> None:
    """Entry point to initiate the step-by-step registration flow."""
    await state.set_state(RegistrationStates.choosing_language)

    text = (
        "👋 <b>Добро пожаловать в EduLingua AI!</b>\n\n"
        "🎓 Умная образовательная платформа: личный ИИ-репетитор по учебным предметам "
        "и интеллектуальный преподаватель иностранных языков.\n\n"
        "🌐 <b>ШАГ 1: Выберите язык интерфейса / Tilni tanlang / Choose language:</b>"
    )
    markup = get_reg_language_keyboard()

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text=text, reply_markup=markup)


# ── STEP 1: Interface Language Selected ───────────────────────────────────

@router.callback_query(
    RegistrationStates.choosing_language,
    RegistrationCallback.filter(F.step == "lang"),
)
async def process_reg_language(
    callback: CallbackQuery,
    callback_data: RegistrationCallback,
    user: User,
    state: FSMContext,
) -> None:
    """Save selected interface language and advance to Name confirmation."""
    chosen_lang = callback_data.value
    await state.update_data(interface_language=chosen_lang)

    suggested_name = user.first_name or user.username or "Student"
    await state.update_data(suggested_name=suggested_name)

    await state.set_state(RegistrationStates.entering_name)

    prompts = {
        "ru": (
            f"✅ Язык интерфейса выбран: <b>Русский 🇷🇺</b>\n\n"
            f"👤 <b>ШАГ 2: Как к вам обращаться?</b>\n\n"
            f"Мы можем использовать ваше имя из Telegram: <b>{suggested_name}</b>, "
            f"или вы можете указать другое:"
        ),
        "uz": (
            f"✅ Interfeys tili tanlandi: <b>O'zbekcha 🇺🇿</b>\n\n"
            f"👤 <b>2-BOSQICH: Sizga qanday murojaat qilaylik?</b>\n\n"
            f"Telegramdagi ismingizni ishlatishimiz mumkin: <b>{suggested_name}</b>, "
            f"yoki boshqa ism kiritishingiz mumkin:"
        ),
        "en": (
            f"✅ Interface language set: <b>English 🇬🇧</b>\n\n"
            f"👤 <b>STEP 2: What should we call you?</b>\n\n"
            f"We can use your Telegram name: <b>{suggested_name}</b>, "
            f"or you can enter a preferred one:"
        ),
    }

    text = prompts.get(chosen_lang, prompts["ru"])
    markup = get_reg_name_confirm_keyboard(suggested_name=suggested_name, lang=chosen_lang)

    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()


# ── STEP 2: Name Confirmation / Custom Input ──────────────────────────────

@router.callback_query(
    RegistrationStates.entering_name,
    RegistrationCallback.filter(F.step == "confirm_name"),
)
async def process_name_confirmation(
    callback: CallbackQuery,
    callback_data: RegistrationCallback,
    state: FSMContext,
) -> None:
    """Handle name confirmation or prompt for text input."""
    data = await state.get_data()
    lang = data.get("interface_language", "ru")

    if callback_data.value == "yes":
        # Keep suggested name
        name = data.get("suggested_name", "Student")
        await state.update_data(name=name)
        await advance_to_study_goal(callback, state, lang)
    else:
        # Prompt user to send custom name via text
        prompts = {
            "ru": "✏️ Напишите ваше имя в ответном сообщении:",
            "uz": "✏️ Ismingizni xabarda yozib yuboring:",
            "en": "✏️ Please type your preferred name in reply:",
        }
        await callback.message.edit_text(prompts.get(lang, prompts["ru"]))  # type: ignore[union-attr]
        await callback.answer()


@router.message(RegistrationStates.entering_name)
async def process_custom_name_input(
    message: Message,
    state: FSMContext,
) -> None:
    """Capture custom user-typed name."""
    data = await state.get_data()
    lang = data.get("interface_language", "ru")

    custom_name = (message.text or "").strip()
    if len(custom_name) < 2 or len(custom_name) > 50:
        err_msg = {
            "ru": "⚠️ Имя должно содержать от 2 до 50 символов. Пожалуйста, попробуйте ещё раз:",
            "uz": "⚠️ Ism 2 tadan 50 tagacha belgidan iborat bo'lishi kerak. Qaytadan urinib ko'ring:",
            "en": "⚠️ Name must be between 2 and 50 characters. Please try again:",
        }.get(lang, "Invalid name length. Try again:")
        await message.answer(err_msg)
        return

    await state.update_data(name=custom_name)

    prompts = {
        "ru": f"✨ Приятно познакомиться, <b>{custom_name}</b>!",
        "uz": f"✨ Tanishganimizdan xursandmiz, <b>{custom_name}</b>!",
        "en": f"✨ Nice to meet you, <b>{custom_name}</b>!",
    }
    await message.answer(prompts.get(lang, prompts["ru"]))
    await advance_to_study_goal(message, state, lang)


async def advance_to_study_goal(
    event: Message | CallbackQuery,
    state: FSMContext,
    lang: str,
) -> None:
    """Prompt user to select their primary learning goal."""
    await state.set_state(RegistrationStates.choosing_goal)

    prompts = {
        "ru": (
            "🎯 <b>ШАГ 3: Выберите вашу основную цель обучения:</b>\n\n"
            "• <b>EduAI</b> — помощь со школьными и вузовскими предметами, "
            "разбор сложных задач по фото, подготовка к экзаменам.\n"
            "• <b>LinguaBot</b> — изучение иностранных языков, словарный запас, "
            "разговорная практика с ИИ, грамматика.\n"
            "• <b>Всё вместе</b> — полный доступ ко всем образовательным направлениям."
        ),
        "uz": (
            "🎯 <b>3-BOSQICH: Asosiy o'quv maqsadingizni tanlang:</b>\n\n"
            "• <b>EduAI</b> — maktab va universitet fanlari bo'yicha yordam, "
            "foto orqali masalalarni yechish, imtihonlarga tayyorgarlik.\n"
            "• <b>LinguaBot</b> — xorijiy tillarni o'rganish, lug'at boyligi, "
            "AI bilan muloqot, grammatika.\n"
            "• <b>Hammasi birga</b> — barcha ta'lim yo'nalishlaridan to'liq foydalanish."
        ),
        "en": (
            "🎯 <b>STEP 3: Choose your primary learning focus:</b>\n\n"
            "• <b>EduAI</b> — homework help, step-by-step problem solving via photo, "
            "exam preparation across academic subjects.\n"
            "• <b>LinguaBot</b> — foreign languages, spaced repetition vocabulary, "
            "interactive AI speaking partner, grammar.\n"
            "• <b>All-in-one</b> — complete access to all educational modules."
        ),
    }

    text = prompts.get(lang, prompts["ru"])
    markup = get_reg_goal_keyboard(lang)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    else:
        await event.answer(text=text, reply_markup=markup)


# ── STEP 3: Study Goal Selected ───────────────────────────────────────────

@router.callback_query(
    RegistrationStates.choosing_goal,
    RegistrationCallback.filter(F.step == "goal"),
)
async def process_study_goal(
    callback: CallbackQuery,
    callback_data: RegistrationCallback,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Handle goal selection. If language-related, prompt for target language."""
    goal = callback_data.value
    await state.update_data(study_goal=goal)

    data = await state.get_data()
    lang = data.get("interface_language", "ru")

    if goal in ("lingua", "both"):
        # Proceed to select foreign language
        await state.set_state(RegistrationStates.choosing_learning_language)
        prompts = {
            "ru": "🌍 <b>ШАГ 4: Какой иностранный язык вы хотите изучать?</b>",
            "uz": "🌍 <b>4-BOSQICH: Qaysi chet tilini o'rganmoqchisiz?</b>",
            "en": "🌍 <b>STEP 4: Which foreign language would you like to learn?</b>",
        }
        await callback.message.edit_text(  # type: ignore[union-attr]
            text=prompts.get(lang, prompts["ru"]),
            reply_markup=get_reg_learning_lang_keyboard(lang),
        )
        await callback.answer()
    else:
        # EduAI only: set default subject and complete registration
        await state.update_data(learning_language="en", target_level="A1")
        await finalize_registration(callback, user, session, state)


# ── STEP 4: Target Learning Language Selected ─────────────────────────────

@router.callback_query(
    RegistrationStates.choosing_learning_language,
    RegistrationCallback.filter(F.step == "learn_lang"),
)
async def process_learning_language(
    callback: CallbackQuery,
    callback_data: RegistrationCallback,
    state: FSMContext,
) -> None:
    """Save target language and prompt for current self-assessed level."""
    learn_lang = callback_data.value
    await state.update_data(learning_language=learn_lang)

    data = await state.get_data()
    lang = data.get("interface_language", "ru")

    await state.set_state(RegistrationStates.choosing_level)

    prompts = {
        "ru": (
            "📊 <b>ШАГ 5: Оцените ваш текущий уровень владения языком:</b>\n\n"
            "<i>(Вы всегда сможете пройти точный тест на уровень позже в LinguaBot)</i>"
        ),
        "uz": (
            "📊 <b>5-BOSQICH: Tilni bilish darajangizni baholang:</b>\n\n"
            "<i>(Keyinchalik LinguaBotda aniq test topshirishingiz mumkin)</i>"
        ),
        "en": (
            "📊 <b>STEP 5: Estimate your current proficiency level:</b>\n\n"
            "<i>(You can take an in-depth AI placement test anytime later in LinguaBot)</i>"
        ),
    }

    await callback.message.edit_text(  # type: ignore[union-attr]
        text=prompts.get(lang, prompts["ru"]),
        reply_markup=get_reg_level_keyboard(lang),
    )
    await callback.answer()


# ── STEP 5: Level Selected & Finalization ─────────────────────────────────

@router.callback_query(
    RegistrationStates.choosing_level,
    RegistrationCallback.filter(F.step == "level"),
)
async def process_level_selection(
    callback: CallbackQuery,
    callback_data: RegistrationCallback,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Save level and complete registration."""
    level = callback_data.value
    await state.update_data(target_level=level)
    await finalize_registration(callback, user, session, state)


async def finalize_registration(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Save all user profile preferences into PostgreSQL, award starter bonus XP, and show Main Menu."""
    data = await state.get_data()
    await state.clear()

    name = data.get("name", user.first_name or "Student")
    interface_lang = data.get("interface_language", "ru")
    study_goal = data.get("study_goal", "both")
    learning_lang = data.get("learning_language", "en")
    target_level = data.get("target_level", "A1")

    # 1. Update in PostgreSQL
    user_repo = UserRepository(session)
    updated_user = await user_repo.complete_registration(
        user_id=user.id,
        name=name,
        interface_language=interface_lang,
        study_goal=study_goal,
        learning_language=learning_lang,
        target_level=target_level,
    )

    # 2. Record initial language level
    lang_repo = LanguageRepository(session)
    target_lang_obj = await lang_repo.get_by_code(learning_lang)
    if target_lang_obj:
        await lang_repo.set_user_level(
            user_id=user.id,
            language_id=target_lang_obj.id,
            level=target_level,
            score=100,
        )

    # 3. Award Starter Bonus XP (50 XP) with idempotency protection
    gamification = GamificationRepository(session)
    idem_key = f"reg_starter_bonus:{user.id}"
    new_xp, awarded = await gamification.award_xp(
        user_id=user.id,
        amount=50,
        source="achievement",
        idempotency_key=idem_key,
        description="Welcome onboarding bonus",
    )

    # 4. Success congratulations message
    congrats = {
        "ru": (
            "🎉 <b>Регистрация успешно завершена!</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"🌐 <b>Язык интерфейса:</b> {interface_lang.upper()}\n"
            f"📚 <b>Цель:</b> {study_goal.capitalize()}\n"
            f"🌍 <b>Изучаемый язык:</b> {learning_lang.upper()} ({target_level})\n\n"
            "🎁 <b>Вам начислен стартовый бонус: +50 XP!</b> ⭐\n\n"
            "Добро пожаловать в мир знаний с EduLingua AI. Выберите действие в меню ниже:"
        ),
        "uz": (
            "🎉 <b>Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!</b>\n\n"
            f"👤 <b>Ism:</b> {name}\n"
            f"🌐 <b>Interfeys tili:</b> {interface_lang.upper()}\n"
            f"📚 <b>Maqsad:</b> {study_goal.capitalize()}\n"
            f"🌍 <b>O'rganilayotgan til:</b> {learning_lang.upper()} ({target_level})\n\n"
            "🎁 <b>Sizga boshlang'ich bonus berildi: +50 XP!</b> ⭐\n\n"
            "EduLingua AI bilan bilimlar olamiga xush kelibsiz. Quyidagi menyudan amalni tanlang:"
        ),
        "en": (
            "🎉 <b>Registration completed successfully!</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🌐 <b>Interface language:</b> {interface_lang.upper()}\n"
            f"📚 <b>Focus:</b> {study_goal.capitalize()}\n"
            f"🌍 <b>Target language:</b> {learning_lang.upper()} ({target_level})\n\n"
            "🎁 <b>Welcome bonus awarded: +50 XP!</b> ⭐\n\n"
            "Welcome to EduLingua AI. Choose an action from the menu below to begin:"
        ),
    }

    text = congrats.get(interface_lang, congrats["ru"])
    markup = get_main_menu_keyboard(interface_lang)

    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()
    logger.info("User registered successfully: id=%s, name=%s, goal=%s", user.id, name, study_goal)
