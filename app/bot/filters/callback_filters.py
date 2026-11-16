"""EduLingua AI — Callback Data Factories.

Typed callback data classes using aiogram 3.x CallbackData pattern.
Each factory encodes/decodes structured data in inline-button callbacks.
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class RegistrationCallback(CallbackData, prefix="reg"):
    """Registration step callbacks."""

    step: str
    value: str = ""


class MenuCallback(CallbackData, prefix="menu"):
    """Main menu navigation callbacks."""

    action: str


class EduAICallback(CallbackData, prefix="eduai"):
    """EduAI tutor callbacks."""

    action: str
    subject: str = ""
    session_id: str = ""
    page: int = 0


class LinguaCallback(CallbackData, prefix="lingua"):
    """LinguaBot language-learning callbacks."""

    action: str
    language: str = ""
    section: str = ""
    scenario: str = ""


class ProfileCallback(CallbackData, prefix="profile"):
    """Profile screen callbacks."""

    action: str


class PremiumCallback(CallbackData, prefix="premium"):
    """Premium subscription callbacks."""

    action: str
    tier: str = ""


class SettingsCallback(CallbackData, prefix="settings"):
    """Settings screen callbacks."""

    action: str
    value: str = ""


class LeaderboardCallback(CallbackData, prefix="lb"):
    """Leaderboard callbacks."""

    period: str = "daily"


class DailyCallback(CallbackData, prefix="daily"):
    """Daily tasks callbacks."""

    action: str
    task_id: str = ""


class AdminCallback(CallbackData, prefix="adm"):
    """Admin panel callbacks."""

    action: str
    value: str = ""
