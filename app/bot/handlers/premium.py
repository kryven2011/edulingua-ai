"""EduLingua AI — Premium Subscription Handler.

Displays tier comparisons (FREE, PRO, ULTIMATE) and handles upgrade inquiries.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import MenuCallback, PremiumCallback
from app.bot.keyboards.premium_kb import get_plan_keyboard, get_premium_keyboard
from app.config import SubscriptionTier, get_settings
from app.database.models.user import User
from app.database.repositories.subscription_repo import SubscriptionRepository
from app.i18n import t
from app.services.payments.payment_service import PaymentService

router = Router(name="premium")


@router.callback_query(MenuCallback.filter(F.action == "premium"))
async def show_premium_options(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Render subscription plans overview."""
    settings = get_settings()
    sub_repo = SubscriptionRepository(session)
    tier = await sub_repo.get_user_tier(user.id)

    text = t(
        "premium_info",
        lang=lang,
        free_limit=settings.free_ai_daily_limit,
        pro_limit=settings.pro_ai_daily_limit,
        ultimate_limit=settings.ultimate_ai_daily_limit,
    )
    text += f"\n\n" + t("current_plan", lang=lang, plan=tier.value.upper())

    markup = get_premium_keyboard(lang)
    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(PremiumCallback.filter(F.action == "select_plan"))
async def select_premium_plan(
    callback: CallbackQuery,
    callback_data: PremiumCallback,
    user: User,
    session: AsyncSession,
    lang: str,
) -> None:
    """Handle plan selection for payment."""
    tier_str = callback_data.tier
    settings = get_settings()
    payment_service = PaymentService(session, settings)

    if not payment_service.is_payment_configured():
        # Cleanly tell user that payment gateway is not yet activated
        await callback.answer(t("payment_not_configured", lang=lang), show_alert=True)
        return

    tier = SubscriptionTier(tier_str) if tier_str in [t.value for t in SubscriptionTier] else SubscriptionTier.PRO
    invoice = await payment_service.create_payment_invoice(user.id, tier)

    await callback.message.edit_text(  # type: ignore[union-attr]
        text=f"💳 Оформление подписки {tier.value.upper()} (${invoice['amount']})\n\nСледуйте инструкциям платёжной системы.",
        reply_markup=get_plan_keyboard(lang=lang, tier=tier.value),
    )
    await callback.answer()
