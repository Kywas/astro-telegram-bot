"""Plain-language compatibility copy that differs by love / friendship / work."""
from __future__ import annotations

from app.synastry_text import _lang


def mode_key(mode: str) -> str:
    return mode if mode in {"love", "friendship", "work"} else "love"


def other_label(locale: str, mode: str) -> str:
    lang = _lang(locale)
    key = mode_key(mode)
    if lang == "ru":
        return {"love": "партнёр", "friendship": "друг", "work": "colleague"}[key].replace(
            "colleague", "коллега"
        )
    return {"love": "partner", "friendship": "friend", "work": "colleague"}[key]


def other_label_cap(locale: str, mode: str) -> str:
    label = other_label(locale, mode)
    return label[:1].upper() + label[1:]


def pair_label(locale: str, mode: str) -> str:
    lang = _lang(locale)
    key = mode_key(mode)
    if lang == "ru":
        return {
            "love": "пара",
            "friendship": "дружба",
            "work": "команда",
        }[key]
    return {"love": "couple", "friendship": "friendship", "work": "team"}[key]
