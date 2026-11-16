"""EduLingua AI — Rate Limiting & Anti-Spam Middleware.

Enforces per-user request throttling using Redis sliding windows.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from redis.asyncio import Redis

from app.config import get_settings
from app.i18n import DEFAULT_LANGUAGE, t

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Enforces rate limits using Redis."""

    def __init__(self, redis: Redis | None = None) -> None:
        self.redis = redis
        self.settings = get_settings()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not self.redis:
            return await handler(event, data)

        telegram_user = None
        if isinstance(event, Message):
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery):
            telegram_user = event.from_user

        if not telegram_user:
            return await handler(event, data)

        key = f"rate_limit:msg:{telegram_user.id}"
        limit = self.settings.rate_limit_messages_per_minute

        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, 60)

            if count > limit:
                lang = data.get("lang", DEFAULT_LANGUAGE)
                msg = t("error_rate_limit", lang=lang, seconds=30)
                if isinstance(event, Message):
                    await event.answer(msg)
                elif isinstance(event, CallbackQuery):
                    await event.answer(msg, show_alert=True)
                return
        except Exception as e:
            logger.warning("Redis rate limit check error: %s", e)

        return await handler(event, data)
