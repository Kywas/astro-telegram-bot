import asyncio
import logging
from datetime import date, datetime, timedelta, timezone

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.admin_alerts import check_and_notify_error_spike
from app.database import Database
from app.evening_checkin import build_evening_checkin_prompt
from app.horoscope import generate_horoscope, personalization_from_profile
from app.moon_calendar import (
    LUNAR_PREVIEW_DAYS,
    LUNAR_PREVIEW_FREE_DAYS,
    format_lunar_daily_reminder,
    format_lunar_day_notification,
    format_lunar_preview_notification,
    major_lunar_phase_on,
    normalize_moon_focus,
    resolve_moon_style,
)
from app.premium import is_premium_active
from app.premium_lifecycle import (
    premium_expiry_period_key,
    premium_expiry_reminder_text,
    premium_renew_keyboard,
    should_send_premium_24h_reminder,
)
from app.timezones import user_local_date_key, user_local_hhmm
from app.ui import send_formatted_message
from app.weekly_digest import send_due_weekly_digests
from app.channel_scheduler import send_due_channel_posts
from app.channel_content_reminder import check_and_notify_channel_content_reminder

LUNAR_NOTIFY_TIME = "10:00"
PREMIUM_24H_REMINDER_PERIOD = "premium_reminder:24h"


def mood_checkin_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for start in (1, 6):
        row = [
            InlineKeyboardButton(text=str(score), callback_data=f"checkin:mood:{score}")
            for score in range(start, start + 5)
        ]
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lunar_notify_keyboard(locale: str) -> InlineKeyboardMarkup:
    moon_label = "🌙 Лунный календарь" if locale == "ru" else "🌙 Moon calendar"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=moon_label, callback_data="nav:moon")],
        ]
    )


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
        date_key = user_local_date_key(now_utc, user.timezone)
        if await db.was_daily_sent(user.user_id, period, date_key):
            continue

        text = generate_horoscope(
            sign=sign,
            locale=locale,
            period=period,
            for_date=date.fromisoformat(date_key),
            personalization=personalization_from_profile(user),
            profile=user,
        )
        try:
            await send_formatted_message(bot, user.user_id, text)
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

        for_date = date.fromisoformat(date_key)
        text = build_evening_checkin_prompt(user.language, profile=user, for_date=for_date)
        try:
            await send_formatted_message(
                bot,
                user.user_id,
                text,
                reply_markup=mood_checkin_keyboard(),
            )
            await db.mark_daily_sent(user.user_id, "evening", date_key)
            await db.log_event(user.user_id, "evening_checkin_sent")
        except Exception:
            await db.log_event(user.user_id, "evening_checkin_failed")


async def _send_lunar_preview(
    db: Database,
    bot: Bot,
    *,
    user,
    locale: str,
    event_date: date,
    phase_key: str,
    days_left: int,
    early: bool,
) -> None:
    period = f"lunar_preview:{'early' if early else 'free'}:{phase_key}"
    date_key = event_date.isoformat()
    if await db.was_daily_sent(user.user_id, period, date_key):
        return
    text = format_lunar_preview_notification(
        phase_key,
        locale,
        event_date,
        days_left=days_left,
        early=early,
        focus=normalize_moon_focus(user.moon_focus),
        style=resolve_moon_style(user),
        timezone_name=user.timezone,
    )
    try:
        await send_formatted_message(
            bot,
            user.user_id,
            text,
            reply_markup=lunar_notify_keyboard(locale),
        )
        await db.mark_daily_sent(user.user_id, period, date_key)
        event_name = "lunar_preview_early_sent" if early else "lunar_preview_free_sent"
        await db.log_event(user.user_id, event_name)
    except Exception:
        event_name = "lunar_preview_early_failed" if early else "lunar_preview_free_failed"
        await db.log_event(user.user_id, event_name)


async def _send_lunar_notifications(db: Database, bot: Bot, now_utc: datetime) -> None:
    recipients = await db.get_lunar_notify_subscribers()
    for user in recipients:
        if user_local_hhmm(now_utc, user.timezone) != LUNAR_NOTIFY_TIME:
            continue

        locale = user.language
        local_today = date.fromisoformat(user_local_date_key(now_utc, user.timezone))
        date_key = local_today.isoformat()

        if is_premium_active(user.premium_until):
            preview_date = local_today + timedelta(days=LUNAR_PREVIEW_DAYS)
            phase_preview = major_lunar_phase_on(preview_date, user.timezone)
            if phase_preview:
                await _send_lunar_preview(
                    db,
                    bot,
                    user=user,
                    locale=locale,
                    event_date=preview_date,
                    phase_key=phase_preview,
                    days_left=LUNAR_PREVIEW_DAYS,
                    early=True,
                )

        preview_date = local_today + timedelta(days=LUNAR_PREVIEW_FREE_DAYS)
        phase_preview = major_lunar_phase_on(preview_date, user.timezone)
        if phase_preview:
            await _send_lunar_preview(
                db,
                bot,
                user=user,
                locale=locale,
                event_date=preview_date,
                phase_key=phase_preview,
                days_left=LUNAR_PREVIEW_FREE_DAYS,
                early=False,
            )

        period = f"lunar_daily:{date_key}"
        if await db.was_daily_sent(user.user_id, period, date_key):
            continue

        focus = normalize_moon_focus(user.moon_focus)
        style = resolve_moon_style(user)
        phase_today = major_lunar_phase_on(local_today, user.timezone)
        if phase_today:
            text = format_lunar_day_notification(
                phase_today,
                locale,
                local_today,
                focus=focus,
                style=style,
                timezone_name=user.timezone,
            )
        else:
            text = format_lunar_daily_reminder(
                locale,
                local_today,
                focus=focus,
                style=style,
                timezone_name=user.timezone,
            )

        try:
            await send_formatted_message(
                bot,
                user.user_id,
                text,
                reply_markup=lunar_notify_keyboard(locale),
            )
            await db.mark_daily_sent(user.user_id, period, date_key)
            await db.log_event(
                user.user_id,
                "lunar_major_sent" if phase_today else "lunar_daily_sent",
            )
        except Exception:
            await db.log_event(
                user.user_id,
                "lunar_major_failed" if phase_today else "lunar_daily_failed",
            )


async def _send_premium_expiry_reminders(db: Database, bot: Bot, now_utc: datetime) -> None:
    recipients = await db.get_users_with_premium()
    for user in recipients:
        if not user.premium_until:
            continue
        if not should_send_premium_24h_reminder(user.premium_until, now_utc):
            continue
        until_key = premium_expiry_period_key(user.premium_until)
        if await db.was_daily_sent(user.user_id, PREMIUM_24H_REMINDER_PERIOD, until_key):
            continue
        locale = user.language or "en"
        text = premium_expiry_reminder_text(
            locale,
            until_iso=user.premium_until,
            hours_left=24,
        )
        try:
            await send_formatted_message(
                bot,
                user.user_id,
                text,
                reply_markup=premium_renew_keyboard(locale),
            )
            await db.mark_daily_sent(user.user_id, PREMIUM_24H_REMINDER_PERIOD, until_key)
            await db.log_event(user.user_id, "premium_reminder_24h_sent")
        except Exception:
            await db.log_event(user.user_id, "premium_reminder_24h_failed")


async def run_daily_loop(
    db: Database,
    bot: Bot,
    *,
    admin_ids: tuple[int, ...] = (),
) -> None:
    logger = logging.getLogger(__name__)
    while True:
        try:
            now = datetime.now(timezone.utc)
            await _send_due_deliveries(db, bot, now)
            await _send_evening_checkins(db, bot, now)
            await _send_lunar_notifications(db, bot, now)
            await _send_premium_expiry_reminders(db, bot, now)
            await send_due_weekly_digests(db, bot, now)
            await send_due_channel_posts(db, bot, now)
            await check_and_notify_channel_content_reminder(db, bot, admin_ids, now)
            await check_and_notify_error_spike(db, bot, admin_ids)
        except Exception:
            logger.exception("daily loop tick failed")
        await asyncio.sleep(60)
