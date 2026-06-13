"""Resolve the user's current location for transits, moon calendar, and notifications."""
from __future__ import annotations

from app.timezones import default_timezone_for_locale, normalize_timezone


def resolve_user_timezone(profile, locale: str) -> str:
    if profile:
        if getattr(profile, "current_timezone", None):
            return normalize_timezone(profile.current_timezone)
        if profile.timezone:
            return normalize_timezone(profile.timezone)
        if profile.birth_timezone:
            return normalize_timezone(profile.birth_timezone)
    return default_timezone_for_locale(locale)


def resolve_user_coords(profile) -> tuple[float | None, float | None]:
    if profile is None:
        return None, None
    if profile.current_lat is not None and profile.current_lon is not None:
        return profile.current_lat, profile.current_lon
    return profile.birth_lat, profile.birth_lon


def current_location_label(profile, locale: str) -> str:
    if profile is None:
        return "-"
    if profile.current_city:
        return profile.current_city
    if locale == "ru":
        return "не указано"
    return "not set"
