"""Daily/evening settings panel renderers."""
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.bot_context import db
from app.i18n import t
from app.keyboards import (
    breadcrumb,
    daily_menu_keyboard,
    daily_timezone_keyboard,
    evening_menu_keyboard,
)
from app.timezones import timezone_label_with_offset
from app.user_location import resolve_user_timezone
from app.text_format import format_screen_body, p, screen_page
from app.ui import edit_or_send, show_panel_from_message


async def render_daily_panel(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    enabled = bool(profile and profile.daily_enabled)
    current_time = profile.daily_time if profile else "09:00"
    current_tz = resolve_user_timezone(profile, locale)
    tz_label = timezone_label_with_offset(locale, current_tz)
    status = (
        t(locale, "daily_status_on", hhmm=current_time, tz=tz_label)
        if enabled
        else t(locale, "daily_status_off", tz=tz_label)
    )
    evening_enabled = bool(profile and profile.evening_enabled)
    evening_time = profile.evening_time if profile else "20:00"
    evening_status = (
        t(locale, "evening_status_on", hhmm=evening_time, tz=tz_label)
        if evening_enabled
        else t(locale, "evening_status_off")
    )
    lunar_enabled = bool(profile.lunar_notify_enabled) if profile else True
    lunar_status = (
        t(locale, "lunar_status_on") if lunar_enabled else t(locale, "lunar_status_off")
    )
    extra_lines = [
        "",
        t(locale, "daily_retention_header"),
        evening_status,
        lunar_status,
    ]
    if profile and profile.mood_streak > 0:
        extra_lines.append(
            t(locale, "evening_streak_line", streak=str(profile.mood_streak))
        )
    extra_block = "\n".join(extra_lines).strip()
    text = screen_page(
        breadcrumb(locale, t(locale, "crumb_settings"), t(locale, "crumb_daily")),
        t(locale, "daily_menu_intro"),
        status,
        p(t(locale, "daily_choose_time"), format_screen_body(extra_block)) if extra_block else t(locale, "daily_choose_time"),
    )
    return text, daily_menu_keyboard(
        locale,
        enabled=enabled,
        current_time=current_time,
        lunar_enabled=lunar_enabled,
    )


async def render_evening_panel(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    enabled = bool(profile and profile.evening_enabled)
    current_time = profile.evening_time if profile else "20:00"
    current_tz = resolve_user_timezone(profile, locale)
    tz_label = timezone_label_with_offset(locale, current_tz)
    status = (
        t(locale, "evening_status_on", hhmm=current_time, tz=tz_label)
        if enabled
        else t(locale, "evening_status_off")
    )
    streak_line = ""
    if profile and profile.mood_streak > 0:
        streak_line = f"\n{t(locale, 'evening_streak_line', streak=str(profile.mood_streak))}\n"
    text = screen_page(
        breadcrumb(locale, t(locale, "crumb_settings"), t(locale, "crumb_daily")),
        p(status, streak_line.strip()) if streak_line else status,
        t(locale, "evening_choose_time"),
    )
    return text, evening_menu_keyboard(locale, enabled=enabled, current_time=current_time)


async def render_daily_timezone_panel(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    current_tz = resolve_user_timezone(profile, locale)
    tz_label = timezone_label_with_offset(locale, current_tz)
    text = screen_page(
        breadcrumb(locale, t(locale, "crumb_settings"), t(locale, "crumb_daily")),
        t(locale, "daily_choose_timezone"),
        tz_label,
    )
    return text, daily_timezone_keyboard(locale, current_tz)


async def show_daily_panel(message: Message, user_id: int, locale: str) -> None:
    text, keyboard = await render_daily_panel(user_id, locale)
    await show_panel_from_message(message, text, reply_markup=keyboard)


async def show_daily_panel_callback(callback: CallbackQuery, user_id: int, locale: str) -> None:
    text, keyboard = await render_daily_panel(user_id, locale)
    await edit_or_send(callback, text, inline_keyboard=keyboard)
