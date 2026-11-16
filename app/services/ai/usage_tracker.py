"""EduLingua AI — AI Usage Tracker.

Tracks per-user daily AI request counts in Redis and enforces
subscription-tier limits.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

from redis.asyncio import Redis

from app.config import Settings, SubscriptionTier

logger = logging.getLogger(__name__)

# Redis key pattern: ai_usage:{user_id}:{date}
_KEY_PREFIX = "ai_usage"


def _usage_key(user_id: int, day: date | None = None) -> str:
    """Build the Redis key for a user's daily AI usage counter."""
    day = day or date.today()
    return f"{_KEY_PREFIX}:{user_id}:{day.isoformat()}"


@dataclass(frozen=True, slots=True)
class UsageInfo:
    """Snapshot of a user's AI usage for the current day."""

    used: int
    limit: int
    remaining: int
    tier: SubscriptionTier


class UsageTracker:
    """Manages per-user daily AI request limits via Redis."""

    # TTL slightly longer than 24 h to cover timezone edge cases.
    _KEY_TTL_SECONDS: int = 90_000  # 25 hours

    def __init__(self, redis: Redis, settings: Settings) -> None:
        self._redis = redis
        self._settings = settings

    def _get_limit(self, tier: SubscriptionTier) -> int:
        """Return the daily AI request limit for *tier*."""
        return self._settings.get_ai_daily_limit(tier)

    async def check_limit(
        self,
        user_id: int,
        tier: SubscriptionTier = SubscriptionTier.FREE,
    ) -> UsageInfo:
        """Check whether the user has remaining AI requests today.

        Returns a ``UsageInfo`` snapshot. The caller can inspect
        ``remaining > 0`` before proceeding.
        """
        key = _usage_key(user_id)
        raw = await self._redis.get(key)
        used = int(raw) if raw else 0
        limit = self._get_limit(tier)
        remaining = max(0, limit - used)

        return UsageInfo(
            used=used,
            limit=limit,
            remaining=remaining,
            tier=tier,
        )

    async def increment_usage(
        self,
        user_id: int,
        tier: SubscriptionTier = SubscriptionTier.FREE,
        *,
        amount: int = 1,
    ) -> UsageInfo:
        """Increment the user's daily usage counter.

        The key auto-expires after ~25 hours so no explicit daily reset
        is required.

        Returns the *post-increment* ``UsageInfo``.
        """
        key = _usage_key(user_id)

        pipe = self._redis.pipeline()
        pipe.incrby(key, amount)
        pipe.expire(key, self._KEY_TTL_SECONDS)
        results = await pipe.execute()

        used = int(results[0])
        limit = self._get_limit(tier)
        remaining = max(0, limit - used)

        logger.debug(
            "Usage incremented: user=%d used=%d/%d tier=%s",
            user_id,
            used,
            limit,
            tier.value,
        )

        return UsageInfo(
            used=used,
            limit=limit,
            remaining=remaining,
            tier=tier,
        )

    async def get_remaining(
        self,
        user_id: int,
        tier: SubscriptionTier = SubscriptionTier.FREE,
    ) -> int:
        """Convenience: return the number of remaining requests today."""
        info = await self.check_limit(user_id, tier)
        return info.remaining

    async def reset_usage(self, user_id: int) -> None:
        """Manually reset a user's daily counter (admin action)."""
        key = _usage_key(user_id)
        await self._redis.delete(key)
        logger.info("Usage reset for user=%d", user_id)
