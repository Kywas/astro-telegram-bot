from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot

from app.database import Database

logger = logging.getLogger(__name__)

ERROR_SPIKE_THRESHOLD = 10
ERROR_SPIKE_WINDOW = timedelta(hours=1)
_ERROR_SPIKE_COOLDOWN = timedelta(hours=1)
_last_error_spike_alert_at: datetime | None = None


async def notify_admins(bot: Bot, admin_ids: tuple[int, ...], text: str) -> None:
    if not admin_ids:
        return
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            logger.debug("Failed to notify admin %s", admin_id, exc_info=True)


async def notify_admins_bot_started(bot: Bot, admin_ids: tuple[int, ...]) -> None:
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await notify_admins(
        bot,
        admin_ids,
        f"✅ AstroPulse запущен\nUTC: {utc_now}",
    )


async def notify_admins_bot_crashed(
    bot: Bot,
    admin_ids: tuple[int, ...],
    *,
    error_type: str,
    message: str,
) -> None:
    snippet = message[:500]
    await notify_admins(
        bot,
        admin_ids,
        f"🚨 Бот упал\n\n{error_type}\n{snippet}",
    )


async def check_and_notify_error_spike(
    db: Database,
    bot: Bot,
    admin_ids: tuple[int, ...],
) -> None:
    global _last_error_spike_alert_at
    if not admin_ids:
        return
    now = datetime.now(timezone.utc)
    if (
        _last_error_spike_alert_at is not None
        and now - _last_error_spike_alert_at < _ERROR_SPIKE_COOLDOWN
    ):
        return

    since = (now - ERROR_SPIKE_WINDOW).isoformat()
    count = await db.count_errors_since(since)
    if count < ERROR_SPIKE_THRESHOLD:
        return

    samples = await db.get_recent_error_summaries(since, limit=5)
    lines = [f"• {item['source']}: {item['error_type']} — {item['message'][:120]}" for item in samples]
    details = "\n".join(lines) if lines else "—"
    await notify_admins(
        bot,
        admin_ids,
        (
            f"⚠️ Всплеск ошибок: {count} за последний час "
            f"(порог {ERROR_SPIKE_THRESHOLD})\n\n"
            f"Последние:\n{details}"
        ),
    )
    _last_error_spike_alert_at = now
