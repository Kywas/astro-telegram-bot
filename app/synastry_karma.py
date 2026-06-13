"""Step 8 synastry: lunar nodes (Rahu/Ketu) and karmic links."""
from __future__ import annotations

from dataclasses import dataclass

import swisseph as swe

from app.forecast_text import _aspect_label

PERSONAL_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")
NODE_KEYS = ("RAHU", "KETU")

ASPECTS = (
    ("conjunction", 0, 8),
    ("sextile", 60, 6),
    ("square", 90, 7),
    ("trine", 120, 8),
    ("opposition", 180, 8),
)

HARMONIOUS = frozenset({"conjunction", "trine", "sextile"})
TENSE = frozenset({"square", "opposition"})

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "RAHU": "Раху (Северный узел)",
        "KETU": "Кету (Южный узел)",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "RAHU": "Rahu (North Node)",
        "KETU": "Ketu (South Node)",
    },
}


@dataclass(frozen=True)
class KarmicLink:
    kind: str
    node_owner: str
    node_key: str
    target_owner: str
    target_planet: str
    aspect: str
    orb: float


@dataclass(frozen=True)
class KarmicAnalysis:
    karmic_tasks: tuple[KarmicLink, ...]
    destined: tuple[KarmicLink, ...]

    @property
    def best_destined(self) -> KarmicLink | None:
        return self.destined[0] if self.destined else None

    @property
    def has_karmic_task(self) -> bool:
        return bool(self.karmic_tasks)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _angle_diff(first: float, second: float) -> float:
    diff = abs(first - second) % 360.0
    return diff if diff <= 180 else 360.0 - diff


def _find_aspect(first: float, second: float) -> tuple[str, float] | None:
    diff = _angle_diff(first, second)
    best: tuple[str, float] | None = None
    for name, exact, orb in ASPECTS:
        delta = abs(diff - exact)
        if delta <= orb and (best is None or delta < best[1]):
            best = (name, delta)
    return best


def _lunar_nodes(julian_day: float) -> dict[str, float]:
    result, _ = swe.calc_ut(julian_day, swe.TRUE_NODE)
    rahu = float(result[0])
    return {"RAHU": rahu, "KETU": (rahu + 180.0) % 360.0}


def _cross_node_links(
    node_owner: str,
    nodes: dict[str, float],
    target_owner: str,
    planets: dict[str, float],
    *,
    include_moon: bool,
) -> list[KarmicLink]:
    links: list[KarmicLink] = []
    for node_key in NODE_KEYS:
        for planet_key in PERSONAL_PLANETS:
            if planet_key == "MOON" and not include_moon:
                continue
            if planet_key not in planets:
                continue
            aspect_info = _find_aspect(nodes[node_key], planets[planet_key])
            if aspect_info is None:
                continue
            aspect, orb = aspect_info
            kind = "destined" if (
                node_key == "RAHU"
                and planet_key in {"SUN", "MOON"}
                and aspect == "conjunction"
                and orb <= 6.0
            ) else "karmic_task"
            links.append(
                KarmicLink(
                    kind=kind,
                    node_owner=node_owner,
                    node_key=node_key,
                    target_owner=target_owner,
                    target_planet=planet_key,
                    aspect=aspect,
                    orb=orb,
                )
            )
    links.sort(key=lambda item: item.orb)
    return links


def analyze_karmic_synastry(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    *,
    user_julian_day: float,
    partner_julian_day: float,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> KarmicAnalysis:
    user_nodes = _lunar_nodes(user_julian_day)
    partner_nodes = _lunar_nodes(partner_julian_day)

    all_links: list[KarmicLink] = []
    all_links.extend(
        _cross_node_links(
            "user",
            user_nodes,
            "partner",
            partner_planets,
            include_moon=partner_has_moon,
        )
    )
    all_links.extend(
        _cross_node_links(
            "partner",
            partner_nodes,
            "user",
            user_planets,
            include_moon=user_has_moon,
        )
    )

    destined = tuple(link for link in all_links if link.kind == "destined")
    destined = tuple(sorted(destined, key=lambda item: item.orb))
    karmic_tasks = tuple(
        sorted(
            (link for link in all_links if link.kind == "karmic_task"),
            key=lambda item: item.orb,
        )
    )
    return KarmicAnalysis(karmic_tasks=karmic_tasks, destined=destined)


def karmic_score_delta(analysis: KarmicAnalysis) -> int:
    delta = 0
    if analysis.best_destined is not None:
        delta += 4 if analysis.best_destined.orb <= 3.0 else 3
    if analysis.has_karmic_task:
        delta += 2 if len(analysis.karmic_tasks) >= 2 else 1
    return delta


def _format_link_line(locale: str, link: KarmicLink) -> str:
    lang = _lang(locale)
    aspect_label = _aspect_label(locale, link.aspect)
    orb_part = f" ({link.orb:.1f}°)" if link.orb <= 2.5 else ""
    node_name = _planet_label(locale, link.node_key)
    target_name = _planet_label(locale, link.target_planet)

    if link.node_owner == "user":
        if lang == "ru":
            return (
                f"ваш {node_name}, {aspect_label} "
                f"к {target_name} партнёра{orb_part}"
            )
        return (
            f"your {node_name} {aspect_label} "
            f"partner's {target_name}{orb_part}"
        )

    if lang == "ru":
        return (
            f"{node_name} партнёра, {aspect_label} "
            f"к вашему {target_name}{orb_part}"
        )
    return (
        f"partner's {node_name} {aspect_label} "
        f"your {target_name}{orb_part}"
    )


def _task_interpretation(locale: str, link: KarmicLink) -> str:
    lang = _lang(locale)
    if link.aspect in HARMONIOUS:
        if lang == "ru":
            return "узел поддерживает рост — задача проживается мягче, но ощутимо."
        return "the node supports growth — the lesson is noticeable but easier to integrate."
    if lang == "ru":
        return "узел создаёт напряжение — отношения тянут к переменам и честности."
    return "the node adds tension — the bond pushes change and honesty."


def format_synastry_step8_section(locale: str, analysis: KarmicAnalysis, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "🪷 Шаг 8. Кармические показатели"
            if use_synastry_terms(style)
            else "🪷 Шаг 8. Глубинные задачи пары"
        )
        if use_synastry_terms(style):
            lines.append(
                "Лунные узлы: Раху (Северный) и Кету (Южный) — темы кармы и "
                "направления роста в паре (тропик, True Node)."
            )
        else:
            lines.append(
                "Темы, которые пара словно «принесла с собой» — "
                "уроки роста и ощущение смысла."
            )
    else:
        lines.append(
            "🪷 Step 8. Karmic indicators"
            if use_synastry_terms(style)
            else "🪷 Step 8. Deep pair themes"
        )
        if use_synastry_terms(style):
            lines.append(
                "Lunar nodes: Rahu (North) and Ketu (South) — karmic themes and "
                "growth direction (tropical True Node)."
            )
        else:
            lines.append(
                "Themes you seem to carry into the bond — lessons, growth, and sense of purpose."
            )

    lines.append("")
    if lang == "ru":
        lines.append("✨ «Предназначенная» связь")
        lines.append(
            "Северный узел (Раху) одного в соединении с Солнцем или Луной другого."
        )
    else:
        lines.append("✨ “Destined” bond")
        lines.append(
            "One partner's North Node (Rahu) conjunct the other's Sun or Moon."
        )

    if analysis.best_destined is None:
        lines.append(
            "• Точного соединения Раху↔Солнце/Луна не найдено — связь не обязана быть «судьбой», "
            "но может быть глубокой по другим показателям."
            if lang == "ru"
            else "• No exact Rahu↔Sun/Moon conjunction — the bond needn't be “fated”, "
            "but can still run deep through other factors."
        )
    else:
        lines.append(f"• {_format_link_line(locale, analysis.best_destined).capitalize()}.")
        if lang == "ru":
            lines.append(
                "• Признак сильной, «узловой» связи — будто вы встретились не случайно."
            )
        else:
            lines.append(
                "• A strong nodal bond — as if the meeting carries a sense of purpose."
            )
        for link in analysis.destined[1:2]:
            lines.append(f"• ↳ {_format_link_line(locale, link).capitalize()}.")

    lines.append("")
    if lang == "ru":
        lines.append("🎯 Кармическая задача")
        lines.append(
            "Узлы одного в аспекте к личным планетам другого — "
            "отношения несут урок и задачу."
        )
    else:
        lines.append("🎯 Karmic task")
        lines.append(
            "One partner's nodes aspecting the other's personal planets — "
            "the relationship carries a lesson."
        )

    if not analysis.has_karmic_task:
        lines.append(
            "• Ярких узловых аспектов к личным планетам нет — кармический урок мягче или "
            "раскрывается через другие шаги."
            if lang == "ru"
            else "• No strong nodal aspects to personal planets — the karmic lesson is lighter "
            "or shows through other steps."
        )
    else:
        for link in analysis.karmic_tasks[:3]:
            lines.append(f"• {_format_link_line(locale, link).capitalize()}.")
            lines.append(f"  ↳ {_task_interpretation(locale, link)}")
        if len(analysis.karmic_tasks) > 3:
            extra = len(analysis.karmic_tasks) - 3
            if lang == "ru":
                lines.append(f"• … и ещё {extra} узловых связей.")
            else:
                lines.append(f"• … plus {extra} more nodal links.")

    return "\n".join(lines)
