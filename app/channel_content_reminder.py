"""Remind admins to prepare new channel posts before the current pool runs out."""
from __future__ import annotations

import logging
import math
from datetime import date, datetime, timedelta

from aiogram import Bot

from app.admin_alerts import notify_admins
from app.channel_posting import channel_configured
from app.channel_scheduler import load_channel_schedule_config

CHANNEL_SENTINEL_USER_ID = 0
from app.database import Database
from app.services.channel_content import count_publishable_posts
from app.timezones import user_local_date_key, user_local_hhmm

logger = logging.getLogger(__name__)

POSTS_PER_DAY = 3
REMINDER_DAYS_BEFORE = 2
REMINDER_HHMM = "09:00"
WEEK_POST_TARGET = POSTS_PER_DAY * 7


def content_runway_days(post_count: int) -> int:
    if post_count <= 0:
        return 0
    return max(1, math.ceil(post_count / POSTS_PER_DAY))


def last_content_day(start_date: date, post_count: int) -> date:
    """Last calendar day covered by the current post pool (3 posts/day)."""
    return start_date + timedelta(days=content_runway_days(post_count) - 1)


def reminder_day(start_date: date, post_count: int) -> date | None:
    if post_count <= 0:
        return None
    return last_content_day(start_date, post_count) - timedelta(days=REMINDER_DAYS_BEFORE)


def content_cycle_key(start_date: str, post_count: int) -> str:
    return f"{start_date}:{post_count}"


def build_channel_content_reminder_text(
    *,
    post_count: int,
    start_date: str,
    timezone: str,
    reminder_date: date,
    last_day: date,
) -> str:
    runway = content_runway_days(post_count)
    posts_for_week = WEEK_POST_TARGET
    return (
        "📢 Посты канала скоро закончатся\n\n"
        f"Сейчас готово: {post_count} пост(ов) · ~{runway} дн. "
        f"({POSTS_PER_DAY} поста/день)\n"
        f"Старт автопостинга: {start_date} ({timezone})\n"
        f"Последний день текущего набора: {last_day.strftime('%d.%m.%Y')}\n"
        "После этой даты начнутся повторы.\n\n"
        f"Сделай ещё посты на неделю — минимум {posts_for_week} шт. "
        f"(7 дней × {POSTS_PER_DAY}):\n"
        "1. marketing/channel/posts/\n"
        "2. python scripts/assign_unique_channel_bases.py\n"
        "3. python scripts/render_channel_gifs.py --all\n"
        "4. git push → на сервере git pull\n\n"
        "Проверка: /channelschedule"
    )


def format_content_reminder_line(start_date: str, post_count: int) -> str:
    if post_count <= 0:
        return "⚠️ Нет готовых постов для автопубликации."
    start = date.fromisoformat(start_date)
    last = last_content_day(start, post_count)
    remind = reminder_day(start, post_count)
    if remind is None:
        return ""
    return (
        f"Напоминание админам: {remind.strftime('%d.%m.%Y')} "
        f"(за {REMINDER_DAYS_BEFORE} дн. до {last.strftime('%d.%m.%Y')})"
    )


async def check_and_notify_channel_content_reminder(
    db: Database,
    bot: Bot,
    admin_ids: tuple[int, ...],
    now_utc: datetime,
) -> None:
    if not admin_ids or not channel_configured():
        return

    cfg = load_channel_schedule_config()
    if not cfg.enabled:
        return

    post_count = count_publishable_posts()
    if post_count <= 0:
        return

    start = date.fromisoformat(cfg.start_date)
    remind = reminder_day(start, post_count)
    if remind is None:
        return

    date_key = user_local_date_key(now_utc, cfg.timezone)
    today = date.fromisoformat(date_key)
    if today != remind:
        return
    if user_local_hhmm(now_utc, cfg.timezone) != REMINDER_HHMM:
        return

    period = f"channel_content_reminder:{content_cycle_key(cfg.start_date, post_count)}"
    if await db.was_daily_sent(CHANNEL_SENTINEL_USER_ID, period, date_key):
        return

    last = last_content_day(start, post_count)
    text = build_channel_content_reminder_text(
        post_count=post_count,
        start_date=cfg.start_date,
        timezone=cfg.timezone,
        reminder_date=remind,
        last_day=last,
    )
    sent = await notify_admins(bot, admin_ids, text)
    if sent:
        await db.mark_daily_sent(CHANNEL_SENTINEL_USER_ID, period, date_key)
        await db.log_event(
            CHANNEL_SENTINEL_USER_ID,
            f"channel_content_reminder:{post_count}:{last.isoformat()}",
        )
        logger.info(
            "channel content reminder sent posts=%s last_day=%s admins=%s",
            post_count,
            last.isoformat(),
            sent,
        )
