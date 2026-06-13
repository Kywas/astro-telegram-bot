"""Premium menu text and checkout helpers."""
from aiogram import Bot
from aiogram.types import LabeledPrice, Message

from app.bot_context import db, settings
from app.i18n import t
from app.keyboards import breadcrumb
from app.payments import (
    PayCurrency,
    available_payment_options,
    get_payment_option,
    parse_premium_payload,
    premium_payload,
)
from app.premium import PREMIUM_PERIOD_DAYS, format_premium_until, is_premium_active
from app.premium_lifecycle import notify_admins_purchase
from app.text_format import format_screen_body, p, screen_page

async def _premium_panel_text(user_id: int, locale: str) -> str:
    profile = await db.get_user(user_id)
    active = bool(profile and is_premium_active(profile.premium_until))
    if active and profile:
        status_text = t(
            locale,
            "premium_active",
            until=format_premium_until(profile.premium_until, locale),
        )
    else:
        status_text = t(locale, "premium_inactive")
    prices_text = _premium_prices_text(locale)
    if prices_text:
        status_text = p(status_text, format_screen_body(prices_text))
    return screen_page(
        breadcrumb(locale, t(locale, "premium_menu_title")),
        status_text,
        t(locale, "premium_features"),
    )


def _premium_prices_text(locale: str) -> str:
    options = available_payment_options(settings)
    if not options:
        return ""
    lines = [t(locale, "premium_prices_header", days=str(PREMIUM_PERIOD_DAYS))]
    for option in options:
        lines.append(option.panel_ru if locale == "ru" else option.panel_en)
    return "\n".join(lines)


def _parse_pay_currency(raw: str) -> PayCurrency | None:
    try:
        return PayCurrency(raw)
    except ValueError:
        return None


async def _send_premium_invoice(
    *,
    bot: Bot,
    chat_id: int,
    user_id: int,
    locale: str,
    currency: PayCurrency,
) -> bool:
    option = get_payment_option(settings, currency)
    if option is None:
        return False
    title, description = _premium_invoice_copy(locale)
    try:
        await bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=premium_payload(currency),
            provider_token=option.provider_token,
            currency=option.telegram_currency,
            prices=[LabeledPrice(label=f"Premium {PREMIUM_PERIOD_DAYS}d", amount=option.invoice_amount)],
        )
        await db.log_event(user_id, f"premium_invoice_sent:{currency.value}")
        return True
    except Exception:
        await db.log_event(user_id, f"premium_invoice_failed:{currency.value}")
        return False


async def _start_premium_checkout(
    *,
    bot: Bot,
    chat_id: int,
    user_id: int,
    locale: str,
    currency: PayCurrency | None = None,
) -> bool | None:
    options = available_payment_options(settings)
    if not options:
        return None
    if currency is None:
        if len(options) == 1:
            currency = options[0].currency
        else:
            return False
    return await _send_premium_invoice(
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
        locale=locale,
        currency=currency,
    )


def _premium_invoice_copy(locale: str) -> tuple[str, str]:
    if locale == "ru":
        return (
            f"AstroPulse Premium · {PREMIUM_PERIOD_DAYS} дн.",
            "Натальная карта, неделя/месяц, совместимость, лунный календарь, напоминания за 7 дней.",
        )
    return (
        f"AstroPulse Premium · {PREMIUM_PERIOD_DAYS} days",
        "Full natal chart, week/month horoscope, compatibility, moon calendar, 7-day lunar alerts.",
    )

