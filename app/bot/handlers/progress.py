"""EduLingua AI — Learning Progress Handler.

Displays XP visual progress bar, level threshold, and streak information.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import MenuCallback
from app.bot.keyboards.common_kb import get_back_to_main_keyboard
from app.database.models.user import User
from app.database.repositories.user_repo import UserRepository
from app.i18n import t
from app.services.gamification.xp_service import XPService
from app.utils.helpers import generate_progress_bar

router = Router(name="progress")


@router.callback_query(MenuCallback.filter(F.action == "progress"))
async def show_progress(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Render gamification progress screen."""
    user_repo = UserRepository(session)
    profile = await user_repo.get_profile(user.id)

    current_xp = profile.xp if profile else 0
    level_info = XPService.get_level_info(current_xp)

    bar = generate_progress_bar(
        current=level_info.xp_in_current_level,
        total=max(1, level_info.next_level_xp - XPService.get_threshold_for_level(level_info.current_level)),
        length=10,
    )

    text = t(
        "progress_title",
        lang=lang,
        progress_bar=f"[{bar}] {level_info.progress_percentage}%",
        xp=current_xp,
        next_level_xp=level_info.next_level_xp,
        level=level_info.current_level,
        streak=profile.streak_days if profile else 1,
        today_xp=min(current_xp, 50),
        week_xp=min(current_xp, 250),
    )

    markup = get_back_to_main_keyboard(lang)
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()
