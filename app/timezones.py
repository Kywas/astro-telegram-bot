from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE_OPTIONS: list[tuple[str, dict[str, str]]] = [
    ("UTC", {"ru": "UTC", "en": "UTC"}),
    ("Europe/Moscow", {"ru": "Москва", "en": "Moscow"}),
    ("Europe/Kyiv", {"ru": "Киев", "en": "Kyiv"}),
    ("Europe/Minsk", {"ru": "Минск", "en": "Minsk"}),
    ("Asia/Almaty", {"ru": "Алматы", "en": "Almaty"}),
    ("Asia/Tashkent", {"ru": "Ташкент", "en": "Tashkent"}),
    ("Asia/Yekaterinburg", {"ru": "Екатеринбург", "en": "Yekaterinburg"}),
    ("Asia/Novosibirsk", {"ru": "Новосибирск", "en": "Novosibirsk"}),
    ("Asia/Vladivostok", {"ru": "Владивосток", "en": "Vladivostok"}),
    ("Europe/London", {"ru": "Лондон", "en": "London"}),
    ("Europe/Berlin", {"ru": "Берлин", "en": "Berlin"}),
    ("America/New_York", {"ru": "Нью-Йорк", "en": "New York"}),
]

VALID_TIMEZONES = {tz for tz, _ in TIMEZONE_OPTIONS}


def normalize_timezone(tz_name: str | None) -> str:
    if not tz_name:
        return "UTC"
    if tz_name in VALID_TIMEZONES:
        return tz_name
    try:
        ZoneInfo(tz_name)
        return tz_name
    except Exception:
        return "UTC"


def timezone_label(locale: str, tz_name: str) -> str:
    normalized = normalize_timezone(tz_name)
    for tz, labels in TIMEZONE_OPTIONS:
        if tz == normalized:
            return labels.get(locale, labels["en"])
    return normalized


def timezone_label_with_offset(locale: str, tz_name: str, *, at: datetime | None = None) -> str:
    normalized = normalize_timezone(tz_name)
    try:
        tz = ZoneInfo(normalized)
    except Exception:
        return timezone_label(locale, normalized)

    moment = at or datetime.now(tz)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
    else:
        moment = moment.astimezone(tz)

    label = timezone_label(locale, normalized)
    offset = moment.strftime("%z")
    if not offset:
        return label

    sign = offset[0]
    hours = int(offset[1:3])
    minutes = int(offset[3:5])
    if minutes:
        offset_text = f"UTC{sign}{hours}:{minutes:02d}"
    else:
        offset_text = f"UTC{sign}{hours}"
    return f"{label} ({offset_text})"


def user_local_hhmm(now_utc: datetime, tz_name: str) -> str:
    tz = ZoneInfo(normalize_timezone(tz_name))
    return now_utc.astimezone(tz).strftime("%H:%M")


def user_local_date_key(now_utc: datetime, tz_name: str) -> str:
    tz = ZoneInfo(normalize_timezone(tz_name))
    return now_utc.astimezone(tz).strftime("%Y-%m-%d")


def default_timezone_for_locale(locale: str) -> str:
    if locale == "ru":
        return "Europe/Moscow"
    return "UTC"
