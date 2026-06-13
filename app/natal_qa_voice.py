"""Plain-language voice for natal chart Q&A — no jargon, friendly tone."""
from __future__ import annotations

import re

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import _house_theme, _lang

_PLAIN_ROLE = {
    "ru": {
        "SUN": "твоя суть",
        "MOON": "твои эмоции",
        "MERCURY": "как ты думаешь и говоришь",
        "VENUS": "твоя нежность и вкус",
        "MARS": "твой напор",
        "JUPITER": "твоя надежда и рост",
        "SATURN": "твои границы",
        "RAHU": "тяга к новому",
        "KETU": "умение отпускать",
    },
    "en": {
        "SUN": "your core",
        "MOON": "your feelings",
        "MERCURY": "how you think and talk",
        "VENUS": "your warmth and taste",
        "MARS": "your drive",
        "JUPITER": "your hope and growth",
        "SATURN": "your boundaries",
        "RAHU": "craving for the new",
        "KETU": "letting go",
    },
}

_PLAIN_AREA = {
    "ru": {
        1: "как ты себя показываешь",
        2: "деньги и ценности",
        3: "разговоры и будни",
        4: "дом и близкие",
        5: "радость и романтика",
        6: "работа и быт",
        7: "партнёр и пара",
        8: "кризисы и общие деньги",
        9: "смысл и путешествия",
        10: "работа и статус",
        11: "друзья и цели",
        12: "отдых и уединение",
    },
    "en": {
        1: "how you show up",
        2: "money and values",
        3: "talk and daily life",
        4: "home and close ones",
        5: "joy and romance",
        6: "work and routine",
        7: "partner and couple",
        8: "crisis and shared money",
        9: "meaning and travel",
        10: "work and status",
        11: "friends and goals",
        12: "rest and solitude",
    },
}

_HUMANIZE_RU = (
    (r"\bуправител\w*\s+\d+-?\s*(?:го|й)\b", "ключ к теме"),
    (r"\b\d+-?\s*(?:й|й)\s+дом\b", "эта сфера"),
    (r"\b\d+-?\s*(?:th|st|nd|rd)\s+house\b", "this area"),
    (r"\bЛагн\w*\b", "как тебя видят"),
    (r"\bЛун\w*\b", "эмоции"),
    (r"\bВенер\w*\b", "нежность"),
    (r"\bСолнц\w*\b", "суть"),
    (r"\bМарс\w*\b", "напор"),
    (r"\bМеркури\w*\b", "мышление"),
    (r"\bЮпитер\w*\b", "рост"),
    (r"\bСатурн\w*\b", "границы"),
    (r"\bРах\w*\b", "амбиции"),
    (r"\bКет\w*\b", "отпускание"),
    (r"\bкарм\w*\b", "урок"),
    (r"\bнакшатр\w*\b", ""),
    (r"\bдхарм\w*\b", "смысл"),
    (r"\bупай\w*\b", "практика"),
    (r"в знаке силы", "очень сильно"),
    (r"в слабом положении", "нужна бережность"),
    (r"в своём знаке", "устойчиво"),
    (r"  +", " "),
)

_HUMANIZE_EN = (
    (r"\b\d+(?:st|nd|rd|th)\s+house\b", "this area"),
    (r"\bhouse\s+\d+\b", "this area"),
    (r"\blord of house\b", "key to"),
    (r"\bLagna\b", "first impression"),
    (r"\bMoon\b", "feelings"),
    (r"\bVenus\b", "warmth"),
    (r"\bSun\b", "core"),
    (r"\bMars\b", "drive"),
    (r"\bMercury\b", "thinking"),
    (r"\bJupiter\b", "growth"),
    (r"\bSaturn\b", "boundaries"),
    (r"\bRahu\b", "ambition"),
    (r"\bKetu\b", "release"),
    (r"\bkarm\w*\b", "lesson"),
    (r"\bnakshatr\w*\b", ""),
    (r"exalted", "very strong"),
    (r"debilitated", "needs care"),
    (r"  +", " "),
)


def plain_role(locale: str, planet_key: str) -> str:
    return _PLAIN_ROLE[_lang(locale)].get(planet_key, planet_key.lower())


def plain_area(locale: str, house: int) -> str:
    lang = _lang(locale)
    return _PLAIN_AREA[lang].get(house, _house_theme(locale, house).lower())


def plain_placement_line(locale: str, pl: PlanetPlacement, *, hint: str = "") -> str:
    lang = _lang(locale)
    sign = sign_label(locale, pl.sign)
    role = plain_role(locale, pl.key)
    area = plain_area(locale, pl.house)
    if lang == "ru":
        line = f"{role.capitalize()} ({sign}) — про {area}"
    else:
        line = f"{role.capitalize()} ({sign}) — about {area}"
    if hint:
        line = f"{line}. {hint}"
    return line


def plain_lord_line(locale: str, chart: JyotishChart, from_house: int) -> str:
    lang = _lang(locale)
    lord_key = chart.house_lords[from_house]
    lord = chart.planets[lord_key]
    source = plain_area(locale, from_house)
    target = plain_area(locale, lord.house)
    sign = sign_label(locale, lord.sign)
    role = plain_role(locale, lord.key)
    if lord.house == from_house:
        if lang == "ru":
            return f"Тема «{source}» у тебя звучит громко — {role} ({sign}) держит её в центре."
        return f"«{source}» is loud for you — {role} ({sign}) keeps it front and center."
    if lang == "ru":
        return f"Тема «{source}» идёт через {target} — смотри на {role} ({sign})."
    return f"«{source}» runs through {target} — watch {role} ({sign})."


def plain_topic_hook(locale: str, question: str, *, hint: str = "") -> str:
    topic = " ".join(question.strip().split()).rstrip("?.!")
    if len(topic) > 80:
        topic = topic[:79].rstrip() + "…"
    lang = _lang(locale)
    if lang == "ru":
        base = f"Про «{topic}» — коротко и без загадок"
        return f"{base}: {hint}" if hint else f"{base}."
    base = f"On «{topic}» — short and clear"
    return f"{base}: {hint}" if hint else f"{base}."


def plain_practice(locale: str, intent: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        tips = {
            "how_relationship": "На неделю: заметь, как ты ведёшь себя в паре — без самокритики, просто наблюдай.",
            "who_partner": "Спроси себя: «меня тянет к похожим или к противоположным?» — ответ часто уже есть.",
            "challenge": "Назови вслух одну привычку, которая мешает. Не чтобы себя ругать — чтобы увидеть паттерн.",
            "money": "Запиши три траты за неделю: «нужно» или «настроение» — так виднее, куда уходит.",
            "career": "Один маленький шаг на месяц в сторону дела — не героизм, а движение.",
            "health": "Сон и режим важнее «закалки характера». Начни с одного вечера без экрана.",
            "general": "Понаблюдай неделю — если узнаёшь себя, значит попали; если нет — не парься, карта не приговор.",
        }
        return tips.get(intent, tips["general"])
    tips = {
        "how_relationship": "For one week, notice how you act in a pair — no self-judgment, just watch.",
        "who_partner": "Ask: «am I drawn to similar or opposite types?» — you often already know.",
        "challenge": "Name one blocking habit out loud — not to scold yourself, to see the pattern.",
        "money": "Log three spends: «need» or «mood» — you'll see where it goes.",
        "career": "One small step toward your work this month — not heroics, just motion.",
        "health": "Sleep beats willpower stunts. Start with one screen-free evening.",
        "general": "Watch for a week — if it fits, good; if not, don't stress, the chart isn't a verdict.",
    }
    return tips.get(intent, tips["general"])


def humanize_natal_plain(text: str, locale: str) -> str:
    if not text.strip():
        return text
    table = _HUMANIZE_RU if _lang(locale) == "ru" else _HUMANIZE_EN
    result = text
    for pattern, replacement in table:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    result = re.sub(r"\s+\.", ".", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()
