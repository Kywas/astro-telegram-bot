"""Block bot usage until new users subscribe to the required channel."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, TelegramObject

from app.bot_context import settings
from app.channel_subscription import show_channel_subscription_panel, user_needs_channel_gate
from app.i18n import t
from app.services.locale_users import get_user_locale


class ChannelGateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id: int | None = None
        if isinstance(event, Message):
            user = event.from_user
            user_id = user.id if user is not None else None
        elif isinstance(event, (CallbackQuery, PreCheckoutQuery)):
            user = event.from_user
            user_id = user.id if user is not None else None

        if user_id is None or not await user_needs_channel_gate(user_id):
            return await handler(event, data)

        locale = await get_user_locale(user_id)

        if isinstance(event, Message):
            text = (event.text or "").strip()
            if text.startswith("/start"):
                return await handler(event, data)
            await show_channel_subscription_panel(locale=locale, message=event)
            return None

        if isinstance(event, CallbackQuery):
            if (event.data or "") == "channel:check":
                return await handler(event, data)
            await event.answer(t(locale, "channel_gate_blocked"), show_alert=True)
            await show_channel_subscription_panel(locale=locale, callback=event)
            return None

        if isinstance(event, PreCheckoutQuery):
            await event.answer(ok=False, error_message=t(locale, "channel_gate_blocked"))
            return None

        return await handler(event, data)
