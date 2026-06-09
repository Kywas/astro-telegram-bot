"""Quick offline checks for payment/premium helpers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.payments import PayCurrency, available_payment_options, parse_premium_payload, premium_payload
from app.premium import DEFAULT_PREMIUM_TRIAL_DAYS, extend_premium_until, is_premium_active
from app.premium_lifecycle import format_payment_amount


def test_payment_payloads() -> None:
    assert parse_premium_payload("premium_30d") == PayCurrency.STARS
    assert parse_premium_payload("premium_30d:rub") == PayCurrency.RUB
    assert parse_premium_payload("premium_30d:usd") == PayCurrency.USD
    assert parse_premium_payload("bad") is None
    assert premium_payload(PayCurrency.RUB) == "premium_30d:rub"


def test_payment_options() -> None:
    settings = Settings(
        bot_token="x",
        enable_payments=True,
        payment_provider_token="prov",
        premium_price_stars=100,
        premium_price_rub=199,
        premium_price_usd_cents=300,
    )
    options = available_payment_options(settings)
    currencies = {opt.currency for opt in options}
    assert currencies == {PayCurrency.STARS, PayCurrency.RUB, PayCurrency.USD}
    assert format_payment_amount(PayCurrency.RUB, 19900, "RUB") == "199 ₽"
    assert format_payment_amount(PayCurrency.USD, 300, "USD") == "$3.00"


def test_referral_profile_requirements() -> None:
    from app.database import UserProfile
    from datetime import date

    complete = UserProfile(
        user_id=1,
        username=None,
        first_name=None,
        birth_date=date(2000, 1, 1),
        birth_time=None,
        city="Moscow",
        birth_lat=None,
        birth_lon=None,
        birth_timezone=None,
        sign="Aries",
        language="ru",
        gender=None,
        relationship_status="single",
        goal="balance",
        mood_score=None,
        mood_updated_at=None,
        daily_enabled=False,
        daily_time="09:00",
        timezone="UTC",
        evening_enabled=True,
        evening_time="20:00",
        mood_streak=0,
        last_mood_date=None,
        lunar_notify_enabled=True,
        premium_until=None,
        trial_used=False,
        natal_mode="full",
        ref_code=None,
        referrer_id=2,
        ref_bonus_count=0,
    )
    assert complete.relationship_status and complete.goal and complete.sign


def test_premium_dates() -> None:
    until = extend_premium_until(None, 7)
    assert is_premium_active(until.isoformat())


def test_start_source_payloads() -> None:
    from app.start_payload import parse_ref_code_from_start, parse_start_source_from_start

    assert parse_start_source_from_start("src_vk") == "vk"
    assert parse_start_source_from_start("src_tg_ads") == "tg_ads"
    assert parse_start_source_from_start("ref_abc") is None
    assert parse_start_source_from_start("src_") is None
    assert parse_start_source_from_start("src_bad-chars") is None
    assert parse_ref_code_from_start("ref_abc123") == "abc123"


def main() -> None:
    test_payment_payloads()
    test_payment_options()
    test_referral_profile_requirements()
    test_premium_dates()
    test_start_source_payloads()
    print(f"OK (trial default={DEFAULT_PREMIUM_TRIAL_DAYS}d)")


if __name__ == "__main__":
    main()
