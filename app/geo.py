"""Approximate coordinates for birth city / timezone fallback."""

from zoneinfo import ZoneInfo

# lat, lon, timezone (optional override)
CITY_COORDS: dict[str, tuple[float, float, str | None]] = {
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
    "ташкент": (41.2995, 69.2401, "Asia/Tashkent"),
    "tashkent": (41.2995, 69.2401, "Asia/Tashkent"),
    "екатеринбург": (56.8389, 60.6057, "Asia/Yekaterinburg"),
    "yekaterinburg": (56.8389, 60.6057, "Asia/Yekaterinburg"),
    "новосибирск": (55.0084, 82.9357, "Asia/Novosibirsk"),
    "novosibirsk": (55.0084, 82.9357, "Asia/Novosibirsk"),
    "владивосток": (43.1155, 131.8855, "Asia/Vladivostok"),
    "vladivostok": (43.1155, 131.8855, "Asia/Vladivostok"),
    "лондон": (51.5074, -0.1278, "Europe/London"),
    "london": (51.5074, -0.1278, "Europe/London"),
    "берлин": (52.5200, 13.4050, "Europe/Berlin"),
    "berlin": (52.5200, 13.4050, "Europe/Berlin"),
    "нью-йорк": (40.7128, -74.0060, "America/New_York"),
    "new york": (40.7128, -74.0060, "America/New_York"),
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


def resolve_birth_location(city: str | None, timezone_name: str) -> tuple[float, float, str]:
    if city:
        key = city.strip().lower()
        if key in CITY_COORDS:
            lat, lon, tz_override = CITY_COORDS[key]
            tz = tz_override or timezone_name
            return lat, lon, tz

    if timezone_name in TIMEZONE_COORDS:
        lat, lon = TIMEZONE_COORDS[timezone_name]
        return lat, lon, timezone_name

    try:
        ZoneInfo(timezone_name)
        return TIMEZONE_COORDS["UTC"][0], TIMEZONE_COORDS["UTC"][1], timezone_name
    except Exception:
        return TIMEZONE_COORDS["UTC"][0], TIMEZONE_COORDS["UTC"][1], "UTC"
