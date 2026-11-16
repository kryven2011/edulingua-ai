"""EduLingua AI — Telegram Handlers Registry."""

from app.bot.handlers.admin import router as admin_router
from app.bot.handlers.daily import router as daily_router
from app.bot.handlers.eduai import router as eduai_router
from app.bot.handlers.leaderboard import router as leaderboard_router
from app.bot.handlers.lingua import router as lingua_router
from app.bot.handlers.menu import router as menu_router
from app.bot.handlers.premium import router as premium_router
from app.bot.handlers.profile import router as profile_router
from app.bot.handlers.progress import router as progress_router
from app.bot.handlers.registration import router as registration_router
from app.bot.handlers.settings import router as settings_router
from app.bot.handlers.start import router as start_router

ALL_ROUTERS = [
    start_router,
    registration_router,
    menu_router,
    eduai_router,
    lingua_router,
    profile_router,
    progress_router,
    daily_router,
    leaderboard_router,
    premium_router,
    settings_router,
    admin_router,
]

__all__ = ["ALL_ROUTERS"]
