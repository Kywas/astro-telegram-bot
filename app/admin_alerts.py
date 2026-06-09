from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot

from app.database import Database

logger = logging.getLogger(__name__)

ERROR_SPIKE_THRESHOLD = 10
ERROR_SPIKE_WINDOW = timedelta(hours=1)
_ERROR_SPIKE_COOLDOWN = timedelta(hours=1)
_last_error_spike_alert_at: datetime | None = None


async def notify_admins(bot: Bot, admin_ids: tuple[int, ...], text: str) -> int:
    if not admin_ids:
        logger.warning("Admin alert skipped: ADMIN_IDS is empty")
        return 0

    sent = 0
    for admin_id in admin_ids:
        delivered = False
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                await bot.send_message(admin_id, text)
                sent += 1
                delivered = True
                break
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    await asyncio.sleep(2)
        if not delivered and last_error is not None:
            logger.warning(
                "Failed to notify admin %s: %s: %s",
                admin_id,
                type(last_error).__name__,
                last_error,
            )
    if sent == 0:
        logger.warning(
            "Admin alert was not delivered to anyone. "
            "Check ADMIN_IDS and send /start to the bot from admin accounts."
        )
    else:
        logger.info("Admin alert delivered to %s/%s admin(s)", sent, len(admin_ids))
    return sent


async def notify_admins_bot_started(bot: Bot, admin_ids: tuple[int, ...]) -> int:
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return await notify_admins(
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
) -> int:
    snippet = message[:500]
    return await notify_admins(
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
