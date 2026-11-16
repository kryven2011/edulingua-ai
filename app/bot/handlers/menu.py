"""EduLingua AI — Main Menu Router.

Handles top-level navigation, return-to-menu callbacks, and help screens.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.filters.callback_filters import MenuCallback
from app.bot.keyboards.main_kb import get_main_menu_keyboard
from app.database.models.user import User
from app.i18n import t

router = Router(name="menu")


@router.callback_query(MenuCallback.filter(F.action.in_(["main", "back"])))
async def return_to_main_menu(
    callback: CallbackQuery,
    user: User,
    lang: str,
    state: FSMContext,
) -> None:
    """Clear any active FSM state and return to main menu."""
    await state.clear()
    name = user.first_name or user.username or "Student"
    await callback.message.edit_text(  # type: ignore[union-attr]
        text=t("welcome_back", lang=lang, name=name),
        reply_markup=get_main_menu_keyboard(lang),
    )
    await callback.answer()


@router.message(Command("menu"))
async def command_menu(message: Message, user: User, lang: str, state: FSMContext) -> None:
    """Display main menu on /menu command."""
    await state.clear()
    name = user.first_name or user.username or "Student"
    await message.answer(
        text=t("welcome_back", lang=lang, name=name),
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.callback_query(MenuCallback.filter(F.action == "help"))
@router.message(Command("help"))
async def show_help(event: Message | CallbackQuery, lang: str) -> None:
    """Display platform help and feature guide."""
    from app.bot.keyboards.common_kb import get_back_to_main_keyboard

    text = t("help_text", lang=lang)
    markup = get_back_to_main_keyboard(lang)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
        await event.answer()
    else:
        await event.answer(text=text, reply_markup=markup)
