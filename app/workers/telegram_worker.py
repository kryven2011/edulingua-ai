"""EduLingua AI — Telegram Update Queue Worker.

Processes incoming Telegram updates from the Redis queue asynchronously.
Feeds updates to aiogram's Dispatcher with retry mechanisms,
dead-letter queue for failed items, and graceful shutdown handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
import signal
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from redis.asyncio import Redis

from app.api.webhook import TELEGRAM_QUEUE_KEY
from app.config import get_settings

logger = logging.getLogger(__name__)

DLQ_KEY = "telegram:updates:dlq"
MAX_RETRIES = 3


class TelegramWorker:
    """Async Redis worker feeding queued updates to aiogram Dispatcher."""

    def __init__(
        self,
        bot: Bot,
        dp: Dispatcher,
        redis: Redis,
    ) -> None:
        self.bot = bot
        self.dp = dp
        self.redis = redis
        self._running = False
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Run the worker event loop."""
        self._running = True
        logger.info("Telegram update worker started listening on '%s'", TELEGRAM_QUEUE_KEY)

        while self._running:
            try:
                # BLPOP blocks for up to 2 seconds waiting for an update
                pop_result = await self.redis.blpop([TELEGRAM_QUEUE_KEY], timeout=2.0)
                if not pop_result:
                    continue

                _, raw_payload = pop_result
                await self._process_update_with_retries(raw_payload)

            except asyncio.CancelledError:
                logger.info("Worker task cancelled")
                break
            except Exception as e:
                logger.error("Unexpected error in worker loop: %s", e, exc_info=True)
                await asyncio.sleep(1)

        logger.info("Telegram update worker terminated gracefully")

    async def _process_update_with_retries(self, raw_payload: str | bytes) -> None:
        """Process a single update JSON with retry tracking."""
        payload_str = raw_payload.decode("utf-8") if isinstance(raw_payload, bytes) else raw_payload

        try:
            data = json.loads(payload_str)
        except Exception as e:
            logger.error("Failed to parse update payload: %s", e)
            await self._push_to_dlq(payload_str, error=f"JSONDecodeError: {str(e)}")
            return

        update_id = data.get("update_id", "unknown")
        retry_count = data.get("_retry_count", 0)

        try:
            # Construct aiogram Update model
            update_obj = Update.model_validate(data)
            # Feed to dispatcher
            await self.dp.feed_update(self.bot, update_obj)
            logger.debug("Successfully processed update_id=%s", update_id)

        except Exception as e:
            logger.error("Error processing update_id=%s: %s", update_id, e, exc_info=True)
            retry_count += 1
            if retry_count <= MAX_RETRIES:
                data["_retry_count"] = retry_count
                logger.info("Re-queueing update_id=%s (attempt %d/%d)", update_id, retry_count, MAX_RETRIES)
                await asyncio.sleep(1.0 * retry_count)
                await self.redis.rpush(TELEGRAM_QUEUE_KEY, json.dumps(data))
            else:
                logger.error("Update_id=%s exceeded max retries (%d). Moving to DLQ.", update_id, MAX_RETRIES)
                await self._push_to_dlq(json.dumps(data), error=str(e))

    async def _push_to_dlq(self, payload: str, error: str) -> None:
        """Transfer dead/unparsable update to dead-letter queue."""
        dlq_entry = json.dumps({"payload": payload, "error": error})
        await self.redis.rpush(DLQ_KEY, dlq_entry)

    def stop(self) -> None:
        """Initiate graceful stop."""
        self._running = False
        self._stop_event.set()
