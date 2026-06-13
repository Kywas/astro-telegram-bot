"""Engaging, human-sounding copy for compatibility readings."""
from __future__ import annotations

import re


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def compat_score_hook(locale: str, score: int, mode: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        if score >= 85:
            return "Между вами правда сильная связь. Сейчас разложу по полочкам, на чём она держится."
        if score >= 70:
            return "Картина хорошая — есть на что опереться. Пройдёмся по деталям."
        if score >= 55:
            return "Не сказка, но и не провал. Скорее живая пара, где многое решает разговор."
        return "Буду честен: не всё просто. Но если дочитаешь — станет понятнее, что с этим делать."
    if score >= 85:
        return "There's a real bond here. I'll walk you through what it's built on."
    if score >= 70:
        return "The picture looks good — plenty to lean on. Let's get into the details."
    if score >= 55:
        return "Not a fairy tale, not a disaster — a real pair where talk matters."
    return "I'll be straight with you: it's not easy. But read through and you'll see clearer next steps."


def theme_menu_teaser(locale: str, theme_key: str) -> str:
    lang = _lang(locale)
    teasers = {
        "ru": {
            "overview": "Кто вы друг для друга и совпадаете ли по темпу.",
            "attraction": "За что тянет — и где может щекотать.",
            "bond": "Быт, «мы» и куда пара смотрит вместе.",
            "depth": "То, о чём обычно молчат, но чувствуют.",
            "symbols": "Числа и карты — взгляд чуть с другой стороны.",
            "result": "Сводка, совет и что из этого вынести.",
        },
        "en": {
            "overview": "Who you are to each other and whether your rhythms match.",
            "attraction": "What pulls you in — and what might sting.",
            "bond": "Daily life, «we», and where you're headed together.",
            "depth": "What people feel but rarely say out loud.",
            "symbols": "Numbers and cards — a slightly different angle.",
            "result": "Summary, advice, and what to take from it.",
        },
    }
    return teasers[lang].get(theme_key, "")


def theme_opening_hook(locale: str, theme_key: str, mode: str, score: int) -> str:
    lang = _lang(locale)
    hooks = {
        "ru": {
            "overview": "Начну с базы — кто вы как пара и на одной ли волне.",
            "attraction": "Тут самое живое: что между вами реально цепляет.",
            "bond": "Теперь про жизнь вдвоём — быт, решения, общий «мы».",
            "depth": "Дальше честнее. Про то, что обычно не выносят на первый разговор.",
            "symbols": "Чуть отступлю от карты — числа и Таро иногда попадают в точку.",
            "result": "Финал. Соберу всё в одну понятную мысль.",
        },
        "en": {
            "overview": "Starting with the basics — who you are as a pair and whether you're in sync.",
            "attraction": "This is the lively part — what actually pulls you together.",
            "bond": "Now daily life as a couple — routines, choices, the shared «we».",
            "depth": "Getting more honest — what people rarely say on a first talk.",
            "symbols": "Stepping slightly aside — numbers and Tarot sometimes nail it.",
            "result": "The wrap-up. One clear thought from everything above.",
        },
    }
    base = hooks[lang].get(theme_key, "")
    if theme_key == "result" and score >= 75 and lang == "ru":
        return f"{base} Если коротко — складывается неплохо."
    if theme_key == "result" and score >= 75:
        return f"{base} Short version — it's looking decent."
    return base


def theme_next_teaser(locale: str, next_title: str, next_key: str) -> str:
    lang = _lang(locale)
    hint = theme_menu_teaser(locale, next_key)
    if lang == "ru":
        return f"Если не устал читать — дальше «{next_title}». {hint}"
    return f"If you're still with me — next up «{next_title}». {hint}"


def menu_pick_cta(locale: str) -> str:
    if _lang(locale) == "ru":
        return "Выбирай тему — с любой можно начать, каждая минут на две–три."
    return "Pick a theme — start anywhere, each takes two or three minutes."


def compatibility_summary_engaging(locale: str, score: int, *, style: str = "terms") -> str:
    plain = style == "plain"
    lang = _lang(locale)
    if lang == "ru":
        if plain:
            if score >= 85:
                return "В двух словах: вы друг другу очень подходите. Берегите это."
            if score >= 70:
                return "В двух словах: между вами много опоры — на это можно опираться."
            if score >= 55:
                return "В двух словах: не идеально, но при желании можно выстроить что-то крепкое."
            return "В двух словах: без терпения будет тяжело, зато картина честная."
        if score >= 85:
            return "Общий фон: очень высокая совместимость — сильная база для союза."
        if score >= 70:
            return "Общий фон: хорошая совместимость — много точек опоры."
        if score >= 55:
            return "Общий фон: смешанная картина — и гармония, и зоны роста."
        return "Общий фон: непростая связь — терпение и диалог обязательны."
    if plain:
        if score >= 85:
            return "In short: you fit each other really well. Hold onto that."
        if score >= 70:
            return "In short: lots of support between you — something solid to lean on."
        if score >= 55:
            return "In short: not perfect, but you can build something strong if you want to."
        return "In short: it'll take patience — but at least the picture is honest."
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
    (r"простым языком", "по-человечески"),
    (r"ниже —", "дальше —"),
    (r"ниже разберём", "сейчас разберу"),
    (r"имеет смысл", "можно"),
    (r"Подсказка:", "Кстати,"),
    (r" — — ", " — "),
    (r"  +", " "),
)

_HUMANIZE_EN = (
    (r"^Bottom line:\s*", "Short version — "),
    (r"^In short:\s*", "Short version — "),
    (r"plain language", "plain words"),
    (r"below —", "next —"),
    (r"below we", "I'll"),
    (r"Hint:", "By the way,"),
    (r" — — ", " — "),
    (r"  +", " "),
)


def humanize_compat_plain(text: str, locale: str) -> str:
    """Light pass to strip template-y phrasing from plain compat text."""
    if not text.strip():
        return text
    table = _HUMANIZE_RU if _lang(locale) == "ru" else _HUMANIZE_EN
    result = text
    for pattern, replacement in table:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.MULTILINE)
    return result.strip()
