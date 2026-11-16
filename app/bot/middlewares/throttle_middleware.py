"""EduLingua AI — Button Click Anti-Flood Throttle Middleware.

Prevents rapid duplicate inline button clicks.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from redis.asyncio import Redis


class ThrottleMiddleware(BaseMiddleware):
    """Prevents double-click race conditions on inline buttons."""

    def __init__(self, redis: Redis | None = None) -> None:
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery) or not self.redis:
            return await handler(event, data)

        user_id = event.from_user.id
        key = f"throttle:btn:{user_id}"

        # Try to set lock with 500ms TTL
        acquired = await self.redis.set(key, "1", px=500, nx=True)
        if not acquired:
            # Drop rapid duplicate click silently with callback answer
            try:
                await event.answer()
            except Exception:
                pass
            return

        return await handler(event, data)
