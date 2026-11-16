"""EduLingua AI — Subscription Models.

Subscription tiers and payment transactions.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier."""

    FREE = "free"
    PRO = "pro"
    ULTIMATE = "ultimate"


class PaymentStatus(str, enum.Enum):
    """Status of a payment transaction."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Subscription(Base):
    """User subscription record."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscriptions_user_id", "user_id"),
        Index("ix_subscriptions_is_active", "is_active"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier, name="subscription_tier_enum", native_enum=False),
        nullable=False,
        server_default=SubscriptionTier.FREE.value,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return (
            f"<Subscription(user_id={self.user_id!r}, tier={self.tier}, "
            f"active={self.is_active})>"
        )


class Transaction(Base):
    """Payment transaction record."""

    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_user_id", "user_id"),
        Index("ix_transactions_status", "status"),
        Index("ix_transactions_provider_payment_id", "provider_payment_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="USD",
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum", native_enum=False),
        nullable=False,
        server_default=PaymentStatus.PENDING.value,
    )
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )
    subscription_tier: Mapped[SubscriptionTier | None] = mapped_column(
        Enum(SubscriptionTier, name="subscription_tier_enum", native_enum=False,
             create_constraint=False),
        nullable=True,
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id!r}, user_id={self.user_id!r}, "
            f"amount={self.amount} {self.currency}, status={self.status})>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.user import User
