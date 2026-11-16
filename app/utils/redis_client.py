"""EduLingua AI — Async Redis Client Utilities.

Provides connection-pool management and simple cache helpers.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import ConnectionPool, Redis

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None
_redis: Redis | None = None


async def get_redis() -> Redis:
    """Return a shared async Redis connection (lazy-initialised)."""
    global _pool, _redis
    if _redis is None:
        settings = get_settings()
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=30,
        )
        _redis = Redis(connection_pool=_pool)
        logger.info("Redis connection pool created (%s)", settings.redis_url)
    return _redis


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _pool, _redis
    if _redis is not None:
        await _redis.close()
        logger.info("Redis connection closed")
        _redis = None
    if _pool is not None:
        await _pool.disconnect()
        _pool = None


# ── cache helpers ────────────────────────────────────────────────


async def cache_get(key: str) -> Any | None:
    """Read a JSON-serialised value from cache. Returns ``None`` on miss."""
    redis = await get_redis()
    raw = await redis.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def cache_set(key: str, value: Any, *, ttl: int | None = None) -> None:
    """Store a JSON-serialisable value in cache.

    Args:
        key: Cache key.
        value: Any JSON-serialisable Python object.
        ttl: Time-to-live in seconds. ``None`` → use default from settings.
    """
    redis = await get_redis()
    if ttl is None:
        ttl = get_settings().redis_cache_ttl
    serialised = json.dumps(value, default=str)
    await redis.set(key, serialised, ex=ttl)


async def cache_delete(key: str) -> None:
    """Delete a cache entry."""
    redis = await get_redis()
    await redis.delete(key)
