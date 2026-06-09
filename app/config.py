import os
from dataclasses import dataclass

from dotenv import load_dotenv

from app.premium import (
    DEFAULT_PREMIUM_PRICE_RUB,
    DEFAULT_PREMIUM_PRICE_STARS,
    DEFAULT_PREMIUM_PRICE_USD_CENTS,
    DEFAULT_PREMIUM_TRIAL_DAYS,
)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: str = "astro_bot.db"
    proxy_url: str | None = None
    admin_ids: tuple[int, ...] = ()
    premium_price_stars: int = DEFAULT_PREMIUM_PRICE_STARS
    enable_payments: bool = False
    payment_provider_token: str | None = None
    payment_provider_token_usd: str | None = None
    premium_price_rub: int = DEFAULT_PREMIUM_PRICE_RUB
    premium_price_usd_cents: int = DEFAULT_PREMIUM_PRICE_USD_CENTS
    premium_trial_days: int = DEFAULT_PREMIUM_TRIAL_DAYS
    feedback_username: str | None = None


def load_settings() -> Settings:
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set. Put it in .env file.")
    proxy_url = os.getenv("BOT_PROXY", "").strip() or None
    if proxy_url is None:
        proxy_url = os.getenv("HTTPS_PROXY", "").strip() or None
    if proxy_url is None:
        proxy_url = os.getenv("HTTP_PROXY", "").strip() or None
    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
    admin_ids: tuple[int, ...] = ()
    if admin_ids_raw:
        ids = []
        for part in admin_ids_raw.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        admin_ids = tuple(ids)

    premium_price_stars_raw = os.getenv("PREMIUM_PRICE_STARS", str(DEFAULT_PREMIUM_PRICE_STARS)).strip()
    premium_price_stars = (
        int(premium_price_stars_raw)
        if premium_price_stars_raw.isdigit()
        else DEFAULT_PREMIUM_PRICE_STARS
    )
    enable_payments_raw = os.getenv("ENABLE_PAYMENTS", "false").strip().lower()
    enable_payments = enable_payments_raw in {"1", "true", "yes", "on"}

    feedback_username_raw = os.getenv("FEEDBACK_USERNAME", "").strip().lstrip("@")
    feedback_username = feedback_username_raw or None

    payment_provider_token_raw = os.getenv("PAYMENT_PROVIDER_TOKEN", "").strip()
    payment_provider_token = payment_provider_token_raw or None
    payment_provider_token_usd_raw = os.getenv("PAYMENT_PROVIDER_TOKEN_USD", "").strip()
    payment_provider_token_usd = payment_provider_token_usd_raw or None

    premium_price_rub_raw = os.getenv("PREMIUM_PRICE_RUB", str(DEFAULT_PREMIUM_PRICE_RUB)).strip()
    premium_price_rub = (
        int(premium_price_rub_raw) if premium_price_rub_raw.isdigit() else DEFAULT_PREMIUM_PRICE_RUB
    )

    premium_price_usd_raw = os.getenv("PREMIUM_PRICE_USD", str(DEFAULT_PREMIUM_PRICE_USD_CENTS)).strip()
    premium_price_usd_cents = (
        int(premium_price_usd_raw)
        if premium_price_usd_raw.isdigit()
        else DEFAULT_PREMIUM_PRICE_USD_CENTS
    )

    premium_trial_days_raw = os.getenv("PREMIUM_TRIAL_DAYS", str(DEFAULT_PREMIUM_TRIAL_DAYS)).strip()
    premium_trial_days = (
        int(premium_trial_days_raw)
        if premium_trial_days_raw.isdigit()
        else DEFAULT_PREMIUM_TRIAL_DAYS
    )

    return Settings(
        bot_token=bot_token,
        proxy_url=proxy_url,
        admin_ids=admin_ids,
        premium_price_stars=premium_price_stars,
        enable_payments=enable_payments,
        payment_provider_token=payment_provider_token,
        payment_provider_token_usd=payment_provider_token_usd,
        premium_price_rub=premium_price_rub,
        premium_price_usd_cents=premium_price_usd_cents,
        premium_trial_days=premium_trial_days,
        feedback_username=feedback_username,
    )
