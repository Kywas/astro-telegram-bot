"""City geocoding: static aliases, DB cache, and OpenStreetMap Nominatim."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import aiohttp
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

from app.timezones import normalize_timezone

if TYPE_CHECKING:
    from app.database import Database

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "AstroPulseTelegramBot/1.0 (contact: astropulse-bot)"
_timezone_finder: TimezoneFinder | None = None

# lat, lon, timezone
STATIC_CITIES: dict[str, tuple[float, float, str]] = {
    "москва": (55.7558, 37.6173, "Europe/Moscow"),
    "moscow": (55.7558, 37.6173, "Europe/Moscow"),
    "санкт-петербург": (59.9311, 30.3609, "Europe/Moscow"),
    "saint petersburg": (59.9311, 30.3609, "Europe/Moscow"),
    "spb": (59.9311, 30.3609, "Europe/Moscow"),
    "питер": (59.9311, 30.3609, "Europe/Moscow"),
    "киев": (50.4501, 30.5234, "Europe/Kyiv"),
    "kyiv": (50.4501, 30.5234, "Europe/Kyiv"),
    "kiev": (50.4501, 30.5234, "Europe/Kyiv"),
    "минск": (53.9006, 27.5590, "Europe/Minsk"),
    "minsk": (53.9006, 27.5590, "Europe/Minsk"),
    "алматы": (43.2220, 76.8512, "Asia/Almaty"),
    "almaty": (43.2220, 76.8512, "Asia/Almaty"),
    "астана": (51.1694, 71.4491, "Asia/Almaty"),
    "astana": (51.1694, 71.4491, "Asia/Almaty"),
    "ташкент": (41.2995, 69.2401, "Asia/Tashkent"),
    "tashkent": (41.2995, 69.2401, "Asia/Tashkent"),
    "екатеринбург": (56.8389, 60.6057, "Asia/Yekaterinburg"),
    "yekaterinburg": (56.8389, 60.6057, "Asia/Yekaterinburg"),
    "новосибирск": (55.0084, 82.9357, "Asia/Novosibirsk"),
    "novosibirsk": (55.0084, 82.9357, "Asia/Novosibirsk"),
    "красноярск": (56.0153, 92.8932, "Asia/Krasnoyarsk"),
    "krasnoyarsk": (56.0153, 92.8932, "Asia/Krasnoyarsk"),
    "челябинск": (55.1644, 61.4368, "Asia/Yekaterinburg"),
    "chelyabinsk": (55.1644, 61.4368, "Asia/Yekaterinburg"),
    "нижний новгород": (56.2965, 43.9361, "Europe/Moscow"),
    "nizhny novgorod": (56.2965, 43.9361, "Europe/Moscow"),
    "тюмень": (57.1530, 65.5343, "Asia/Yekaterinburg"),
    "tyumen": (57.1530, 65.5343, "Asia/Yekaterinburg"),
    "хабаровск": (48.4827, 135.0838, "Asia/Vladivostok"),
    "khabarovsk": (48.4827, 135.0838, "Asia/Vladivostok"),
    "саратов": (51.5336, 46.0343, "Europe/Saratov"),
    "saratov": (51.5336, 46.0343, "Europe/Saratov"),
    "тольятти": (53.5078, 49.4204, "Europe/Samara"),
    "tolyatti": (53.5078, 49.4204, "Europe/Samara"),
    "ижевск": (56.8527, 53.2115, "Europe/Samara"),
    "izhevsk": (56.8527, 53.2115, "Europe/Samara"),
    "барнаул": (53.3480, 83.7798, "Asia/Barnaul"),
    "barnaul": (53.3480, 83.7798, "Asia/Barnaul"),
    "ульяновск": (54.3142, 48.4031, "Europe/Ulyanovsk"),
    "ulyanovsk": (54.3142, 48.4031, "Europe/Ulyanovsk"),
    "томск": (56.4846, 84.9482, "Asia/Tomsk"),
    "tomsk": (56.4846, 84.9482, "Asia/Tomsk"),
    "кемерово": (55.3909, 86.0468, "Asia/Novokuznetsk"),
    "kemerovo": (55.3909, 86.0468, "Asia/Novokuznetsk"),
    "ярославль": (57.6261, 39.8845, "Europe/Moscow"),
    "yaroslavl": (57.6261, 39.8845, "Europe/Moscow"),
    "махачкала": (42.9849, 47.5047, "Europe/Moscow"),
    "makhachkala": (42.9849, 47.5047, "Europe/Moscow"),
    "казань": (55.7963, 49.1088, "Europe/Moscow"),
    "kazan": (55.7963, 49.1088, "Europe/Moscow"),
    "самара": (53.1959, 50.1002, "Europe/Samara"),
    "samara": (53.1959, 50.1002, "Europe/Samara"),
    "ростов-на-дону": (47.2357, 39.7015, "Europe/Moscow"),
    "rostov-on-don": (47.2357, 39.7015, "Europe/Moscow"),
    "краснодар": (45.0355, 38.9753, "Europe/Moscow"),
    "krasnodar": (45.0355, 38.9753, "Europe/Moscow"),
    "уфа": (54.7388, 55.9721, "Asia/Yekaterinburg"),
    "ufa": (54.7388, 55.9721, "Asia/Yekaterinburg"),
    "пермь": (58.0105, 56.2502, "Asia/Yekaterinburg"),
    "perm": (58.0105, 56.2502, "Asia/Yekaterinburg"),
    "воронеж": (51.6720, 39.1843, "Europe/Moscow"),
    "volgograd": (48.7080, 44.5133, "Europe/Volgograd"),
    "волгоград": (48.7080, 44.5133, "Europe/Volgograd"),
    "сочи": (43.6028, 39.7342, "Europe/Moscow"),
    "sochi": (43.6028, 39.7342, "Europe/Moscow"),
    "владивосток": (43.1155, 131.8855, "Asia/Vladivostok"),
    "vladivostok": (43.1155, 131.8855, "Asia/Vladivostok"),
    "иркутск": (52.2869, 104.3050, "Asia/Irkutsk"),
    "irkutsk": (52.2869, 104.3050, "Asia/Irkutsk"),
    "омск": (54.9885, 73.3242, "Asia/Omsk"),
    "omsk": (54.9885, 73.3242, "Asia/Omsk"),
    "тбилиси": (41.7151, 44.8271, "Asia/Tbilisi"),
    "tbilisi": (41.7151, 44.8271, "Asia/Tbilisi"),
    "ереван": (40.1792, 44.4991, "Asia/Yerevan"),
    "yerevan": (40.1792, 44.4991, "Asia/Yerevan"),
    "баку": (40.4093, 49.8671, "Asia/Baku"),
    "baku": (40.4093, 49.8671, "Asia/Baku"),
    "лондон": (51.5074, -0.1278, "Europe/London"),
    "london": (51.5074, -0.1278, "Europe/London"),
    "берлин": (52.5200, 13.4050, "Europe/Berlin"),
    "berlin": (52.5200, 13.4050, "Europe/Berlin"),
    "париж": (48.8566, 2.3522, "Europe/Paris"),
    "paris": (48.8566, 2.3522, "Europe/Paris"),
    "нью-йорк": (40.7128, -74.0060, "America/New_York"),
    "new york": (40.7128, -74.0060, "America/New_York"),
    "дубай": (25.2048, 55.2708, "Asia/Dubai"),
    "dubai": (25.2048, 55.2708, "Asia/Dubai"),
    "стамбул": (41.0082, 28.9784, "Europe/Istanbul"),
    "istanbul": (41.0082, 28.9784, "Europe/Istanbul"),
}

TIMEZONE_COORDS: dict[str, tuple[float, float]] = {
    "UTC": (51.5074, 0.0),
    "Europe/Moscow": (55.7558, 37.6173),
    "Europe/Kyiv": (50.4501, 30.5234),
    "Europe/Minsk": (53.9006, 27.5590),
    "Asia/Almaty": (43.2220, 76.8512),
    "Asia/Tashkent": (41.2995, 69.2401),
    "Asia/Yekaterinburg": (56.8389, 60.6057),
    "Asia/Novosibirsk": (55.0084, 82.9357),
    "Asia/Vladivostok": (43.1155, 131.8855),
    "Europe/London": (51.5074, -0.1278),
    "Europe/Berlin": (52.5200, 13.4050),
    "America/New_York": (40.7128, -74.0060),
}


@dataclass(frozen=True)
class GeocodedLocation:
    display_name: str
    lat: float
    lon: float
    timezone: str
    source: str


def normalize_city_query(city: str) -> str:
    value = city.strip().lower().replace("ё", "е")
    for prefix in ("г.", "г ", "город "):
        if value.startswith(prefix):
            value = value[len(prefix) :].strip()
    value = re.sub(r"\s+", " ", value)
    return value


def lookup_static_city(city: str) -> GeocodedLocation | None:
    normalized = normalize_city_query(city)
    keys = [normalized]
    if "," in normalized:
        keys.append(normalized.split(",", 1)[0].strip())
    for key in keys:
        if not key:
            continue
        hit = STATIC_CITIES.get(key)
        if hit is None:
            continue
        lat, lon, tz = hit
        return GeocodedLocation(
            display_name=city.strip(),
            lat=lat,
            lon=lon,
            timezone=normalize_timezone(tz),
            source="static",
        )
    return None


def _timezone_at_sync(lat: float, lon: float) -> str:
    global _timezone_finder
    try:
        if _timezone_finder is None:
            _timezone_finder = TimezoneFinder(in_memory=True)
        tz_name = _timezone_finder.timezone_at(lat=lat, lng=lon)
        if tz_name:
            ZoneInfo(tz_name)
            return tz_name
    except Exception:
        logger.debug("timezone lookup failed lat=%s lon=%s", lat, lon, exc_info=True)
    return "UTC"


async def timezone_at(lat: float, lon: float) -> str:
    return await asyncio.to_thread(_timezone_at_sync, lat, lon)


def warm_timezone_finder() -> None:
    """Load timezone polygons once; safe to call from a background thread at startup."""
    _timezone_at_sync(55.7558, 37.6173)


def shorten_display_name(display_name: str, fallback: str) -> str:
    first = display_name.split(",", 1)[0].strip()
    return first or fallback.strip()


async def _fetch_nominatim(query: str) -> GeocodedLocation | None:
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(NOMINATIM_URL, params=params) as response:
                if response.status != 200:
                    return None
                data = await response.json()
    except Exception:
        logger.warning("nominatim request failed query=%r", query, exc_info=True)
        return None

    if not data:
        return None

    item = data[0]
    try:
        lat = float(item["lat"])
        lon = float(item["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    raw_name = str(item.get("display_name") or query.strip())
    display_name = shorten_display_name(raw_name, query)
    tz = await timezone_at(lat, lon)
    return GeocodedLocation(
        display_name=display_name,
        lat=lat,
        lon=lon,
        timezone=tz,
        source="nominatim",
    )


async def resolve_city(city: str, db: Database | None = None) -> GeocodedLocation | None:
    raw = city.strip()
    if len(raw) < 2:
        return None

    static = lookup_static_city(raw)
    if static is not None:
        if db is not None:
            await db.save_city_geocache(normalize_city_query(raw), static)
        return static

    cache_key = normalize_city_query(raw)
    if db is not None:
        cached = await db.get_city_geocache(cache_key)
        if cached is not None:
            return cached

    for query in (raw, cache_key):
        result = await _fetch_nominatim(query)
        if result is not None:
            if db is not None:
                await db.save_city_geocache(cache_key, result)
            return result

    return None


def resolve_birth_location(
    city: str | None,
    timezone_name: str,
    *,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> tuple[float, float, str]:
    if lat is not None and lon is not None and birth_timezone:
        return lat, lon, normalize_timezone(birth_timezone)

    if birth_timezone:
        tz = normalize_timezone(birth_timezone)
        if tz in TIMEZONE_COORDS:
            fb_lat, fb_lon = TIMEZONE_COORDS[tz]
            return fb_lat, fb_lon, tz
        try:
            ZoneInfo(tz)
            return TIMEZONE_COORDS["UTC"][0], TIMEZONE_COORDS["UTC"][1], tz
        except Exception:
            pass

    if city:
        static = lookup_static_city(city)
        if static is not None:
            return static.lat, static.lon, static.timezone

    fallback_tz = normalize_timezone(timezone_name)
    if fallback_tz in TIMEZONE_COORDS:
        fb_lat, fb_lon = TIMEZONE_COORDS[fallback_tz]
        return fb_lat, fb_lon, fallback_tz

    try:
        ZoneInfo(fallback_tz)
        return TIMEZONE_COORDS["UTC"][0], TIMEZONE_COORDS["UTC"][1], fallback_tz
    except Exception:
        return TIMEZONE_COORDS["UTC"][0], TIMEZONE_COORDS["UTC"][1], "UTC"
