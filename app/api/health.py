"""EduLingua AI — Health Check Endpoints.

Provides simple ping for load balancers and detailed dependency diagnostics
for PostgreSQL, Redis, and Telegram Webhook status.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database.session import get_db_session
from app.utils.redis_client import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_ping() -> dict[str, str]:
    """Basic health check for container orchestrators."""
    return {"status": "ok", "service": "edulingua-ai"}


@router.get("/health/detailed")
async def health_detailed() -> dict[str, Any]:
    """In-depth diagnostics of all infrastructure dependencies."""
    settings = get_settings()
    results: dict[str, Any] = {
        "status": "healthy",
        "service": "edulingua-ai",
        "environment": settings.app_env.value,
        "database": "unknown",
        "redis": "unknown",
        "telegram_webhook": "unknown",
    }

    # 1. PostgreSQL check
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
            results["database"] = "connected"
    except Exception as e:
        results["database"] = f"error: {str(e)}"
        results["status"] = "degraded"

    # 2. Redis check
    try:
        redis = get_redis_client()
        if redis and await redis.ping():
            results["redis"] = "connected"
        else:
            results["redis"] = "unavailable"
            results["status"] = "degraded"
    except Exception as e:
        results["redis"] = f"error: {str(e)}"
        results["status"] = "degraded"

    # 3. Telegram Webhook check
    token = settings.telegram_bot_token.get_secret_value()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
            if resp.status_code == 200:
                data = resp.json().get("result", {})
                results["telegram_webhook"] = {
                    "url": data.get("url"),
                    "has_custom_certificate": data.get("has_custom_certificate"),
                    "pending_update_count": data.get("pending_update_count", 0),
                    "last_error_message": data.get("last_error_message"),
                }
            else:
                results["telegram_webhook"] = f"http_{resp.status_code}"
    except Exception as e:
        results["telegram_webhook"] = f"check_failed: {str(e)}"

    return results
