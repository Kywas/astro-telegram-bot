import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: str = "astro_bot.db"
    proxy_url: str | None = None
    admin_ids: tuple[int, ...] = ()
    premium_price_stars: int = 100
    enable_payments: bool = False
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

    premium_price_stars_raw = os.getenv("PREMIUM_PRICE_STARS", "100").strip()
    premium_price_stars = int(premium_price_stars_raw) if premium_price_stars_raw.isdigit() else 100
    enable_payments_raw = os.getenv("ENABLE_PAYMENTS", "false").strip().lower()
    enable_payments = enable_payments_raw in {"1", "true", "yes", "on"}

    feedback_username_raw = os.getenv("FEEDBACK_USERNAME", "").strip().lstrip("@")
    feedback_username = feedback_username_raw or None

    return Settings(
        bot_token=bot_token,
        proxy_url=proxy_url,
        admin_ids=admin_ids,
        premium_price_stars=premium_price_stars,
        enable_payments=enable_payments,
        feedback_username=feedback_username,
    )
