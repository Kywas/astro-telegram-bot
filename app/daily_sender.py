import asyncio
from datetime import date, datetime, timedelta, timezone

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database import Database
from app.evening_checkin import build_evening_checkin_prompt
from app.horoscope import generate_horoscope, personalization_from_profile
from app.moon_calendar import (
    LUNAR_PREVIEW_DAYS,
    format_lunar_day_notification,
    format_lunar_preview_notification,
    major_lunar_phase_on,
)
from app.premium import is_premium_active
from app.timezones import user_local_date_key, user_local_hhmm

LUNAR_NOTIFY_TIME = "10:00"


def mood_checkin_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for start in (1, 6):
        row = [
            InlineKeyboardButton(text=str(score), callback_data=f"checkin:mood:{score}")
            for score in range(start, start + 5)
        ]
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


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

        text = generate_horoscope(
            sign=sign,
            locale=locale,
            period=period,
            personalization=personalization_from_profile(user),
            profile=user,
        )
        try:
            await bot.send_message(chat_id=user.user_id, text=text)
            await db.mark_daily_sent(user.user_id, period, date_key)
            await db.log_event(user.user_id, "daily_sent")
        except Exception:
            await db.log_event(user.user_id, "daily_send_failed")


async def _send_evening_checkins(db: Database, bot: Bot, now_utc: datetime) -> None:
    recipients = await db.get_evening_subscribers()
    for user in recipients:
        if user_local_hhmm(now_utc, user.timezone) != user.evening_time:
            continue

        date_key = user_local_date_key(now_utc, user.timezone)
        if await db.was_daily_sent(user.user_id, "evening", date_key):
            continue

        text = build_evening_checkin_prompt(user.language)
        try:
            await bot.send_message(
                chat_id=user.user_id,
                text=text,
                reply_markup=mood_checkin_keyboard(),
            )
            await db.mark_daily_sent(user.user_id, "evening", date_key)
            await db.log_event(user.user_id, "evening_checkin_sent")
        except Exception:
            await db.log_event(user.user_id, "evening_checkin_failed")


async def _send_lunar_notifications(db: Database, bot: Bot, now_utc: datetime) -> None:
    recipients = await db.get_lunar_notify_subscribers()
    for user in recipients:
        if user_local_hhmm(now_utc, user.timezone) != LUNAR_NOTIFY_TIME:
            continue

        locale = user.language
        local_today = date.fromisoformat(user_local_date_key(now_utc, user.timezone))

        phase_today = major_lunar_phase_on(local_today)
        if phase_today:
            date_key = local_today.isoformat()
            period = f"lunar_day:{phase_today}"
            if not await db.was_daily_sent(user.user_id, period, date_key):
                text = format_lunar_day_notification(phase_today, locale, local_today)
                try:
                    await bot.send_message(chat_id=user.user_id, text=text)
                    await db.mark_daily_sent(user.user_id, period, date_key)
                    await db.log_event(user.user_id, "lunar_day_sent")
                except Exception:
                    await db.log_event(user.user_id, "lunar_day_failed")

        if not is_premium_active(user.premium_until):
            continue

        preview_date = local_today + timedelta(days=LUNAR_PREVIEW_DAYS)
        phase_preview = major_lunar_phase_on(preview_date)
        if not phase_preview:
            continue

        preview_key = preview_date.isoformat()
        period = f"lunar_preview:{phase_preview}"
        if await db.was_daily_sent(user.user_id, period, preview_key):
            continue

        text = format_lunar_preview_notification(
            phase_preview,
            locale,
            preview_date,
            days_left=LUNAR_PREVIEW_DAYS,
        )
        try:
            await bot.send_message(chat_id=user.user_id, text=text)
            await db.mark_daily_sent(user.user_id, period, preview_key)
            await db.log_event(user.user_id, "lunar_preview_sent")
        except Exception:
            await db.log_event(user.user_id, "lunar_preview_failed")


async def run_daily_loop(db: Database, bot: Bot) -> None:
    while True:
        now = datetime.now(timezone.utc)
        await _send_due_deliveries(db, bot, now)
        await _send_evening_checkins(db, bot, now)
        await _send_lunar_notifications(db, bot, now)
        await asyncio.sleep(60)
