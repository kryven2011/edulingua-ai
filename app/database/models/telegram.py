"""EduLingua AI — Telegram Update Tracking Model.

Stores raw Telegram updates for idempotent webhook processing.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class TelegramUpdate(Base):
    """Tracks processed Telegram webhook updates for idempotency."""

    __tablename__ = "telegram_updates"
    __table_args__ = (
        Index("ix_telegram_updates_update_id", "update_id", unique=True),
        Index("ix_telegram_updates_processed", "processed"),
    )

    # Override base id — use update_id as natural PK is optional;
    # we keep the UUID PK from Base and add update_id as a unique column.
    update_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False,
    )
    processed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TelegramUpdate(update_id={self.update_id}, "
            f"processed={self.processed})>"
        )
