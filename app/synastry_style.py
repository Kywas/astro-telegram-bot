"""Compatibility report style: plain language vs astrological terms."""
from __future__ import annotations

import re

from app.forecast_text import _aspect_label

PLAIN_ASPECT = {
    "ru": {
        "conjunction": "усиливает",
        "sextile": "мягко поддерживает",
        "trine": "легко поддерживает",
        "square": "давит на",
        "opposition": "тянет в разные стороны",
    },
    "en": {
        "conjunction": "intensifies",
        "sextile": "gently supports",
        "trine": "easily supports",
        "square": "presses on",
        "opposition": "pulls in opposite directions",
    },
}

PLAIN_ASPECT_NOUN = {
    "ru": {
        "conjunction": "усиление",
        "sextile": "мягкий контакт",
        "trine": "лёгкая поддержка",
        "square": "напряжение",
        "opposition": "контраст",
    },
    "en": {
        "conjunction": "intensification",
        "sextile": "gentle contact",
        "trine": "easy support",
        "square": "tension",
        "opposition": "contrast",
    },
}

USER_PLANET_PLAIN = {
    "ru": {
        "SUN": "ваша суть и цели",
        "MOON": "ваши эмоции",
        "MERCURY": "ваш стиль общения",
        "VENUS": "ваша забота и притяжение",
        "MARS": "ваша энергия и инициатива",
        "JUPITER": "ваш рост и опора",
        "SATURN": "ваши границы и ответственность",
    },
    "en": {
        "SUN": "your core and goals",
        "MOON": "your emotions",
        "MERCURY": "your communication style",
        "VENUS": "your affection and attraction",
        "MARS": "your drive and initiative",
        "JUPITER": "your growth and support",
        "SATURN": "your boundaries and responsibility",
    },
}

PARTNER_PLANET_PLAIN = {
    "ru": {
        "SUN": "суть и цели партнёра",
        "MOON": "эмоции партнёра",
        "MERCURY": "стиль общения партнёра",
        "VENUS": "забота и притяжение партнёра",
        "MARS": "энергия партнёра",
        "JUPITER": "рост и опора партнёра",
        "SATURN": "границы партнёра",
    },
    "en": {
        "SUN": "partner's core and goals",
        "MOON": "partner's emotions",
        "MERCURY": "partner's communication style",
        "VENUS": "partner's affection and attraction",
        "MARS": "partner's drive",
        "JUPITER": "partner's growth and support",
        "SATURN": "partner's boundaries",
    },
}

ELEMENT_PLAIN = {
    "ru": {"fire": "энергия", "earth": "стабильность", "air": "общение", "water": "чувства"},
    "en": {"fire": "energy", "earth": "stability", "air": "communication", "water": "feelings"},
}

_ORB_PATTERN = re.compile(r"\s*\(\d+\.\d+°\)")


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def resolve_compat_style(profile, *, default: str = "terms") -> str:
    if profile is None:
        return default
    style = (
        getattr(profile, "compat_style", None)
        or getattr(profile, "horoscope_style", None)
        or getattr(profile, "natal_style", None)
        or default
    )
    return "plain" if style == "plain" else "terms"


def use_synastry_terms(style: str) -> bool:
    return style != "plain"


def format_aspect_label(locale: str, aspect: str, style: str) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        return _aspect_label(locale, aspect)
    return PLAIN_ASPECT_NOUN[lang].get(aspect, aspect)


def format_aspect_verb(locale: str, aspect: str, style: str) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        return _aspect_label(locale, aspect)
    return PLAIN_ASPECT[lang].get(aspect, aspect)


def format_orb_suffix(orb: float, style: str, *, tight_only: bool = True) -> str:
    if not use_synastry_terms(style):
        return ""
    if tight_only and orb > 2.5:
        return ""
    return f" ({orb:.1f}°)"


def format_user_planet(locale: str, planet: str, style: str) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        labels = {
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
        return labels[lang].get(planet, planet)
    return USER_PLANET_PLAIN[lang].get(planet, planet)


def format_partner_planet(locale: str, planet: str, style: str) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        labels = {
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
        return labels[lang].get(planet, planet)
    return PARTNER_PLANET_PLAIN[lang].get(planet, planet)


def format_element_plain(locale: str, element: str) -> str:
    return ELEMENT_PLAIN[_lang(locale)].get(element, element)


def format_comprehensive_scope_intro(locale: str, *, style: str = "terms") -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        if lang == "ru":
            return (
                "Комплексная оценка: базовый (знаки, ASC) · средний (синастрия, дома) · "
                "продвинутый (композит, прогрессии, Лилит/Селена, карма, транзиты) · "
                "эзотерический (нумерология, Таро, энергии). Итог — таблица +1/−1."
            )
        return (
            "Comprehensive assessment: basic (signs, ASC) · medium (synastry, houses) · "
            "advanced (composite, progressions, Lilith/Selena, karma, transits) · "
            "esoteric (numerology, Tarot, energies). Final scorecard: +1/−1."
        )
    if lang == "ru":
        return (
            "Полный разбор: характер и образ пары, связи планет и дома, "
            "глубинные и будущие темы, числа и карты — всё сводится в итоговую таблицу."
        )
    return (
        "Full reading: character and pair image, planet links and houses, "
        "deeper and future themes, numbers and cards — all roll up into the final table."
    )


def format_report_header(
    locale: str,
    *,
    mode_label: str,
    user_sign: str,
    partner_sign: str,
    style: str,
) -> list[str]:
    lang = _lang(locale)
    if use_synastry_terms(style):
        if lang == "ru":
            return [
                f"Расчёт: Swiss Ephemeris · режим «{mode_label}»",
                f"• {user_sign} + {partner_sign}",
            ]
        return [
            f"Calculation: Swiss Ephemeris · {mode_label} mode",
            f"• {user_sign} + {partner_sign}",
        ]
    if lang == "ru":
        return [
            "💬 Совместимость · простым языком",
            f"• Режим «{mode_label}» · {user_sign} + {partner_sign}",
        ]
    return [
        "💬 Compatibility · plain language",
        f"• {mode_label} mode · {user_sign} + {partner_sign}",
    ]


def format_cross_link_line(
    locale: str,
    user_planet: str,
    partner_planet: str,
    aspect: str,
    tone: str,
    orb: float,
    style: str,
) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        user_name = format_user_planet(locale, user_planet, style)
        partner_name = format_partner_planet(locale, partner_planet, style)
        aspect_label = format_aspect_label(locale, aspect, style)
        orb_part = format_orb_suffix(orb, style)
        if lang == "ru":
            return f"ваше {user_name}, {aspect_label} к {partner_name}{orb_part} — {tone}"
        return f"your {user_name} {aspect_label} partner's {partner_name}{orb_part} — {tone}"

    user_role = format_user_planet(locale, user_planet, style)
    partner_role = format_partner_planet(locale, partner_planet, style)
    verb = format_aspect_verb(locale, aspect, style)
    if lang == "ru":
        return f"{user_role.capitalize()} {verb} {partner_role} — {tone}"
    return f"{user_role.capitalize()} {verb} {partner_role} — {tone}"


def format_seal_link_line(
    locale: str,
    *,
    direction: str,
    source_planet: str,
    target_planet: str,
    aspect: str,
    style: str,
    source_label: str,
    target_label: str,
) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        aspect_label = format_aspect_label(locale, aspect, style)
        if lang == "ru":
            if direction == "user_to_partner":
                return f"ваш {source_label}, {aspect_label} к {target_label} партнёра"
            return f"{source_label} партнёра, {aspect_label} к вашему {target_label}"
        if direction == "user_to_partner":
            return f"your {source_label} {aspect_label} partner's {target_label}"
        return f"partner's {source_label} {aspect_label} your {target_label}"

    if source_planet == "JUPITER":
        source_plain = "щедрость и поддержка" if lang == "ru" else "generosity and support"
    else:
        source_plain = "ограничения и уроки" if lang == "ru" else "limits and lessons"
    if target_planet == "SUN":
        target_plain = (
            "суть партнёра" if direction == "user_to_partner" and lang == "ru"
            else "partner's core" if direction == "user_to_partner"
            else "ваша суть" if lang == "ru"
            else "your core"
        )
    else:
        target_plain = (
            "эмоции партнёра" if direction == "user_to_partner" and lang == "ru"
            else "partner's emotions" if direction == "user_to_partner"
            else "ваши эмоции" if lang == "ru"
            else "your emotions"
        )
    verb = format_aspect_verb(locale, aspect, style)
    if lang == "ru":
        if direction == "user_to_partner":
            return f"ваша {source_plain} {verb} {target_plain}"
        return f"{source_plain} партнёра {verb} {target_plain}"
    if direction == "user_to_partner":
        return f"your {source_plain} {verb} {target_plain}"
    return f"partner's {source_plain} {verb} {target_plain}"


def format_transit_hit_line(
    locale: str,
    *,
    transit_planet: str,
    target_owner: str,
    target_planet: str,
    aspect: str,
    style: str,
    transit_name: str,
    target_name: str,
    owner_label: str,
    aspect_label: str,
) -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        if lang == "ru":
            return (
                f"транзитный {transit_name}, {aspect_label} "
                f"к {owner_label} {target_name}"
            )
        return (
            f"transiting {transit_name} {aspect_label} "
            f"{owner_label} {target_name}"
        )

    transit_plain = {
        "JUPITER": "период расширения" if lang == "ru" else "expansion phase",
        "VENUS": "период тепла" if lang == "ru" else "warm phase",
        "SATURN": "период проверки" if lang == "ru" else "testing phase",
        "URANUS": "время перемен" if lang == "ru" else "change phase",
        "PLUTO": "глубокая трансформация" if lang == "ru" else "deep transformation",
    }.get(transit_planet, transit_name)
    target_plain = (
        format_user_planet(locale, target_planet, style)
        if target_owner == "user"
        else format_partner_planet(locale, target_planet, style)
    )
    verb = format_aspect_verb(locale, aspect, style)
    if lang == "ru":
        return f"сейчас {transit_plain} {verb} {target_plain}"
    return f"now {transit_plain} {verb} {target_plain}"


def apply_synastry_style(text: str, locale: str, style: str) -> str:
    if use_synastry_terms(style):
        return text
    result = _ORB_PATTERN.sub("", text)
    result = re.sub(r"  +", " ", result)
    return re.sub(r" +\n", "\n", result)
