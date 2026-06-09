from dataclasses import dataclass
from datetime import date, time

from app.astro_engine import build_synastry_analysis
from app.compatibility import compatibility_summary
from app.zodiac import resolve_sun_sign


@dataclass
class SynastryResult:
    score: int
    relation_mode: str
    partner_sign: str
    details: str
    partner_name: str | None = None


def build_synastry(
    locale: str,
    user_sign: str,
    partner_birth_date: date,
    relation_mode: str,
    *,
    user_birth_date: date | None = None,
    user_birth_time: time | None = None,
    user_city: str | None = None,
    user_timezone: str = "UTC",
    user_id: int | None = None,
    partner_birth_time: time | None = None,
    partner_city: str | None = None,
    partner_timezone: str | None = None,
    user_lat: float | None = None,
    user_lon: float | None = None,
    user_birth_timezone: str | None = None,
    partner_lat: float | None = None,
    partner_lon: float | None = None,
    partner_birth_timezone: str | None = None,
    partner_name: str | None = None,
) -> SynastryResult:
    if user_birth_date is None:
        partner_sign = resolve_sun_sign(
            partner_birth_date,
            partner_birth_time,
            city=partner_city,
            timezone_name=partner_timezone or user_timezone or "UTC",
            lat=partner_lat,
            lon=partner_lon,
            birth_timezone=partner_birth_timezone,
        )
        unavailable = (
            "Синастрия недоступна — заполните дату рождения в профиле."
            if locale == "ru"
            else "Synastry unavailable — complete your birth date in profile."
        )
        return SynastryResult(
            score=0,
            relation_mode=relation_mode,
            partner_sign=partner_sign,
            details=unavailable,
            partner_name=partner_name,
        )

    analysis = build_synastry_analysis(
        user_birth_date=user_birth_date,
        user_birth_time=user_birth_time,
        user_city=user_city,
        user_timezone=user_timezone,
        partner_birth_date=partner_birth_date,
        partner_birth_time=partner_birth_time,
        partner_city=partner_city,
        partner_timezone=partner_timezone,
        relation_mode=relation_mode,
        locale=locale,
        user_id=user_id,
        user_lat=user_lat,
        user_lon=user_lon,
        user_birth_timezone=user_birth_timezone,
        partner_lat=partner_lat,
        partner_lon=partner_lon,
        partner_birth_timezone=partner_birth_timezone,
    )
    if analysis is None:
        partner_sign = resolve_sun_sign(
            partner_birth_date,
            partner_birth_time,
            city=partner_city,
            timezone_name=partner_timezone or user_timezone or "UTC",
            lat=partner_lat,
            lon=partner_lon,
            birth_timezone=partner_birth_timezone,
        )
        unavailable = (
            "Не удалось рассчитать синастрию. Попробуйте позже."
            if locale == "ru"
            else "Could not calculate synastry. Please try again later."
        )
        return SynastryResult(
            score=0,
            relation_mode=relation_mode,
            partner_sign=partner_sign,
            details=unavailable,
            partner_name=partner_name,
        )

    details = f"{analysis.details}\n\n{compatibility_summary(locale, analysis.score)}"
    return SynastryResult(
        score=analysis.score,
        relation_mode=relation_mode,
        partner_sign=analysis.partner_sign,
        details=details,
        partner_name=partner_name,
    )


def build_synastry_for_partner_profile(
    locale: str,
    user_profile,
    partner,
    relation_mode: str,
) -> SynastryResult:
    return build_synastry(
        locale,
        user_profile.sign or "",
        partner.birth_date,
        relation_mode,
        user_birth_date=user_profile.birth_date,
        user_birth_time=user_profile.birth_time,
        user_city=user_profile.city,
        user_timezone=user_profile.timezone or "UTC",
        user_id=user_profile.user_id,
        user_lat=user_profile.birth_lat,
        user_lon=user_profile.birth_lon,
        user_birth_timezone=user_profile.birth_timezone,
        partner_birth_time=partner.birth_time,
        partner_city=partner.city,
        partner_timezone=partner.timezone or user_profile.birth_timezone or user_profile.timezone or "UTC",
        partner_lat=partner.lat,
        partner_lon=partner.lon,
        partner_birth_timezone=partner.timezone,
        partner_name=partner.name,
    )
