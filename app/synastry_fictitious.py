"""Synastry: fictitious points — Black Moon (Lilith) and White Moon (Selena)."""
from __future__ import annotations

from dataclasses import dataclass

import swisseph as swe

from app.forecast_text import _aspect_label

PERSONAL_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")
SELENA_TARGETS = ("SUN", "MOON")

ASPECTS = (
    ("conjunction", 0, 6),
    ("sextile", 60, 4),
    ("square", 90, 5),
    ("trine", 120, 5),
    ("opposition", 180, 6),
)

HARMONIOUS = frozenset({"conjunction", "trine", "sextile"})
TENSE = frozenset({"square", "opposition"})

POINT_LABELS = {
    "ru": {
        "LILITH": "Лилит (Чёрная Луна)",
        "SELENA": "Селена (Белая Луна)",
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
    },
    "en": {
        "LILITH": "Lilith (Black Moon)",
        "SELENA": "Selena (White Moon)",
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
    },
}

POINT_LABELS_PLAIN = {
    "ru": {
        "LILITH": "теневая сторона",
        "SELENA": "светлая поддержка",
    },
    "en": {
        "LILITH": "shadow side",
        "SELENA": "light support",
    },
}


@dataclass(frozen=True)
class FictitiousLink:
    point_owner: str
    point_key: str
    target_owner: str
    target_planet: str
    aspect: str
    orb: float
    kind: str


@dataclass(frozen=True)
class FictitiousAnalysis:
    lilith_links: tuple[FictitiousLink, ...]
    selena_links: tuple[FictitiousLink, ...]

    @property
    def best_lilith(self) -> FictitiousLink | None:
        return self.lilith_links[0] if self.lilith_links else None

    @property
    def best_selena(self) -> FictitiousLink | None:
        harmonious = [link for link in self.selena_links if link.aspect in HARMONIOUS]
        if harmonious:
            return harmonious[0]
        return self.selena_links[0] if self.selena_links else None

    @property
    def has_angelic_protection(self) -> bool:
        return any(
            link.aspect in HARMONIOUS and link.orb <= 4.0
            for link in self.selena_links
        )


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _label(locale: str, key: str, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if not use_synastry_terms(style) and key in {"LILITH", "SELENA"}:
        return POINT_LABELS_PLAIN[lang][key]
    return POINT_LABELS[lang].get(key, key)


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


def _fictitious_points(julian_day: float) -> dict[str, float]:
    result, _ = swe.calc_ut(julian_day, swe.MEAN_APOG)
    lilith = float(result[0])
    return {"LILITH": lilith, "SELENA": (lilith + 180.0) % 360.0}


def _cross_links(
    point_owner: str,
    points: dict[str, float],
    target_owner: str,
    planets: dict[str, float],
    *,
    point_key: str,
    target_planets: tuple[str, ...],
    include_moon: bool,
    kind: str,
) -> list[FictitiousLink]:
    links: list[FictitiousLink] = []
    for planet_key in target_planets:
        if planet_key == "MOON" and not include_moon:
            continue
        if planet_key not in planets:
            continue
        aspect_info = _find_aspect(points[point_key], planets[planet_key])
        if aspect_info is None:
            continue
        aspect, orb = aspect_info
        links.append(
            FictitiousLink(
                point_owner=point_owner,
                point_key=point_key,
                target_owner=target_owner,
                target_planet=planet_key,
                aspect=aspect,
                orb=orb,
                kind=kind,
            )
        )
    links.sort(key=lambda item: item.orb)
    return links


def analyze_fictitious_synastry(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    *,
    user_julian_day: float,
    partner_julian_day: float,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> FictitiousAnalysis:
    user_points = _fictitious_points(user_julian_day)
    partner_points = _fictitious_points(partner_julian_day)

    lilith_links: list[FictitiousLink] = []
    lilith_links.extend(
        _cross_links(
            "user",
            user_points,
            "partner",
            partner_planets,
            point_key="LILITH",
            target_planets=PERSONAL_PLANETS,
            include_moon=partner_has_moon,
            kind="lilith_shadow",
        )
    )
    lilith_links.extend(
        _cross_links(
            "partner",
            partner_points,
            "user",
            user_planets,
            point_key="LILITH",
            target_planets=PERSONAL_PLANETS,
            include_moon=user_has_moon,
            kind="lilith_shadow",
        )
    )

    selena_links: list[FictitiousLink] = []
    selena_links.extend(
        _cross_links(
            "user",
            user_points,
            "partner",
            partner_planets,
            point_key="SELENA",
            target_planets=SELENA_TARGETS,
            include_moon=partner_has_moon,
            kind="selena_light",
        )
    )
    selena_links.extend(
        _cross_links(
            "partner",
            partner_points,
            "user",
            user_planets,
            point_key="SELENA",
            target_planets=SELENA_TARGETS,
            include_moon=user_has_moon,
            kind="selena_light",
        )
    )

    lilith_links.sort(key=lambda item: item.orb)
    selena_links.sort(key=lambda item: (0 if item.aspect in HARMONIOUS else 1, item.orb))
    return FictitiousAnalysis(
        lilith_links=tuple(lilith_links),
        selena_links=tuple(selena_links),
    )


def fictitious_score_delta(analysis: FictitiousAnalysis) -> int:
    delta = 0
    if analysis.has_angelic_protection:
        delta += 3 if analysis.best_selena and analysis.best_selena.orb <= 2.5 else 2
    lilith = analysis.best_lilith
    if lilith is not None and lilith.aspect in TENSE and lilith.orb <= 3.0:
        delta -= 2
    elif lilith is not None and lilith.orb <= 2.0:
        delta -= 1
    return delta


def _format_link_line(locale: str, link: FictitiousLink, *, style: str) -> str:
    lang = _lang(locale)
    aspect_label = _aspect_label(locale, link.aspect)
    orb_part = f" ({link.orb:.1f}°)" if link.orb <= 2.5 else ""
    point_name = _label(locale, link.point_key, style=style)
    target_name = _label(locale, link.target_planet, style=style)

    if link.point_owner == "user":
        if lang == "ru":
            return f"ваша {point_name}, {aspect_label} к {target_name} партнёра{orb_part}"
        return f"your {point_name} {aspect_label} partner's {target_name}{orb_part}"

    if lang == "ru":
        return f"{point_name} партнёра, {aspect_label} к вашему {target_name}{orb_part}"
    return f"partner's {point_name} {aspect_label} your {target_name}{orb_part}"


def _lilith_interpretation(locale: str, link: FictitiousLink, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if link.aspect in TENSE:
        if lang == "ru":
            if use_synastry_terms(style):
                return (
                    "теневая зона: возможны искушения, манипуляции или "
                    "эмоциональная зависимость — важна осознанность."
                )
            return (
                "теневая зона: риск давления, игр или зависимости — "
                "важны границы и честность."
            )
        if use_synastry_terms(style):
            return (
                "shadow zone: temptations, manipulation, or dependency may surface — "
                "awareness matters."
            )
        return "shadow zone: pressure, games, or dependency — boundaries and honesty help."

    if lang == "ru":
        if use_synastry_terms(style):
            return "тень проявляется мягче, но тема соблазнов и слабых мест в паре всё равно активна."
        return "слабые места и соблазны заметны, но проявляются не так остро."
    if use_synastry_terms(style):
        return "the shadow runs softer, but temptations and weak spots in the bond stay active."
    return "weak spots and temptations are present but less sharp."


def _selena_interpretation(locale: str, link: FictitiousLink, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if link.aspect in HARMONIOUS:
        if lang == "ru":
            if use_synastry_terms(style):
                return (
                    "светлая карма и поддержка — ощущение «ангельской» защиты "
                    "в паре, особенно для Солнца/Луны."
                )
            return "зона светлой поддержки — чувство, что вас берегут и сопровождают в паре."
        if use_synastry_terms(style):
            return (
                "light karma and support — a sense of “angelic” protection in the bond, "
                "especially for Sun/Moon."
            )
        return "a zone of gentle support — feeling guarded and accompanied in the pair."

    if lang == "ru":
        return "поддержка есть, но через испытание — свет проявляется после честного диалога."
    return "support is present through a test — the light shows after honest dialogue."


def format_synastry_fictitious_section(
    locale: str,
    analysis: FictitiousAnalysis,
    *,
    style: str = "terms",
) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "🌑 Фиктивные точки · Лилит и Селена"
            if use_synastry_terms(style)
            else "🌑 Тень и свет в паре"
        )
        if use_synastry_terms(style):
            lines.append(
                "Лилит (средняя апогейная Чёрная Луна) — искушения и теневые стороны; "
                "Селена (точка, противоположная Лилит) — светлая карма и поддержка."
            )
        else:
            lines.append(
                "Теневая сторона — соблазны и слабые места; "
                "светлая сторона — зоны поддержки и бережного сопровождения."
            )
    else:
        lines.append(
            "🌑 Fictitious points · Lilith and Selena"
            if use_synastry_terms(style)
            else "🌑 Shadow and light in the pair"
        )
        if use_synastry_terms(style):
            lines.append(
                "Lilith (mean apogee Black Moon) — temptations and shadow sides; "
                "Selena (point opposite Lilith) — light karma and support."
            )
        else:
            lines.append(
                "The shadow side — temptations and weak spots; "
                "the light side — zones of support and gentle guardianship."
            )

    lines.append("")
    if lang == "ru":
        lines.append("Чёрная Луна (Лилит)" if use_synastry_terms(style) else "Теневая сторона")
    else:
        lines.append("Black Moon (Lilith)" if use_synastry_terms(style) else "Shadow side")

    if not analysis.lilith_links:
        lines.append(
            "• Точных связей Лилит с личными планетами партнёра нет — тень не доминирует."
            if lang == "ru"
            else "• No tight Lilith links to partner's personal planets — shadow doesn't dominate."
        )
    else:
        for link in analysis.lilith_links[:3]:
            lines.append(f"• {_format_link_line(locale, link, style=style)}.")
            lines.append(f"  {_lilith_interpretation(locale, link, style=style)}")

    lines.append("")
    if lang == "ru":
        lines.append("Белая Луна (Селена)" if use_synastry_terms(style) else "Светлая поддержка")
    else:
        lines.append("White Moon (Selena)" if use_synastry_terms(style) else "Light support")

    if not analysis.selena_links:
        lines.append(
            "• Селена не аспектирует Солнце/Луну партнёра — «ангельская» опора не выделена."
            if lang == "ru"
            else "• Selena doesn't aspect partner's Sun/Moon — no highlighted “angelic” support."
        )
    else:
        for link in analysis.selena_links[:3]:
            lines.append(f"• {_format_link_line(locale, link, style=style)}.")
            lines.append(f"  {_selena_interpretation(locale, link, style=style)}")

    return "\n".join(lines)
