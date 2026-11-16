"""EduLingua AI — /start Command & Registration Router.

Checks user registration status in PostgreSQL:
- Unregistered users are directed through the multi-step registration flow.
- Registered users are welcomed directly to the main menu.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.registration import start_registration_flow
from app.bot.keyboards.main_kb import get_main_menu_keyboard
from app.database.models.user import User
from app.i18n import t

router = Router(name="start")


@router.message(CommandStart())
async def handle_start_command(
    message: Message,
    user: User,
    lang: str,
    state: FSMContext,
) -> None:
    """Handle /start from user. Checks PostgreSQL registration status."""
    # Check registration status in database
    if not user.is_registered:
        # Launch multi-step registration flow
        await start_registration_flow(message, state)
        return

    # Returning registered user: display welcome and main menu
    await state.clear()
    name = user.first_name or user.username or "Student"
    await message.answer(
        text=t("welcome_back", lang=lang, name=name),
        reply_markup=get_main_menu_keyboard(lang),
    )
