"""EduLingua AI — Daily Task Models.

DailyTask definitions and DailyProgress tracking.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class DailyTaskType(str, enum.Enum):
    """Type of daily task."""

    QUIZ = "quiz"
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    READING = "reading"
    WRITING = "writing"


class DailyTask(Base):
    """A daily task template (recurring if date is null)."""

    __tablename__ = "daily_tasks"
    __table_args__ = (
        Index("ix_daily_tasks_date", "date"),
        Index("ix_daily_tasks_task_type", "task_type"),
    )

    task_type: Mapped[DailyTaskType] = mapped_column(
        Enum(DailyTaskType, name="daily_task_type_enum", native_enum=False),
        nullable=False,
    )
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False)
    description_uz: Mapped[str] = mapped_column(Text, nullable=False)
    description_en: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="10",
    )
    target_value: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true",
    )
    date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # --- Relationships ---
    progress: Mapped[list["DailyProgress"]] = relationship(
        back_populates="task", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<DailyTask(id={self.id!r}, type={self.task_type}, date={self.date})>"


class DailyProgress(Base):
    """User progress on a daily task for a specific date."""

    __tablename__ = "daily_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", "date", name="uq_daily_progress"),
        Index("ix_daily_progress_user_id", "user_id"),
        Index("ix_daily_progress_date", "date"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("daily_tasks.id", ondelete="CASCADE"), nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    current_value: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    xp_awarded: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="daily_progress")
    task: Mapped["DailyTask"] = relationship(back_populates="progress")

    def __repr__(self) -> str:
        return (
            f"<DailyProgress(user_id={self.user_id!r}, task_id={self.task_id!r}, "
            f"date={self.date}, completed={self.is_completed})>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.user import User
