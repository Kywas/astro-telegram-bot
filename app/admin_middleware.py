from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.auth import is_admin
from app.i18n import t
from app.services.locale_users import get_user_locale


class AdminOnlyMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: tuple[int, ...]) -> None:
        super().__init__()
        self._admin_ids = admin_ids

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if user is None or not is_admin(user.id, self._admin_ids):
            locale = await get_user_locale(user.id)
            deny_text = t(locale, "admin_only")
            if isinstance(event, Message):
                await event.answer(deny_text)
            elif isinstance(event, CallbackQuery) and event.message:
                await event.message.answer(deny_text)
                await event.answer()
            return None
        return await handler(event, data)
