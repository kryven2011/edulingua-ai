"""EduLingua AI — Telegram Webhook Receiver.

HIGH-PERFORMANCE PRODUCTION WEBHOOK ENDPOINT:
1. Validates X-Telegram-Bot-Api-Secret-Token header in constant time.
2. Parses incoming Telegram update JSON.
3. Performs update_id deduplication via Redis SETNX with 24h TTL.
4. Pushes update payload to asynchronous Redis queue.
5. Returns fast HTTP 200 response.
6. Absolutely NO polling or getUpdates.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from app.config import get_settings
from app.utils.redis_client import get_redis_client
from app.utils.security import verify_webhook_secret

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhook"])

TELEGRAM_QUEUE_KEY = "telegram:updates:queue"
SEEN_UPDATE_PREFIX = "telegram:seen_update:"
SEEN_TTL_SECONDS = 86400  # 24 hours


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> Response:
    """Receive and queue incoming updates from Telegram Webhook."""
    settings = get_settings()
    expected_secret = settings.webhook_secret.get_secret_value()

    # 1. Constant-time secret header validation
    if not x_telegram_bot_api_secret_token or not verify_webhook_secret(
        x_telegram_bot_api_secret_token, expected_secret
    ):
        logger.warning("Rejected unauthorized webhook request: invalid secret token")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram secret token",
        )

    # 2. Parse JSON payload
    try:
        body = await request.body()
        data = json.loads(body)
    except Exception as e:
        logger.error("Malformed JSON payload in webhook: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON",
        ) from e

    update_id = data.get("update_id")
    if update_id is None:
        logger.warning("Received webhook update without update_id")
        return Response(content="ok", media_type="text/plain", status_code=200)

    # 3. Deduplication check via Redis
    redis = get_redis_client()
    if redis:
        seen_key = f"{SEEN_UPDATE_PREFIX}{update_id}"
        # nx=True returns True only if key was NOT present
        is_new = await redis.set(seen_key, "1", ex=SEEN_TTL_SECONDS, nx=True)
        if not is_new:
            # Already processed or queued; return 200 idempotently
            return Response(content="ok", media_type="text/plain", status_code=200)

        # 4. Push to processing queue
        await redis.rpush(TELEGRAM_QUEUE_KEY, body.decode("utf-8"))
    else:
        logger.error("Redis client is not available to enqueue update_id=%s", update_id)

    # 5. Immediate return HTTP 200
    return Response(content="ok", media_type="text/plain", status_code=200)
