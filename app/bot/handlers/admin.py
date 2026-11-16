"""EduLingua AI — Telegram Admin Bot Handler.

Enables administrators to view live stats and perform quick maintenance inside Telegram.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.repositories.user_repo import UserRepository

router = Router(name="admin_bot")


@router.message(Command("admin"))
async def handle_admin_command(
    message: Message,
    user: User,
    session: AsyncSession,
) -> None:
    """Show admin stats summary if caller has admin permissions."""
    if not user.is_admin:
        await message.answer("🚫 У вас нет прав администратора.")
        return

    user_repo = UserRepository(session)
    total_users = await user_repo.count_total_users()
    active_today = await user_repo.count_active_today()

    text = (
        "👑 <b>Панель администратора EduLingua AI</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"🔥 Активных сегодня: <b>{active_today}</b>\n\n"
        "🌐 Веб-панель управления доступна по адресу: <code>/admin</code>"
    )
    await message.answer(text=text)
