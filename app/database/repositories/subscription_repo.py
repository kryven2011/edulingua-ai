"""EduLingua AI — Subscription and Transaction Repository.

Handles user premium tiers, subscriptions, and financial transactions.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Sequence

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SubscriptionTier
from app.database.models.subscription import Subscription, Transaction
from app.database.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for user subscriptions and transaction audit trail."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Subscription, session)

    async def get_active_subscription(self, user_id: uuid.UUID) -> Subscription | None:
        """Fetch current valid subscription for user."""
        now = datetime.utcnow()
        stmt = (
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.is_active == True,  # noqa: E712
                Subscription.expires_at > now,
            )
            .order_by(Subscription.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_tier(self, user_id: uuid.UUID) -> SubscriptionTier:
        """Resolve current active tier (FREE / PRO / ULTIMATE)."""
        sub = await self.get_active_subscription(user_id)
        if sub and sub.tier in [t.value for t in SubscriptionTier]:
            return SubscriptionTier(sub.tier)
        return SubscriptionTier.FREE

    async def create_subscription(
        self,
        user_id: uuid.UUID,
        tier: SubscriptionTier,
        duration_days: int = 30,
        payment_id: str | None = None,
    ) -> Subscription:
        """Activate new subscription for user and deactivate previous ones."""
        # Deactivate old
        deact_stmt = (
            update(Subscription)
            .where(Subscription.user_id == user_id, Subscription.is_active == True)  # noqa: E712
            .values(is_active=False)
        )
        await self.session.execute(deact_stmt)

        now = datetime.utcnow()
        expires = now + timedelta(days=duration_days)
        new_sub = Subscription(
            user_id=user_id,
            tier=tier.value,
            started_at=now,
            expires_at=expires,
            is_active=True,
            payment_id=payment_id,
        )
        self.session.add(new_sub)
        await self.session.flush()
        return new_sub

    async def record_transaction(
        self,
        user_id: uuid.UUID,
        amount: float,
        currency: str,
        status: str,
        provider: str,
        provider_payment_id: str | None = None,
        subscription_tier: str | None = None,
        meta_data: dict[str, Any] | None = None,
    ) -> Transaction:
        """Save payment transaction in immutable audit ledger."""
        tx = Transaction(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status=status,
            provider=provider,
            provider_payment_id=provider_payment_id,
            subscription_tier=subscription_tier,
            metadata_=meta_data or {},
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def get_user_transactions(
        self, user_id: uuid.UUID, limit: int = 20
    ) -> Sequence[Transaction]:
        """Fetch payment history for a user."""
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
