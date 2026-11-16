"""EduLingua AI — Telegram Bot & Dispatcher Factory.

Assembles Bot instance and aiogram Dispatcher with routers, middlewares,
and Redis-backed FSM storage.
"""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.bot.handlers import ALL_ROUTERS
from app.bot.middlewares.db_middleware import DatabaseMiddleware
from app.bot.middlewares.rate_limit_middleware import RateLimitMiddleware
from app.bot.middlewares.throttle_middleware import ThrottleMiddleware
from app.bot.middlewares.user_middleware import UserMiddleware

logger = logging.getLogger(__name__)


def create_bot(token: str) -> Bot:
    """Instantiate Telegram Bot with HTML parse mode."""
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(redis: Redis | None = None) -> Dispatcher:
    """Build and configure the central Dispatcher."""
    storage = RedisStorage(redis=redis) if redis else MemoryStorage()
    dp = Dispatcher(storage=storage)

    # 1. Register outer middlewares
    dp.update.outer_middleware(DatabaseMiddleware())
    dp.update.outer_middleware(UserMiddleware())
    if redis:
        dp.update.outer_middleware(RateLimitMiddleware(redis))
        dp.callback_query.outer_middleware(ThrottleMiddleware(redis))

    # 2. Register all feature routers
    for r in ALL_ROUTERS:
        dp.include_router(r)

    logger.info("Dispatcher assembled with %d routers", len(ALL_ROUTERS))
    return dp
