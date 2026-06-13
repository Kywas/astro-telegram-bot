"""Step 4 synastry: happiness and unhappiness seals (Jupiter/Saturn to Sun/Moon)."""
from __future__ import annotations

from dataclasses import dataclass

from app.forecast_text import _aspect_label
from app.synastry_style import format_seal_link_line, use_synastry_terms

SynastryHit = tuple[float, str, str, str]

HARMONIOUS_ASPECTS = frozenset({"conjunction", "trine", "sextile"})
TENSE_ASPECTS = frozenset({"square", "opposition"})
LUMINARIES = frozenset({"SUN", "MOON"})

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
    },
}


@dataclass(frozen=True)
class SynastrySeal:
    kind: str
    direction: str
    orb: float
    source_planet: str
    target_planet: str
    aspect: str


@dataclass(frozen=True)
class SynastrySeals:
    happiness: tuple[SynastrySeal, ...]
    unhappiness: tuple[SynastrySeal, ...]

    @property
    def best_happiness(self) -> SynastrySeal | None:
        return self.happiness[0] if self.happiness else None

    @property
    def best_unhappiness(self) -> SynastrySeal | None:
        return self.unhappiness[0] if self.unhappiness else None

    @property
    def seal_hit_keys(self) -> frozenset[tuple[str, str, str]]:
        keys: set[tuple[str, str, str]] = set()
        for seal in (*self.happiness, *self.unhappiness):
            if seal.direction == "user_to_partner":
                keys.add((seal.source_planet, seal.target_planet, seal.aspect))
            else:
                keys.add((seal.target_planet, seal.source_planet, seal.aspect))
        return frozenset(keys)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _parse_seal_hit(hit: SynastryHit) -> SynastrySeal | None:
    orb, user_planet, partner_planet, aspect = hit

    if user_planet == "JUPITER" and partner_planet in LUMINARIES and aspect in HARMONIOUS_ASPECTS:
        return SynastrySeal(
            kind="happiness",
            direction="user_to_partner",
            orb=orb,
            source_planet="JUPITER",
            target_planet=partner_planet,
            aspect=aspect,
        )
    if partner_planet == "JUPITER" and user_planet in LUMINARIES and aspect in HARMONIOUS_ASPECTS:
        return SynastrySeal(
            kind="happiness",
            direction="partner_to_user",
            orb=orb,
            source_planet="JUPITER",
            target_planet=user_planet,
            aspect=aspect,
        )
    if user_planet == "SATURN" and partner_planet in LUMINARIES and aspect in TENSE_ASPECTS:
        return SynastrySeal(
            kind="unhappiness",
            direction="user_to_partner",
            orb=orb,
            source_planet="SATURN",
            target_planet=partner_planet,
            aspect=aspect,
        )
    if partner_planet == "SATURN" and user_planet in LUMINARIES and aspect in TENSE_ASPECTS:
        return SynastrySeal(
            kind="unhappiness",
            direction="partner_to_user",
            orb=orb,
            source_planet="SATURN",
            target_planet=user_planet,
            aspect=aspect,
        )
    return None


def analyze_synastry_seals(hits: list[SynastryHit]) -> SynastrySeals:
    happiness: list[SynastrySeal] = []
    unhappiness: list[SynastrySeal] = []
    for hit in hits:
        seal = _parse_seal_hit(hit)
        if seal is None:
            continue
        if seal.kind == "happiness":
            happiness.append(seal)
        else:
            unhappiness.append(seal)
    happiness.sort(key=lambda item: item.orb)
    unhappiness.sort(key=lambda item: item.orb)
    return SynastrySeals(happiness=tuple(happiness), unhappiness=tuple(unhappiness))


def seal_score_delta(seals: SynastrySeals) -> int:
    delta = 0
    if seals.best_happiness is not None:
        delta += 4
    if seals.best_unhappiness is not None:
        delta -= 4
    return delta


def filter_hits_for_step3(hits: list[SynastryHit], seals: SynastrySeals) -> list[SynastryHit]:
    keys = seals.seal_hit_keys
    if not keys:
        return hits
    return [hit for hit in hits if (hit[1], hit[2], hit[3]) not in keys]


def _format_seal_aspect_line(locale: str, seal: SynastrySeal, *, style: str = "terms") -> str:
    return format_seal_link_line(
        locale,
        direction=seal.direction,
        source_planet=seal.source_planet,
        target_planet=seal.target_planet,
        aspect=seal.aspect,
        style=style,
        source_label=_planet_label(locale, seal.source_planet),
        target_label=_planet_label(locale, seal.target_planet),
    )


def format_synastry_step4_section(locale: str, seals: SynastrySeals, *, style: str = "terms") -> str:
    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append("✨ Шаг 4. Печати в синастрии" if use_synastry_terms(style) else "✨ Шаг 4. Сильные маркеры пары")
        if use_synastry_terms(style):
            lines.append(
                "Классические «печати» — связи Юпитера и Сатурна одного партнёра "
                "с Солнцем или Луной другого."
            )
        else:
            lines.append(
                "Отмечаем, где один из вас приносит поддержку или серьёзные уроки "
                "в тему личности и эмоций другого."
            )
        lines.append("")
        lines.append("😊 Печать счастья" if use_synastry_terms(style) else "😊 Поддержка и радость")
        if use_synastry_terms(style):
            lines.append(
                "Юпитер → Солнце/Луна другого в гармоничном аспекте "
                "(0°, 60°, 120°) — радость и поддержка."
            )
        else:
            lines.append("Щедрость и оптимизм одного легко подпитывают суть или эмоции другого.")
    else:
        lines.append("✨ Step 4. Synastry seals" if use_synastry_terms(style) else "✨ Step 4. Strong pair markers")
        if use_synastry_terms(style):
            lines.append(
                "Classic “seals” — one partner's Jupiter or Saturn linked to "
                "the other's Sun or Moon."
            )
        else:
            lines.append(
                "Where one of you brings support or serious lessons "
                "into the other's core or emotional life."
            )
        lines.append("")
        lines.append("😊 Seal of happiness" if use_synastry_terms(style) else "😊 Support and joy")
        if use_synastry_terms(style):
            lines.append(
                "Jupiter → other's Sun/Moon in a harmonious aspect "
                "(0°, 60°, 120°) — joy and support."
            )
        else:
            lines.append("One partner's generosity easily feeds the other's core or feelings.")

    if seals.best_happiness is None:
        lines.append(
            "• Не найдена — базовая поддержка может идти из других связей карты."
            if lang == "ru"
            else "• Not found — support may come from other chart links."
        )
    else:
        lines.append(f"• {_format_seal_aspect_line(locale, seals.best_happiness, style=style).capitalize()}.")
        if lang == "ru":
            lines.append("• Печать счастья — больше лёгкости, оптимизма и ощущения «нам хорошо вместе».")
        else:
            lines.append("• Seal of happiness — more ease, optimism, and a sense that the bond feels good.")

    lines.append("")
    if lang == "ru":
        lines.append("😔 Печать несчастья")
        lines.append(
            "Сатурн → Солнце/Луна другого в напряжённом аспекте "
            "(90°, 180°) — ограничения и тяжесть."
        )
    else:
        lines.append("😔 Seal of unhappiness")
        lines.append(
            "Saturn → other's Sun/Moon in a tense aspect "
            "(90°, 180°) — restriction and heaviness."
        )

    if seals.best_unhappiness is None:
        lines.append(
            "• Не найдена — явного «сатурнианского» груза в этой паре по печати нет."
            if lang == "ru"
            else "• Not found — no strong Saturn seal weighing on this pair."
        )
    else:
        lines.append(f"• {_format_seal_aspect_line(locale, seals.best_unhappiness, style=style).capitalize()}.")
        if lang == "ru":
            lines.append(
                "• Печать несчастья — риск чувства долга, дистанции или «надо терпеть»; "
                "важны границы и реалистичные ожидания."
            )
        else:
            lines.append(
                "• Seal of unhappiness — risk of duty, distance, or “we must endure”; "
                "boundaries and realistic expectations help."
            )

    if len(seals.happiness) > 1 or len(seals.unhappiness) > 1:
        lines.append("")
        extra_label = "Дополнительные печати" if lang == "ru" else "Additional seals"
        lines.append(f"{extra_label}:")
        for seal in seals.happiness[1:2]:
            prefix = "😊" if seal.kind == "happiness" else "😔"
            lines.append(f"{prefix} {_format_seal_aspect_line(locale, seal, style=style).capitalize()}.")
        for seal in seals.unhappiness[1:2]:
            lines.append(f"😔 {_format_seal_aspect_line(locale, seal, style=style).capitalize()}.")

    return "\n".join(lines)
