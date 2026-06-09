from __future__ import annotations

from datetime import date, time

from app.astro_engine import compute_sun_sign

ZODIAC_RANGES = [
    ("Capricorn", (12, 22), (1, 19)),
    ("Aquarius", (1, 20), (2, 18)),
    ("Pisces", (2, 19), (3, 20)),
    ("Aries", (3, 21), (4, 19)),
    ("Taurus", (4, 20), (5, 20)),
    ("Gemini", (5, 21), (6, 20)),
    ("Cancer", (6, 21), (7, 22)),
    ("Leo", (7, 23), (8, 22)),
    ("Virgo", (8, 23), (9, 22)),
    ("Libra", (9, 23), (10, 22)),
    ("Scorpio", (10, 23), (11, 21)),
    ("Sagittarius", (11, 22), (12, 21)),
]


def calendar_zodiac_sign(birth_date: date) -> str:
    """Approximate Sun sign from calendar date ranges (fallback only)."""
    month = birth_date.month
    day = birth_date.day

    for sign, (start_month, start_day), (end_month, end_day) in ZODIAC_RANGES:
        if start_month <= end_month:
            if (month == start_month and day >= start_day) or (
                month == end_month and day <= end_day
            ) or (start_month < month < end_month):
                return sign
        else:
            if (month == start_month and day >= start_day) or (
                month == end_month and day <= end_day
            ) or (month > start_month or month < end_month):
                return sign

    return "Unknown"


def resolve_sun_sign(
    birth_date: date,
    birth_time: time | None = None,
    *,
    city: str | None = None,
    timezone_name: str = "UTC",
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> str:
    sign = compute_sun_sign(
        birth_date,
        birth_time,
        timezone_name,
        city=city,
        lat=lat,
        lon=lon,
        birth_timezone=birth_timezone,
    )
    if sign:
        return sign
    return calendar_zodiac_sign(birth_date)


def zodiac_sign(birth_date: date) -> str:
    """Backward-compatible alias: ephemeris Sun at UTC noon when only date is known."""
    return resolve_sun_sign(birth_date, birth_time=None, timezone_name="UTC")
