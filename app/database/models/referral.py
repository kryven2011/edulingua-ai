"""EduLingua AI — Referral Models.

Referral tracking between users.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class Referral(Base):
    """Tracks user-to-user referrals."""

    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("referred_id", name="uq_referral_referred_id"),
        Index("ix_referrals_referrer_id", "referrer_id"),
    )

    referrer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    referred_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    bonus_awarded: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )

    # --- Relationships ---
    referrer: Mapped["User"] = relationship(
        back_populates="referrals_made",
        foreign_keys=[referrer_id],
    )
    referred: Mapped["User"] = relationship(
        back_populates="referred_by",
        foreign_keys=[referred_id],
    )

    def __repr__(self) -> str:
        return (
            f"<Referral(referrer_id={self.referrer_id!r}, "
            f"referred_id={self.referred_id!r})>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.user import User
