"""Benign Telegram API errors that should not alert admins."""
from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest

_BENIGN_CALLBACK_MARKERS = (
    "query is too old",
    "response timeout expired",
    "query id is invalid",
    "query too old",
    "query is already answered",
    "already answered",
)


def is_benign_callback_query_error(exc: BaseException) -> bool:
    if not isinstance(exc, TelegramBadRequest):
        return False
    message = str(exc).lower()
    return any(marker in message for marker in _BENIGN_CALLBACK_MARKERS)


def is_benign_dispatcher_error(exc: BaseException) -> bool:
    return is_benign_callback_query_error(exc)


def is_benign_telegram_error_message(message: str) -> bool:
    lowered = message.lower()
    return any(marker in lowered for marker in _BENIGN_CALLBACK_MARKERS)
