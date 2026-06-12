from __future__ import annotations

from datetime import date, time

from app.jyotish_text import build_jyotish_reading


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _missing_time_message(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            "Для ведического разбора нужны **точное время** и **город** рождения.\n\n"
            "Укажи время в профиле через /start — без него нельзя рассчитать Лагну и дома."
        ).replace("**", "")
    return (
        "Vedic reading requires **exact birth time** and **city**.\n\n"
        "Add time in your profile via /start — without it Lagna and houses cannot be calculated."
    ).replace("**", "")


def build_natal_summary(
    *,
    locale: str,
    sign_name: str,
    sign_key: str | None,
    birth_date: date,
    birth_time: time | None,
    city: str,
    relationship_status: str | None = None,
    goal: str | None = None,
    mood_score: int | None = None,
    mode: str = "full",
    part: int = 1,
    timezone: str = "UTC",
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> str:
    del sign_name, sign_key, relationship_status, goal, mood_score
    lang = _lang(locale)

    if birth_time is None:
        return _missing_time_message(locale)
    if not city or city.strip() in {"-", ""}:
        if lang == "ru":
            return "Укажи город рождения в профиле — он нужен для расчёта Лагны."
        return "Add your birth city in profile — it is required for Lagna."

    normalized_part = max(1, min(3, part))
    if mode == "short":
        normalized_part = 1

    text = build_jyotish_reading(
        locale=locale,
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        timezone=timezone,
        lat=lat,
        lon=lon,
        birth_timezone=birth_timezone,
        part=normalized_part,
    )
    if text is None:
        return (
            "Не удалось рассчитать карту. Проверь дату, время, город и координаты в профиле."
            if lang == "ru"
            else "Could not compute the chart. Check date, time, city, and profile coordinates."
        )
    return text
