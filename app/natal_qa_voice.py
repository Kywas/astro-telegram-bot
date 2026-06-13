"""Plain-language voice for natal chart Q&A — Joyti-style narrative, no jargon."""
from __future__ import annotations

import re
from html import unescape

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import _house_theme, _lang
from app.text_format import b, h, p, sentence_paragraphs

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")

_PLAIN_ROLE = {
    "ru": {
        "SUN": "твоя суть",
        "MOON": "твои эмоции",
        "MERCURY": "мышление и речь",
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
        "MERCURY": "thinking and speech",
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
        line = f"{role.capitalize()} ({sign}) — про {area}."
    else:
        line = f"{role.capitalize()} ({sign}) — about {area}."
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
        return f"Тема «{source}» идёт через {target} — обрати внимание на {role} ({sign})."
    return f"«{source}» runs through {target} — watch {role} ({sign})."


def strip_telegram_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"</?(?:b|i|u|code|pre)>", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return unescape(cleaned).strip()


def plain_disclaimer(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            "Важно помнить: карта показывает потенциал, а не приговор. "
            "Итог зависит от твоего выбора, зрелости и того, как ты ведёшь себя в жизни."
        )
    return (
        "Remember: the chart shows potential, not a verdict. "
        "The outcome depends on your choices, maturity, and how you act."
    )


def _marker_to_prose(locale: str, line: str) -> str:
    text = humanize_natal_plain(strip_telegram_html(line), locale)
    text = text.lstrip("•·- ").strip()
    if not text:
        return ""
    if text[0].islower():
        text = text[0].upper() + text[1:]
    if not text.endswith((".", "!", "?", "…")):
        text += "."
    return text


def _build_summary(locale: str, sentences: list[str], markers: tuple[str, ...]) -> str:
    lang = _lang(locale)
    if len(sentences) >= 2:
        return sentences[-1] if len(sentences[-1]) < 220 else sentences[0]
    if markers:
        first = _marker_to_prose(locale, markers[0])
        if first:
            return first
    if lang == "ru":
        return "Картина индивидуальная — смотри, откликается ли тебе описание."
    return "The picture is individual — see if it resonates."


def compose_plain_qa_answer(
    locale: str,
    core_html: str,
    markers: tuple[str, ...] = (),
    practice: str = "",
) -> str:
    """Flowing plain answer: hook → story → extras → punchline → tip."""
    lang = _lang(locale)
    core = sanitize_plain_qa_text(strip_telegram_html(core_html), locale)
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(core) if s.strip()]

    blocks: list[str] = []

    if sentences:
        blocks.append(h(sentences[0]))
        if len(sentences) > 1:
            rest = " ".join(sentences[1:])
            if lang == "ru":
                if not any(rest.lower().startswith(p) for p in ("скажу", "короче", "если")):
                    lead = rest[0].lower() + rest[1:] if rest else rest
                    rest = f"Скажу прямо: {lead}"
            elif not rest.lower().startswith("to be clear"):
                rest = f"To be clear: {rest[0].lower()}{rest[1:]}" if rest else rest
            blocks.append(sentence_paragraphs(rest, sentences_per_para=2))

    why_lines: list[str] = []
    seen: set[str] = set()
    core_lower = core.lower()
    for marker in markers[:2]:
        line = _marker_to_prose(locale, marker)
        if not line or line.lower() in seen:
            continue
        if line.lower()[:40] in core_lower:
            continue
        seen.add(line.lower())
        why_lines.append(line)

    if why_lines:
        header = "А вот откуда это 🌿" if lang == "ru" else "Where this comes from 🌿"
        blocks.append(b(header))
        blocks.append(h(" ".join(why_lines)))

    blocks.append(b("Короче 🌙" if lang == "ru" else "Short version 🌙"))
    blocks.append(h(_build_summary(locale, sentences, markers)))

    blocks.append(
        h(
            "Карта — подсказка, не приговор. Итог всё равно за тобой — и это, честно, хорошая новость."
            if lang == "ru"
            else "The chart is a hint, not a verdict. You're still in charge — honestly, good news."
        )
    )

    practice_clean = sanitize_plain_qa_text(strip_telegram_html(practice), locale)
    if practice_clean:
        prefix = "💡 Попробуй на этой неделе: " if lang == "ru" else "💡 Try this week: "
        blocks.append(h(prefix + practice_clean))

    return p(*blocks)


def plain_topic_hook(locale: str, question: str, *, hint: str = "") -> str:
    topic = " ".join(question.strip().split()).rstrip("?.!")
    if len(topic) > 80:
        topic = topic[:79].rstrip() + "…"
    lang = _lang(locale)
    q = question.lower()
    if lang == "ru":
        if any(w in q for w in ("здоров", "тело", "энерг", "рутин", "режим", "сон")):
            base = "Начну с главного — про твоё тело и ресурс сил"
        elif any(w in q for w in ("деньг", "доход", "финанс", "карьер", "ценност", "инвест", "работ")):
            base = "Начну с главного — про твою линию с деньгами и делом"
        elif any(w in q for w in ("люб", "роман", "брак", "партн", "отношен", "союз")):
            base = "Начну с главного — про твою линию в любви и близости"
        elif any(w in q for w in ("карм", "прошл", "урок", "воплощ")):
            base = "Начну с главного — про уроки, которые жизнь повторяет"
        else:
            base = f"Отвечаю на «{topic}» — без загадок и без словаря астролога"
        return f"{base}: {hint}" if hint else f"{base}."
    if any(w in q for w in ("love", "romance", "marriage", "partner", "relationship")):
        base = "Main point first — your line in love and closeness"
    elif any(w in q for w in ("money", "income", "finance", "career", "work")):
        base = "Main point first — your line with money and work"
    else:
        base = f"On «{topic}» — clear words, no astro dictionary"
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


def sanitize_plain_qa_text(text: str, locale: str) -> str:
    """Strip leftover jargon and tighten plain Q&A prose."""
    if not text.strip():
        return text
    lang = _lang(locale)
    result = humanize_natal_plain(text, locale)
    extra: tuple[tuple[str, str], ...] = (
        (r"\b\d+\s*[-‑]?\s*(?:й|го)\s+дом\b", "эта сфера"),
        (r"\(\s*\)", ""),
        (r"\s{2,}", " "),
        (r" · · ", " · "),
    )
    if lang == "ru":
        extra = (
            (r"управител\w*", "ключ"),
            (r"стеллиум\w*", "скученность"),
            (r"ретроград\w*", "внутренний разворот"),
            (r"накшатр\w*", ""),
            (r"джйотиш\w*", ""),
            (r"ведическ\w*", ""),
            *extra,
        )
    for pattern, replacement in extra:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result.strip(" ·,")
