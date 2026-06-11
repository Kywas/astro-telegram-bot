"""Central error logging with optional admin Telegram alerts."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from aiogram import Bot

from app.admin_alerts import notify_admins
from app.bot_context import db

_ERROR_ALERT_COOLDOWN = timedelta(minutes=10)
_recent_error_alert_keys: dict[str, datetime] = {}


def _error_alert_key(source: str, error_type: str, message: str) -> str:
    return f"{source}|{error_type}|{message[:120]}"


def _should_notify(source: str, *, notify: bool) -> bool:
    if not notify:
        return False
    # Routine per-user delivery failures during broadcast.
    return source != "broadcast"


def _prune_recent_alerts(now: datetime) -> None:
    if len(_recent_error_alert_keys) <= 200:
        return
    cutoff = now - _ERROR_ALERT_COOLDOWN
    for key, seen_at in list(_recent_error_alert_keys.items()):
        if seen_at < cutoff:
            del _recent_error_alert_keys[key]


async def notify_admins_new_error(
    bot: Bot,
    admin_ids: tuple[int, ...],
    *,
    source: str,
    error_type: str,
    message: str,
    context: str | None = None,
) -> int:
    if not admin_ids:
        return 0

    key = _error_alert_key(source, error_type, message)
    now = datetime.now(timezone.utc)
    last = _recent_error_alert_keys.get(key)
    if last is not None and now - last < _ERROR_ALERT_COOLDOWN:
        return 0
    _recent_error_alert_keys[key] = now
    _prune_recent_alerts(now)

    lines = [
        "⚠️ Новая ошибка",
        "",
        f"Источник: {source}",
        f"Тип: {error_type}",
        f"Сообщение: {message[:400]}",
    ]
    if context:
        lines.extend(["", f"Контекст: {context[:200]}"])
    lines.extend(["", "Admin → Stats для истории"])
    return await notify_admins(bot, admin_ids, "\n".join(lines))


async def report_error(
    *,
    bot: Bot | None,
    admin_ids: tuple[int, ...],
    source: str,
    error_type: str,
    message: str,
    context: str | None = None,
    notify: bool = True,
) -> None:
    await db.log_error(
        source=source,
        error_type=error_type,
        message=message,
        context=context,
    )
    if bot is None or not _should_notify(source, notify=notify):
        return
    await notify_admins_new_error(
        bot,
        admin_ids,
        source=source,
        error_type=error_type,
        message=message,
        context=context,
    )
