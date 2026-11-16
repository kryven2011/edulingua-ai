"""EduLingua AI — Notification and Broadcasting Service.

Handles daily streak reminders, level-up alerts, achievement notices,
and administrator broadcasts.
"""

from __future__ import annotations

import logging
import uuid
from typing import Sequence

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.i18n import t

logger = logging.getLogger(__name__)


class NotificationService:
    """Service dispatching asynchronous notifications to students."""

    def __init__(self, bot: Bot, session: AsyncSession) -> None:
        self.bot = bot
        self.session = session

    async def notify_level_up(
        self, telegram_id: int, new_level: int, lang: str = "ru"
    ) -> bool:
        """Send congratulatory level-up message."""
        try:
            msg = t("level_up", lang=lang, level=new_level)
            await self.bot.send_message(chat_id=telegram_id, text=msg)
            return True
        except Exception as e:
            logger.warning("Failed to send level-up alert to %d: %s", telegram_id, e)
            return False

    async def notify_achievement(
        self,
        telegram_id: int,
        title: str,
        description: str,
        icon: str = "🏆",
        lang: str = "ru",
    ) -> bool:
        """Send achievement unlock alert."""
        try:
            msg = f"{icon} <b>Достижение разблокировано!</b>\n\n<b>{title}</b>\n{description}"
            await self.bot.send_message(chat_id=telegram_id, text=msg)
            return True
        except Exception as e:
            logger.warning("Failed to send achievement alert to %d: %s", telegram_id, e)
            return False

    async def broadcast(self, text: str, admin_id: uuid.UUID | None = None) -> dict[str, int]:
        """Broadcast message to all active users."""
        stmt = select(User.telegram_id).where(User.is_blocked == False)  # noqa: E712
        telegram_ids = (await self.session.execute(stmt)).scalars().all()

        sent = 0
        failed = 0
        for tid in telegram_ids:
            try:
                await self.bot.send_message(chat_id=tid, text=text)
                sent += 1
            except Exception:
                failed += 1

        logger.info("Broadcast finished: %d sent, %d failed", sent, failed)
        return {"total": len(telegram_ids), "sent": sent, "failed": failed}
