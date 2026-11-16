"""EduLingua AI — FastAPI Application & Webhook Server.

Main API server handling webhook reception, health diagnostics,
and administrator REST endpoints.

CRITICAL INVARIANT:
Runs strictly in WEBHOOK mode. Absolutely NO polling anywhere.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path

from app.api.admin.auth import router as admin_auth_router
from app.api.admin.routes import router as admin_routes_router
from app.api.health import router as health_router
from app.api.webhook import router as webhook_router
from admin_panel.app import router as admin_frontend_router
from app.config import get_settings
from app.database.session import close_engine, get_engine
from app.utils.redis_client import close_redis, get_redis_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("edulingua")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    settings = get_settings()
    logger.info("Starting EduLingua AI (Environment: %s)", settings.app_env.value)

    # 1. Initialize DB and Redis
    engine = get_engine()
    get_redis_client()

    # Auto-initialize database tables and seed data if needed
    try:
        from app.database.models.base import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema synchronized")

        from app.database.session import get_db_session
        from app.services.education.subject_service import SubjectService
        from app.services.gamification.achievement_service import AchievementService
        from app.services.gamification.daily_task_service import DailyTaskService
        from app.services.language.language_tutor_service import LanguageTutorService

        async with get_db_session() as session:
            await SubjectService(session).get_active_subjects()
            await LanguageTutorService(session, ai_provider=None).get_active_languages()  # type: ignore[arg-type]
            await AchievementService(session).ensure_defaults()
            await DailyTaskService(session).ensure_daily_tasks()
            await session.commit()
        logger.info("Default seed data verified")
    except Exception as e:
        logger.warning("Database schema/seed check notice: %s", e)

    # 2. Register Webhook with Telegram API (PRODUCTION WEBHOOK ONLY)
    token = settings.telegram_bot_token.get_secret_value()
    secret = settings.webhook_secret.get_secret_value()
    webhook_target = settings.webhook_url

    if webhook_target:
        logger.info("Registering Telegram Webhook: target=%s", webhook_target)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"https://api.telegram.org/bot{token}/setWebhook",
                    json={
                        "url": webhook_target,
                        "secret_token": secret,
                        "drop_pending_updates": False,
                        "allowed_updates": ["message", "callback_query"],
                    },
                )
                if resp.status_code == 200 and resp.json().get("ok"):
                    logger.info("Telegram Webhook registered successfully!")
                else:
                    logger.warning(
                        "Telegram setWebhook returned status %d: %s",
                        resp.status_code,
                        resp.text,
                    )
        except Exception as e:
            logger.error("Could not register Telegram webhook on startup: %s", e)
    else:
        logger.warning(
            "WEBHOOK_BASE_URL is not set yet. Webhook auto-registration skipped. "
            "Set WEBHOOK_BASE_URL in Railway variables or run scripts/manage_webhook.py set"
        )

    yield

    # Shutdown sequence:
    logger.info("Shutting down EduLingua AI...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"https://api.telegram.org/bot{token}/deleteWebhook")
            logger.info("Telegram Webhook deregistered")
    except Exception as e:
        logger.warning("Failed to deregister webhook on shutdown: %s", e)

    await close_redis()
    await close_engine()
    logger.info("EduLingua AI shutdown complete")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    settings = get_settings()

    app = FastAPI(
        title="EduLingua AI",
        description="Production-Ready Telegram Educational AI Platform",
        version="1.0.0",
        docs_url="/docs" if settings.is_debug else None,
        redoc_url="/redoc" if settings.is_debug else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routers
    app.include_router(webhook_router)
    app.include_router(health_router)
    app.include_router(admin_auth_router)
    app.include_router(admin_routes_router)
    app.include_router(admin_frontend_router)

    # Static assets for admin panel
    static_dir = Path(__file__).resolve().parent.parent / "admin_panel" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app


app = create_app()
