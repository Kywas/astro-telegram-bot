"""Automatic channel posting — 3 slots per day (morning / lunch / evening)."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from typing import TYPE_CHECKING

from aiogram import Bot

from app.bot_context import PROJECT_ROOT
from app.channel_posting import channel_configured, send_channel_animation
from app.config import load_settings
from app.services.channel_content import load_post_bundle, pick_slug_for_slot
from app.timezones import user_local_date_key, user_local_hhmm, user_local_weekday

if TYPE_CHECKING:
    from app.database import Database

logger = logging.getLogger(__name__)

SCHEDULE_PATH = PROJECT_ROOT / "marketing" / "channel" / "schedule.json"
CHANNEL_SENTINEL_USER_ID = 0

_DEFAULT_WEEKDAY = {"morning": "08:30", "lunch": "13:00", "evening": "19:30"}
_DEFAULT_WEEKEND = {"morning": "10:30", "lunch": "14:30", "evening": "20:00"}
_SLOT_ORDER = ("morning", "lunch", "evening")


@dataclass(frozen=True)
class ChannelScheduleConfig:
    timezone: str
    enabled: bool
    start_date: str
    weekday: dict[str, str]
    weekend: dict[str, str]


def _load_schedule_file() -> dict:
    if not SCHEDULE_PATH.is_file():
        return {}
    return json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))


def load_channel_schedule_config() -> ChannelScheduleConfig:
    raw = _load_schedule_file()
    settings = load_settings()

    weekday = dict(_DEFAULT_WEEKDAY)
    weekday.update(raw.get("weekday") or {})
    weekend = dict(_DEFAULT_WEEKEND)
    weekend.update(raw.get("weekend") or {})

    tz = settings.channel_schedule_timezone or str(raw.get("timezone") or "Europe/Moscow")
    start_date = settings.channel_schedule_start or str(raw.get("start_date") or "2026-06-21")

    return ChannelScheduleConfig(
        timezone=tz.strip(),
        enabled=settings.channel_schedule_enabled,
        start_date=start_date.strip(),
        weekday=weekday,
        weekend=weekend,
    )


def slots_for_date(now_utc: datetime, *, config: ChannelScheduleConfig | None = None) -> dict[str, str]:
    cfg = config or load_channel_schedule_config()
    weekday = user_local_weekday(now_utc, cfg.timezone)
    return cfg.weekend if weekday >= 5 else cfg.weekday


def due_slot_names(now_utc: datetime, *, config: ChannelScheduleConfig | None = None) -> tuple[str, ...]:
    cfg = config or load_channel_schedule_config()
    hhmm = user_local_hhmm(now_utc, cfg.timezone)
    return tuple(name for name in _SLOT_ORDER if slots_for_date(now_utc, config=cfg).get(name) == hhmm)


def planned_posts_for_date(date_key: str, *, config: ChannelScheduleConfig | None = None) -> list[tuple[str, str, str]]:
    """Return [(slot, time, slug), …] for a calendar day key."""
    cfg = config or load_channel_schedule_config()
    day = date.fromisoformat(date_key)
    weekday = day.weekday()
    times = cfg.weekend if weekday >= 5 else cfg.weekday
    return [
        (slot, times[slot], pick_slug_for_slot(slot, date_key))
        for slot in _SLOT_ORDER
        if slot in times
    ]


def format_schedule_preview(date_key: str | None = None) -> str:
    cfg = load_channel_schedule_config()
    if date_key is None:
        date_key = user_local_date_key(datetime.now(timezone.utc), cfg.timezone)
    day = date.fromisoformat(date_key)
    weekday_names = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
    lines = [
        f"📅 Расписание канала · {date_key} ({weekday_names[day.weekday()]}) · {cfg.timezone}",
        f"Старт: {cfg.start_date} · авто: {'вкл' if cfg.enabled else 'выкл'}",
        "",
    ]
    for slot, hhmm, slug in planned_posts_for_date(date_key, config=cfg):
        label = {"morning": "Утро", "lunch": "Обед", "evening": "Вечер"}.get(slot, slot)
        lines.append(f"• {label} {hhmm} → {slug}")
    from app.channel_content_reminder import format_content_reminder_line
    from app.services.channel_content import count_publishable_posts

    reminder_line = format_content_reminder_line(cfg.start_date, count_publishable_posts())
    if reminder_line:
        lines.extend(["", reminder_line])
    lines.extend(
        [
            "",
            "Будни:",
            f"  {cfg.weekday.get('morning')} / {cfg.weekday.get('lunch')} / {cfg.weekday.get('evening')}",
            "Выходные:",
            f"  {cfg.weekend.get('morning')} / {cfg.weekend.get('lunch')} / {cfg.weekend.get('evening')}",
        ]
    )
    return "\n".join(lines)


async def _send_scheduled_slot(
    db: Database,
    bot: Bot,
    *,
    slot: str,
    date_key: str,
    slug: str,
) -> bool:
    period = f"channel:{slot}"
    if await db.was_daily_sent(CHANNEL_SENTINEL_USER_ID, period, date_key):
        return False

    bundle = load_post_bundle(slug)
    await send_channel_animation(bot, bundle.gif_path, bundle.caption)
    await db.mark_daily_sent(CHANNEL_SENTINEL_USER_ID, period, date_key)
    await db.log_event(CHANNEL_SENTINEL_USER_ID, f"channel_scheduled:{slot}:{slug}")
    logger.info("channel post sent slot=%s slug=%s date=%s", slot, slug, date_key)
    return True


async def send_due_channel_posts(db: Database, bot: Bot, now_utc: datetime) -> None:
    cfg = load_channel_schedule_config()
    if not cfg.enabled:
        return
    if not channel_configured():
        return

    date_key = user_local_date_key(now_utc, cfg.timezone)
    if date.fromisoformat(date_key) < date.fromisoformat(cfg.start_date):
        return

    for slot in due_slot_names(now_utc, config=cfg):
        slug = pick_slug_for_slot(slot, date_key)
        try:
            await _send_scheduled_slot(db, bot, slot=slot, date_key=date_key, slug=slug)
        except FileNotFoundError:
            logger.warning("channel schedule skip slot=%s slug=%s (bundle missing)", slot, slug)
        except Exception:
            logger.exception("channel schedule failed slot=%s slug=%s date=%s", slot, slug, date_key)
            await db.log_event(CHANNEL_SENTINEL_USER_ID, f"channel_scheduled_fail:{slot}:{slug}")
