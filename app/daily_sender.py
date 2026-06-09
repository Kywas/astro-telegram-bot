import asyncio
from datetime import datetime, timezone

from aiogram import Bot

from app.database import Database
from app.horoscope import generate_horoscope
from app.premium import is_premium_active
from app.timezones import user_local_date_key, user_local_hhmm


async def _send_due_deliveries(db: Database, bot: Bot, now_utc: datetime) -> None:
    recipients = await db.get_daily_subscribers()
    for user in recipients:
        if user_local_hhmm(now_utc, user.timezone) != user.daily_time:
            continue

        locale = user.language
        sign = user.sign
        if not sign:
            continue

        period = "day"
        if is_premium_active(user.premium_until):
            period = "week"

        date_key = user_local_date_key(now_utc, user.timezone)
        if await db.was_daily_sent(user.user_id, period, date_key):
            continue

        text = generate_horoscope(sign=sign, locale=locale, period=period)
        try:
            await bot.send_message(
                chat_id=user.user_id,
                text=text,
            )
            await db.mark_daily_sent(user.user_id, period, date_key)
            await db.log_event(user.user_id, "daily_sent")
        except Exception:
            await db.log_event(user.user_id, "daily_send_failed")


async def run_daily_loop(db: Database, bot: Bot) -> None:
    # Minimal scheduler: checks once per minute.
    while True:
        now = datetime.now(timezone.utc)
        await _send_due_deliveries(db, bot, now)
        await asyncio.sleep(60)
