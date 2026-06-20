from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.payments import PayCurrency
from app.premium import format_premium_until
from app.text_format import format_screen_body
from app.timezones import normalize_timezone

PREMIUM_24H_REMINDER_HOURS = 24
PREMIUM_24H_REMINDER_WINDOW = timedelta(hours=1)


def _parse_premium_until(premium_until: str) -> datetime | None:
    try:
        until = datetime.fromisoformat(premium_until)
    except ValueError:
        return None
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    return until


def format_payment_amount(currency: PayCurrency, invoice_amount: int, telegram_currency: str) -> str:
    if currency == PayCurrency.STARS or telegram_currency == "XTR":
        return f"{invoice_amount} Stars"
    if telegram_currency == "RUB":
        return f"{invoice_amount / 100:.0f} ₽"
    if telegram_currency == "USD":
        return f"${invoice_amount / 100:.2f}"
    return f"{invoice_amount} {telegram_currency}"


def days_until_premium_end(premium_until: str | None, user_timezone: str) -> int | None:
    if not premium_until:
        return None
    try:
        until = _parse_premium_until(premium_until)
        if until is None:
            return None
        tz = ZoneInfo(normalize_timezone(user_timezone))
        until_local = until.astimezone(tz).date()
        today_local = datetime.now(tz).date()
        return (until_local - today_local).days
    except KeyError:
        return None


def seconds_until_premium_end(premium_until: str | None, now_utc: datetime | None = None) -> float | None:
    if not premium_until:
        return None
    until = _parse_premium_until(premium_until)
    if until is None:
        return None
    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return (until - now).total_seconds()


def should_send_premium_24h_reminder(
    premium_until: str | None,
    now_utc: datetime | None = None,
) -> bool:
    seconds_left = seconds_until_premium_end(premium_until, now_utc)
    if seconds_left is None or seconds_left <= 0:
        return False
    target = PREMIUM_24H_REMINDER_HOURS * 3600
    window = int(PREMIUM_24H_REMINDER_WINDOW.total_seconds())
    return (target - window) <= seconds_left <= (target + window)


def premium_expiry_period_key(premium_until: str) -> str:
    until = _parse_premium_until(premium_until)
    if until is None:
        return premium_until
    return until.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M")


def premium_until_date_key(premium_until: str | None, user_timezone: str) -> str | None:
    if not premium_until:
        return None
    until = _parse_premium_until(premium_until)
    if until is None:
        return None
    try:
        tz = ZoneInfo(normalize_timezone(user_timezone))
        return until.astimezone(tz).date().isoformat()
    except KeyError:
        return None


def premium_renew_keyboard(locale: str) -> InlineKeyboardMarkup:
    label = "⭐ Продлить Premium" if locale == "ru" else "⭐ Renew Premium"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data="nav:premium")]]
    )


def premium_expiry_reminder_text(
    locale: str,
    *,
    until_iso: str,
    hours_left: int | None = None,
    days_left: int | None = None,
) -> str:
    until = format_premium_until(until_iso, locale)
    if hours_left == 24:
        if locale == "ru":
            return format_screen_body(
                f"⏳ Через 24 часа заканчивается Premium (до {until}).\n\n"
                "Если чувствуешь пользу от гороскопов, полной карты и лунного календаря — можно мягко продлить сейчас,"
                " чтобы доступ не прерывался."
            )
        return format_screen_body(
            f"⏳ Premium expires in 24 hours (until {until}).\n\n"
            "If the readings and tools feel helpful, you can gently renew now so access continues without a break."
        )
    if locale == "ru":
        if days_left == 0:
            return format_screen_body(
                f"⏳ Premium заканчивается сегодня ({until}).\n\n"
                "Продли сейчас — неделя/месяц, полная карта и лунный календарь."
            )
        if days_left == 1:
            return format_screen_body(
                f"⏳ Premium заканчивается завтра ({until}).\n\n"
                "Продли сейчас — неделя/месяц, полная карта и лунный календарь."
            )
        return format_screen_body(
            f"⏳ Premium заканчивается через {days_left} дня ({until}).\n\n"
            "Продли заранее, чтобы не потерять доступ."
        )
    if days_left == 1:
        return format_screen_body(
            f"⏳ Premium expires tomorrow ({until}).\n\n"
            "Renew now to keep week/month horoscopes, full chart, and moon calendar."
        )
    if days_left == 0:
        return format_screen_body(
            f"⏳ Premium expires today ({until}).\n\n"
            "Renew now to keep week/month horoscopes, full chart, and moon calendar."
        )
    return format_screen_body(
        f"⏳ Premium expires in {days_left} days ({until}).\n\n"
        "Renew early so you don't lose access."
    )


async def notify_admins_purchase(
    bot: Bot,
    *,
    admin_ids: tuple[int, ...],
    buyer_id: int,
    buyer_username: str | None,
    buyer_first_name: str | None,
    currency: PayCurrency,
    telegram_currency: str,
    invoice_amount: int,
    until_iso: str,
) -> None:
    if not admin_ids:
        return
    display = f"@{buyer_username}" if buyer_username else (buyer_first_name or str(buyer_id))
    amount = format_payment_amount(currency, invoice_amount, telegram_currency)
    until = format_premium_until(until_iso, "ru")
    text = (
        "💰 Premium оплачен\n\n"
        f"Пользователь: {display}\n"
        f"ID: {buyer_id}\n"
        f"Сумма: {amount}\n"
        f"Premium до: {until}"
    )
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass
