"""EduLingua AI — User Registration & Resolution Middleware.

Resolves Telegram user in DB, populates context, updates active streak,
and blocks restricted accounts.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.user_repo import UserRepository
from app.i18n import DEFAULT_LANGUAGE, t

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """Middleware that resolves DB user, updates streak, and handles blocking."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        telegram_user = None
        if isinstance(event, Message):
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery):
            telegram_user = event.from_user

        if not telegram_user:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        user_repo = UserRepository(session)
        user, created = await user_repo.get_or_create_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            default_language=DEFAULT_LANGUAGE,
        )

        if user.is_blocked:
            lang = user.interface_language or DEFAULT_LANGUAGE
            msg = t("error_blocked", lang=lang)
            if isinstance(event, Message):
                await event.answer(msg)
            elif isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            return

        # Update streak
        await user_repo.update_activity_streak(user.id)

        data["user"] = user
        data["user_repo"] = user_repo
        data["lang"] = user.interface_language or DEFAULT_LANGUAGE
        data["is_new_user"] = created

        return await handler(event, data)
