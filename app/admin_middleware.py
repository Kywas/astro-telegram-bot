from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.auth import is_admin


class AdminOnlyMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: tuple[int, ...], deny_text: str) -> None:
        super().__init__()
        self._admin_ids = admin_ids
        self._deny_text = deny_text

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if user is None or not is_admin(user.id, self._admin_ids):
            if isinstance(event, Message):
                await event.answer(self._deny_text)
            elif isinstance(event, CallbackQuery) and event.message:
                await event.message.answer(self._deny_text)
                await event.answer()
            return None
        return await handler(event, data)
