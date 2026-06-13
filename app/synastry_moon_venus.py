"""Step 7 synastry: Moon and Venus cross-aspects for emotional closeness."""
from __future__ import annotations

from dataclasses import dataclass

from app.forecast_text import _aspect_label

SynastryHit = tuple[float, str, str, str]

HARMONIOUS_ASPECTS = frozenset({"conjunction", "trine", "sextile"})
TENSE_ASPECTS = frozenset({"square", "opposition"})

MOON_VENUS_PAIRS = frozenset({("MOON", "VENUS"), ("VENUS", "MOON")})

PLANET_LABELS = {
    "ru": {"MOON": "Луна", "VENUS": "Венера"},
    "en": {"MOON": "Moon", "VENUS": "Venus"},
}


@dataclass(frozen=True)
class MoonVenusLink:
    direction: str
    moon_owner: str
    venus_owner: str
    orb: float
    aspect: str
    tone: str

    @property
    def is_harmonious(self) -> bool:
        return self.aspect in HARMONIOUS_ASPECTS

    @property
    def is_tense(self) -> bool:
        return self.aspect in TENSE_ASPECTS


@dataclass(frozen=True)
class MoonVenusAnalysis:
    harmonious: tuple[MoonVenusLink, ...]
    tense: tuple[MoonVenusLink, ...]
    user_has_moon: bool
    partner_has_moon: bool

    @property
    def best_harmonious(self) -> MoonVenusLink | None:
        return self.harmonious[0] if self.harmonious else None

    @property
    def best_tense(self) -> MoonVenusLink | None:
        return self.tense[0] if self.tense else None


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)][planet]


def _parse_moon_venus_hit(hit: SynastryHit) -> MoonVenusLink | None:
    orb, user_planet, partner_planet, aspect = hit
    pair = (user_planet, partner_planet)
    if pair not in MOON_VENUS_PAIRS:
        return None

    if user_planet == "MOON":
        return MoonVenusLink(
            direction="user_moon_partner_venus",
            moon_owner="user",
            venus_owner="partner",
            orb=orb,
            aspect=aspect,
            tone="harmonious" if aspect in HARMONIOUS_ASPECTS else "tense",
        )
    return MoonVenusLink(
        direction="partner_moon_user_venus",
        moon_owner="partner",
        venus_owner="user",
        orb=orb,
        aspect=aspect,
        tone="harmonious" if aspect in HARMONIOUS_ASPECTS else "tense",
    )


def analyze_moon_venus_links(
    hits: list[SynastryHit],
    *,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> MoonVenusAnalysis:
    harmonious: list[MoonVenusLink] = []
    tense: list[MoonVenusLink] = []
    for hit in hits:
        link = _parse_moon_venus_hit(hit)
        if link is None:
            continue
        if link.moon_owner == "user" and not user_has_moon:
            continue
        if link.moon_owner == "partner" and not partner_has_moon:
            continue
        if link.is_harmonious:
            harmonious.append(link)
        elif link.is_tense:
            tense.append(link)
    harmonious.sort(key=lambda item: item.orb)
    tense.sort(key=lambda item: item.orb)
    return MoonVenusAnalysis(
        harmonious=tuple(harmonious),
        tense=tuple(tense),
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
    )


def moon_venus_score_delta(analysis: MoonVenusAnalysis) -> int:
    delta = 0
    if analysis.best_harmonious is not None:
        delta += 4 if analysis.best_harmonious.orb <= 2.0 else 3
    if analysis.best_tense is not None:
        delta -= 3 if analysis.best_tense.orb <= 2.0 else 2
    if analysis.best_harmonious and analysis.best_tense:
        delta = max(-2, min(4, delta))
    return delta


def _format_link_line(locale: str, link: MoonVenusLink) -> str:
    lang = _lang(locale)
    aspect_label = _aspect_label(locale, link.aspect)
    orb_part = f" ({link.orb:.1f}°)" if link.orb <= 2.5 else ""

    if link.direction == "user_moon_partner_venus":
        if lang == "ru":
            return (
                f"ваша {_planet_label(locale, 'MOON')}, {aspect_label} "
                f"к {_planet_label(locale, 'VENUS')} партнёра{orb_part}"
            )
        return (
            f"your {_planet_label(locale, 'MOON')} {aspect_label} "
            f"partner's {_planet_label(locale, 'VENUS')}{orb_part}"
        )

    if lang == "ru":
        return (
            f"{_planet_label(locale, 'MOON')} партнёра, {aspect_label} "
            f"к вашей {_planet_label(locale, 'VENUS')}{orb_part}"
        )
    return (
        f"partner's {_planet_label(locale, 'MOON')} {aspect_label} "
        f"your {_planet_label(locale, 'VENUS')}{orb_part}"
    )


def format_synastry_step7_section(locale: str, analysis: MoonVenusAnalysis, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "💞 Шаг 7. Луна и Венера — эмоциональная связь"
            if use_synastry_terms(style)
            else "💞 Шаг 7. Эмоции и забота"
        )
        if use_synastry_terms(style):
            lines.append(
                "Луна — эмоциональная реакция и потребность в заботе; "
                "Венера — любовь, эстетика и комфорт."
            )
            lines.append("Смотрим аспекты между Луной одного и Венерой другого.")
        else:
            lines.append(
                "Насколько ваши чувства и способ проявлять заботу совпадают "
                "с тем, что нужно партнёру."
            )
    else:
        lines.append(
            "💞 Step 7. Moon and Venus — emotional bond"
            if use_synastry_terms(style)
            else "💞 Step 7. Feelings and care"
        )
        if use_synastry_terms(style):
            lines.append(
                "Moon — emotional reactions and need for care; "
                "Venus — love, beauty, and comfort."
            )
            lines.append("We check aspects between one partner's Moon and the other's Venus.")
        else:
            lines.append(
                "How your feelings and way of showing care match what the partner needs."
            )

    if not analysis.user_has_moon:
        lines.append(
            "• Ваше время рождения не указано — ваша Луна не участвует."
            if lang == "ru"
            else "• Your birth time is missing — your Moon is not included."
        )
    if not analysis.partner_has_moon:
        lines.append(
            "• У партнёра нет времени рождения — Луна партнёра не участвует."
            if lang == "ru"
            else "• Partner birth time is missing — partner Moon is not included."
        )

    lines.append("")
    if lang == "ru":
        lines.append("😊 Гармония — душевная близость")
    else:
        lines.append("😊 Harmony — soul closeness")

    if analysis.best_harmonious is None:
        lines.append(
            "• Яркой связи Луна↔Венера не найдено — близость может строиться через другие темы карты."
            if lang == "ru"
            else "• No strong Moon↔Venus link — closeness may grow through other chart themes."
        )
    else:
        lines.append(f"• {_format_link_line(locale, analysis.best_harmonious).capitalize()}.")
        if lang == "ru":
            lines.append(
                "• Гармоничный аспект — легче чувствовать заботу, нежность и «меня понимают»."
            )
        else:
            lines.append(
                "• A harmonious aspect — easier to feel cared for, cherished, and understood."
            )
        for link in analysis.harmonious[1:2]:
            lines.append(f"• ↳ {_format_link_line(locale, link).capitalize()}.")

    lines.append("")
    if lang == "ru":
        lines.append("😔 Напряжение — разные языки заботы")
    else:
        lines.append("😔 Tension — different love languages")

    if analysis.best_tense is None:
        lines.append(
            "• Напряжённых аспектов Луна↔Венера нет — меньше типичных обид из‑за «как любить»."
            if lang == "ru"
            else "• No tense Moon↔Venus aspects — fewer typical hurts around “how to love.”"
        )
    else:
        lines.append(f"• {_format_link_line(locale, analysis.best_tense).capitalize()}.")
        if lang == "ru":
            lines.append(
                "• Напряжённый аспект — риск обид, если ждёте заботу «как у себя»; "
                "проговаривайте, что для вас комфорт."
            )
        else:
            lines.append(
                "• A tense aspect — risk of hurt if you expect care “your way”; "
                "name what comfort means to each of you."
            )
        for link in analysis.tense[1:2]:
            lines.append(f"• ↳ {_format_link_line(locale, link).capitalize()}.")

    if analysis.best_harmonious and analysis.best_tense:
        lines.append("")
        if lang == "ru":
            lines.append(
                "• В паре и притяжение, и чувствительность — опирайтесь на гармонию "
                "и не принимайте различия на личный счёт."
            )
        else:
            lines.append(
                "• You have both pull and sensitivity — lean on the harmony "
                "and don't take differences personally."
            )
    elif not analysis.user_has_moon or not analysis.partner_has_moon:
        lines.append("")
        if lang == "ru":
            lines.append(
                "• Для полного анализа Луна↔Венера добавьте время рождения обоим."
            )
        else:
            lines.append(
                "• For full Moon↔Venus analysis, add birth time for both partners."
            )

    return "\n".join(lines)
