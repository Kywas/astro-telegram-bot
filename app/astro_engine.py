from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from app.geo import resolve_birth_location
from app.forecast_text import (
    format_advice,
    format_affirmation,
    format_avoid,
    format_domain_section,
    format_summary_aspect,
)
from app.synastry_text import format_synastry_report
from app.timezones import normalize_timezone

logger = logging.getLogger(__name__)

ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

SIGN_ELEMENTS = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

PLANETS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
}

TRANSIT_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
NATAL_CHART_BODIES = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
NATAL_POINTS = NATAL_CHART_BODIES
DOMAINS = ("energy", "work", "finance", "love", "social", "health")

ASPECTS = (
    ("conjunction", 0, 8),
    ("sextile", 60, 6),
    ("square", 90, 7),
    ("trine", 120, 8),
    ("opposition", 180, 8),
)

PLANET_DOMAINS: dict[str, list[str]] = {
    "SUN": ["energy"],
    "MOON": ["health", "love"],
    "MERCURY": ["work", "social"],
    "VENUS": ["love", "finance"],
    "MARS": ["energy", "work"],
    "JUPITER": ["finance", "work"],
    "SATURN": ["work", "health"],
    "ASC": ["energy", "social"],
}

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
        "ASC": "Асцендент",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
        "ASC": "Ascendant",
    },
}

SIGN_LABELS = {
    "ru": {
        "Aries": "Овен",
        "Taurus": "Телец",
        "Gemini": "Близнецы",
        "Cancer": "Рак",
        "Leo": "Лев",
        "Virgo": "Дева",
        "Libra": "Весы",
        "Scorpio": "Скорпион",
        "Sagittarius": "Стрелец",
        "Capricorn": "Козерог",
        "Aquarius": "Водолей",
        "Pisces": "Рыбы",
    },
    "en": {sign: sign for sign in ZODIAC_SIGNS},
}

ASPECT_LABELS = {
    "ru": {
        "conjunction": "соединение",
        "sextile": "секстиль",
        "square": "квадрат",
        "trine": "трин",
        "opposition": "оппозиция",
    },
    "en": {
        "conjunction": "conjunction",
        "sextile": "sextile",
        "square": "square",
        "trine": "trine",
        "opposition": "opposition",
    },
}


@dataclass
class SectionForecast:
    text: str
    score: int


@dataclass
class AstroForecast:
    summary_lines: list[str]
    energy: SectionForecast
    work: SectionForecast
    finance: SectionForecast
    love: SectionForecast
    social: SectionForecast
    health: SectionForecast
    lucky_time: str
    avoid: str
    affirmation: str
    advice: str
    moon_sign: str = ""
    period_key: str = "day"
    period_start: date | None = None
    period_end: date | None = None


@dataclass
class AstroHoroscopeContext:
    """Backward-compatible subset used by legacy callers."""

    summary_lines: list[str]
    score_adjustments: dict[str, int] = field(default_factory=dict)
    moon_sign: str = ""


def _longitude_to_sign(longitude: float) -> str:
    normalized = longitude % 360
    index = int(normalized // 30) % 12
    return ZODIAC_SIGNS[index]


def _sign_index(sign: str) -> int:
    try:
        return ZODIAC_SIGNS.index(sign)
    except ValueError:
        return 0


def _element_relation(first_sign: str, second_sign: str) -> str:
    first = SIGN_ELEMENTS.get(first_sign, "fire")
    second = SIGN_ELEMENTS.get(second_sign, "fire")
    if first == second:
        return "harmony"
    pairs = {frozenset({"fire", "air"}), frozenset({"earth", "water"})}
    if frozenset({first, second}) in pairs:
        return "support"
    return "tension"


def _angle_diff(first: float, second: float) -> float:
    diff = abs(first - second) % 360
    return diff if diff <= 180 else 360 - diff


def _find_aspect(first: float, second: float) -> tuple[str, float] | None:
    diff = _angle_diff(first, second)
    best: tuple[str, float] | None = None
    for name, exact, orb in ASPECTS:
        delta = abs(diff - exact)
        if delta <= orb and (best is None or delta < best[1]):
            best = (name, delta)
    return best


def _planet_longitude(julian_day: float, planet_id: int) -> float:
    result, _retflag = swe.calc_ut(julian_day, planet_id)
    return float(result[0])


def _local_moment_jd(
    for_date: date,
    timezone_name: str,
    *,
    hour: int = 12,
    minute: int = 0,
) -> float:
    tz = ZoneInfo(timezone_name)
    moment = datetime.combine(for_date, time(hour, minute), tzinfo=tz).astimezone(timezone.utc)
    ut_hours = moment.hour + moment.minute / 60 + moment.second / 3600
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def _natal_julian_day(
    birth_date: date,
    birth_time: time | None,
    timezone_name: str,
) -> float:
    if birth_time is None:
        return _local_moment_jd(birth_date, timezone_name, hour=12, minute=0)
    tz = ZoneInfo(timezone_name)
    moment = datetime.combine(birth_date, birth_time, tzinfo=tz).astimezone(timezone.utc)
    ut_hours = moment.hour + moment.minute / 60 + moment.second / 3600
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def _collect_longitudes(julian_day: float, keys: tuple[str, ...]) -> dict[str, float]:
    return {key: _planet_longitude(julian_day, PLANETS[key]) for key in keys}


def _planet_label(locale: str, key: str) -> str:
    lang = "ru" if locale == "ru" else "en"
    return PLANET_LABELS[lang].get(key, key)


def _sign_label(locale: str, sign: str) -> str:
    lang = "ru" if locale == "ru" else "en"
    return SIGN_LABELS[lang].get(sign, sign)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def planet_label(locale: str, key: str) -> str:
    return _planet_label(locale, key)


def sign_label(locale: str, sign: str) -> str:
    return _sign_label(locale, sign)


def longitude_to_sign(longitude: float) -> str:
    return _longitude_to_sign(longitude)


def _solar_natal_longitudes(sign: str) -> dict[str, float]:
    sun_lon = _sign_index(sign) * 30 + 15
    return {"SUN": sun_lon}


def _transit_moment_jd(
    for_date: date,
    timezone_name: str,
    *,
    now_utc: datetime | None = None,
) -> float:
    """Today uses the user's current local time; other dates use local noon."""
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    local_now = now_utc.astimezone(ZoneInfo(timezone_name))
    if for_date == local_now.date():
        return _local_moment_jd(
            for_date,
            timezone_name,
            hour=local_now.hour,
            minute=local_now.minute,
        )
    return _local_moment_jd(for_date, timezone_name, hour=12, minute=0)


def _build_natal_forecast_longitudes(
    birth_date: date,
    birth_time: time | None,
    timezone_name: str,
    *,
    lat: float | None = None,
    lon: float | None = None,
) -> tuple[dict[str, float], bool, bool]:
    """Natal longitudes for transit forecast: 7 planets, Moon if time known, ASC if time+coords."""
    natal_jd = _natal_julian_day(birth_date, birth_time, timezone_name)
    has_birth_time = birth_time is not None
    if has_birth_time:
        keys: tuple[str, ...] = NATAL_CHART_BODIES
    else:
        keys = tuple(key for key in NATAL_CHART_BODIES if key != "MOON")
    longitudes = _collect_longitudes(natal_jd, keys)
    has_asc = False
    if has_birth_time and lat is not None and lon is not None:
        _cusps, ascmc = swe.houses(natal_jd, lat, lon, b"P")
        longitudes["ASC"] = float(ascmc[0])
        has_asc = True
    return longitudes, has_birth_time, has_asc


def _period_dates(period: str, for_date: date) -> list[date]:
    if period == "week":
        week_start = for_date - timedelta(days=for_date.weekday())
        return [week_start + timedelta(days=i) for i in range(7)]
    if period == "month":
        month_start = for_date.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        days = (next_month - month_start).days
        return [month_start + timedelta(days=i) for i in range(days)]
    return [for_date]


def _score_delta(aspect: str, transit: str) -> int:
    if aspect in {"trine", "sextile"}:
        return 1
    if aspect == "conjunction":
        return 1 if transit in {"VENUS", "JUPITER", "SUN"} else -1
    return -1


def _hit_domains(transit: str, natal: str) -> set[str]:
    domains: set[str] = set()
    domains.update(PLANET_DOMAINS.get(transit, []))
    domains.update(PLANET_DOMAINS.get(natal, []))
    return domains


def _collect_hits(
    natal_longitudes: dict[str, float],
    transit_longitudes: dict[str, float],
    *,
    birth_time: time | None,
    include_moon_transits: bool = False,
) -> list[tuple[float, str, str, str]]:
    hits: list[tuple[float, str, str, str]] = []
    for transit_key in TRANSIT_PLANETS:
        if transit_key == "MOON" and not include_moon_transits:
            continue
        for natal_key in natal_longitudes:
            if natal_key == "MOON" and birth_time is None:
                continue
            aspect_info = _find_aspect(
                transit_longitudes[transit_key],
                natal_longitudes[natal_key],
            )
            if aspect_info is None:
                continue
            aspect_name, orb_delta = aspect_info
            hits.append((orb_delta, transit_key, natal_key, aspect_name))
    hits.sort(key=lambda item: item[0])
    return hits


def _domain_hits(
    hits: list[tuple[float, str, str, str]],
    domain: str,
) -> list[tuple[float, str, str, str]]:
    return [hit for hit in hits if domain in _hit_domains(hit[1], hit[2])]


def _domain_score(domain_hits: list[tuple[float, str, str, str]]) -> int:
    score = 5
    for _orb, transit_key, _natal_key, aspect_name in domain_hits:
        score += _score_delta(aspect_name, transit_key)
    return max(1, min(10, score))


def _dedupe_hits(
    hits: list[tuple[float, str, str, str]],
) -> list[tuple[float, str, str, str]]:
    unique: dict[tuple[str, str, str], tuple[float, str, str, str]] = {}
    for hit in hits:
        key = (hit[1], hit[2], hit[3])
        if key not in unique or hit[0] < unique[key][0]:
            unique[key] = hit
    return sorted(unique.values(), key=lambda item: item[0])


def _hits_for_day(
    natal_longitudes: dict[str, float],
    for_date: date,
    timezone_name: str,
    *,
    birth_time: time | None,
    include_moon_transits: bool,
    now_utc: datetime | None = None,
) -> tuple[list[tuple[float, str, str, str]], str, dict[str, float]]:
    transit_jd = _transit_moment_jd(for_date, timezone_name, now_utc=now_utc)
    transit_longitudes = _collect_longitudes(transit_jd, TRANSIT_PLANETS)
    moon_sign = _longitude_to_sign(transit_longitudes["MOON"])
    hits = _collect_hits(
        natal_longitudes,
        transit_longitudes,
        birth_time=birth_time,
        include_moon_transits=include_moon_transits,
    )
    return hits, moon_sign, transit_longitudes


def _peak_day_label(locale: str, day: date, period: str) -> str:
    lang = _lang(locale)
    if period == "month":
        if lang == "ru":
            return f"{day.day} числа"
        return f"the {day.day}th"
    weekday_names_ru = [
        "понедельник",
        "вторник",
        "среда",
        "четверг",
        "пятница",
        "суббота",
        "воскресенье",
    ]
    weekday_names_en = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    names = weekday_names_ru if lang == "ru" else weekday_names_en
    return names[day.weekday()]


def _rank_period_hits(
    natal_longitudes: dict[str, float],
    period_dates: list[date],
    timezone_name: str,
    *,
    birth_time: time | None,
    period: str,
    now_utc: datetime | None = None,
) -> list[tuple[tuple[float, str, str, str], date, int]]:
    """Rank transits by how often they appear in the period (with tightest orb per hit)."""
    include_moon = period == "day"
    hit_days: dict[tuple[str, str, str], list[tuple[float, date]]] = {}
    for day in period_dates:
        hits, _, _ = _hits_for_day(
            natal_longitudes,
            day,
            timezone_name,
            birth_time=birth_time,
            include_moon_transits=include_moon,
            now_utc=now_utc,
        )
        seen_today: set[tuple[str, str, str]] = set()
        for orb_delta, transit_key, natal_key, aspect_name in hits:
            key = (transit_key, natal_key, aspect_name)
            if key in seen_today:
                continue
            seen_today.add(key)
            hit_days.setdefault(key, []).append((orb_delta, day))

    ranked: list[tuple[float, tuple[float, str, str, str], date, int]] = []
    for key, occurrences in hit_days.items():
        best_orb, peak_day = min(occurrences, key=lambda item: item[0])
        day_count = len(occurrences)
        hit = (best_orb, key[0], key[1], key[2])
        weight = day_count * 10.0 - best_orb
        if key[0] in {"JUPITER", "SATURN"} and period == "month":
            weight += 3.0
        if key[0] == "MOON" and period == "day":
            weight += 2.0
        ranked.append((weight, hit, peak_day, day_count))
    ranked.sort(key=lambda item: (-item[0], item[1][0]))
    return [(hit, peak_day, day_count) for _, hit, peak_day, day_count in ranked]


def _domain_text_for_period(
    locale: str,
    domain: str,
    natal_longitudes: dict[str, float],
    period_dates: list[date],
    timezone_name: str,
    *,
    birth_time: time | None,
    period: str,
    natal_sun_sign: str,
    relationship_status: str | None = None,
    style: str = "terms",
    now_utc: datetime | None = None,
) -> str:
    include_moon = period == "day"
    best_hit: tuple[float, str, str, str] | None = None
    best_day: date | None = None
    best_score = -999
    best_moon = "Aries"

    for day in period_dates:
        hits, day_moon, _ = _hits_for_day(
            natal_longitudes,
            day,
            timezone_name,
            birth_time=birth_time,
            include_moon_transits=include_moon,
            now_utc=now_utc,
        )
        domain_hits = _domain_hits(hits, domain)
        score = _domain_score(domain_hits)
        if domain_hits and (
            score > best_score
            or (score == best_score and domain_hits[0][0] < (best_hit[0] if best_hit else 999.0))
        ):
            best_score = score
            best_hit = domain_hits[0]
            best_day = day
            best_moon = day_moon

    if best_hit is None:
        mid_day = period_dates[len(period_dates) // 2]
        _, mid_moon, _ = _hits_for_day(
            natal_longitudes,
            mid_day,
            timezone_name,
            birth_time=birth_time,
            include_moon_transits=False,
            now_utc=now_utc,
        )
        return format_domain_section(
            locale,
            domain,
            [],
            moon_sign=mid_moon,
            natal_sun_sign=natal_sun_sign,
            relationship_status=relationship_status,
            style=style,
            period=period,
        )

    text = format_domain_section(
        locale,
        domain,
        [best_hit],
        moon_sign=best_moon,
        natal_sun_sign=natal_sun_sign,
        relationship_status=relationship_status,
        style=style,
        period=period,
    )
    if period != "day" and best_day is not None:
        peak = _peak_day_label(locale, best_day, period)
        lang = _lang(locale)
        if lang == "ru":
            text += f" Ярче всего: {peak}."
        else:
            text += f" Strongest: {peak}."
    return text


def _format_hour_ranges(hours: list[int], locale: str) -> str:
    if not hours:
        lang = _lang(locale)
        return (
            "нет ярко выраженных окон — ориентируйся на спокойный ритм"
            if lang == "ru"
            else "no strong windows — follow a calm daily rhythm"
        )

    ranges: list[tuple[int, int]] = []
    start = prev = hours[0]
    for hour in hours[1:]:
        if hour == prev + 1:
            prev = hour
            continue
        ranges.append((start, prev))
        start = prev = hour
    ranges.append((start, prev))

    parts = []
    for start_hour, end_hour in ranges[:2]:
        end_display = end_hour + 1
        parts.append(f"{start_hour:02d}:00-{end_display:02d}:00")

    lang = _lang(locale)
    if len(parts) == 1:
        return parts[0]
    connector = " и " if lang == "ru" else " and "
    return connector.join(parts)


def _lucky_hours_for_day(
    for_date: date,
    timezone_name: str,
    natal_longitudes: dict[str, float],
    *,
    birth_time: time | None,
) -> list[int]:
    lucky: list[int] = []
    natal_targets = [key for key in ("SUN", "VENUS", "JUPITER") if key in natal_longitudes]
    if not natal_targets:
        natal_targets = ["SUN"]

    for hour in range(7, 22):
        jd = _local_moment_jd(for_date, timezone_name, hour=hour, minute=0)
        moon_lon = _planet_longitude(jd, PLANETS["MOON"])
        for natal_key in natal_targets:
            if natal_key == "MOON" and birth_time is None:
                continue
            aspect_info = _find_aspect(moon_lon, natal_longitudes[natal_key])
            if aspect_info and aspect_info[0] in {"trine", "sextile", "conjunction"}:
                lucky.append(hour)
                break
    return lucky


def _lucky_time_text(
    period: str,
    period_dates: list[date],
    timezone_name: str,
    natal_longitudes: dict[str, float],
    locale: str,
    *,
    birth_time: time | None,
) -> str:
    if period == "day":
        hours = _lucky_hours_for_day(
            period_dates[0],
            timezone_name,
            natal_longitudes,
            birth_time=birth_time,
        )
        return _format_hour_ranges(hours, locale)

    best_date = period_dates[0]
    best_hours: list[int] = []
    for day in period_dates:
        hours = _lucky_hours_for_day(day, timezone_name, natal_longitudes, birth_time=birth_time)
        if len(hours) > len(best_hours):
            best_date = day
            best_hours = hours

    hours_text = _format_hour_ranges(best_hours, locale)
    lang = _lang(locale)
    if lang == "ru":
        weekday_names = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        day_label = weekday_names[best_date.weekday()]
        if period == "month":
            day_label = f"{best_date.day} число"
        return f"{day_label}, {hours_text}"
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_label = weekday_names[best_date.weekday()]
    if period == "month":
        day_label = f"the {best_date.day}th"
    return f"{day_label}, {hours_text}"


def _avoid_text(
    hits: list[tuple[float, str, str, str]],
    locale: str,
    *,
    period: str = "day",
) -> str:
    return format_avoid(locale, hits, period=period)


def _affirmation_text(
    hits: list[tuple[float, str, str, str]],
    locale: str,
    *,
    period: str = "day",
) -> str:
    return format_affirmation(locale, hits, period=period)


def _advice_text(
    hits: list[tuple[float, str, str, str]],
    locale: str,
    *,
    moon_sign: str,
    period: str = "day",
) -> str:
    return format_advice(locale, hits, moon_sign, period=period)


def _aspect_phrase(
    locale: str,
    transit: str,
    natal: str,
    aspect: str,
    orb: float,
    *,
    style: str = "terms",
    period: str = "day",
) -> str:
    return format_summary_aspect(locale, transit, natal, aspect, orb, style=style, period=period)


def _build_summary_lines(
    locale: str,
    ranked_hits: list[tuple[tuple[float, str, str, str], date, int]],
    moon_sign: str,
    *,
    birth_time: time | None,
    solar_only: bool,
    period: str,
    style: str = "terms",
    has_asc: bool = False,
) -> list[str]:
    del moon_sign
    lang = _lang(locale)
    summary: list[str] = []
    if ranked_hits:
        hit, peak_day, _day_count = ranked_hits[0]
        orb_delta, transit_key, natal_key, aspect_name = hit
        line = _aspect_phrase(
            locale,
            transit_key,
            natal_key,
            aspect_name,
            orb_delta,
            style=style,
            period=period,
        )
        if period == "week":
            peak = _peak_day_label(locale, peak_day, period)
            if lang == "ru":
                line += f" Пик недели — {peak}."
            else:
                line += f" Week peak — {peak}."
        elif period == "month":
            peak = _peak_day_label(locale, peak_day, period)
            if lang == "ru":
                line += f" Пик месяца — {peak}."
            else:
                line += f" Month peak — {peak}."
        summary.append(line)
        if period != "day" and len(ranked_hits) > 1:
            hit2, peak2, _ = ranked_hits[1]
            line2 = _aspect_phrase(
                locale,
                hit2[1],
                hit2[2],
                hit2[3],
                hit2[0],
                style=style,
                period=period,
            )
            if lang == "ru":
                summary.append(f"↳ Второй акцент — {line2.lower()}")
            else:
                summary.append(f"↳ Second theme — {line2}")
    if solar_only:
        summary.append(
            "ℹ️ Расчёт по солнечному знаку — укажите дату рождения для персональной карты."
            if lang == "ru"
            else "ℹ️ Solar-sign only — add your birth date for a personal chart."
        )
    elif has_asc:
        summary.append(
            "ℹ️ Персональный расчёт: транзиты к вашей карте (планеты + ASC)."
            if lang == "ru"
            else "ℹ️ Personal chart: transits to your planets and Ascendant."
        )
    elif birth_time is None:
        summary.append(
            "ℹ️ Без времени рождения Луна и ASC не участвуют — добавьте время в профиле."
            if lang == "ru"
            else "ℹ️ Without birth time, Moon and Ascendant are omitted — add time in profile."
        )
    else:
        summary.append(
            "ℹ️ Персональный расчёт по дате, времени и планетам. Проверьте город для ASC."
            if lang == "ru"
            else "ℹ️ Personal chart from date, time, and planets. Check city for Ascendant."
        )
    if period == "day" and not solar_only and lang == "ru":
        summary.append("ℹ️ На «сегодня» учтены транзиты Луны и актуальное локальное время.")
    elif period == "day" and not solar_only:
        summary.append("ℹ️ For today: Moon transits and your current local time are included.")
    elif period == "week" and lang == "ru":
        summary.append("ℹ️ Недельный прогноз: каждый блок — свой пик дня, не копия «сегодня».")
    elif period == "week":
        summary.append("ℹ️ Weekly forecast: each block has its own peak day, not a copy of today.")
    elif period == "month" and lang == "ru":
        summary.append("ℹ️ Месячный прогноз: акценты по дням месяца, медленные планеты важнее.")
    elif period == "month":
        summary.append("ℹ️ Monthly forecast: themes by day of month; slow planets weigh more.")
    return summary


def _aggregate_hits(
    natal_longitudes: dict[str, float],
    period_dates: list[date],
    timezone_name: str,
    *,
    birth_time: time | None,
    period: str = "day",
    now_utc: datetime | None = None,
) -> tuple[list[tuple[float, str, str, str]], str, dict[str, float]]:
    all_hits: list[tuple[float, str, str, str]] = []
    last_transit: dict[str, float] = {}
    moon_sign = "Aries"
    include_moon_transits = period == "day"

    for day in period_dates:
        transit_jd = _transit_moment_jd(day, timezone_name, now_utc=now_utc)
        transit_longitudes = _collect_longitudes(transit_jd, TRANSIT_PLANETS)
        last_transit = transit_longitudes
        moon_sign = _longitude_to_sign(transit_longitudes["MOON"])
        day_hits = _collect_hits(
            natal_longitudes,
            transit_longitudes,
            birth_time=birth_time,
            include_moon_transits=include_moon_transits,
        )
        all_hits.extend(day_hits)

    unique: dict[tuple[str, str, str], tuple[float, str, str, str]] = {}
    for hit in all_hits:
        key = (hit[1], hit[2], hit[3])
        if key not in unique or hit[0] < unique[key][0]:
            unique[key] = hit
    merged = sorted(unique.values(), key=lambda item: item[0])
    return merged, moon_sign, last_transit


def build_astro_forecast(
    *,
    birth_date: date | None,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    for_date: date,
    locale: str,
    period: str = "day",
    sign: str | None = None,
    relationship_status: str | None = None,
    user_id: int | None = None,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
    style: str = "terms",
) -> AstroForecast | None:
    try:
        tz = normalize_timezone(birth_timezone or timezone_name)
        resolved_lat, resolved_lon, resolved_tz = resolve_birth_location(
            city,
            tz,
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        period_key = period if period in {"day", "week", "month"} else "day"
        period_dates = _period_dates(period_key, for_date)
        now_utc = datetime.now(timezone.utc)
        include_moon_transits = period_key == "day"
        has_asc = False

        solar_only = birth_date is None
        if solar_only:
            if not sign:
                return None
            natal_longitudes = _solar_natal_longitudes(sign)
        else:
            natal_longitudes, _has_birth_time, has_asc = _build_natal_forecast_longitudes(
                birth_date,
                birth_time,
                resolved_tz,
                lat=resolved_lat,
                lon=resolved_lon,
            )

        hits, moon_sign, _transit_longitudes = _aggregate_hits(
            natal_longitudes,
            period_dates,
            timezone_name,
            birth_time=birth_time,
            period=period_key,
            now_utc=now_utc,
        )
        ranked_hits = _rank_period_hits(
            natal_longitudes,
            period_dates,
            timezone_name,
            birth_time=birth_time,
            period=period_key,
            now_utc=now_utc,
        )
        opening_moon_sign = moon_sign
        if period_key != "day":
            _, opening_moon_sign, _ = _hits_for_day(
                natal_longitudes,
                period_dates[0],
                timezone_name,
                birth_time=birth_time,
                include_moon_transits=False,
                now_utc=now_utc,
            )
        natal_sun_sign = _longitude_to_sign(natal_longitudes["SUN"])

        summary_lines = _build_summary_lines(
            locale,
            ranked_hits,
            opening_moon_sign,
            birth_time=birth_time,
            solar_only=solar_only,
            period=period_key,
            style=style,
            has_asc=has_asc,
        )

        sections = {}
        for domain in DOMAINS:
            domain_hits = _domain_hits(hits, domain)
            if len(period_dates) > 1:
                daily_scores = []
                for day in period_dates:
                    day_hits, _, _ = _hits_for_day(
                        natal_longitudes,
                        day,
                        timezone_name,
                        birth_time=birth_time,
                        include_moon_transits=include_moon_transits,
                        now_utc=now_utc,
                    )
                    daily_scores.append(_domain_score(_domain_hits(day_hits, domain)))
                score = max(1, min(10, round(sum(daily_scores) / len(daily_scores))))
            else:
                score = _domain_score(domain_hits)
            text = _domain_text_for_period(
                locale,
                domain,
                natal_longitudes,
                period_dates,
                timezone_name,
                birth_time=birth_time,
                period=period_key,
                natal_sun_sign=natal_sun_sign,
                relationship_status=relationship_status,
                style=style,
                now_utc=now_utc,
            )
            sections[domain] = SectionForecast(text=text, score=score)

        lucky_time = _lucky_time_text(
            period_key,
            period_dates,
            tz,
            natal_longitudes,
            locale,
            birth_time=birth_time,
        )

        advice_hits = [hit for hit, _, _ in ranked_hits] if ranked_hits else hits

        return AstroForecast(
            summary_lines=summary_lines,
            energy=sections["energy"],
            work=sections["work"],
            finance=sections["finance"],
            love=sections["love"],
            social=sections["social"],
            health=sections["health"],
            lucky_time=lucky_time,
            avoid=_avoid_text(advice_hits, locale, period=period_key),
            affirmation=_affirmation_text(advice_hits, locale, period=period_key),
            advice=_advice_text(
                advice_hits,
                locale,
                moon_sign=opening_moon_sign,
                period=period_key,
            ),
            moon_sign=opening_moon_sign,
            period_key=period_key,
            period_start=period_dates[0],
            period_end=period_dates[-1],
        )
    except Exception:
        logger.warning(
            (
                "astro forecast failed user_id=%s birth_date=%s birth_time=%s "
                "city=%r timezone=%s for_date=%s period=%s locale=%s sign=%s"
            ),
            user_id,
            birth_date,
            birth_time,
            city,
            timezone_name,
            for_date,
            period,
            locale,
            sign,
            exc_info=True,
        )
        return None


def build_astro_horoscope_context(
    *,
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    for_date: date,
    locale: str,
    user_id: int | None = None,
) -> AstroHoroscopeContext | None:
    forecast = build_astro_forecast(
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        timezone_name=timezone_name,
        for_date=for_date,
        locale=locale,
        period="day",
        user_id=user_id,
    )
    if forecast is None:
        return None

    adjustments: dict[str, int] = {}
    for domain, section in (
        ("energy", forecast.energy),
        ("work", forecast.work),
        ("finance", forecast.finance),
        ("love", forecast.love),
        ("social", forecast.social),
        ("health", forecast.health),
    ):
        adjustments[domain] = section.score - 5

    return AstroHoroscopeContext(
        summary_lines=forecast.summary_lines,
        score_adjustments=adjustments,
        moon_sign=forecast.moon_sign,
    )


@dataclass
class NatalAspectHit:
    planet_a: str
    planet_b: str
    aspect: str
    orb: float


@dataclass
class NatalChartData:
    longitudes: dict[str, float]
    ascendant: float | None
    aspects: list[NatalAspectHit]
    has_birth_time: bool
    moon_included: bool
    asc_included: bool
    coordinates_available: bool
    resolved_timezone: str
    sun_sign: str


def _collect_natal_aspects(
    longitudes: dict[str, float],
    ascendant: float | None,
) -> list[NatalAspectHit]:
    points: dict[str, float] = dict(longitudes)
    if ascendant is not None:
        points["ASC"] = ascendant
    keys = list(points.keys())
    hits: list[NatalAspectHit] = []
    for index, first_key in enumerate(keys):
        for second_key in keys[index + 1 :]:
            aspect_info = _find_aspect(points[first_key], points[second_key])
            if aspect_info is None:
                continue
            aspect_name, orb_delta = aspect_info
            hits.append(NatalAspectHit(first_key, second_key, aspect_name, orb_delta))
    hits.sort(key=lambda item: item.orb)
    return hits


def build_natal_chart_data(
    *,
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> NatalChartData | None:
    try:
        resolved_lat, resolved_lon, resolved_tz = resolve_birth_location(
            city,
            normalize_timezone(birth_timezone or timezone_name),
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
        has_birth_time = birth_time is not None
        keys: tuple[str, ...]
        if has_birth_time:
            keys = NATAL_CHART_BODIES
        else:
            keys = tuple(key for key in NATAL_CHART_BODIES if key != "MOON")
        longitudes = _collect_longitudes(natal_jd, keys)

        ascendant: float | None = None
        asc_included = False
        coordinates_available = resolved_lat is not None and resolved_lon is not None
        if has_birth_time and coordinates_available:
            _cusps, ascmc = swe.houses(natal_jd, resolved_lat, resolved_lon, b"P")
            ascendant = float(ascmc[0])
            asc_included = True

        aspects = _collect_natal_aspects(longitudes, ascendant)
        sun_sign = _longitude_to_sign(longitudes["SUN"])
        return NatalChartData(
            longitudes=longitudes,
            ascendant=ascendant,
            aspects=aspects,
            has_birth_time=has_birth_time,
            moon_included="MOON" in longitudes,
            asc_included=asc_included,
            coordinates_available=coordinates_available,
            resolved_timezone=resolved_tz,
            sun_sign=sun_sign,
        )
    except Exception:
        logger.warning(
            "natal chart failed birth_date=%s birth_time=%s city=%r timezone=%s",
            birth_date,
            birth_time,
            city,
            timezone_name,
            exc_info=True,
        )
        return None


def compute_sun_sign(
    birth_date: date,
    birth_time: time | None,
    timezone_name: str,
    *,
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> str | None:
    try:
        _lat, _lon, resolved_tz = resolve_birth_location(
            city,
            normalize_timezone(birth_timezone or timezone_name),
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
        sun_lon = _planet_longitude(natal_jd, swe.SUN)
        return _longitude_to_sign(sun_lon)
    except Exception:
        logger.warning(
            "sun sign failed birth_date=%s birth_time=%s city=%r timezone=%s",
            birth_date,
            birth_time,
            city,
            timezone_name,
            exc_info=True,
        )
        return None


SYNODIC_MONTH_DAYS = 29.530588853
LUNAR_DAYS_PER_CYCLE = 30
LUNAR_DAY_ARC_DEGREES = 360.0 / LUNAR_DAYS_PER_CYCLE
LUNAR_DAY_MEAN_HOURS = SYNODIC_MONTH_DAYS / LUNAR_DAYS_PER_CYCLE * 24.0
# Mean shift of the lunar-day boundary vs civil midnight (~22–23 min/day).
LUNAR_DAY_DRIFT_MINUTES = round((24.0 - LUNAR_DAY_MEAN_HOURS) * 60.0, 1)
# Primary phases from Swiss Ephemeris (JPL DE); matches USNO/NASA lunar calculators.
MAJOR_PHASE_KEYS = ("new_moon", "first_quarter", "full_moon", "last_quarter")
MAJOR_PHASE_ELONGATION = {
    "new_moon": 0.0,
    "first_quarter": 90.0,
    "full_moon": 180.0,
    "last_quarter": 270.0,
}


@dataclass
class MoonDayData:
    for_date: date
    phase_key: str
    elongation: float
    age_days: float
    lunar_day: int
    illumination: int
    moon_sign: str
    next_phase_key: str
    next_phase_days: int
    next_phase_jd: float
    new_moon_jd: float
    lunar_day_start_jd: float
    next_lunar_day_start_jd: float
    timezone_name: str


def _elongation_delta(elongation: float, target: float) -> float:
    return (elongation - target + 180.0) % 360.0 - 180.0


def _phase_delta(jd: float, target_elongation: float) -> float:
    return _elongation_delta(_moon_elongation_ahead(jd), target_elongation)


def _bisect_phase_crossing(left: float, right: float, target_elongation: float) -> float:
    for _ in range(64):
        mid = (left + right) / 2.0
        mid_delta = _phase_delta(mid, target_elongation)
        if abs(mid_delta) < 1e-4:
            return mid
        if _phase_delta(left, target_elongation) * mid_delta <= 0:
            right = mid
        else:
            left = mid
    return (left + right) / 2.0


def _find_phase_jd(
    near_jd: float,
    target_elongation: float,
    *,
    search_backward: bool = False,
    window_days: float | None = None,
) -> float:
    max_scan = window_days if window_days is not None else SYNODIC_MONTH_DAYS / 4.0 + 1.5
    step = 0.25
    if search_backward:
        probe = near_jd - max_scan
        limit = near_jd
    else:
        probe = near_jd
        limit = near_jd + max_scan

    prev_jd = probe
    prev_delta = _phase_delta(prev_jd, target_elongation)
    probe += step
    while probe <= limit + 1e-9:
        cur_delta = _phase_delta(probe, target_elongation)
        if abs(cur_delta) < 0.01:
            return probe
        if prev_delta * cur_delta <= 0 and abs(prev_delta - cur_delta) > 0.05:
            return _bisect_phase_crossing(prev_jd, probe, target_elongation)
        prev_jd = probe
        prev_delta = cur_delta
        probe += step

    left, right = (near_jd - max_scan, near_jd) if search_backward else (near_jd, near_jd + max_scan)

    def error(jd: float) -> float:
        return abs(_phase_delta(jd, target_elongation))

    golden = (5**0.5 - 1) / 2
    for _ in range(64):
        probe_a = right - golden * (right - left)
        probe_b = left + golden * (right - left)
        if error(probe_a) < error(probe_b):
            right = probe_b
        else:
            left = probe_a
    return (left + right) / 2.0


def _find_last_new_moon_jd(julian_day: float) -> float:
    return _find_phase_jd(
        julian_day,
        0.0,
        search_backward=True,
        window_days=SYNODIC_MONTH_DAYS + 1.0,
    )


def _lunar_day_from_elongation(elongation: float) -> int:
    return min(LUNAR_DAYS_PER_CYCLE, int(elongation / LUNAR_DAY_ARC_DEGREES) + 1)


def _lunar_day_start_jd(new_moon_jd: float, lunar_day: int) -> float:
    if lunar_day <= 1:
        return new_moon_jd
    target = (lunar_day - 1) * LUNAR_DAY_ARC_DEGREES
    estimate = new_moon_jd + (lunar_day - 1) * (SYNODIC_MONTH_DAYS / LUNAR_DAYS_PER_CYCLE)
    return _find_phase_jd(
        estimate - 0.5,
        target,
        search_backward=False,
        window_days=1.5,
    )


def _lunar_day_bounds(
    julian_day: float,
    new_moon_jd: float,
) -> tuple[int, float, float]:
    elongation = _moon_elongation_ahead(julian_day)
    lunar_day = _lunar_day_from_elongation(elongation)
    start_jd = _lunar_day_start_jd(new_moon_jd, lunar_day)
    if lunar_day >= LUNAR_DAYS_PER_CYCLE:
        next_start = _refine_forward_phase(julian_day, 0.0)
    else:
        next_start = _lunar_day_start_jd(new_moon_jd, lunar_day + 1)
    return lunar_day, start_jd, next_start


def _evaluation_jd(for_date: date, timezone_name: str) -> float:
    tz = ZoneInfo(normalize_timezone(timezone_name))
    now_local = datetime.now(tz)
    if for_date == now_local.date():
        return _local_moment_jd(
            for_date,
            timezone_name,
            hour=now_local.hour,
            minute=now_local.minute,
        )
    return _local_moment_jd(for_date, timezone_name, hour=12, minute=0)


def _refine_forward_phase(from_jd: float, target_elongation: float) -> float:
    elongation = _moon_elongation_ahead(from_jd)
    delta_deg = (target_elongation - elongation) % 360.0
    if delta_deg < 1e-3:
        delta_deg = 360.0
    estimate = from_jd + delta_deg / 360.0 * SYNODIC_MONTH_DAYS
    return _find_phase_jd(
        estimate - 1.5,
        target_elongation,
        search_backward=False,
        window_days=3.0,
    )


def _next_major_phase(julian_day: float) -> tuple[str, int, float]:
    best_jd: float | None = None
    best_key: str | None = None
    for phase_key in MAJOR_PHASE_KEYS:
        target = MAJOR_PHASE_ELONGATION[phase_key]
        candidate = _refine_forward_phase(julian_day, target)
        if candidate <= julian_day + 1e-6:
            continue
        if best_jd is None or candidate < best_jd:
            best_jd = candidate
            best_key = phase_key
    assert best_jd is not None and best_key is not None
    return best_key, max(0, round(best_jd - julian_day)), best_jd


def jd_to_local_datetime(julian_day: float, timezone_name: str) -> datetime:
    year, month, day, hour = swe.revjul(julian_day, swe.GREG_CAL)
    hour_int = int(hour)
    minute = int(round((hour - hour_int) * 60.0))
    if minute >= 60:
        minute = 0
        hour_int += 1
    utc_moment = datetime(year, month, day, hour_int, minute, tzinfo=timezone.utc)
    return utc_moment.astimezone(ZoneInfo(normalize_timezone(timezone_name)))


def major_phase_on_local_date(for_date: date, timezone_name: str) -> str | None:
    tz = normalize_timezone(timezone_name)
    day_start = _local_moment_jd(for_date, tz, hour=0, minute=0)
    day_end = _local_moment_jd(for_date + timedelta(days=1), tz, hour=0, minute=0)
    for phase_key in MAJOR_PHASE_KEYS:
        target = MAJOR_PHASE_ELONGATION[phase_key]
        phase_jd = _find_phase_jd(
            day_end - 1e-8,
            target,
            search_backward=True,
            window_days=1.0,
        )
        if day_start <= phase_jd < day_end and abs(_phase_delta(phase_jd, target)) < 3.0:
            return phase_key
    return None


def _moon_elongation_ahead(julian_day: float) -> float:
    sun_lon = _planet_longitude(julian_day, swe.SUN)
    moon_lon = _planet_longitude(julian_day, swe.MOON)
    return (moon_lon - sun_lon) % 360


def _phase_key_from_elongation(elongation: float) -> str:
    if elongation < 22.5 or elongation >= 337.5:
        return "new_moon"
    if elongation < 67.5:
        return "waxing_crescent"
    if elongation < 112.5:
        return "first_quarter"
    if elongation < 157.5:
        return "waxing_gibbous"
    if elongation < 202.5:
        return "full_moon"
    if elongation < 247.5:
        return "waning_gibbous"
    if elongation < 292.5:
        return "last_quarter"
    return "waning_crescent"


def _moon_illumination_percent(julian_day: float) -> int:
    result = swe.pheno_ut(julian_day, swe.MOON, swe.FLG_SWIEPH)
    return round(float(result[1]) * 100)


def build_moon_day_data(
    for_date: date,
    *,
    timezone_name: str = "UTC",
) -> MoonDayData | None:
    try:
        tz = normalize_timezone(timezone_name)
        julian_day = _evaluation_jd(for_date, tz)
        elongation = _moon_elongation_ahead(julian_day)
        new_moon_jd = _find_last_new_moon_jd(julian_day)
        age_days = max(0.0, julian_day - new_moon_jd)
        lunar_day, lunar_day_start_jd, next_lunar_day_start_jd = _lunar_day_bounds(
            julian_day,
            new_moon_jd,
        )
        moon_lon = _planet_longitude(julian_day, swe.MOON)
        next_phase_key, next_phase_days, next_phase_jd = _next_major_phase(julian_day)
        return MoonDayData(
            for_date=for_date,
            phase_key=_phase_key_from_elongation(elongation),
            elongation=elongation,
            age_days=age_days,
            lunar_day=lunar_day,
            illumination=_moon_illumination_percent(julian_day),
            moon_sign=_longitude_to_sign(moon_lon),
            next_phase_key=next_phase_key,
            next_phase_days=next_phase_days,
            next_phase_jd=next_phase_jd,
            new_moon_jd=new_moon_jd,
            lunar_day_start_jd=lunar_day_start_jd,
            next_lunar_day_start_jd=next_lunar_day_start_jd,
            timezone_name=tz,
        )
    except Exception:
        logger.warning(
            "moon day data failed for_date=%s timezone=%s",
            for_date,
            timezone_name,
            exc_info=True,
        )
        return None


@dataclass
class EveningSnapshot:
    moon_sign: str
    moon_phase_key: str
    energy_score: int
    top_hit: tuple[float, str, str, str] | None
    challenging_count: int
    supportive_count: int
    avoid_line: str
    solar_only: bool


def build_evening_snapshot(
    *,
    birth_date: date | None,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    for_date: date,
    locale: str,
    sign: str | None = None,
    user_id: int | None = None,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> EveningSnapshot | None:
    try:
        tz = normalize_timezone(birth_timezone or timezone_name)
        _lat, _lon, resolved_tz = resolve_birth_location(
            city,
            tz,
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        solar_only = birth_date is None
        if solar_only:
            if not sign:
                return None
            natal_longitudes = _solar_natal_longitudes(sign)
        else:
            natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
            natal_longitudes = _collect_longitudes(natal_jd, NATAL_POINTS)

        hits, moon_sign, _transit_longitudes = _aggregate_hits(
            natal_longitudes,
            [for_date],
            resolved_tz,
            birth_time=birth_time,
        )
        moon_data = build_moon_day_data(for_date, timezone_name=tz)
        phase_key = moon_data.phase_key if moon_data else "waxing_gibbous"
        energy_score = _domain_score(_domain_hits(hits, "energy"))
        challenging_count = sum(1 for hit in hits if hit[3] in {"square", "opposition"})
        supportive_count = sum(1 for hit in hits if hit[3] in {"trine", "sextile", "conjunction"})
        avoid_line = format_avoid(locale, hits)

        return EveningSnapshot(
            moon_sign=moon_sign,
            moon_phase_key=phase_key,
            energy_score=energy_score,
            top_hit=hits[0] if hits else None,
            challenging_count=challenging_count,
            supportive_count=supportive_count,
            avoid_line=avoid_line,
            solar_only=solar_only,
        )
    except Exception:
        logger.warning(
            "evening snapshot failed user_id=%s for_date=%s",
            user_id,
            for_date,
            exc_info=True,
        )
        return None


SYNASTRY_POINTS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")

MODE_PLANET_WEIGHT: dict[str, dict[str, float]] = {
    "love": {"SUN": 1.0, "MOON": 2.0, "MERCURY": 0.8, "VENUS": 2.5, "MARS": 1.5},
    "friendship": {"SUN": 1.5, "MOON": 1.2, "MERCURY": 2.0, "VENUS": 1.0, "MARS": 0.8},
    "work": {"SUN": 1.2, "MOON": 0.6, "MERCURY": 2.2, "VENUS": 0.8, "MARS": 1.5},
}

MODE_LABELS = {
    "ru": {"love": "любовь", "friendship": "дружба", "work": "работа"},
    "en": {"love": "love", "friendship": "friendship", "work": "work"},
}


@dataclass
class SynastryAnalysis:
    score: int
    details: str
    partner_sign: str


def _natal_chart(
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    *,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> tuple[dict[str, float], str]:
    tz = normalize_timezone(birth_timezone or timezone_name)
    _lat, _lon, resolved_tz = resolve_birth_location(
        city,
        tz,
        lat=lat,
        lon=lon,
        birth_timezone=birth_timezone,
    )
    natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
    keys = SYNASTRY_POINTS if birth_time is not None else tuple(k for k in SYNASTRY_POINTS if k != "MOON")
    longitudes = _collect_longitudes(natal_jd, keys)
    sun_sign = _longitude_to_sign(longitudes["SUN"])
    return longitudes, sun_sign


def _collect_synastry_hits(
    user_chart: dict[str, float],
    partner_chart: dict[str, float],
) -> list[tuple[float, float, str, str, str]]:
    hits: list[tuple[float, float, str, str, str]] = []
    for user_planet, user_lon in user_chart.items():
        for partner_planet, partner_lon in partner_chart.items():
            aspect_info = _find_aspect(user_lon, partner_lon)
            if aspect_info is None:
                continue
            aspect_name, orb_delta = aspect_info
            hits.append((orb_delta, orb_delta, user_planet, partner_planet, aspect_name))
    hits.sort(key=lambda item: item[0])
    return hits


def _synastry_pair_weight(planet_a: str, planet_b: str, mode: str) -> float:
    weights = MODE_PLANET_WEIGHT.get(mode, MODE_PLANET_WEIGHT["love"])
    return (weights.get(planet_a, 1.0) + weights.get(planet_b, 1.0)) / 2


def _synastry_aspect_delta(aspect: str, planet_a: str, planet_b: str) -> int:
    if aspect in {"trine", "sextile"}:
        return 4 if aspect == "trine" else 3
    if aspect == "conjunction":
        benefics = {"VENUS", "JUPITER", "SUN", "MOON"}
        if planet_a in benefics or planet_b in benefics:
            return 3
        if planet_a in {"SATURN", "MARS"} and planet_b in {"SATURN", "MARS"}:
            return -3
        return 1
    if aspect == "opposition":
        return -2
    return -4


def _synastry_score(hits: list[tuple[float, float, str, str, str]], mode: str) -> int:
    if not hits:
        return 55
    total = 50.0
    for _orb, _orb2, planet_a, planet_b, aspect in hits:
        delta = _synastry_aspect_delta(aspect, planet_a, planet_b)
        weight = _synastry_pair_weight(planet_a, planet_b, mode)
        total += delta * weight
    return max(35, min(98, round(total)))


def build_synastry_analysis(
    *,
    user_birth_date: date,
    user_birth_time: time | None,
    user_city: str | None,
    user_timezone: str,
    partner_birth_date: date,
    partner_birth_time: time | None = None,
    partner_city: str | None = None,
    partner_timezone: str | None = None,
    relation_mode: str,
    locale: str,
    user_id: int | None = None,
    user_lat: float | None = None,
    user_lon: float | None = None,
    user_birth_timezone: str | None = None,
    partner_lat: float | None = None,
    partner_lon: float | None = None,
    partner_birth_timezone: str | None = None,
) -> SynastryAnalysis | None:
    try:
        mode = relation_mode if relation_mode in MODE_PLANET_WEIGHT else "love"
        partner_tz = partner_birth_timezone or partner_timezone or user_birth_timezone or user_timezone

        user_chart, user_sign_key = _natal_chart(
            user_birth_date,
            user_birth_time,
            user_city,
            user_birth_timezone or user_timezone,
            lat=user_lat,
            lon=user_lon,
            birth_timezone=user_birth_timezone,
        )
        partner_chart, partner_sign_key = _natal_chart(
            partner_birth_date,
            partner_birth_time,
            partner_city,
            partner_tz,
            lat=partner_lat,
            lon=partner_lon,
            birth_timezone=partner_birth_timezone,
        )
        hits = _collect_synastry_hits(user_chart, partner_chart)
        score = _synastry_score(hits, mode)

        ranked = sorted(
            hits,
            key=lambda item: abs(_synastry_aspect_delta(item[4], item[2], item[3]))
            * _synastry_pair_weight(item[2], item[3], mode),
            reverse=True,
        )
        ranked_hits = [(item[0], item[2], item[3], item[4]) for item in ranked]
        details = format_synastry_report(
            locale,
            mode=mode,
            score=score,
            hits=ranked_hits,
            user_sign=_sign_label(locale, user_sign_key),
            partner_sign=_sign_label(locale, partner_sign_key),
            user_has_moon=user_birth_time is not None,
            partner_has_moon=partner_birth_time is not None,
        )

        return SynastryAnalysis(
            score=score,
            details=details,
            partner_sign=partner_sign_key,
        )
    except Exception:
        logger.warning(
            (
                "synastry analysis failed user_id=%s user_birth=%s partner_birth=%s "
                "mode=%s locale=%s"
            ),
            user_id,
            user_birth_date,
            partner_birth_date,
            relation_mode,
            locale,
            exc_info=True,
        )
        return None
