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
        "SUN": "ваш характер",
        "MOON": "ваши чувства",
        "MERCURY": "как вы говорите",
        "VENUS": "ваша нежность",
        "MARS": "ваша активность",
        "JUPITER": "ваша поддержка",
        "SATURN": "ваши правила",
    },
    "en": {
        "SUN": "your character",
        "MOON": "your feelings",
        "MERCURY": "how you talk",
        "VENUS": "your warmth",
        "MARS": "your drive",
        "JUPITER": "your support",
        "SATURN": "your boundaries",
    },
}

PARTNER_PLANET_PLAIN = {
    "ru": {
        "SUN": "характер партнёра",
        "MOON": "чувства партнёра",
        "MERCURY": "как говорит партнёр",
        "VENUS": "нежность партнёра",
        "MARS": "активность партнёра",
        "JUPITER": "поддержка партнёра",
        "SATURN": "правила партнёра",
    },
    "en": {
        "SUN": "partner's character",
        "MOON": "partner's feelings",
        "MERCURY": "how your partner talks",
        "VENUS": "partner's warmth",
        "MARS": "partner's drive",
        "JUPITER": "partner's support",
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


def resolve_compat_style(profile, *, default: str = "plain") -> str:
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
            "Я разбил разбор на несколько коротких кусков — про характер, притяжение, быт и вывод. "
            "Можно читать подряд, можно перепрыгнуть к тому, что зацепило."
        )
    return (
        "I split this into a few short chunks — character, pull, daily life, and the takeaway. "
        "Read straight through or jump to what grabs you."
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
            f"💞 Разбор пары · {mode_label}",
            f"{user_sign} и {partner_sign}",
        ]
    return [
        f"💞 Pair reading · {mode_label}",
        f"{user_sign} and {partner_sign}",
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
    if lang == "ru":
        return f"Тут стыкуются {user_role} и {partner_role}. {tone.capitalize()}."
    return f"Here your {user_role} meets {partner_role}. {tone.capitalize()}."


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


_PLAIN_STEP_HEADER = re.compile(r"(^|\n)([☀️⚖️🏠🌐✨📊💞🔢🌑🤝📋][^\n]*?)Шаг \d+\.\s*", re.MULTILINE)


def _plain_house_name(locale: str, house: str) -> str:
    from app.synastry_houses import HOUSE_SECTION_PLAIN

    lang = _lang(locale)
    number = int(house)
    entry = HOUSE_SECTION_PLAIN[lang].get(number)
    if entry:
        return entry[0].lower() if lang == "ru" else entry[0]
    return f"сфера {number}" if lang == "ru" else f"area {number}"


def _plain_house_replacer_ru(match: re.Match[str]) -> str:
    return _plain_house_name("ru", match.group(1))


def _plain_house_replacer_en(match: re.Match[str]) -> str:
    return _plain_house_name("en", match.group(1))


_PLAIN_REPLACEMENTS = {
    "ru": (
        (r"\bсинастри\w*", "связь"),
        (r"\bкомпозит\w*", "союз"),
        (r"\bнатальн\w*", ""),
        (r"\bстихи\w*", "тип темпа"),
        (r"\bASC\b", "образ"),
        (r"\bDSC\b", "партнёр"),
        (r"сфера (\d+)", _plain_house_replacer_ru),
        (r"(\d+)‑й дом", _plain_house_replacer_ru),
        (r"(\d+)-й дом", _plain_house_replacer_ru),
        (r"Placidus", ""),
        (r"Swiss Ephemeris", ""),
        (r"  +", " "),
    ),
    "en": (
        (r"\bsynastr\w*", "bond"),
        (r"\bcomposite\b", "union"),
        (r"\bnatal\b", ""),
        (r"\belement\w*", "pace type"),
        (r"\bASC\b", "self-image"),
        (r"\bDSC\b", "partner"),
        (r"area (\d+)", _plain_house_replacer_en),
        (r"(\d+)th house", _plain_house_replacer_en),
        (r"Placidus", ""),
        (r"Swiss Ephemeris", ""),
        (r"  +", " "),
    ),
}


_PLAIN_BULLET_LIMIT = {
    "overview": 4,
    "attraction": 5,
    "bond": 4,
    "depth": 4,
    "symbols": 4,
    "result": 5,
}

_PLAIN_HEADER = re.compile(
    r"^[☀️⚖️🏠🌐✨📊💞🔢🌑🤝📋↗️🔗🔥🧠💡ℹ️⚠️]",
)


def compact_plain_theme_body(text: str, theme_key: str, locale: str) -> str:
    """Trim plain themed compat pages for shorter Telegram reads."""
    if not text.strip():
        return text
    lang = _lang(locale)
    skip_prefixes = ("ℹ️", "⚠️", "💡 Что бы")
    if lang == "ru":
        skip_contains = ("Swiss Ephemeris", "Placidus", "данный разбор", "не является")
    else:
        skip_contains = ("Swiss Ephemeris", "Placidus", "this reading", "not a substitute")

    cleaned_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if any(stripped.startswith(prefix) for prefix in skip_prefixes):
            continue
        if any(part in stripped.lower() for part in skip_contains):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    bullet_limit = _PLAIN_BULLET_LIMIT.get(theme_key, 5)
    bullets_used = 0
    kept_blocks: list[str] = []

    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        header = lines[0]
        if _PLAIN_HEADER.match(header):
            compact = [header]
            intro_added = False
            for ln in lines[1:]:
                if ln.startswith("•"):
                    if bullets_used >= bullet_limit:
                        continue
                    bullets_used += 1
                    compact.append(ln)
                elif not intro_added and len(compact) == 1:
                    sentence = ln.split(". ")[0].strip()
                    if len(sentence) > 100:
                        sentence = sentence[:97].rstrip() + "…"
                    if sentence and not sentence.endswith((".", "…", "!")):
                        sentence += "."
                    if sentence:
                        compact.append(sentence)
                        intro_added = True
            if len(compact) > 1:
                kept_blocks.append("\n".join(compact))
        else:
            bullets = [ln for ln in lines if ln.startswith("•")]
            prose = [ln for ln in lines if not ln.startswith("•")]
            if bullets:
                for ln in bullets:
                    if bullets_used >= bullet_limit:
                        break
                    kept_blocks.append(ln)
                    bullets_used += 1
            elif theme_key == "result" and prose:
                kept_blocks.append("\n".join(prose[:2]))

    result = re.sub(r"\n{3,}", "\n\n", "\n\n".join(kept_blocks).strip())
    return result.strip()


def apply_synastry_style(text: str, locale: str, style: str) -> str:
    if use_synastry_terms(style):
        return text
    result = _ORB_PATTERN.sub("", text)
    result = _PLAIN_STEP_HEADER.sub(r"\1\2", result)
    result = re.sub(r"Шаг \d+\.\s*", "", result)
    result = re.sub(r"Step \d+\.\s*", "", result, flags=re.IGNORECASE)
    lang = _lang(locale)
    for pattern, replacement in _PLAIN_REPLACEMENTS[lang]:
        if callable(replacement):
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        else:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    result = re.sub(r" — — ", " — ", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = re.sub(r" +\n", "\n", result.strip())
    from app.reading_voice import humanize_compat_plain

    return humanize_compat_plain(result, locale)
