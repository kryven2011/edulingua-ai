"""EduLingua AI — Admin Models.

Admin users and usage logging.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class AdminRole(str, enum.Enum):
    """Admin panel role."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


class Admin(Base):
    """Admin panel user (separate from Telegram users)."""

    __tablename__ = "admins"
    __table_args__ = (
        Index("ix_admins_username", "username", unique=True),
    )

    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole, name="admin_role_enum", native_enum=False),
        nullable=False,
        server_default=AdminRole.MODERATOR.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Admin(username={self.username!r}, role={self.role})>"


class UsageLog(Base):
    """Audit / usage log entry."""

    __tablename__ = "usage_logs"
    __table_args__ = (
        Index("ix_usage_logs_user_id", "user_id"),
        Index("ix_usage_logs_action", "action"),
        Index("ix_usage_logs_created_at", "created_at"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # --- Relationships ---
    user: Mapped["User | None"] = relationship(back_populates="usage_logs")

    def __repr__(self) -> str:
        return f"<UsageLog(action={self.action!r}, user_id={self.user_id!r})>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.user import User
