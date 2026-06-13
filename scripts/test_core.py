"""Quick offline checks for payment/premium helpers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.payments import PayCurrency, available_payment_options, get_payment_option, parse_premium_payload, premium_payload
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
    assert currencies == {PayCurrency.STARS, PayCurrency.RUB}
    assert options[0].currency == PayCurrency.RUB
    assert "ЮKassa" in options[0].button_ru
    assert format_payment_amount(PayCurrency.RUB, 19900, "RUB") == "199 ₽"

    rub_only_ui = Settings(
        bot_token="x",
        enable_payments=True,
        premium_price_rub=199,
    )
    rub_options = available_payment_options(rub_only_ui)
    assert len(rub_options) == 1
    assert rub_options[0].currency == PayCurrency.RUB
    assert get_payment_option(rub_only_ui, PayCurrency.RUB) is None


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
        moon_focus="practices",
        moon_style="terms",
        horoscope_style="terms",
        compat_style="terms",
        premium_until=None,
        trial_used=False,
        natal_mode="full",
        natal_style="terms",
        natal_qa_free_used=False,
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


def test_stats_keys() -> None:
    import asyncio
    import tempfile
    from pathlib import Path

    from app.database import Database

    async def run() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "test.db")
            database = Database(db_path)
            await database.init()
            stats = await database.get_stats()
            for key in (
                "total_users",
                "new_users_7d",
                "new_users_30d",
                "premium_users",
                "referrals_7d",
                "referrals_30d",
                "errors_24h",
                "total_errors",
            ):
                assert key in stats

    asyncio.run(run())


def test_sun_sign_compat() -> None:
    from app.sun_sign_compat import SunSignKind, analyze_sun_sign_compat, format_sun_sign_compat_section

    assert analyze_sun_sign_compat("Aries", "Aries").kind == SunSignKind.SAME_SIGN
    assert analyze_sun_sign_compat("Aries", "Libra").kind == SunSignKind.OPPOSITE
    assert analyze_sun_sign_compat("Aries", "Leo").kind == SunSignKind.SAME_ELEMENT
    assert analyze_sun_sign_compat("Aries", "Gemini").kind == SunSignKind.COMPATIBLE_ELEMENTS
    assert analyze_sun_sign_compat("Aries", "Cancer").kind == SunSignKind.CHALLENGING_ELEMENTS
    text = format_sun_sign_compat_section("ru", analyze_sun_sign_compat("Taurus", "Scorpio"))
    assert "Противоположные" in text
    assert "Земля" in text and "Вода" in text


def test_synastry_style() -> None:
    from types import SimpleNamespace

    from app.synastry_style import (
        apply_synastry_style,
        format_cross_link_line,
        resolve_compat_style,
        use_synastry_terms,
    )

    profile = SimpleNamespace(compat_style="plain", horoscope_style="terms", natal_style="terms")
    assert resolve_compat_style(profile) == "plain"

    terms_line = format_cross_link_line(
        "ru", "MOON", "VENUS", "trine", "сильная поддержка", 1.0, "terms"
    )
    plain_line = format_cross_link_line(
        "ru", "MOON", "VENUS", "trine", "сильная поддержка", 1.0, "plain"
    )
    assert "трин" in terms_line or "Луна" in terms_line
    assert "трин" not in plain_line
    assert "эмоции" in plain_line or "забота" in plain_line
    assert terms_line != plain_line
    assert not use_synastry_terms("plain")
    assert use_synastry_terms("terms")
    assert "Простым языком" not in apply_synastry_style(terms_line, "ru", "terms")


def test_horoscope_style() -> None:
    from datetime import date, time
    from types import SimpleNamespace

    from app.horoscope import generate_horoscope, resolve_horoscope_style

    profile = SimpleNamespace(
        horoscope_style="plain",
        natal_style="terms",
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        city="Moscow",
        birth_lat=55.75,
        birth_lon=37.62,
        birth_timezone="Europe/Moscow",
        timezone="Europe/Moscow",
        relationship_status=None,
        user_id=None,
    )
    assert resolve_horoscope_style(profile) == "plain"

    common = dict(
        sign="Taurus",
        locale="ru",
        period="day",
        for_date=date(2026, 6, 12),
        profile=profile,
    )
    terms_text = generate_horoscope(**common, style="terms")
    plain_text = generate_horoscope(**common, style="plain")

    assert terms_text != plain_text
    assert "простым языком" in plain_text.lower()
    assert any(word in terms_text for word in ("секстиль", "оппозиция", "трин", "квадрат"))
    assert not any(word in plain_text for word in ("секстиль", "оппозиция", "трин", "квадрат"))
    assert "транзит" not in plain_text.lower()
    assert "транзит" in terms_text.lower() or "ASC" in terms_text


def test_lucky_time_varies_by_day() -> None:
    from datetime import date, time, timedelta

    from app.astro_engine import build_astro_forecast

    birth_date = date(1990, 5, 15)
    lucky_times: list[str] = []
    for offset in range(7):
        forecast = build_astro_forecast(
            birth_date=birth_date,
            birth_time=time(14, 30),
            city="Moscow",
            timezone_name="Europe/Moscow",
            for_date=date(2026, 6, 12) + timedelta(days=offset),
            period="day",
            locale="ru",
        )
        assert forecast is not None
        lucky_times.append(forecast.lucky_time)
        assert "07:00-22:00" not in forecast.lucky_time
        assert "08:00-22:00" not in forecast.lucky_time

    assert len(set(lucky_times)) >= 3


def test_synastry_asc() -> None:
    from app.synastry_asc import (
        AngleMatchKind,
        analyze_asc_dsc_synastry,
        asc_dsc_score_delta,
        format_synastry_step2_section,
    )

    # Aries ASC (0°), Libra DSC (180°); partner with Libra ASC (180°), Aries DSC (0°)
    user_cusps = [i * 30.0 for i in range(12)]
    partner_cusps = [(i * 30.0 + 180.0) % 360.0 for i in range(12)]

    analysis = analyze_asc_dsc_synastry(user_cusps, partner_cusps)
    assert analysis.full_analysis
    assert analysis.user_asc_sign == "Aries"
    assert analysis.user_dsc_sign == "Libra"
    assert analysis.partner_asc_sign == "Libra"
    assert analysis.partner_dsc_sign == "Aries"
    assert AngleMatchKind.USER_ASC_PARTNER_DSC in analysis.matches
    assert AngleMatchKind.PARTNER_ASC_USER_DSC in analysis.matches
    assert AngleMatchKind.OPPOSITE_ASC in analysis.matches
    assert asc_dsc_score_delta(analysis) > 0

    text = format_synastry_step2_section("ru", analysis, style="terms")
    assert "Шаг 2" in text
    assert "ASC" in text and "DSC" in text
    plain = format_synastry_step2_section("ru", analysis, style="plain")
    assert plain != text
    assert "ASC" not in plain or "образ" in plain

    same_asc = analyze_asc_dsc_synastry(user_cusps, user_cusps)
    assert AngleMatchKind.SAME_ASC in same_asc.matches


def test_synastry_composite() -> None:
    from datetime import date, time

    from app.astro_engine import _natal_chart
    from app.synastry_composite import (
        build_composite_analysis,
        composite_score_delta,
        format_synastry_composite_section,
        midpoint_longitude,
    )

    assert midpoint_longitude(350.0, 10.0) == 0.0

    user_chart, _, user_cusps = _natal_chart(
        date(1990, 3, 21), time(12, 0), "Moscow", "Europe/Moscow"
    )
    partner_chart, _, partner_cusps = _natal_chart(
        date(1995, 8, 20), time(18, 30), "Moscow", "Europe/Moscow"
    )
    analysis = build_composite_analysis(
        user_chart,
        partner_chart,
        user_cusps,
        partner_cusps,
        user_has_moon=True,
        partner_has_moon=True,
    )
    assert analysis.has_houses
    assert "SUN" in analysis.planets
    text = format_synastry_composite_section("ru", analysis, style="terms")
    assert "Композитная карта" in text
    assert "Солнце композита" in text
    assert "угловых домах" in text
    plain = format_synastry_composite_section("ru", analysis, style="plain")
    assert plain != text
    assert composite_score_delta(analysis) >= 0


def test_synastry_progressions() -> None:
    from datetime import date, time

    from app.astro_engine import _natal_julian_day, _natal_chart
    from app.synastry_progressions import (
        analyze_synastry_progressions,
        format_synastry_progressions_section,
        progressions_score_delta,
    )

    user_chart, _, _ = _natal_chart(date(1990, 3, 21), time(12, 0), "Moscow", "Europe/Moscow")
    partner_chart, _, _ = _natal_chart(
        date(1995, 8, 20), time(18, 30), "Moscow", "Europe/Moscow"
    )
    user_jd = _natal_julian_day(date(1990, 3, 21), time(12, 0), "Europe/Moscow")
    partner_jd = _natal_julian_day(date(1995, 8, 20), time(18, 30), "Europe/Moscow")
    ref = date(2026, 6, 12)

    analysis = analyze_synastry_progressions(
        user_birth_date=date(1990, 3, 21),
        partner_birth_date=date(1995, 8, 20),
        user_julian_day=user_jd,
        partner_julian_day=partner_jd,
        user_has_moon=True,
        partner_has_moon=True,
        reference_date=ref,
    )
    assert analysis.user_age_years > 30
    text = format_synastry_progressions_section("ru", analysis, style="terms")
    assert "Временные дирекции" in text
    assert "прогрессивн" in text.lower()
    assert analysis.moon_phases
    plain = format_synastry_progressions_section("ru", analysis, style="plain")
    assert plain != text
    assert isinstance(progressions_score_delta(analysis), int)


def test_synastry_fictitious() -> None:
    from datetime import date, time

    from app.astro_engine import _natal_chart, _natal_julian_day
    from app.synastry_fictitious import (
        analyze_fictitious_synastry,
        fictitious_score_delta,
        format_synastry_fictitious_section,
    )

    user_chart, _, _ = _natal_chart(date(1990, 3, 21), time(12, 0), "Moscow", "Europe/Moscow")
    partner_chart, _, _ = _natal_chart(
        date(1995, 8, 20), time(18, 30), "Moscow", "Europe/Moscow"
    )
    user_jd = _natal_julian_day(date(1990, 3, 21), time(12, 0), "Europe/Moscow")
    partner_jd = _natal_julian_day(date(1995, 8, 20), time(18, 30), "Europe/Moscow")

    analysis = analyze_fictitious_synastry(
        user_chart,
        partner_chart,
        user_julian_day=user_jd,
        partner_julian_day=partner_jd,
        user_has_moon=True,
        partner_has_moon=True,
    )
    assert analysis.lilith_links or analysis.selena_links
    text = format_synastry_fictitious_section("ru", analysis, style="terms")
    assert "Лилит" in text
    assert "Селена" in text
    plain = format_synastry_fictitious_section("ru", analysis, style="plain")
    assert plain != text
    assert isinstance(fictitious_score_delta(analysis), int)


def test_synastry_tarot() -> None:
    from datetime import date

    from app.synastry_tarot import (
        POSITION_KEYS,
        analyze_couple_tarot_spread,
        format_synastry_tarot_section,
        tarot_score_delta,
    )

    user_date = date(1990, 3, 15)
    partner_date = date(1995, 8, 20)

    spread_a = analyze_couple_tarot_spread(user_date, partner_date, locale="ru")
    spread_b = analyze_couple_tarot_spread(user_date, partner_date, locale="ru")
    assert spread_a.cards == spread_b.cards
    assert len(spread_a.cards) == len(POSITION_KEYS)
    assert {card.position for card in spread_a.cards} == set(POSITION_KEYS)
    assert all(card.name and card.reading for card in spread_a.cards)
    assert isinstance(tarot_score_delta(spread_a), int)

    text = format_synastry_tarot_section("ru", spread_a)
    assert "Таро-расклад «Совместимость пары»" in text
    assert "Прошлое — что привело вас друг к другу" in text
    assert "Совет — как улучшить отношения" in text

    plain = format_synastry_tarot_section("ru", spread_a, style="plain")
    assert "Карты вашей пары" in plain


def test_synastry_numerology() -> None:
    from datetime import date

    from app.synastry_numerology import (
        analyze_relationship_numerology,
        format_synastry_numerology_section,
        life_path_number,
        numerology_score_delta,
    )

    user_date = date(1990, 3, 15)
    partner_date = date(1995, 8, 20)

    user_path, user_raw = life_path_number(user_date)
    assert user_raw == 28
    assert user_path == 1

    analysis = analyze_relationship_numerology(user_date, partner_date)
    assert analysis.user_life_path == 1
    assert analysis.partner_life_path == 7
    assert analysis.compatibility_number == 8
    assert isinstance(numerology_score_delta(analysis), int)

    text = format_synastry_numerology_section(
        "ru",
        analysis,
        user_birth_date=user_date,
        partner_birth_date=partner_date,
    )
    assert "Нумерология отношений" in text
    assert "28→10→1" in text
    assert "Число совместимости" in text
    assert "Интерпретация:" in text
    assert "риск меркантильности" in text

    plain = format_synastry_numerology_section(
        "ru",
        analysis,
        user_birth_date=user_date,
        partner_birth_date=partner_date,
        style="plain",
    )
    assert "Числа вашей пары" in plain
    assert "28→10→1" not in plain


def test_synastry_summary() -> None:
    from datetime import date

    from app.synastry_numerology import analyze_relationship_numerology
    from app.synastry_tarot import analyze_couple_tarot_spread
    from app.synastry_progressions import analyze_synastry_progressions
    from app.synastry_composite import build_composite_analysis
    from app.synastry_asc import analyze_asc_dsc_synastry
    from app.synastry_fictitious import analyze_fictitious_synastry
    from app.synastry_elements import analyze_element_balance
    from app.synastry_houses import build_house_overlay
    from app.synastry_karma import analyze_karmic_synastry
    from app.synastry_moon_venus import analyze_moon_venus_links
    from app.synastry_seals import analyze_synastry_seals
    from app.synastry_summary import (
        CompatibilityLevel,
        build_synastry_summary,
        classify_compatibility_level,
        format_synastry_step10_section,
    )
    from app.synastry_transits import analyze_synastry_transits

    user = {"SUN": 0.0, "MOON": 30.0, "MERCURY": 60.0, "VENUS": 90.0, "MARS": 120.0}
    partner = {"SUN": 180.0, "MOON": 210.0, "MERCURY": 240.0, "VENUS": 270.0, "MARS": 300.0}
    hits = [(1.0, "MOON", "VENUS", "trine"), (2.0, "JUPITER", "MOON", "trine")]
    seals = analyze_synastry_seals(hits)
    moon_venus = analyze_moon_venus_links(hits, user_has_moon=True, partner_has_moon=True)
    element_balance = analyze_element_balance(user, partner)
    summary = build_synastry_summary(
        locale="ru",
        score=78,
        hits=hits,
        user_sign_key="Aries",
        partner_sign_key="Libra",
        seals=seals,
        asc_dsc=analyze_asc_dsc_synastry(None, None),
        composite=build_composite_analysis(
            user,
            partner,
            None,
            None,
            user_has_moon=True,
            partner_has_moon=True,
        ),
        progressions=analyze_synastry_progressions(
            user_birth_date=date(1990, 3, 21),
            partner_birth_date=date(1995, 8, 20),
            user_julian_day=2448027.0,
            partner_julian_day=2448027.0,
            user_has_moon=True,
            partner_has_moon=True,
            reference_date=date(2026, 6, 12),
        ),
        numerology=analyze_relationship_numerology(
            date(1990, 3, 21),
            date(1995, 8, 20),
        ),
        tarot=analyze_couple_tarot_spread(
            date(1990, 3, 21),
            date(1995, 8, 20),
            locale="ru",
        ),
        house_overlay=build_house_overlay(user, partner, None, None),
        element_balance=element_balance,
        moon_venus=moon_venus,
        karma=analyze_karmic_synastry(
            user,
            partner,
            user_julian_day=2448027.0,
            partner_julian_day=2448027.0,
            user_has_moon=True,
            partner_has_moon=True,
        ),
        fictitious=analyze_fictitious_synastry(
            user,
            partner,
            user_julian_day=2448027.0,
            partner_julian_day=2448027.0,
            user_has_moon=True,
            partner_has_moon=True,
        ),
        transits=analyze_synastry_transits(
            user,
            partner,
            timezone_name="Europe/Moscow",
            user_has_moon=True,
            partner_has_moon=True,
            reference_date=date(2026, 6, 12),
        ),
        user_has_moon=True,
        partner_has_moon=True,
    )
    text = format_synastry_step10_section("ru", summary)
    assert "Шаг 10" in text
    assert "Суммарный баланс" in text
    assert "Базовый уровень" in text
    assert "Эзотерический уровень" in text
    assert "Интерпретация" in text
    assert "Овен + Весы" in text
    assert any(row.criterion == "Луна↔Венера" for row in summary.rows)
    assert any(row.criterion == "Нумерология" for row in summary.rows)
    assert any(row.criterion == "Таро" for row in summary.rows)
    assert any(row.tier.value == "basic" for row in summary.rows)
    assert summary.net_balance == sum(row.points for row in summary.rows)
    assert len(summary.tier_totals) == 4
    assert summary.level in CompatibilityLevel
    high_hits = [
        (1.0, "SUN", "MOON", "trine"),
        (1.2, "VENUS", "MARS", "sextile"),
        (1.5, "JUPITER", "SUN", "trine"),
        (2.0, "MERCURY", "MERCURY", "trine"),
    ]
    assert (
        classify_compatibility_level(
            high_hits,
            seals=analyze_synastry_seals(high_hits),
            element_balance=element_balance,
            moon_venus=analyze_moon_venus_links(high_hits, user_has_moon=True, partner_has_moon=True),
            user_has_moon=True,
            partner_has_moon=True,
        )
        in {CompatibilityLevel.HIGH, CompatibilityLevel.MODERATE}
    )


def test_synastry_transits() -> None:
    from datetime import date

    from app.synastry_transits import analyze_synastry_transits, format_synastry_step9_section

    user = {"SUN": 0.0, "MOON": 30.0, "MERCURY": 60.0, "VENUS": 90.0, "MARS": 120.0}
    partner = {"SUN": 45.0, "MOON": 75.0, "MERCURY": 105.0, "VENUS": 135.0, "MARS": 165.0}
    analysis = analyze_synastry_transits(
        user,
        partner,
        timezone_name="Europe/Moscow",
        user_has_moon=True,
        partner_has_moon=True,
        reference_date=date(2026, 6, 12),
    )
    text = format_synastry_step9_section("ru", analysis)
    assert "Шаг 9" in text
    assert analysis.forecast_end > analysis.forecast_start


def test_synastry_karma() -> None:
    from app.synastry_karma import analyze_karmic_synastry, karmic_score_delta

    user = {"SUN": 0.0, "MOON": 30.0, "MERCURY": 60.0, "VENUS": 90.0, "MARS": 120.0}
    partner = {"SUN": 5.0, "MOON": 35.0, "MERCURY": 65.0, "VENUS": 95.0, "MARS": 125.0}
    analysis = analyze_karmic_synastry(
        user,
        partner,
        user_julian_day=2448027.0,
        partner_julian_day=2448027.0,
        user_has_moon=True,
        partner_has_moon=True,
    )
    assert isinstance(analysis.karmic_tasks, tuple)
    assert karmic_score_delta(analysis) >= 0


def test_synastry_moon_venus() -> None:
    from app.synastry_moon_venus import analyze_moon_venus_links, moon_venus_score_delta

    hits = [
        (1.0, "MOON", "VENUS", "trine"),
        (2.5, "VENUS", "MOON", "square"),
    ]
    analysis = analyze_moon_venus_links(hits, user_has_moon=True, partner_has_moon=True)
    assert analysis.best_harmonious is not None
    assert analysis.best_tense is not None
    assert moon_venus_score_delta(analysis) == 2


def test_synastry_elements() -> None:
    from app.synastry_elements import analyze_element_balance, element_score_delta

    # Mostly fire signs (Aries 0°, Leo 120°, etc.)
    user = {"SUN": 10.0, "MOON": 130.0, "MARS": 250.0}
    partner = {"SUN": 60.0, "MOON": 200.0, "VENUS": 300.0}
    balance = analyze_element_balance(user, partner)
    assert balance.user.counts["fire"] >= 2
    assert element_score_delta(balance) != 0


def test_synastry_houses() -> None:
    from app.synastry_houses import (
        ANGULAR_HOUSES,
        FOCUS_HOUSES,
        build_house_overlay,
        format_synastry_step5_section,
        house_score_delta,
        planet_house,
    )

    assert 1 in FOCUS_HOUSES and 10 in FOCUS_HOUSES
    assert ANGULAR_HOUSES == frozenset({1, 4, 7, 10})

    cusps = [i * 30.0 for i in range(12)]
    assert planet_house(15.0, cusps) == 1
    assert planet_house(95.0, cusps) == 4

    overlay = build_house_overlay(
        {"MOON": 15.0, "SUN": 100.0, "MERCURY": 65.0},
        {"VENUS": 200.0, "MARS": 15.0},
        cusps,
        cusps,
    )
    assert overlay.full_overlay
    assert "MOON" in overlay.user_in_partner[1]
    assert overlay.angular_placements() >= 1
    assert house_score_delta(overlay) >= 1

    text = format_synastry_step5_section("ru", overlay, style="terms")
    assert "Шаг 5" in text
    assert "Синастрия по домам" in text
    assert "1‑й дом" in text
    assert "10‑й дом" in text
    assert "угловых домах" in text


def test_synastry_seals() -> None:
    from app.synastry_seals import analyze_synastry_seals, seal_score_delta

    hits = [
        (0.9, "JUPITER", "SUN", "trine"),
        (1.1, "SATURN", "MOON", "square"),
    ]
    seals = analyze_synastry_seals(hits)
    assert seals.best_happiness is not None
    assert seals.best_unhappiness is not None
    assert seal_score_delta(seals) == 0


def test_synastry_overlay() -> None:
    from app.synastry_overlay import KEY_PAIRS, find_best_key_pair_hit

    hits = [
        (1.2, "SUN", "MOON", "trine"),
        (0.8, "VENUS", "MARS", "sextile"),
        (2.0, "MERCURY", "MERCURY", "square"),
    ]
    sun_moon = find_best_key_pair_hit(hits, KEY_PAIRS[0])
    assert sun_moon is not None and sun_moon[3] == "trine"
    mercury = find_best_key_pair_hit(hits, KEY_PAIRS[2])
    assert mercury is not None and mercury[3] == "square"

    from datetime import date
    from app.synastry import build_synastry

    result = build_synastry(
        "ru",
        "Aries",
        date(1995, 8, 20),
        "love",
        user_birth_date=date(1990, 3, 21),
        user_birth_time=__import__("datetime").time(12, 0),
        partner_birth_time=__import__("datetime").time(18, 30),
    )
    assert "Шаг 1" in result.details
    assert "Шаг 2" in result.details
    assert "Шаг 3" in result.details
    assert "Лилит" in result.details or "фиктивн" in result.details.lower()
    assert "Композитная карта" in result.details or "композит" in result.details.lower()
    assert "Временные дирекции" in result.details or "прогресс" in result.details.lower()
    assert "Нумерология" in result.details or "Числа вашей пары" in result.details
    assert "Таро" in result.details or "Карты вашей пары" in result.details
    assert "Шаг 4" in result.details
    assert "Шаг 5" in result.details
    assert "Шаг 6" in result.details
    assert "Шаг 7" in result.details
    assert "Шаг 8" in result.details
    assert "Шаг 9" in result.details
    assert "Шаг 10" in result.details
    assert "Интерпретация" in result.details
    assert "Комплексная оценка" in result.details or "Полный разбор" in result.details
    assert "Важные рекомендации" in result.details
    assert "Печать счастья" in result.details
    assert "Солнце ↔ Луна" in result.details
    assert "Венера ↔ Марс" in result.details
    assert "Меркурий ↔ Меркурий" in result.details


def main() -> None:
    test_payment_payloads()
    test_payment_options()
    test_referral_profile_requirements()
    test_premium_dates()
    test_start_source_payloads()
    test_stats_keys()
    test_sun_sign_compat()
    test_synastry_style()
    test_horoscope_style()
    test_lucky_time_varies_by_day()
    test_synastry_asc()
    test_synastry_composite()
    test_synastry_progressions()
    test_synastry_numerology()
    test_synastry_tarot()
    test_synastry_fictitious()
    test_synastry_summary()
    test_synastry_transits()
    test_synastry_karma()
    test_synastry_moon_venus()
    test_synastry_elements()
    test_synastry_houses()
    test_synastry_seals()
    test_synastry_overlay()
    print(f"OK (trial default={DEFAULT_PREMIUM_TRIAL_DAYS}d)")


if __name__ == "__main__":
    main()
