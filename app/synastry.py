from dataclasses import dataclass
from datetime import date, time

from app.sun_sign_compat import (
    analyze_sun_sign_compat,
    format_sun_sign_compat_section,
    normalize_sign_key,
    sun_sign_base_score,
)
from app.astro_engine import build_synastry_analysis
from app.compatibility import compatibility_summary
from app.synastry_style import apply_synastry_style, compact_plain_theme_body
from app.synastry_sections import SynastrySection, SynastryTheme, group_synastry_themes
from app.zodiac import resolve_sun_sign


@dataclass
class SynastryResult:
    score: int
    relation_mode: str
    partner_sign: str
    details: str
    partner_name: str | None = None
    themes: tuple = ()


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
    style: str = "plain",
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
        user_sign_key = normalize_sign_key(user_sign)
        sun_compat = (
            analyze_sun_sign_compat(user_sign_key or user_sign, partner_sign)
            if user_sign_key or user_sign
            else None
        )
        if sun_compat is None:
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
        if style == "plain":
            details_lines = [
                apply_synastry_style(format_sun_sign_compat_section(locale, sun_compat, style=style), locale, style),
                "",
                (
                    "ℹ️ Это базовый разбор по знакам. "
                    "Добавьте дату рождения в профиль — откроется полный разбор."
                    if locale == "ru"
                    else "ℹ️ Sun-sign baseline only. Add your birth date in profile for the full reading."
                ),
            ]
        else:
            details_lines = [
                apply_synastry_style(format_sun_sign_compat_section(locale, sun_compat), locale, style),
                "",
                (
                    "ℹ️ Это базовый уровень по солнечным знакам. "
                    "Укажите дату рождения в профиле — откроется полная синастрия по планетам."
                    if locale == "ru"
                    else "ℹ️ Sun-sign baseline only. Add your birth date in profile for full planetary synastry."
                ),
            ]
        score = sun_sign_base_score(sun_compat)
        body = "\n".join(details_lines)
        basic_title = "☀️ Совместимость по знакам" if locale == "ru" else "☀️ Sun sign match"

        return SynastryResult(
            score=score,
            relation_mode=relation_mode,
            partner_sign=partner_sign,
            details=body,
            partner_name=partner_name,
            themes=(SynastryTheme("basic", basic_title, body),),
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
        style=style,
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

    summary_text = compatibility_summary(locale, analysis.score, style=style, mode=relation_mode)
    sections = (*analysis.sections, SynastrySection("compat_summary", summary_text))
    themes = tuple(group_synastry_themes(locale, list(sections), style=style, mode=relation_mode))
    if style == "plain":
        themes = tuple(
            SynastryTheme(
                theme.key,
                theme.title,
                compact_plain_theme_body(
                    apply_synastry_style(theme.body, locale, style),
                    theme.key,
                    locale,
                ),
            )
            for theme in themes
        )
    details = apply_synastry_style(f"{analysis.details}\n\n{summary_text}", locale, style)
    return SynastryResult(
        score=analysis.score,
        relation_mode=relation_mode,
        partner_sign=analysis.partner_sign,
        details=details,
        partner_name=partner_name,
        themes=themes,
    )


def build_synastry_for_partner_profile(
    locale: str,
    user_profile,
    partner,
    relation_mode: str,
    *,
    style: str = "plain",
) -> SynastryResult:
    return build_synastry(
        locale,
        user_profile.sign or "",
        partner.birth_date,
        relation_mode,
        style=style,
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
