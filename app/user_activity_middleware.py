"""Track real user interactions (messages, buttons, payments)."""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, TelegramObject

from app.bot_context import db

_TOUCH_INTERVAL_SEC = 300
_last_touch: dict[int, float] = {}


def _extract_user_id(event: TelegramObject) -> int | None:
    if isinstance(event, Message):
        user = event.from_user
    elif isinstance(event, CallbackQuery):
        user = event.from_user
    elif isinstance(event, PreCheckoutQuery):
        user = event.from_user
    else:
        return None
    return user.id if user is not None else None


class UserActivityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = _extract_user_id(event)
        if user_id is not None:
            now = time.monotonic()
            last = _last_touch.get(user_id, 0.0)
            if now - last >= _TOUCH_INTERVAL_SEC:
                _last_touch[user_id] = now
                await db.touch_user_activity(user_id)
        return await handler(event, data)
