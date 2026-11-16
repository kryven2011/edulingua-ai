"""EduLingua AI — Database Session Middleware.

Provides an isolated AsyncSession to every Telegram update handler.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database.session import get_db_session


class DatabaseMiddleware(BaseMiddleware):
    """Middleware that injects an async database session into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with get_db_session() as session:
            data["session"] = session
            return await handler(event, data)
