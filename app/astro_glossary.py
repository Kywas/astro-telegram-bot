"""Plain-language glosses for astrological phrases shown to beginners."""
from __future__ import annotations

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
    "en": {
        "Aries": "Aries",
        "Taurus": "Taurus",
        "Gemini": "Gemini",
        "Cancer": "Cancer",
        "Leo": "Leo",
        "Virgo": "Virgo",
        "Libra": "Libra",
        "Scorpio": "Scorpio",
        "Sagittarius": "Sagittarius",
        "Capricorn": "Capricorn",
        "Aquarius": "Aquarius",
        "Pisces": "Pisces",
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _sign_label(locale: str, sign_key: str) -> str:
    return SIGN_LABELS[_lang(locale)].get(sign_key, sign_key)

# How the Moon feels in each zodiac sign (sign key = English name).
MOON_IN_SIGN_HINT = {
    "ru": {
        "Aries": "настроение прямое и энергичное — легче действовать, сложнее ждать",
        "Taurus": "хочется спокойствия, комфорта и предсказуемости",
        "Gemini": "много мыслей и разговоров, внимание быстро переключается",
        "Cancer": "чувствительность выше — важны близость и ощущение защищённости",
        "Leo": "эмоции ярче, хочется признания и тёплого отклика",
        "Virgo": "практичный настрой — внимание к деталям и порядку",
        "Libra": "фокус на гармонии в отношениях, сложнее принимать резкие решения",
        "Scorpio": "чувства глубже и интенсивнее, возможна скрытность",
        "Sagittarius": "оптимизм и тяга к свободе, новым идеям и планам",
        "Capricorn": "сдержанность и деловой тон — меньше суеты, больше ответственности",
        "Aquarius": "отстранённость и интерес к идеям, нестандартным решениям",
        "Pisces": "мечтательность и эмпатия, границы между «своим» и «чужим» размыты",
    },
    "en": {
        "Aries": "mood runs direct and energetic — easier to act, harder to wait",
        "Taurus": "a need for calm, comfort, and predictability",
        "Gemini": "lots of thoughts and talk, attention shifts quickly",
        "Cancer": "higher sensitivity — closeness and safety matter more",
        "Leo": "feelings grow brighter; recognition and warmth feel important",
        "Virgo": "a practical tone — focus on details and order",
        "Libra": "focus on harmony in relationships; sharp calls feel harder",
        "Scorpio": "deeper, more intense feelings; privacy may increase",
        "Sagittarius": "optimism and a pull toward freedom, ideas, and plans",
        "Capricorn": "restraint and a businesslike tone — less fuss, more duty",
        "Aquarius": "some distance and interest in ideas and unusual solutions",
        "Pisces": "dreaminess and empathy; boundaries between self and others blur",
    },
}

SIGN_TONE_HINT = {
    "ru": {
        "Aries": "огненный знак — импульс, инициатива, прямота",
        "Taurus": "земный знак — стабильность, терпение, практичность",
        "Gemini": "воздушный знак — любознательность, общение, гибкость",
        "Cancer": "водный знак — чувствительность, забота, память",
        "Leo": "огненный знак — самовыражение, щедрость, уверенность",
        "Virgo": "земный знак — анализ, полезность, внимание к мелочам",
        "Libra": "воздушный знак — партнёрство, вкус, поиск баланса",
        "Scorpio": "водный знак — глубина, трансформация, интенсивность",
        "Sagittarius": "огненный знак — поиск смысла, свобода, оптимизм",
        "Capricorn": "земный знак — цели, дисциплина, зрелость",
        "Aquarius": "воздушный знак — независимость, идеи, будущее",
        "Pisces": "водный знак — интуиция, сочувствие, воображение",
    },
    "en": {
        "Aries": "fire sign — impulse, initiative, directness",
        "Taurus": "earth sign — stability, patience, practicality",
        "Gemini": "air sign — curiosity, talk, flexibility",
        "Cancer": "water sign — sensitivity, care, memory",
        "Leo": "fire sign — self-expression, generosity, confidence",
        "Virgo": "earth sign — analysis, usefulness, attention to detail",
        "Libra": "air sign — partnership, taste, balance",
        "Scorpio": "water sign — depth, transformation, intensity",
        "Sagittarius": "fire sign — meaning, freedom, optimism",
        "Capricorn": "earth sign — goals, discipline, maturity",
        "Aquarius": "air sign — independence, ideas, the future",
        "Pisces": "water sign — intuition, empathy, imagination",
    },
}

PLANET_ROLE_HINT = {
    "ru": {
        "SUN": "ядро личности и жизненная цель",
        "MOON": "эмоции, привычные реакции и потребности",
        "MERCURY": "мышление, речь и обучение",
        "VENUS": "ценности, притяжение и эстетика",
        "MARS": "воля, напор и способ действовать",
        "JUPITER": "рост, вера и масштаб возможностей",
        "SATURN": "структура, дисциплина и границы",
        "ASC": "первое впечатление и стиль самопроявления",
    },
    "en": {
        "SUN": "core identity and life direction",
        "MOON": "emotions, habits, and needs",
        "MERCURY": "thinking, speech, and learning",
        "VENUS": "values, attraction, and aesthetics",
        "MARS": "will, drive, and how you act",
        "JUPITER": "growth, faith, and sense of possibility",
        "SATURN": "structure, discipline, and boundaries",
        "ASC": "first impression and outward style",
    },
}

ASPECT_PLAIN = {
    "ru": {
        "conjunction": "планеты в одной теме — эффект усиливается",
        "sextile": "мягкая поддержка — возможности открываются легче",
        "trine": "гармоничный поток — тема идёт естественно",
        "square": "напряжение — нужна осознанность и компромисс",
        "opposition": "полюса тянут в разные стороны — ищи баланс",
    },
    "en": {
        "conjunction": "planets merge themes — the effect intensifies",
        "sextile": "gentle support — openings come more easily",
        "trine": "harmonious flow — the theme moves naturally",
        "square": "tension — awareness and compromise help",
        "opposition": "poles pull apart — look for balance",
    },
}

LUNAR_DAY_HINT = {
    "ru": "лунный день — порядковый номер цикла от новолуния; у каждого дня свой эмоциональный оттенок",
    "en": "lunar day — the day number since the new moon; each day has its own emotional tone",
}

MOON_SIGN_LEGEND = {
    "ru": (
        "«Луна в …» — Луна сейчас в этом знаке зодиака (Овен, Телец и т.д.), "
        "а не на планете. От знака зависят настроение и бытовой ритм дня."
    ),
    "en": (
        "“Moon in …” means the Moon is currently in that zodiac sign (Aries, Taurus, etc.), "
        "not on a planet. The sign shapes mood and the day's rhythm."
    ),
}

TRANSIT_LEGEND = {
    "ru": (
        "Транзит — как небо сегодня «касается» вашей натальной карты. "
        "Квадрат и оппозиция — напряжение; трин и секстиль — поддержка."
    ),
    "en": (
        "A transit is how today's sky touches your natal chart. "
        "Squares and oppositions bring tension; trines and sextiles bring support."
    ),
}


def moon_in_sign_hint(locale: str, sign_key: str) -> str:
    lang = _lang(locale)
    return MOON_IN_SIGN_HINT[lang].get(sign_key, "")


def sign_tone_hint(locale: str, sign_key: str) -> str:
    lang = _lang(locale)
    return SIGN_TONE_HINT[lang].get(sign_key, "")


def planet_role_hint(locale: str, planet_key: str) -> str:
    lang = _lang(locale)
    return PLANET_ROLE_HINT[lang].get(planet_key, planet_key)


def aspect_plain(locale: str, aspect_key: str) -> str:
    lang = _lang(locale)
    return ASPECT_PLAIN[lang].get(aspect_key, "")


def format_moon_in_sign_short(locale: str, sign_key: str) -> str:
    sign_name = _sign_label(locale, sign_key)
    if _lang(locale) == "ru":
        return f"Луна в {sign_name}"
    return f"Moon in {sign_name}"


def format_moon_in_sign(locale: str, sign_key: str) -> str:
    """«Луна в Овне» with a beginner-friendly gloss (for help screens)."""
    line = format_moon_in_sign_short(locale, sign_key)
    hint = moon_in_sign_hint(locale, sign_key)
    if hint:
        return f"{line} — {hint}"
    return line


def format_moon_in_sign_bullet(locale: str, sign_key: str) -> str:
    return f"• {format_moon_in_sign_short(locale, sign_key)}"


def format_placement_plain(locale: str, planet_key: str, sign_key: str) -> str:
    """Short gloss for natal «planet in sign» lines."""
    lang = _lang(locale)
    sign_name = _sign_label(locale, sign_key)
    role = planet_role_hint(locale, planet_key)
    tone = sign_tone_hint(locale, sign_key)
    if lang == "ru":
        return f"{role.capitalize()}; в {sign_name} — {tone}."
    return f"{role.capitalize()}; in {sign_name} — {tone}."


def gloss_aspect_line(locale: str, aspect_key: str, base_line: str) -> str:
    plain = aspect_plain(locale, aspect_key)
    if not plain:
        return base_line
    if _lang(locale) == "ru":
        return f"{base_line}\n   ↳ {plain.capitalize()}."
    return f"{base_line}\n   ↳ {plain.capitalize()}."


def moon_glossary_footer(locale: str, *, include_lunar_day: bool = False) -> str:
    lang = _lang(locale)
    lines = [f"💡 {MOON_SIGN_LEGEND[lang]}"]
    if include_lunar_day:
        lines.append(f"💡 {LUNAR_DAY_HINT[lang].capitalize()}.")
    return "\n".join(lines)


def transit_glossary_footer(locale: str) -> str:
    lang = _lang(locale)
    return f"💡 {TRANSIT_LEGEND[lang]}"


def _sign_hints_block(locale: str) -> str:
    lang = _lang(locale)
    lines: list[str] = []
    for sign_key in SIGN_LABELS["en"]:
        hint = moon_in_sign_hint(locale, sign_key)
        if not hint:
            continue
        lines.append(f"• {format_moon_in_sign_short(locale, sign_key)} — {hint}")
    title = "Знаки зодиака и настроение дня" if lang == "ru" else "Zodiac signs and daily mood"
    return f"{title}:\n" + "\n".join(lines)


def _planets_block(locale: str) -> str:
    lang = _lang(locale)
    lines = []
    for key in ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "ASC"):
        role = planet_role_hint(locale, key)
        label = "Асцендент" if key == "ASC" and lang == "ru" else (
            "Ascendant" if key == "ASC" else _planet_name(locale, key)
        )
        lines.append(f"• {label} — {role}")
    title = "Планеты в карте" if lang == "ru" else "Planets in the chart"
    return f"{title}:\n" + "\n".join(lines)


def _planet_name(locale: str, key: str) -> str:
    names = {
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
    return names[_lang(locale)].get(key, key)


def _aspects_block(locale: str) -> str:
    lang = _lang(locale)
    lines = []
    for aspect_key in ("conjunction", "sextile", "trine", "square", "opposition"):
        plain = aspect_plain(locale, aspect_key)
        if not plain:
            continue
        label = {
            "ru": {
                "conjunction": "соединение",
                "sextile": "секстиль",
                "trine": "трин",
                "square": "квадрат",
                "opposition": "оппозиция",
            },
            "en": {
                "conjunction": "conjunction",
                "sextile": "sextile",
                "trine": "trine",
                "square": "square",
                "opposition": "opposition",
            },
        }[lang][aspect_key]
        lines.append(f"• {label} — {plain}")
    title = "Аспекты" if lang == "ru" else "Aspects"
    return f"{title}:\n" + "\n".join(lines)


def build_glossary_help(locale: str, topic: str, *, moon_sign_key: str | None = None) -> str:
    lang = _lang(locale)
    title = "❓ Простыми словами" if lang == "ru" else "❓ In plain language"
    blocks: list[str] = [title, ""]

    if topic == "moon":
        if lang == "ru":
            blocks.append(MOON_SIGN_LEGEND[lang])
            blocks.append(LUNAR_DAY_HINT[lang].capitalize() + ".")
            blocks.append(
                "Фазы Луны (новолуние, полнолуние и т.д.) — сколько света видно на небе "
                "и в какой фазе цикла мы сейчас."
            )
        else:
            blocks.append(MOON_SIGN_LEGEND[lang])
            blocks.append(LUNAR_DAY_HINT[lang].capitalize() + ".")
            blocks.append(
                "Moon phases (new moon, full moon, etc.) show how much light is visible "
                "and where we are in the lunar cycle."
            )
        if moon_sign_key:
            blocks.extend(["", format_moon_in_sign(locale, moon_sign_key)])
        blocks.extend(["", _sign_hints_block(locale)])
        return "\n".join(blocks)

    if topic == "horo":
        if lang == "ru":
            blocks.extend(
                [
                    MOON_SIGN_LEGEND[lang],
                    TRANSIT_LEGEND[lang],
                    (
                        "В прогнозе «Марс квадрат к Луне» значит: сегодняшний Марс давит на вашу "
                        "эмоциональную сферу (Луну в натальной карте). Это не «Луна на Марсе»."
                    ),
                ]
            )
        else:
            blocks.extend(
                [
                    MOON_SIGN_LEGEND[lang],
                    TRANSIT_LEGEND[lang],
                    (
                        "“Mars square Moon” means today's Mars presses on your emotional Moon "
                        "in the natal chart — not “Moon on Mars.”"
                    ),
                ]
            )
        blocks.extend(["", _aspects_block(locale)])
        if moon_sign_key:
            blocks.extend(["", format_moon_in_sign(locale, moon_sign_key)])
        return "\n".join(blocks)

    if topic == "natal":
        if lang == "ru":
            blocks.append(
                "«Солнце в Тельце» или «Луна в Раке» — это положение планеты в знаке зодиака "
                "в момент рождения, а не на другой планете."
            )
        else:
            blocks.append(
                "“Sun in Taurus” or “Moon in Cancer” is a planet's position in a zodiac sign "
                "at birth — not on another planet."
            )
        blocks.extend(["", _planets_block(locale), "", _aspects_block(locale)])
        return "\n".join(blocks)

    if topic == "compat":
        if lang == "ru":
            blocks.extend(
                [
                    (
                        "Совместимость сравнивает вашу карту и карту партнёра. "
                        "«Ваше Солнце — трин — Венера партнёра» — гармоничная связь между темами."
                    ),
                    TRANSIT_LEGEND[lang],
                ]
            )
        else:
            blocks.extend(
                [
                    (
                        "Compatibility compares your chart with your partner's. "
                        "“Your Sun trine partner's Venus” is a harmonious link between themes."
                    ),
                    TRANSIT_LEGEND[lang],
                ]
            )
        blocks.extend(["", _aspects_block(locale)])
        return "\n".join(blocks)

    return title
