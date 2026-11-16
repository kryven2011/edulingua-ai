"""EduLingua AI — Leaderboard Service.

Retrieves and caches competitive user rankings with Redis.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.gamification_repo import GamificationRepository

logger = logging.getLogger(__name__)


class LeaderboardService:
    """Service providing daily, weekly, and all-time user leaderboards."""

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self.session = session
        self.redis = redis
        self.repo = GamificationRepository(session)

    async def get_leaderboard(
        self, period: str = "daily", limit: int = 15
    ) -> list[dict[str, Any]]:
        """Fetch ranked leaderboard entries, using Redis cache if available."""
        cache_key = f"leaderboard:{period}:{limit}"

        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning("Redis cache read failed for leaderboard: %s", e)

        # Database query
        data = await self.repo.get_leaderboard(period=period, limit=limit)

        if self.redis:
            try:
                # Convert UUIDs to str for JSON serialization
                clean_data = [
                    {k: str(v) if k == "user_id" else v for k, v in item.items()}
                    for item in data
                ]
                await self.redis.set(cache_key, json.dumps(clean_data), ex=self.CACHE_TTL_SECONDS)
            except Exception as e:
                logger.warning("Redis cache write failed for leaderboard: %s", e)

        return data
