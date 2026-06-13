"""Engaging, human-sounding copy for compatibility readings."""
from __future__ import annotations

import re


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def compat_score_hook(locale: str, score: int, mode: str, *, style: str = "plain") -> str:
    lang = _lang(locale)
    if style != "plain":
        if lang == "ru":
            return (
                f"Итоговая оценка {score}/100 (Swiss Ephemeris). "
                f"Ниже — разбор по шагам синастрии."
            )
        return (
            f"Composite score {score}/100 (Swiss Ephemeris). "
            f"Step-by-step synastry breakdown below."
        )
    if lang == "ru":
        if score >= 85:
            return "Оценка высокая — вы друг другу реально зашли. Сейчас разложу по полочкам, без занудства."
        if score >= 70:
            return "Картина хорошая — есть на что опереться. Дальше по деталям, коротко и по делу."
        if score >= 55:
            return "Не сказка и не катастрофа — как в жизни. Сейчас разберу по частям, без загадок."
        return "Честно: не всё просто. Но если дочитаешь — станет яснее, где копать и где не париться."
    if score >= 85:
        return "High score — you genuinely click. I'll break it down without the lecture."
    if score >= 70:
        return "Solid picture — plenty to lean on. Details ahead, kept short."
    if score >= 55:
        return "Not a fairy tale, not a disaster — real life, where talking beats guessing."
    return "I'll be straight: it's not effortless. Read through and you'll see where to focus."


def theme_menu_teaser(locale: str, theme_key: str, *, style: str = "plain") -> str:
    lang = _lang(locale)
    if style != "plain":
        teasers = {
            "ru": {
                "overview": "Солнечные знаки, стихии, общий фон пары.",
                "attraction": "ASC/DSC, аспекты синастрии, Луна и Венера.",
                "bond": "Композитная карта, наложение домов, прогрессии.",
                "depth": "Лилит, Селена, кармические узлы, транзиты.",
                "symbols": "Число союза, расклад Таро на пару.",
                "result": "Сводная таблица +1/−1, рекомендации.",
            },
            "en": {
                "overview": "Sun signs, elements, pair baseline.",
                "attraction": "ASC/DSC, synastry aspects, Moon and Venus.",
                "bond": "Composite chart, house overlay, progressions.",
                "depth": "Lilith, Selena, lunar nodes, transits.",
                "symbols": "Union number, couple Tarot spread.",
                "result": "+1/−1 scorecard and recommendations.",
            },
        }
        return teasers[lang].get(theme_key, "")
    teasers = {
        "ru": {
            "overview": "Кто вы и совпадает ли темп — без загадок.",
            "attraction": "Что тянет друг к другу — и где может укусить.",
            "bond": "Как вы живёте «мы», а не только «я и ты».",
            "depth": "То, о чём на первом свидании молчат (а зря).",
            "symbols": "Числа и карты — взгляд сбоку, иногда попадает в точку.",
            "result": "Финал: одна мысль, с которой можно уйти.",
        },
        "en": {
            "overview": "Who you are together and whether your rhythms match.",
            "attraction": "What pulls you in — and what might nip.",
            "bond": "Daily «we», not just «me and you».",
            "depth": "What people feel but rarely say out loud on date one.",
            "symbols": "Numbers and cards — sideways glance, sometimes spot-on.",
            "result": "Wrap-up: one thought to take with you.",
        },
    }
    return teasers[lang].get(theme_key, "")


def theme_opening_hook(locale: str, theme_key: str, mode: str, score: int, *, style: str = "plain") -> str:
    lang = _lang(locale)
    if style != "plain":
        hooks = {
            "ru": {
                "overview": "Базовый уровень: знаки Солнца и баланс стихий.",
                "attraction": "ASC/DSC и ключевые аспекты синастрии.",
                "bond": "Композит, дома и прогрессии — структура союза.",
                "depth": "Кармические и транзитные маркеры.",
                "symbols": "Нумерология и Таро — дополнительный слой.",
                "result": "Сводка по всем шагам и итоговая рекомендация.",
            },
            "en": {
                "overview": "Baseline: Sun signs and element balance.",
                "attraction": "ASC/DSC and key synastry aspects.",
                "bond": "Composite, houses, and progressions — union structure.",
                "depth": "Karmic and transit markers.",
                "symbols": "Numerology and Tarot — an extra layer.",
                "result": "Full step summary and final recommendation.",
            },
        }
        return hooks[lang].get(theme_key, "")
    hooks = {
        "ru": {
            "overview": "Начнём с простого: кто вы как пара и на одной ли волне.",
            "attraction": "Самое живое — что вас реально цепляет (и где щекотит).",
            "bond": "Теперь быт вдвоём: привычки, «мы» и куда это катится.",
            "depth": "Поглубже — про то, что обычно не говорят вслух с первого раза.",
            "symbols": "Немного магии: числа и карты — не закон, но иногда попадают.",
            "result": "Финал. Одна понятная мысль — без воды.",
        },
        "en": {
            "overview": "Starting simple — who you are as a pair and whether you're in sync.",
            "attraction": "The lively bit — what actually pulls you together.",
            "bond": "Daily life as a couple — routines, «we», and where it's heading.",
            "depth": "Getting honest — what rarely gets said on a first talk.",
            "symbols": "A little magic — numbers and cards aren't law, but sometimes nail it.",
            "result": "The wrap-up. One clear thought — no fluff.",
        },
    }
    base = hooks[lang].get(theme_key, "")
    if theme_key == "result" and score >= 75 and lang == "ru":
        return f"{base} Если совсем коротко — складывается неплохо, можно не искать подвох на ровном месте."
    if theme_key == "result" and score >= 75:
        return f"{base} Short version — looking decent, no need to hunt for drama."
    return base


def theme_next_teaser(locale: str, next_title: str, next_key: str, *, style: str = "plain") -> str:
    lang = _lang(locale)
    hint = theme_menu_teaser(locale, next_key, style=style)
    if style != "plain":
        if lang == "ru":
            return f"Далее: «{next_title}». {hint}"
        return f"Next: «{next_title}». {hint}"
    if lang == "ru":
        return f"Не устал? Дальше «{next_title}» — {hint.lower()}"
    return f"Still with me? Next «{next_title}» — {hint.lower()}"


def menu_pick_cta(locale: str, *, style: str = "plain") -> str:
    if style != "plain":
        if _lang(locale) == "ru":
            return "Выберите блок — внутри шаги синастрии с терминами и маркерами карты."
        return "Pick a block — each contains synastry steps with chart markers."
    if _lang(locale) == "ru":
        return "6 тем — начинай с любой. Как меню в ресторане: можно не есть всё подряд."
    return "Six themes — start anywhere. Like a menu: you don't have to order everything."


def compatibility_summary_engaging(locale: str, score: int, *, style: str = "terms") -> str:
    plain = style == "plain"
    lang = _lang(locale)
    if lang == "ru":
        if plain:
            if score >= 85:
                return "Короче: вы друг другу очень подходите. Берегите это — и не забудьте иногда сказать вслух."
            if score >= 70:
                return "Короче: между вами много опоры. На это можно опираться, а не только на надежду."
            if score >= 55:
                return "Короче: не идеально, но при желании можно выстроить что-то крепкое. Главное — не молчать."
            return "Короче: без терпения будет тяжело. Зато картина честная — лучше знать заранее."
        if score >= 85:
            return "Общий фон: очень высокая совместимость — сильная база для союза."
        if score >= 70:
            return "Общий фон: хорошая совместимость — много точек опоры."
        if score >= 55:
            return "Общий фон: смешанная картина — и гармония, и зоны роста."
        return "Общий фон: непростая связь — терпение и диалог обязательны."
    if plain:
        if score >= 85:
            return "Short version: you fit each other really well. Hold onto that — say it out loud sometimes."
        if score >= 70:
            return "Short version: lots of support between you — something solid to lean on."
        if score >= 55:
            return "Short version: not perfect, but you can build something strong if you talk."
        return "Short version: it'll take patience — at least the picture is honest."
    if score >= 85:
        return "Overall: very high compatibility — a strong base for the bond."
    if score >= 70:
        return "Overall: good compatibility — many supportive links."
    if score >= 55:
        return "Overall: mixed picture — harmony and growth points together."
    return "Overall: challenging bond — patience and dialogue are essential."


_HUMANIZE_RU = (
    (r"^Итог:\s*", "Короче, "),
    (r"^В двух словах:\s*", "Короче, "),
    (r"простым языком", ""),
    (r"по-человечески", ""),
    (r"ниже —", "дальше —"),
    (r"ниже разберём", "сейчас разберу"),
    (r"имеет смысл", "можно"),
    (r"Подсказка:", "Кстати,"),
    (r"синастри\w*", "связь"),
    (r"композит\w*", "ваше «мы»"),
    (r"аспект\w*", "связь"),
    (r"стихи\w*", "тип темпа"),
    (r"натальн\w*", ""),
    (r"транзит\w*", "сейчас"),
    (r"прогресс\w*", "развитие"),
    (r"карм\w*", "урок"),
    (r" — — ", " — "),
    (r"  +", " "),
)

_HUMANIZE_EN = (
    (r"^Bottom line:\s*", "Short version — "),
    (r"^In short:\s*", "Short version — "),
    (r"plain language", ""),
    (r"plain words", ""),
    (r"below —", "next —"),
    (r"below we", "I'll"),
    (r"Hint:", "By the way,"),
    (r"\bsynastr\w*", "bond"),
    (r"\bcomposite\b", "your «we»"),
    (r"\baspect\w*", "link"),
    (r"\belement\w*", "pace"),
    (r"\bnatal\b", ""),
    (r"\btransit\w*", "now"),
    (r"\bkarm\w*", "lesson"),
    (r" — — ", " — "),
    (r"  +", " "),
)


def humanize_compat_plain(text: str, locale: str) -> str:
    """Strip template-y phrasing and leftover jargon from plain compat text."""
    if not text.strip():
        return text
    table = _HUMANIZE_RU if _lang(locale) == "ru" else _HUMANIZE_EN
    result = text
    for pattern, replacement in table:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.MULTILINE)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()
