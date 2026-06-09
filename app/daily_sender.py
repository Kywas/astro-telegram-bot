import asyncio
from datetime import datetime, timezone

from aiogram import Bot

from app.database import Database
from app.horoscope import generate_horoscope
from app.premium import is_premium_active


async def _send_for_time(db: Database, bot: Bot, hhmm: str, now: datetime) -> None:
    recipients = await db.get_daily_recipients(hhmm)
    for user in recipients:
        locale = user.language
        sign = user.sign
        if not sign:
            continue

        period = "day"
        if is_premium_active(user.premium_until):
            period = "week"

        date_key = now.strftime("%Y-%m-%d")
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
        hhmm = now.strftime("%H:%M")
        await _send_for_time(db, bot, hhmm, now)
        await asyncio.sleep(60)
