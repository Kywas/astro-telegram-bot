"""Vedic (Jyotish) natal chart calculations — sidereal Lahiri, whole-sign houses."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, time

import swisseph as swe

from app.astro_engine import SIGN_ELEMENTS, ZODIAC_SIGNS, _longitude_to_sign, _natal_julian_day
from app.geo import resolve_birth_location
from app.timezones import normalize_timezone

logger = logging.getLogger(__name__)

JYOTISH_BODIES = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")

SWE_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
    "RAHU": swe.TRUE_NODE,
}

SIGN_LORD = {
    "Aries": "MARS",
    "Taurus": "VENUS",
    "Gemini": "MERCURY",
    "Cancer": "MOON",
    "Leo": "SUN",
    "Virgo": "MERCURY",
    "Libra": "VENUS",
    "Scorpio": "MARS",
    "Sagittarius": "JUPITER",
    "Capricorn": "SATURN",
    "Aquarius": "SATURN",
    "Pisces": "JUPITER",
}

OWN_SIGNS: dict[str, tuple[str, ...]] = {
    "SUN": ("Leo",),
    "MOON": ("Cancer",),
    "MARS": ("Aries", "Scorpio"),
    "MERCURY": ("Gemini", "Virgo"),
    "JUPITER": ("Sagittarius", "Pisces"),
    "VENUS": ("Taurus", "Libra"),
    "SATURN": ("Capricorn", "Aquarius"),
    "RAHU": ("Aquarius",),
    "KETU": ("Scorpio",),
}

EXALTATION = {
    "SUN": "Aries",
    "MOON": "Taurus",
    "MARS": "Capricorn",
    "MERCURY": "Virgo",
    "JUPITER": "Cancer",
    "VENUS": "Pisces",
    "SATURN": "Libra",
    "RAHU": "Taurus",
    "KETU": "Scorpio",
}

DEBILITATION = {
    "SUN": "Libra",
    "MOON": "Scorpio",
    "MARS": "Cancer",
    "MERCURY": "Pisces",
    "JUPITER": "Capricorn",
    "VENUS": "Virgo",
    "SATURN": "Aries",
    "RAHU": "Scorpio",
    "KETU": "Taurus",
}

DIG_BALA_HOUSE = {
    "SUN": 10,
    "MOON": 4,
    "MARS": 10,
    "MERCURY": 1,
    "JUPITER": 1,
    "VENUS": 4,
    "SATURN": 7,
}

NAKSHATRA_NAMES = {
    "ru": [
        "Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира", "Ардра",
        "Пунарvasu", "Пушья", "Ашлеша", "Магха", "Пурва Phalguni", "Уттара Phalguni",
        "Хаста", "Читра", "Свати", "Вишakha", "Анuradha", "Джyeshtha",
        "Мула", "Пурва Ashadha", "Уттара Ashadha", "Шравana", "Dhanishta", "Shatabhisha",
        "Пурва Bhadrapada", "Уттара Bhadrapada", "Ревати",
    ],
    "en": [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
    ],
}

KENDRA_HOUSES = (1, 4, 7, 10)
DUSTHANA_HOUSES = (6, 8, 12)
Trikona_HOUSES = (1, 5, 9)

GANDANTA_PAIRS = (
    ("Pisces", "Aries"),
    ("Cancer", "Leo"),
    ("Scorpio", "Sagittarius"),
)

NAKSHATRA_SPAN = 360.0 / 27.0


@dataclass
class PlanetPlacement:
    key: str
    longitude: float
    sign: str
    house: int
    degree_in_sign: float
    nakshatra: str
    nakshatra_index: int
    dignity: str
    retrograde: bool
    dig_bala: bool


@dataclass
class JyotishChart:
    lagna_sign: str
    lagna_degree: float
    planets: dict[str, PlanetPlacement]
    house_signs: dict[int, str]
    house_lords: dict[int, str]
    house_planet_count: dict[int, int]
    sign_planet_count: dict[str, int]
    dominant_element: str
    element_counts: dict[str, int]
    retrograde_planets: list[str]
    stellium_sign: str | None
    stellium_house: int | None
    stellium_planets: list[str]
    strong_houses: list[int]
    kendra_planet_count: int
    dusthana_planet_count: int
    gandanta_lagna: bool
    gandanta_moon: bool
    moon_waxing: bool
    has_birth_time: bool
    coordinates_available: bool
    resolved_timezone: str


def _sign_index(sign: str) -> int:
    try:
        return ZODIAC_SIGNS.index(sign)
    except ValueError:
        return 0


def _house_for_sign(planet_sign: str, lagna_sign: str) -> int:
    return (_sign_index(planet_sign) - _sign_index(lagna_sign)) % 12 + 1


def _house_sign(lagna_sign: str, house: int) -> str:
    return ZODIAC_SIGNS[(_sign_index(lagna_sign) + house - 1) % 12]


def _nakshatra_index(longitude: float) -> int:
    return int((longitude % 360.0) // NAKSHATRA_SPAN) % 27


def _nakshatra_name(longitude: float, locale: str) -> str:
    lang = "ru" if locale == "ru" else "en"
    return NAKSHATRA_NAMES[lang][_nakshatra_index(longitude)]


def _dignity(planet: str, sign: str) -> str:
    if planet in EXALTATION and EXALTATION[planet] == sign:
        return "exalted"
    if planet in DEBILITATION and DEBILITATION[planet] == sign:
        return "debilitated"
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return "own"
    return "neutral"


def _is_gandanta(sign: str, degree_in_sign: float) -> bool:
    for water, fire in GANDANTA_PAIRS:
        if sign == water and degree_in_sign >= 26.6667:
            return True
        if sign == fire and degree_in_sign <= 3.3333:
            return True
    return False


def _sidereal_longitude(jd: float, planet_id: int) -> tuple[float, float]:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    result, _ = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    lon = float(result[0]) % 360.0
    speed = float(result[3])
    return lon, speed


def _sidereal_ascendant(jd: float, lat: float, lon: float) -> float:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    _cusps, ascmc = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
    return float(ascmc[0]) % 360.0


def _moon_waxing(sun_lon: float, moon_lon: float) -> bool:
    diff = (moon_lon - sun_lon) % 360.0
    return diff < 180.0


def build_jyotish_chart(
    *,
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    locale: str = "ru",
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> JyotishChart | None:
    try:
        resolved_lat, resolved_lon, resolved_tz = resolve_birth_location(
            city,
            normalize_timezone(birth_timezone or timezone_name),
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        has_birth_time = birth_time is not None
        coordinates_available = resolved_lat is not None and resolved_lon is not None
        if not has_birth_time or not coordinates_available:
            return None

        jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
        asc_lon = _sidereal_ascendant(jd, resolved_lat, resolved_lon)
        lagna_sign = _longitude_to_sign(asc_lon)
        lagna_degree = asc_lon % 30.0

        planets: dict[str, PlanetPlacement] = {}
        longitudes: dict[str, float] = {}

        for key in JYOTISH_BODIES:
            if key == "KETU":
                continue
            lon_p, speed = _sidereal_longitude(jd, SWE_IDS[key])
            longitudes[key] = lon_p
            sign = _longitude_to_sign(lon_p)
            degree = lon_p % 30.0
            house = _house_for_sign(sign, lagna_sign)
            planets[key] = PlanetPlacement(
                key=key,
                longitude=lon_p,
                sign=sign,
                house=house,
                degree_in_sign=degree,
                nakshatra=_nakshatra_name(lon_p, locale),
                nakshatra_index=_nakshatra_index(lon_p),
                dignity=_dignity(key, sign),
                retrograde=speed < 0,
                dig_bala=DIG_BALA_HOUSE.get(key) == house,
            )

        rahu_lon = longitudes["RAHU"]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        ketu_sign = _longitude_to_sign(ketu_lon)
        ketu_house = _house_for_sign(ketu_sign, lagna_sign)
        planets["KETU"] = PlanetPlacement(
            key="KETU",
            longitude=ketu_lon,
            sign=ketu_sign,
            house=ketu_house,
            degree_in_sign=ketu_lon % 30.0,
            nakshatra=_nakshatra_name(ketu_lon, locale),
            nakshatra_index=_nakshatra_index(ketu_lon),
            dignity=_dignity("KETU", ketu_sign),
            retrograde=True,
            dig_bala=False,
        )

        house_signs = {h: _house_sign(lagna_sign, h) for h in range(1, 13)}
        house_lords = {h: SIGN_LORD[house_signs[h]] for h in range(1, 13)}

        house_planet_count: dict[int, int] = {h: 0 for h in range(1, 13)}
        sign_planet_count: dict[str, int] = {s: 0 for s in ZODIAC_SIGNS}
        element_counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        retrograde_planets: list[str] = []

        for key, pl in planets.items():
            if key in {"RAHU", "KETU"}:
                continue
            house_planet_count[pl.house] += 1
            sign_planet_count[pl.sign] += 1
            element_counts[SIGN_ELEMENTS.get(pl.sign, "air")] += 1
            if pl.retrograde:
                retrograde_planets.append(key)

        element_counts[SIGN_ELEMENTS.get(lagna_sign, "air")] += 1
        dominant_element = max(element_counts, key=lambda k: element_counts[k])

        stellium_sign = None
        stellium_house = None
        stellium_planets: list[str] = []
        for sign, count in sign_planet_count.items():
            if count >= 3:
                members = [k for k, pl in planets.items() if pl.sign == sign and k not in {"RAHU", "KETU"}]
                if len(members) >= 3:
                    stellium_sign = sign
                    stellium_planets = members
                    stellium_house = planets[members[0]].house
                    break

        strong_houses = sorted(
            [h for h, c in house_planet_count.items() if c >= 2],
            key=lambda h: house_planet_count[h],
            reverse=True,
        )
        if not strong_houses and stellium_house:
            strong_houses = [stellium_house]

        kendra_planet_count = sum(
            1 for pl in planets.values() if pl.house in KENDRA_HOUSES and pl.key not in {"RAHU", "KETU"}
        )
        dusthana_planet_count = sum(
            1 for pl in planets.values() if pl.house in DUSTHANA_HOUSES and pl.key not in {"RAHU", "KETU"}
        )

        moon = planets["MOON"]
        sun = planets["SUN"]

        return JyotishChart(
            lagna_sign=lagna_sign,
            lagna_degree=lagna_degree,
            planets=planets,
            house_signs=house_signs,
            house_lords=house_lords,
            house_planet_count=house_planet_count,
            sign_planet_count=sign_planet_count,
            dominant_element=dominant_element,
            element_counts=element_counts,
            retrograde_planets=retrograde_planets,
            stellium_sign=stellium_sign,
            stellium_house=stellium_house,
            stellium_planets=stellium_planets,
            strong_houses=strong_houses[:4],
            kendra_planet_count=kendra_planet_count,
            dusthana_planet_count=dusthana_planet_count,
            gandanta_lagna=_is_gandanta(lagna_sign, lagna_degree),
            gandanta_moon=_is_gandanta(moon.sign, moon.degree_in_sign),
            moon_waxing=_moon_waxing(sun.longitude, moon.longitude),
            has_birth_time=True,
            coordinates_available=True,
            resolved_timezone=resolved_tz,
        )
    except Exception:
        logger.warning(
            "jyotish chart failed birth_date=%s birth_time=%s city=%r",
            birth_date,
            birth_time,
            city,
            exc_info=True,
        )
        return None
