"""EduLingua AI — User Profile Handler.

Displays comprehensive account metrics, achievements count, XP, and subscription status.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import MenuCallback
from app.bot.keyboards.profile_kb import get_profile_keyboard
from app.database.models.user import User
from app.database.repositories.subscription_repo import SubscriptionRepository
from app.database.repositories.user_repo import UserRepository
from app.i18n import t

router = Router(name="profile")


@router.callback_query(MenuCallback.filter(F.action == "profile"))
async def show_profile(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Render beautiful user profile card."""
    user_repo = UserRepository(session)
    profile = await user_repo.get_profile(user.id)

    sub_repo = SubscriptionRepository(session)
    tier = await sub_repo.get_user_tier(user.id)

    registered_str = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"
    learning_lang = (user.settings.learning_language or "en").upper() if user.settings else "EN"
    target_level = (user.settings.target_level or "A1") if user.settings else "A1"

    text = t(
        "profile_info",
        lang=lang,
        name=user.first_name or user.username or "Student",
        telegram_id=user.telegram_id,
        registered=registered_str,
        interface_lang=user.interface_language.upper(),
        learning_lang=learning_lang,
        level=target_level,
        tasks_solved=profile.tasks_solved if profile else 0,
        correct_answers=profile.correct_answers if profile else 0,
        lessons_completed=profile.lessons_completed if profile else 0,
        words_learned=profile.words_learned if profile else 0,
        xp=profile.xp if profile else 0,
        user_level=profile.level if profile else 1,
        active_days=profile.streak_days if profile else 1,
        subscription=tier.value.upper(),
    )

    markup = get_profile_keyboard(lang)
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()
