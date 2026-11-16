"""EduLingua AI — User Settings Handler.

Allows modifying interface language, target learning language, and notifications.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.callback_filters import MenuCallback, SettingsCallback
from app.bot.keyboards.settings_kb import (
    get_language_change_keyboard,
    get_settings_keyboard,
)
from app.database.models.user import User
from app.database.repositories.user_repo import UserRepository
from app.i18n import get_language_name, t

router = Router(name="settings")


@router.callback_query(MenuCallback.filter(F.action == "settings"))
async def open_settings_menu(
    callback: CallbackQuery,
    user: User,
    lang: str,
) -> None:
    """Render settings screen."""
    cur_lang = get_language_name(user.interface_language, interface_lang=lang)
    learning_code = user.settings.learning_language if user.settings else "en"
    learning_lang = get_language_name(learning_code or "en", interface_lang=lang)

    text = t("settings_menu", lang=lang, language=cur_lang, learning_lang=learning_lang)
    markup = get_settings_keyboard(lang)

    await callback.message.edit_text(text=text, reply_markup=markup)  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(SettingsCallback.filter(F.action == "change_lang"))
async def prompt_change_language(
    callback: CallbackQuery,
    lang: str,
) -> None:
    """Show language selection list."""
    await callback.message.edit_text(  # type: ignore[union-attr]
        text=t("choose_language", lang=lang),
        reply_markup=get_language_change_keyboard(),
    )
    await callback.answer()


@router.callback_query(SettingsCallback.filter(F.action == "set_lang"))
async def apply_new_language(
    callback: CallbackQuery,
    callback_data: SettingsCallback,
    user: User,
    session: AsyncSession,
) -> None:
    """Save updated interface language."""
    new_lang = callback_data.value
    user_repo = UserRepository(session)
    await user_repo.update_interface_language(user.id, new_lang)
    user.interface_language = new_lang

    await callback.answer(t("language_set", lang=new_lang))
    await open_settings_menu(callback, user, new_lang)
