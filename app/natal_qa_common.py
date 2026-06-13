"""Shared helpers for structured natal chart Q&A blocks."""
from __future__ import annotations

from dataclasses import dataclass

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import _house_theme, _lang, _pl, _use_terms
from app.natal_qa_voice import humanize_natal_plain, plain_area as voice_plain_area, plain_lord_line, plain_placement_line, plain_role
from app.text_format import b, h, p

_DIGNITY = {
    "ru": {
        "exalted": "в знаке силы",
        "own": "в своём знаке",
        "debilitated": "в слабом положении",
        "neutral": "",
    },
    "en": {
        "exalted": "exalted",
        "own": "in own sign",
        "debilitated": "debilitated",
        "neutral": "",
    },
}

_PLAIN_AREA = {
    "ru": {
        1: "образ и самопроявление",
        2: "деньги и ценности",
        3: "общение и повседневность",
        4: "дом и семья",
        5: "радость и романтика",
        6: "работа и быт",
        7: "партнёрство и брак",
        8: "кризисы и общие ресурсы",
        9: "смысл и расширение",
        10: "карьера и статус",
        11: "друзья и цели",
        12: "уединение и отпускание",
    },
    "en": {
        1: "identity and self-expression",
        2: "money and values",
        3: "communication and daily life",
        4: "home and family",
        5: "joy and romance",
        6: "work and routine",
        7: "partnership and marriage",
        8: "crisis and shared resources",
        9: "meaning and expansion",
        10: "career and status",
        11: "friends and goals",
        12: "solitude and release",
    },
}

# Where a house lord's theme lands when it sits in each house (generic Jyotish logic).
_LORD_IN_TARGET = {
    "ru": {
        1: "связано с образом и тем, как ты себя проявляешь",
        2: "идёт через деньги, ресурсы и личные ценности",
        3: "через общение, смелость и короткие поездки",
        4: "через дом, семью и внутреннюю опору",
        5: "через радость, творчество и риск",
        6: "через работу, режим, службу и здоровье",
        7: "через партнёра и договорённости один на один",
        8: "через кризисы, тайны и общие ресурсы",
        9: "через смысл, учёбу, дальние поездки и наставников",
        10: "через карьеру, статус и публичную реализацию",
        11: "через друзей, цели и социальную поддержку",
        12: "через уединение, отпускание, заграницу или потери",
    },
    "en": {
        1: "ties to identity and self-presentation",
        2: "runs through money, resources, and values",
        3: "through talk, courage, and short trips",
        4: "through home, family, and inner support",
        5: "through joy, creativity, and risk",
        6: "through work, routine, service, and health",
        7: "through partner and one-to-one agreements",
        8: "through crisis, secrets, and shared resources",
        9: "through meaning, study, travel, and teachers",
        10: "through career, status, and public life",
        11: "through friends, goals, and social support",
        12: "through solitude, release, abroad, or loss",
    },
}


@dataclass(frozen=True)
class StructuredQaAnswer:
    brief: str
    markers: tuple[str, ...]
    practice: str


def planets_in_house(chart: JyotishChart, house: int) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")
    return [chart.planets[key] for key in order if chart.planets[key].house == house]


def lord_of(chart: JyotishChart, house: int) -> PlanetPlacement:
    return chart.planets[chart.house_lords[house]]


_DIGNITY_PLAIN = {
    "ru": {
        "exalted": "очень сильно",
        "own": "устойчиво",
        "debilitated": "нужна бережность",
        "neutral": "",
    },
    "en": {
        "exalted": "very strong",
        "own": "steady",
        "debilitated": "needs care",
        "neutral": "",
    },
}


def dignity_note(locale: str, pl: PlanetPlacement, *, style: str = "terms") -> str:
    lang = _lang(locale)
    if not _use_terms(style):
        return _DIGNITY_PLAIN[lang].get(pl.dignity, "")
    return _DIGNITY[lang].get(pl.dignity, "")


def plain_area(locale: str, house: int) -> str:
    return voice_plain_area(locale, house)


def placement_label(
    locale: str,
    pl: PlanetPlacement,
    *,
    style: str,
    role: str = "",
) -> str:
    lang = _lang(locale)
    sign = sign_label(locale, pl.sign)
    dig = dignity_note(locale, pl, style=style)
    if _use_terms(style):
        theme = _house_theme(locale, pl.house)
        pname = _pl(locale, pl.key)
        base = f"{pname} в {sign}, {pl.house}-й дом («{theme}»)"
        return f"{base} · {dig}" if dig else base
    line = plain_placement_line(locale, pl, hint=role if role else "")
    if dig and lang == "ru":
        return f"{line} ({dig})"
    if dig:
        return f"{line} ({dig})"
    return line


def lord_of_house_note(locale: str, chart: JyotishChart, from_house: int, *, style: str = "terms") -> str:
    if not _use_terms(style):
        return plain_lord_line(locale, chart, from_house)
    lang = _lang(locale)
    lord_pl = lord_of(chart, from_house)
    h_sign = sign_label(locale, chart.house_signs[from_house])
    pname = _pl(locale, lord_pl.key)
    source = _house_theme(locale, from_house)
    if lord_pl.house == from_house:
        if lang == "ru":
            return (
                f"Управитель {from_house}-го ({pname}) в своём доме — "
                f"тема «{source}» звучит прямо и сильно"
            )
        return f"Lord of house {from_house} ({pname}) in its own house — {source} is direct and strong"
    effect = _LORD_IN_TARGET[lang].get(lord_pl.house, _LORD_IN_TARGET[lang][1])
    if lang == "ru":
        return (
            f"Управитель {from_house}-го ({h_sign}, {pname}) в {lord_pl.house}-м доме — {effect}"
        )
    return f"Lord of house {from_house} ({h_sign}, {pname}) in house {lord_pl.house} — {effect}"


def topic_frame(locale: str, question: str, *, ru: str, en: str, style: str = "terms") -> str:
    from app.natal_qa_voice import plain_topic_hook

    if not _use_terms(style):
        return plain_topic_hook(locale, question)
    topic = question.strip().rstrip("?.!")
    lang = _lang(locale)
    return ru.format(topic=topic) if lang == "ru" else en.format(topic=topic)


def make_brief(locale: str, frame: str, body: str) -> str:
    return p(b(frame), h(body))


def pick_markers(
    locale: str,
    placements: list[PlanetPlacement],
    *,
    style: str,
    roles: tuple[str, ...] = (),
    limit: int = 3,
) -> tuple[str, ...]:
    lines: list[str] = []
    for i, pl in enumerate(placements[:limit]):
        role = roles[i] if i < len(roles) else ""
        lines.append(placement_label(locale, pl, style=style, role=role))
    return tuple(lines)


def rank_dignity(pl: PlanetPlacement) -> int:
    return {"exalted": 4, "own": 3, "neutral": 2, "debilitated": 1}.get(pl.dignity, 2)
