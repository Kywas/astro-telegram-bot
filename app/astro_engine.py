from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from app.geo import resolve_birth_location
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
NATAL_POINTS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")

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
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
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
class AstroHoroscopeContext:
    summary_lines: list[str]
    score_adjustments: dict[str, int] = field(default_factory=dict)
    moon_sign: str = ""


def _longitude_to_sign(longitude: float) -> str:
    normalized = longitude % 360
    index = int(normalized // 30) % 12
    return ZODIAC_SIGNS[index]


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


def _aspect_phrase(locale: str, transit: str, natal: str, aspect: str) -> str:
    lang = "ru" if locale == "ru" else "en"
    aspect_name = ASPECT_LABELS[lang][aspect]
    if lang == "ru":
        tone = {
            "trine": "поддерживает и облегчает",
            "sextile": "открывает возможности",
            "conjunction": "усиливает тему",
            "square": "создаёт напряжение",
            "opposition": "требует баланса",
        }[aspect]
        return (
            f"Транзитный {_planet_label(locale, transit)} — {aspect_name} "
            f"к натальному {_planet_label(locale, natal)}: {tone}."
        )
    tone = {
        "trine": "supports and eases the flow",
        "sextile": "opens opportunities",
        "conjunction": "intensifies the theme",
        "square": "creates tension",
        "opposition": "asks for balance",
    }[aspect]
    return (
        f"Transit {_planet_label(locale, transit)} {aspect_name} "
        f"natal {_planet_label(locale, natal)}: {tone}."
    )


def _score_delta(aspect: str, transit: str) -> int:
    if aspect in {"trine", "sextile"}:
        return 1
    if aspect == "conjunction":
        return 1 if transit in {"VENUS", "JUPITER", "SUN"} else -1
    return -1


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
    try:
        tz = normalize_timezone(timezone_name)
        _lat, _lon, resolved_tz = resolve_birth_location(city, tz)
        natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
        transit_jd = _local_moment_jd(for_date, tz, hour=12, minute=0)

        natal_longitudes = _collect_longitudes(natal_jd, NATAL_POINTS)
        transit_longitudes = _collect_longitudes(transit_jd, TRANSIT_PLANETS)

        hits: list[tuple[float, str, str, str]] = []
        score_adjustments: dict[str, int] = {}

        for transit_key in TRANSIT_PLANETS:
            if transit_key == "MOON":
                continue
            for natal_key in NATAL_POINTS:
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
                delta = _score_delta(aspect_name, transit_key)
                for domain in PLANET_DOMAINS.get(natal_key, []):
                    score_adjustments[domain] = score_adjustments.get(domain, 0) + delta

        hits.sort(key=lambda item: item[0])
        moon_sign = _longitude_to_sign(transit_longitudes["MOON"])

        lang = "ru" if locale == "ru" else "en"
        summary_lines = [
            "🪐 Астрологический фон (Swiss Ephemeris)" if lang == "ru" else "🪐 Astrological backdrop (Swiss Ephemeris)",
            (
                f"• Луна сегодня в {_sign_label(locale, moon_sign)}"
                if lang == "ru"
                else f"• Moon today in {_sign_label(locale, moon_sign)}"
            ),
        ]

        if birth_time is None:
            summary_lines.append(
                "• Натал: время рождения не указано — точность снижена."
                if lang == "ru"
                else "• Natal chart: birth time missing — accuracy is reduced."
            )

        if not hits:
            summary_lines.append(
                "• Ярких транзитных аспектов к наталу сегодня нет — день более ровный."
                if lang == "ru"
                else "• No major transits to your natal chart today — a steadier day."
            )
        else:
            for _orb, transit_key, natal_key, aspect_name in hits[:3]:
                summary_lines.append(
                    f"• {_aspect_phrase(locale, transit_key, natal_key, aspect_name)}"
                )

        return AstroHoroscopeContext(
            summary_lines=summary_lines,
            score_adjustments=score_adjustments,
            moon_sign=moon_sign,
        )
    except Exception:
        logger.warning(
            (
                "astro horoscope block skipped user_id=%s birth_date=%s "
                "birth_time=%s city=%r timezone=%s for_date=%s locale=%s"
            ),
            user_id,
            birth_date,
            birth_time,
            city,
            timezone_name,
            for_date,
            locale,
            exc_info=True,
        )
        return None
