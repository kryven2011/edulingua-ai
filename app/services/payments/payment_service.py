"""EduLingua AI — Payment Processing Service.

Architecture for handling Telegram Payments / Payment Gateways securely.
Real payments are strictly verified and require valid provider credentials.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, SubscriptionTier, get_settings
from app.database.models.subscription import Transaction
from app.database.repositories.subscription_repo import SubscriptionRepository
from app.services.payments.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class PaymentService:
    """Service handling payment creation, provider communication, and verification."""

    TIER_PRICES = {
        SubscriptionTier.PRO: 4.99,
        SubscriptionTier.ULTIMATE: 12.99,
    }

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.sub_repo = SubscriptionRepository(session)
        self.sub_service = SubscriptionService(session, self.settings)

    def is_payment_configured(self) -> bool:
        """Check if production payment credentials are set."""
        return self.settings.has_payment_provider

    async def create_payment_invoice(
        self,
        user_id: uuid.UUID,
        tier: SubscriptionTier,
    ) -> dict[str, Any]:
        """Create pending invoice for user."""
        if not self.is_payment_configured():
            return {
                "available": False,
                "error": "Payment provider is not yet configured by platform administrator.",
            }

        price = self.TIER_PRICES.get(tier, 4.99)
        currency = self.settings.payment_currency

        # Record pending transaction
        tx = await self.sub_repo.record_transaction(
            user_id=user_id,
            amount=price,
            currency=currency,
            status="pending",
            provider="telegram_payments",
            subscription_tier=tier.value,
        )

        return {
            "available": True,
            "transaction_id": str(tx.id),
            "amount": price,
            "currency": currency,
            "provider_token": self.settings.payment_provider_token,
        }

    async def process_successful_payment(
        self,
        user_id: uuid.UUID,
        tier: SubscriptionTier,
        provider_payment_id: str,
        amount: float,
        currency: str,
    ) -> Transaction:
        """Handle verified payment confirmation webhook/callback."""
        # Record completed transaction
        tx = await self.sub_repo.record_transaction(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status="completed",
            provider="telegram_payments",
            provider_payment_id=provider_payment_id,
            subscription_tier=tier.value,
        )

        # Grant subscription
        await self.sub_service.activate_subscription(
            user_id=user_id,
            tier=tier,
            duration_days=30,
            payment_id=provider_payment_id,
        )

        logger.info(
            "Subscription activated via verified payment: user=%s, tier=%s, payment_id=%s",
            user_id,
            tier.value,
            provider_payment_id,
        )
        return tx
