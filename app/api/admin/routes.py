"""EduLingua AI — Admin Panel Management Endpoints.

Provides administrative controls for users, analytics, subscriptions,
curriculum management, and announcements.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, func, select, update

from app.api.admin.dependencies import get_current_admin
from app.config import SubscriptionTier, get_settings
from app.database.models.admin import Admin
from app.database.models.education import Subject
from app.database.models.language import Language
from app.database.models.subscription import Subscription, Transaction
from app.database.models.user import User, UserProfile
from app.database.session import get_db_session
from app.services.payments.subscription_service import SubscriptionService

router = APIRouter(prefix="/api/admin", tags=["admin_routes"])


class ManualPremiumRequest(BaseModel):
    tier: str
    duration_days: int = 30


class BroadcastRequest(BaseModel):
    message: str


@router.get("/dashboard")
async def get_dashboard_stats(
    admin: Admin = Depends(get_current_admin),
) -> dict[str, Any]:
    """Retrieve operational metrics for dashboard overview."""
    async with get_db_session() as session:
        # User counts
        total_users = (
            await session.execute(select(func.count()).select_from(User))
        ).scalar_one() or 0

        # Subscriptions
        active_pro = (
            await session.execute(
                select(func.count())
                .select_from(Subscription)
                .where(Subscription.tier == "pro", Subscription.is_active == True)  # noqa: E712
            )
        ).scalar_one() or 0

        active_ultimate = (
            await session.execute(
                select(func.count())
                .select_from(Subscription)
                .where(Subscription.tier == "ultimate", Subscription.is_active == True)  # noqa: E712
            )
        ).scalar_one() or 0

        # Total revenue
        revenue = (
            await session.execute(
                select(func.sum(Transaction.amount)).where(Transaction.status == "completed")
            )
        ).scalar_one() or 0.0

        return {
            "total_users": total_users,
            "active_subscriptions": {
                "pro": active_pro,
                "ultimate": active_ultimate,
            },
            "total_revenue_usd": round(float(revenue), 2),
        }


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
) -> dict[str, Any]:
    """List registered users with pagination."""
    async with get_db_session() as session:
        stmt = (
            select(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = (await session.execute(stmt)).scalars().all()
        total = (await session.execute(select(func.count()).select_from(User))).scalar_one() or 0

        return {
            "total": total,
            "users": [
                {
                    "id": str(u.id),
                    "telegram_id": u.telegram_id,
                    "username": u.username,
                    "name": u.first_name,
                    "language": u.interface_language,
                    "is_blocked": u.is_blocked,
                    "is_registered": u.is_registered,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
        }


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: uuid.UUID,
    admin: Admin = Depends(get_current_admin),
) -> dict[str, str]:
    """Block user from accessing the platform."""
    async with get_db_session() as session:
        stmt = update(User).where(User.id == user_id).values(is_blocked=True)
        res = await session.execute(stmt)
        if (res.rowcount or 0) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "blocked", "user_id": str(user_id)}


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: uuid.UUID,
    admin: Admin = Depends(get_current_admin),
) -> dict[str, str]:
    """Unblock user account."""
    async with get_db_session() as session:
        stmt = update(User).where(User.id == user_id).values(is_blocked=False)
        res = await session.execute(stmt)
        if (res.rowcount or 0) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "unblocked", "user_id": str(user_id)}


@router.post("/users/{user_id}/premium")
async def grant_manual_premium(
    user_id: uuid.UUID,
    payload: ManualPremiumRequest,
    admin: Admin = Depends(get_current_admin),
) -> dict[str, Any]:
    """Manually assign premium tier to user."""
    tier_enum = SubscriptionTier(payload.tier.lower())
    async with get_db_session() as session:
        sub_service = SubscriptionService(session)
        sub = await sub_service.activate_subscription(
            user_id=user_id,
            tier=tier_enum,
            duration_days=payload.duration_days,
            payment_id=f"admin_granted_{admin.username}",
        )
        return {
            "status": "granted",
            "tier": sub.tier,
            "expires_at": sub.expires_at.isoformat(),
        }


@router.post("/broadcast")
async def broadcast_announcement(
    payload: BroadcastRequest,
    admin: Admin = Depends(get_current_admin),
) -> dict[str, Any]:
    """Queue platform broadcast to active Telegram students."""
    # Enqueue notification in Redis or execute directly
    from app.bot.setup import create_bot
    from app.services.notifications.notification_service import NotificationService

    settings = get_settings()
    bot = create_bot(settings.telegram_bot_token.get_secret_value())

    async with get_db_session() as session:
        notif = NotificationService(bot=bot, session=session)
        stats = await notif.broadcast(text=payload.message, admin_id=admin.id)
        await bot.session.close()
        return stats
