"""Mandatory channel subscription during bot registration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from app.auth import is_admin
from app.bot_context import db, settings
from app.channel_posting import channel_configured, normalize_channel_chat_id
from app.i18n import t
from app.keyboards import channel_subscription_keyboard, home_panel_keyboard, language_keyboard
from app.services.home import build_home_panel_text
from app.ui import edit_or_send, show_panel_from_message

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

    from app.database import UserProfile

logger = logging.getLogger(__name__)

_ACTIVE_MEMBER_STATUSES = frozenset(
    {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }
)


async def user_needs_channel_gate(user_id: int, profile: UserProfile | None = None) -> bool:
    if is_admin(user_id, settings.admin_ids):
        return False
    if not channel_configured():
        return False
    if profile is None:
        profile = await db.get_user(user_id)
    if profile is None:
        return True
    if profile.channel_verified:
        return False
    if profile.sign:
        return False
    return True


async def check_channel_subscription(bot: Bot, user_id: int) -> tuple[bool, str | None]:
    raw = (settings.channel_id or "").strip()
    if not raw:
        return True, None
    try:
        chat_id = normalize_channel_chat_id(raw)
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in _ACTIVE_MEMBER_STATUSES, None
    except TelegramBadRequest as exc:
        logger.warning("channel subscription check failed for user %s: %s", user_id, exc)
        return False, str(exc)


async def show_channel_subscription_panel(
    *,
    locale: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> None:
    text = t(locale, "channel_subscribe_required")
    keyboard = channel_subscription_keyboard(locale)
    if callback is not None:
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return
    if message is not None:
        await show_panel_from_message(
            message,
            text,
            reply_markup=keyboard,
            prefer_new=True,
        )


async def continue_registration_after_channel(
    *,
    user_id: int,
    locale: str,
    state: FSMContext,
    callback: CallbackQuery | None = None,
    message: Message | None = None,
) -> None:
    await state.clear()
    profile = await db.get_user(user_id)
    if profile and profile.sign:
        lang = profile.language or locale
        panel_text = await build_home_panel_text(user_id, lang, variant="start")
        if callback is not None:
            await edit_or_send(callback, panel_text, inline_keyboard=home_panel_keyboard(lang))
        elif message is not None:
            await show_panel_from_message(message, panel_text, reply_markup=home_panel_keyboard(lang))
        return

    if callback is not None:
        await edit_or_send(
            callback,
            "Выбери язык / Choose language:",
            inline_keyboard=language_keyboard(prefix="startlang"),
        )
    elif message is not None:
        await show_panel_from_message(
            message,
            "Выбери язык / Choose language:",
            reply_markup=language_keyboard(prefix="startlang"),
        )
