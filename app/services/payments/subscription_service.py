"""EduLingua AI — Subscription Service.

Server-side enforcement of subscription tiers, limits, and premium access.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, SubscriptionTier, get_settings
from app.database.models.subscription import Subscription
from app.database.repositories.subscription_repo import SubscriptionRepository

logger = logging.getLogger(__name__)


@dataclass
class TierLimits:
    """Configured limits for subscription tier."""

    tier: SubscriptionTier
    daily_ai_limit: int
    daily_tasks_limit: int
    has_speaking_full: bool
    has_priority_support: bool


class SubscriptionService:
    """Service governing subscription plans and server-side feature authorization."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repo = SubscriptionRepository(session)

    async def get_user_tier(self, user_id: uuid.UUID) -> SubscriptionTier:
        """Resolve current active tier."""
        return await self.repo.get_user_tier(user_id)

    def get_tier_limits(self, tier: SubscriptionTier) -> TierLimits:
        """Get capabilities configured for tier."""
        if tier == SubscriptionTier.ULTIMATE:
            return TierLimits(
                tier=tier,
                daily_ai_limit=self.settings.ultimate_ai_daily_limit,
                daily_tasks_limit=self.settings.ultimate_daily_tasks,
                has_speaking_full=True,
                has_priority_support=True,
            )
        if tier == SubscriptionTier.PRO:
            return TierLimits(
                tier=tier,
                daily_ai_limit=self.settings.pro_ai_daily_limit,
                daily_tasks_limit=self.settings.pro_daily_tasks,
                has_speaking_full=True,
                has_priority_support=False,
            )
        return TierLimits(
            tier=tier,
            daily_ai_limit=self.settings.free_ai_daily_limit,
            daily_tasks_limit=self.settings.free_daily_tasks,
            has_speaking_full=False,
            has_priority_support=False,
        )

    async def get_user_limits(self, user_id: uuid.UUID) -> TierLimits:
        """Get limits for user based on their active subscription."""
        tier = await self.get_user_tier(user_id)
        return self.get_tier_limits(tier)

    async def activate_subscription(
        self,
        user_id: uuid.UUID,
        tier: SubscriptionTier,
        duration_days: int = 30,
        payment_id: str | None = None,
    ) -> Subscription:
        """Assign paid tier to user."""
        return await self.repo.create_subscription(
            user_id=user_id,
            tier=tier,
            duration_days=duration_days,
            payment_id=payment_id,
        )
