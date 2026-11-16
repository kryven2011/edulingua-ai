"""EduLingua AI — Leaderboard Handler.

Displays rankings for daily, weekly, and all-time achievements.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import LeaderboardCallback, MenuCallback
from app.bot.keyboards.leaderboard_kb import get_leaderboard_keyboard
from app.i18n import t
from app.services.gamification.leaderboard_service import LeaderboardService
from app.utils.redis_client import get_redis_client

router = Router(name="leaderboard")


@router.callback_query(MenuCallback.filter(F.action == "leaderboard"))
@router.callback_query(LeaderboardCallback.filter())
async def show_leaderboard(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
    callback_data: LeaderboardCallback | None = None,
) -> None:
    """Render competitive ranking."""
    period = callback_data.period if callback_data else "daily"

    redis = get_redis_client()
    lb_service = LeaderboardService(session=session, redis=redis)
    entries = await lb_service.get_leaderboard(period=period, limit=10)

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = []
    for item in entries:
        rank = item["rank"]
        medal = medals.get(rank, "▫️")
        name = item["name"]
        xp = item["xp"]
        lines.append(f"{rank}. {medal} <b>{name}</b> — <b>{xp}</b> XP")

    entries_str = "\n".join(lines) if lines else "Пока нет результатов в этом периоде."
    text = t("leaderboard_title", lang=lang, period=period.capitalize(), entries=entries_str)

    markup = get_leaderboard_keyboard(lang=lang)
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()
