from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.config import Settings
from app.premium import (
    DEFAULT_PREMIUM_PRICE_RUB,
    DEFAULT_PREMIUM_PRICE_STARS,
)


class PayCurrency(StrEnum):
    STARS = "stars"
    RUB = "rub"
    USD = "usd"


@dataclass(frozen=True)
class PremiumPaymentOption:
    currency: PayCurrency
    invoice_amount: int
    telegram_currency: str
    provider_token: str
    button_ru: str
    button_en: str
    panel_ru: str
    panel_en: str


def premium_payload(currency: PayCurrency) -> str:
    return f"premium_30d:{currency.value}"


def parse_premium_payload(payload: str) -> PayCurrency | None:
    if payload == "premium_30d":
        return PayCurrency.STARS
    if not payload.startswith("premium_30d:"):
        return None
    suffix = payload.split(":", 1)[1]
    try:
        return PayCurrency(suffix)
    except ValueError:
        return None


def available_payment_options(settings: Settings) -> tuple[PremiumPaymentOption, ...]:
    if not settings.enable_payments:
        return ()

    options: list[PremiumPaymentOption] = []

    if settings.premium_price_rub > 0:
        rub_label = f"{settings.premium_price_rub} ₽"
        options.append(
            PremiumPaymentOption(
                currency=PayCurrency.RUB,
                invoice_amount=settings.premium_price_rub * 100,
                telegram_currency="RUB",
                provider_token=settings.payment_provider_token or "",
                button_ru=f"💳 {rub_label} · ЮKassa",
                button_en=f"💳 {rub_label} · card",
                panel_ru=f"💳 Карта / СБП · {rub_label}",
                panel_en=f"💳 Card · {rub_label}",
            )
        )

    if settings.premium_price_stars > 0:
        options.append(
            PremiumPaymentOption(
                currency=PayCurrency.STARS,
                invoice_amount=settings.premium_price_stars,
                telegram_currency="XTR",
                provider_token="",
                button_ru=f"⭐ {settings.premium_price_stars} Stars",
                button_en=f"⭐ {settings.premium_price_stars} Stars",
                panel_ru=f"⭐ {settings.premium_price_stars} Stars",
                panel_en=f"⭐ {settings.premium_price_stars} Stars",
            )
        )

    return tuple(options)


def get_payment_option(settings: Settings, currency: PayCurrency) -> PremiumPaymentOption | None:
    for option in available_payment_options(settings):
        if option.currency != currency:
            continue
        if option.currency == PayCurrency.STARS:
            return option
        if option.provider_token:
            return option
    return None
