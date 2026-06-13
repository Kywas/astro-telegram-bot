"""Step 10 synastry: final compatibility summary table and interpretation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.forecast_text import _aspect_label
from app.sun_sign_compat import (
    SIGN_LABELS,
    SunSignCompat,
    SunSignKind,
    analyze_sun_sign_compat,
    _element_label,
)
from app.synastry_elements import (
    COMPATIBLE_ELEMENT_PAIRS,
    CHALLENGING_ELEMENT_PAIRS,
    ElementBalance,
)
from app.synastry_style import format_aspect_label, format_element_plain, use_synastry_terms
from app.synastry_asc import AngleMatchKind, AscDscAnalysis
from app.synastry_composite import CompositeAnalysis
from app.synastry_numerology import NumerologyCompat
from app.synastry_tarot import TarotCompatSpread
from app.synastry_progressions import ProgressionsAnalysis
from app.synastry_fictitious import FictitiousAnalysis
from app.synastry_houses import PLANET_LABELS as HOUSE_PLANET_LABELS, SynastryHouseOverlay
from app.synastry_karma import KarmicAnalysis
from app.synastry_moon_venus import MoonVenusAnalysis
from app.synastry_overlay import KEY_PAIRS, HARMONIOUS_ASPECTS, find_best_key_pair_hit
from app.synastry_seals import PLANET_LABELS as SEAL_PLANET_LABELS, SynastrySeals
from app.synastry_transits import SynastryTransitAnalysis

SynastryHit = tuple[float, str, str, str]

LUMINARIES = frozenset({"SUN", "MOON", "VENUS", "MARS"})


class CompatibilityLevel(StrEnum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class AssessmentTier(StrEnum):
    BASIC = "basic"
    MEDIUM = "medium"
    ADVANCED = "advanced"
    ESOTERIC = "esoteric"


@dataclass(frozen=True)
class SummaryRow:
    criterion: str
    indicator: str
    rating: str
    tone: str
    tier: AssessmentTier = AssessmentTier.BASIC

    @property
    def points(self) -> int:
        if self.tone == "harmony":
            return 1
        if self.tone == "tension":
            return -1
        return 0


@dataclass(frozen=True)
class TierTotals:
    tier: AssessmentTier
    label: str
    harmony: int
    tension: int
    neutral: int
    net: int


@dataclass(frozen=True)
class SynastrySummary:
    score: int
    level: CompatibilityLevel
    level_label: str
    harmonious_pct: int
    interpretation: str
    rows: tuple[SummaryRow, ...]
    tier_totals: tuple[TierTotals, ...]
    net_balance: int

def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _tier_label(locale: str, tier: AssessmentTier, *, style: str = "terms") -> str:
    lang = _lang(locale)
    if tier == AssessmentTier.BASIC:
        return (
            "Базовый уровень: солнечные знаки + асценденты"
            if use_synastry_terms(style) and lang == "ru"
            else "Basic: Sun signs + ascendants"
            if use_synastry_terms(style)
            else ("Базовый уровень" if lang == "ru" else "Basic level")
        )
    if tier == AssessmentTier.MEDIUM:
        return (
            "Средний уровень: синастрия + дома"
            if use_synastry_terms(style) and lang == "ru"
            else "Medium: synastry + houses"
            if use_synastry_terms(style)
            else ("Средний уровень" if lang == "ru" else "Medium level")
        )
    if tier == AssessmentTier.ADVANCED:
        return (
            "Продвинутый уровень: композит + дирекции + фиктивные точки"
            if use_synastry_terms(style) and lang == "ru"
            else "Advanced: composite + directions + fictitious points"
            if use_synastry_terms(style)
            else ("Продвинутый уровень" if lang == "ru" else "Advanced level")
        )
    return (
        "Эзотерический уровень: нумерология + Таро + энергии"
        if use_synastry_terms(style) and lang == "ru"
        else "Esoteric: numerology + Tarot + energies"
        if use_synastry_terms(style)
        else ("Эзотерический уровень" if lang == "ru" else "Esoteric level")
    )


def _tag(row: SummaryRow, tier: AssessmentTier) -> SummaryRow:
    return SummaryRow(
        row.criterion,
        row.indicator,
        row.rating,
        row.tone,
        tier=tier,
    )


def _points_label(tone: str) -> str:
    if tone == "harmony":
        return "+1"
    if tone == "tension":
        return "−1"
    return "0"


def _compute_tier_totals(locale: str, rows: list[SummaryRow], *, style: str = "terms") -> tuple[TierTotals, ...]:
    totals: list[TierTotals] = []
    for tier in AssessmentTier:
        tier_rows = [row for row in rows if row.tier == tier]
        if not tier_rows:
            continue
        harmony = sum(1 for row in tier_rows if row.tone == "harmony")
        tension = sum(1 for row in tier_rows if row.tone == "tension")
        neutral = sum(1 for row in tier_rows if row.tone == "neutral")
        net = sum(row.points for row in tier_rows)
        totals.append(
            TierTotals(
                tier=tier,
                label=_tier_label(locale, tier, style=style),
                harmony=harmony,
                tension=tension,
                neutral=neutral,
                net=net,
            )
        )
    return tuple(totals)


def _harmony_ratio(hits: list[SynastryHit]) -> float:
    if not hits:
        return 0.5
    harmonious = sum(1 for hit in hits if hit[3] in HARMONIOUS_ASPECTS)
    return harmonious / len(hits)


def _elements_balanced(balance: ElementBalance) -> bool:
    pair = (balance.user.dominant, balance.partner.dominant)
    return pair in COMPATIBLE_ELEMENT_PAIRS or balance.user.dominant == balance.partner.dominant


def _elements_imbalanced(balance: ElementBalance) -> bool:
    pair = (balance.user.dominant, balance.partner.dominant)
    return pair in CHALLENGING_ELEMENT_PAIRS


def _sun_moon_harmonious(
    hits: list[SynastryHit],
    *,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> bool | None:
    if not user_has_moon and not partner_has_moon:
        return None
    hit = find_best_key_pair_hit(hits, KEY_PAIRS[0])
    if hit is None:
        return False
    return hit[3] in HARMONIOUS_ASPECTS


def _moon_venus_harmonious(analysis: MoonVenusAnalysis) -> bool | None:
    if not analysis.user_has_moon and not analysis.partner_has_moon:
        return None
    if analysis.best_harmonious is None:
        return analysis.best_tense is None
    if analysis.best_tense is None:
        return True
    return analysis.best_harmonious.orb <= analysis.best_tense.orb


def _level_label(locale: str, level: CompatibilityLevel) -> str:
    lang = _lang(locale)
    if level == CompatibilityLevel.HIGH:
        return "высокая совместимость" if lang == "ru" else "high compatibility"
    if level == CompatibilityLevel.MODERATE:
        return "умеренная совместимость" if lang == "ru" else "moderate compatibility"
    return "низкая совместимость" if lang == "ru" else "low compatibility"


def integrate_comprehensive_score(base_score: int, net_balance: int) -> int:
    """Nudge /100 score from the +1/−1 scorecard so all layers affect the headline."""
    nudge = max(-8, min(8, round(net_balance * 1.5)))
    return max(35, min(98, base_score + nudge))


def classify_compatibility_level(
    hits: list[SynastryHit],
    *,
    seals: SynastrySeals,
    element_balance: ElementBalance,
    moon_venus: MoonVenusAnalysis,
    user_has_moon: bool,
    partner_has_moon: bool,
    net_balance: int = 0,
) -> CompatibilityLevel:
    harmony_ratio = _harmony_ratio(hits)
    has_happiness = seals.best_happiness is not None
    has_unhappiness = seals.best_unhappiness is not None
    elements_ok = _elements_balanced(element_balance)
    elements_bad = _elements_imbalanced(element_balance)
    sun_moon = _sun_moon_harmonious(
        hits,
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
    )
    moon_venus_ok = _moon_venus_harmonious(moon_venus)

    if harmony_ratio > 0.7 and has_happiness and elements_ok:
        return CompatibilityLevel.HIGH

    if net_balance >= 5 and harmony_ratio > 0.55 and not has_unhappiness:
        return CompatibilityLevel.HIGH

    low_signals = sum(
        (
            harmony_ratio <= 0.5,
            has_unhappiness,
            elements_bad,
        )
    )
    if low_signals >= 2:
        return CompatibilityLevel.LOW

    if net_balance <= -4:
        return CompatibilityLevel.LOW

    key_links: list[bool] = []
    if sun_moon is not None:
        key_links.append(sun_moon)
    if moon_venus_ok is not None:
        key_links.append(moon_venus_ok)
    if key_links and all(key_links):
        return CompatibilityLevel.MODERATE

    if harmony_ratio <= 0.45 or (has_unhappiness and elements_bad):
        return CompatibilityLevel.LOW
    if harmony_ratio > 0.55 and has_happiness:
        return CompatibilityLevel.MODERATE
    if harmony_ratio > 0.5:
        return CompatibilityLevel.MODERATE
    return CompatibilityLevel.LOW


def _format_interpretation(
    locale: str,
    level: CompatibilityLevel,
    *,
    harmonious_pct: int,
    seals: SynastrySeals,
    element_balance: ElementBalance,
    sun_moon: bool | None,
    moon_venus_ok: bool | None,
    net_balance: int = 0,
    tier_totals: tuple[TierTotals, ...] = (),
) -> str:
    lang = _lang(locale)
    elements_ok = _elements_balanced(element_balance)
    has_happiness = seals.best_happiness is not None
    has_unhappiness = seals.best_unhappiness is not None
    elements_bad = _elements_imbalanced(element_balance)

    scope_line = ""
    if tier_totals:
        if lang == "ru":
            scope_line = (
                f"Комплексная карта (4 уровня): баланс {net_balance:+d} "
                f"(+1 гармония, −1 напряжение по каждому критерию)."
            )
        else:
            scope_line = (
                f"Four-level scorecard: balance {net_balance:+d} "
                f"(+1 harmony, −1 tension per criterion)."
            )

    if level == CompatibilityLevel.HIGH:
        if lang == "ru":
            lines = [
                "Высокая совместимость: более 70% гармоничных аспектов, "
                "есть печать счастья, баланс стихий.",
                f"• Гармоничных аспектов: {harmonious_pct}% (>70%).",
            ]
            if scope_line:
                lines.append(f"• {scope_line}")
            if has_happiness:
                lines.append("• Печать счастья — есть.")
            if elements_ok:
                lines.append("• Стихии дополняют друг друга.")
            return "\n".join(lines)

        lines = [
            "High compatibility: over 70% harmonious aspects, "
            "happiness seal present, balanced elements.",
            f"• Harmonious aspects: {harmonious_pct}% (>70%).",
        ]
        if scope_line:
            lines.append(f"• {scope_line}")
        if has_happiness:
            lines.append("• Seal of happiness — yes.")
        if elements_ok:
            lines.append("• Elements complement each other.")
        return "\n".join(lines)

    if level == CompatibilityLevel.MODERATE:
        if lang == "ru":
            lines = [
                "Умеренная совместимость: смешанные показатели, "
                "но ключевые связи (Луна‑Венера, Солнце‑Луна) гармоничны.",
                f"• Гармоничных аспектов: {harmonious_pct}% — смешанный фон.",
            ]
            if scope_line:
                lines.append(f"• {scope_line}")
        else:
            lines = [
                "Moderate compatibility: mixed indicators, "
                "but key links (Moon‑Venus, Sun‑Moon) are harmonious.",
                f"• Harmonious aspects: {harmonious_pct}% — mixed background.",
            ]
            if scope_line:
                lines.append(f"• {scope_line}")
        if sun_moon:
            lines.append(
                "• Солнце↔Луна — гармония." if lang == "ru" else "• Sun↔Moon — harmony."
            )
        elif sun_moon is False:
            lines.append(
                "• Солнце↔Луна — не главный ресурс пары."
                if lang == "ru"
                else "• Sun↔Moon — not the main resource."
            )
        if moon_venus_ok:
            lines.append(
                "• Луна↔Венера — гармония." if lang == "ru" else "• Moon↔Venus — harmony."
            )
        elif moon_venus_ok is False:
            lines.append(
                "• Луна↔Венера — зона внимания."
                if lang == "ru"
                else "• Moon↔Venus — area to nurture."
            )
        return "\n".join(lines)

    if lang == "ru":
        lines = [
            "Низкая совместимость: доминируют напряжённые аспекты, "
            "печать несчастья или дисбаланс стихий.",
            f"• Гармоничных аспектов: {harmonious_pct}% — напряжение сильнее.",
        ]
        if scope_line:
            lines.append(f"• {scope_line}")
    else:
        lines = [
            "Low compatibility: tense aspects dominate, "
            "unhappiness seal or elemental imbalance.",
            f"• Harmonious aspects: {harmonious_pct}% — tension weighs more.",
        ]
        if scope_line:
            lines.append(f"• {scope_line}")
    if has_unhappiness:
        lines.append("• Печать несчастья — есть." if lang == "ru" else "• Seal of unhappiness — yes.")
    if elements_bad:
        lines.append(
            "• Стихии тянут в разные стороны."
            if lang == "ru"
            else "• Elements pull in different directions."
        )
    if harmonious_pct <= 50:
        lines.append(
            "• Больше напряжённых, чем поддерживающих связей."
            if lang == "ru"
            else "• More tense than supportive links."
        )
    return "\n".join(lines)


def _sun_sign_row(locale: str, compat: SunSignCompat | None, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    if compat is None:
        criterion = "Солнечные знаки" if lang == "ru" else "Sun signs"
        return SummaryRow(criterion, "—", "—", "neutral")

    user_name = SIGN_LABELS[lang][compat.user_sign]
    partner_name = SIGN_LABELS[lang][compat.partner_sign]
    indicator = f"{user_name} + {partner_name}"

    kind = compat.kind
    if kind == SunSignKind.OPPOSITE:
        rating = (
            "Напряжение (противоположности)"
            if lang == "ru"
            else "Tension (opposites)"
        )
        tone = "tension"
    elif kind == SunSignKind.CHALLENGING_ELEMENTS:
        rating = "Напряжение (стихии)" if lang == "ru" else "Tension (elements)"
        tone = "tension"
    elif kind == SunSignKind.SAME_SIGN:
        rating = "Гармония (один знак)" if lang == "ru" else "Harmony (same sign)"
        tone = "harmony"
    elif kind == SunSignKind.SAME_ELEMENT:
        rating = "Гармония (одна стихия)" if lang == "ru" else "Harmony (same element)"
        tone = "harmony"
    elif kind == SunSignKind.COMPATIBLE_ELEMENTS:
        rating = "Гармония (стихии)" if lang == "ru" else "Harmony (elements)"
        tone = "harmony"
    else:
        rating = "Нейтрально" if lang == "ru" else "Neutral"
        tone = "neutral"

    criterion = "Солнечные знаки" if lang == "ru" else "Sun signs"
    if not use_synastry_terms(style):
        criterion = "Характер" if lang == "ru" else "Character"
    return SummaryRow(criterion, indicator, rating, tone)


def _asc_dsc_row(locale: str, analysis: AscDscAnalysis, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "ASC↔DSC" if lang == "ru" else "ASC↔DSC"
    if not use_synastry_terms(style):
        criterion = "Образ и партнёр" if lang == "ru" else "Self and partner"

    if not analysis.full_analysis:
        missing = "Нет времени рождения" if lang == "ru" else "Birth times missing"
        return SummaryRow(criterion, "—", missing, "neutral")

    if not analysis.matches:
        return SummaryRow(
            criterion,
            "—",
            "Нейтрально" if lang == "ru" else "Neutral",
            "neutral",
        )

    primary = analysis.matches[0]
    if primary in {
        AngleMatchKind.USER_ASC_PARTNER_DSC,
        AngleMatchKind.PARTNER_ASC_USER_DSC,
    }:
        indicator = "ASC = DSC" if use_synastry_terms(style) else "Совпадение" if lang == "ru" else "Match"
        rating = "Притяжение" if lang == "ru" else "Attraction"
        tone = "harmony"
    elif primary == AngleMatchKind.SAME_ASC:
        indicator = "ASC = ASC" if use_synastry_terms(style) else "Похожи" if lang == "ru" else "Similar"
        rating = "Гармония" if lang == "ru" else "Harmony"
        tone = "harmony"
    elif primary in {AngleMatchKind.OPPOSITE_ASC_DSC, AngleMatchKind.OPPOSITE_ASC}:
        indicator = "Противоп." if lang == "ru" else "Opposites"
        rating = "Магнетизм" if lang == "ru" else "Magnetism"
        tone = "harmony"
    else:
        indicator = "—"
        rating = "Нейтрально" if lang == "ru" else "Neutral"
        tone = "neutral"
    return SummaryRow(criterion, indicator, rating, tone)


def _synastry_aspects_row(
    locale: str,
    hits: list[SynastryHit],
    *,
    style: str = "terms",
) -> SummaryRow:
    lang = _lang(locale)
    criterion = "Синастрия (аспекты)" if lang == "ru" else "Synastry (aspects)"
    if not use_synastry_terms(style):
        criterion = "Связи планет" if lang == "ru" else "Planet links"

    if not hits:
        return SummaryRow(
            criterion,
            "—",
            "Нейтрально" if lang == "ru" else "Neutral",
            "neutral",
        )

    ratio = _harmony_ratio(hits)
    pct = round(ratio * 100)
    indicator = f"{pct}%" + (" гарм." if lang == "ru" else " harm.")

    if ratio > 0.6:
        rating = "Гармония" if lang == "ru" else "Harmony"
        tone = "harmony"
    elif ratio < 0.4:
        rating = "Напряжение" if lang == "ru" else "Tension"
        tone = "tension"
    else:
        rating = "Смешанно" if lang == "ru" else "Mixed"
        tone = "neutral"
    return SummaryRow(criterion, indicator, rating, tone)


def _houses_row(locale: str, overlay: SynastryHouseOverlay, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Дома" if lang == "ru" else "Houses"
    if not use_synastry_terms(style):
        criterion = "Сферы жизни" if lang == "ru" else "Life areas"

    if not overlay.available:
        return SummaryRow(
            criterion,
            "—",
            "Нужны время и город" if lang == "ru" else "Need time and city",
            "neutral",
        )

    angular = overlay.angular_placements()
    partner_in_user_7 = overlay.partner_in_user.get(7, ())
    user_in_partner_7 = overlay.user_in_partner.get(7, ())

    if "SUN" in partner_in_user_7 or "SUN" in user_in_partner_7:
        indicator = "☉ в 7‑м" if lang == "ru" else "☉ in 7th"
        return SummaryRow(
            criterion,
            indicator,
            "Сильная связь" if lang == "ru" else "Strong bond",
            "harmony",
        )

    if angular >= 3:
        indicator = (
            f"угловые {angular}"
            if lang == "ru"
            else f"angular {angular}"
        )
        return SummaryRow(
            criterion,
            indicator,
            "Сильное влияние" if lang == "ru" else "Strong influence",
            "harmony",
        )

    if angular >= 1:
        indicator = (
            f"угловые {angular}"
            if lang == "ru"
            else f"angular {angular}"
        )
        return SummaryRow(
            criterion,
            indicator,
            "Есть связи" if lang == "ru" else "Links present",
            "neutral",
        )

    return SummaryRow(
        criterion,
        "—",
        "Слабое" if lang == "ru" else "Weak",
        "neutral",
    )


def _energy_row(locale: str, balance: ElementBalance, *, style: str = "terms") -> SummaryRow:
    row = _elements_row(locale, balance, style=style)
    lang = _lang(locale)
    criterion = "Энергии стихий" if lang == "ru" else "Element energies"
    if not use_synastry_terms(style):
        criterion = "Энергии" if lang == "ru" else "Energies"
    return SummaryRow(criterion, row.indicator, row.rating, row.tone)


def _tarot_row(locale: str, analysis: TarotCompatSpread, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Таро" if lang == "ru" else "Tarot"
    if not use_synastry_terms(style):
        criterion = "Карты" if lang == "ru" else "Cards"

    strengths = next(card for card in analysis.cards if card.position == "strengths")
    weaknesses = next(card for card in analysis.cards if card.position == "weaknesses")
    indicator = f"{strengths.name} / {weaknesses.name}"

    if analysis.score_delta >= 3:
        rating = "Опора" if lang == "ru" else "Support"
        tone = "harmony"
    elif analysis.score_delta >= 1:
        rating = "Благоприятно" if lang == "ru" else "Favorable"
        tone = "harmony"
    elif analysis.score_delta <= -1:
        rating = "Риски" if lang == "ru" else "Risks"
        tone = "tension"
    else:
        rating = "Ровно" if lang == "ru" else "Steady"
        tone = "neutral"
    return SummaryRow(criterion, indicator, rating, tone)


def _numerology_row(locale: str, analysis: NumerologyCompat, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Нумерология" if lang == "ru" else "Numerology"
    if not use_synastry_terms(style):
        criterion = "Числа" if lang == "ru" else "Numbers"

    compat = analysis.compatibility_number
    if use_synastry_terms(style):
        indicator = (
            f"{analysis.user_life_path}+{analysis.partner_life_path}→{compat}"
            if lang == "ru"
            else f"{analysis.user_life_path}+{analysis.partner_life_path}→{compat}"
        )
    else:
        indicator = str(compat)

    if analysis.score_delta >= 3:
        rating = "Гармония" if lang == "ru" else "Harmony"
        tone = "harmony"
    elif analysis.score_delta >= 2:
        rating = "Благоприятно" if lang == "ru" else "Favorable"
        tone = "harmony"
    elif analysis.score_delta >= 1:
        rating = "Ровно" if lang == "ru" else "Steady"
        tone = "neutral"
    else:
        rating = "Сложнее" if lang == "ru" else "Challenging"
        tone = "tension"
    return SummaryRow(criterion, indicator, rating, tone)


def _progressions_row(locale: str, analysis: ProgressionsAnalysis, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Прогрессии" if lang == "ru" else "Progressions"
    if not use_synastry_terms(style):
        criterion = "Развитие" if lang == "ru" else "Evolution"

    if analysis.best_harmony is not None:
        aspect = format_aspect_label(locale, analysis.best_harmony.aspect, style)
        indicator = aspect.capitalize()
        rating = "Благоприятно" if lang == "ru" else "Favorable"
        return SummaryRow(criterion, indicator, rating, "harmony")

    if analysis.best_tension is not None:
        aspect = format_aspect_label(locale, analysis.best_tension.aspect, style)
        indicator = aspect.capitalize()
        rating = "Испытание" if lang == "ru" else "Testing"
        return SummaryRow(criterion, indicator, rating, "tension")

    if analysis.emotional_reset_active:
        return SummaryRow(
            criterion,
            "Луна ↻" if use_synastry_terms(style) else ("Сброс" if lang == "ru" else "Reset"),
            "Перезагрузка" if lang == "ru" else "Reload",
            "neutral",
        )

    return SummaryRow(
        criterion,
        "—",
        "Спокойно" if lang == "ru" else "Calm",
        "neutral",
    )


def _composite_row(locale: str, analysis: CompositeAnalysis, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Композит" if lang == "ru" else "Composite"
    if not use_synastry_terms(style):
        criterion = "Союз" if lang == "ru" else "Union"

    if not analysis.available:
        return SummaryRow(criterion, "—", "—", "neutral")

    sun_part = _sign_name(locale, analysis.sun_sign)
    if analysis.sun_house is not None:
        indicator = f"☉ {sun_part}, {analysis.sun_house} дом" if lang == "ru" else f"☉ {sun_part}, h{analysis.sun_house}"
    else:
        indicator = f"☉ {sun_part}"

    if analysis.sun_house in {5, 7, 8}:
        rating = "Сильное ядро" if lang == "ru" else "Strong core"
        tone = "harmony"
    elif analysis.angular_planets:
        rating = "Угловые темы" if lang == "ru" else "Angular themes"
        tone = "harmony"
    else:
        rating = "Ровно" if lang == "ru" else "Steady"
        tone = "neutral"
    return SummaryRow(criterion, indicator, rating, tone)


def _sign_name(locale: str, sign: str) -> str:
    return SIGN_LABELS[_lang(locale)][sign]


def _fictitious_row(locale: str, analysis: FictitiousAnalysis, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Лилит / Селена" if lang == "ru" else "Lilith / Selena"
    if not use_synastry_terms(style):
        criterion = "Тень / свет" if lang == "ru" else "Shadow / light"

    lilith = analysis.best_lilith
    selena = analysis.best_selena

    if lilith is None and selena is None:
        return SummaryRow(
            criterion,
            "—",
            "Нейтрально" if lang == "ru" else "Neutral",
            "neutral",
        )

    if analysis.has_angelic_protection and (
        lilith is None or lilith.aspect not in {"square", "opposition"} or lilith.orb > 3.0
    ):
        indicator = "Селена ✓" if use_synastry_terms(style) else ("Свет ✓" if lang == "ru" else "Light ✓")
        rating = "Поддержка" if lang == "ru" else "Support"
        return SummaryRow(criterion, indicator, rating, "harmony")

    if lilith is not None and lilith.aspect in {"square", "opposition"} and lilith.orb <= 3.0:
        indicator = "Лилит ⚠" if use_synastry_terms(style) else ("Тень ⚠" if lang == "ru" else "Shadow ⚠")
        rating = "Осторожно" if lang == "ru" else "Caution"
        return SummaryRow(criterion, indicator, rating, "tension")

    if selena is not None and selena.aspect in {"trine", "sextile", "conjunction"}:
        indicator = "Селена" if use_synastry_terms(style) else ("Свет" if lang == "ru" else "Light")
        rating = "Поддержка" if lang == "ru" else "Support"
        return SummaryRow(criterion, indicator, rating, "harmony")

    return SummaryRow(
        criterion,
        "Лилит" if use_synastry_terms(style) else ("Тень" if lang == "ru" else "Shadow"),
        "Заметно" if lang == "ru" else "Notable",
        "neutral",
    )


def _moon_venus_row(locale: str, analysis: MoonVenusAnalysis, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Луна↔Венера" if lang == "ru" else "Moon↔Venus"
    if not use_synastry_terms(style):
        criterion = "Эмоции и забота" if lang == "ru" else "Feelings and care"

    if not analysis.user_has_moon and not analysis.partner_has_moon:
        missing = "Нет времени рождения" if lang == "ru" else "Birth times missing"
        return SummaryRow(criterion, "—", missing, "neutral")

    best = analysis.best_harmonious
    tense = analysis.best_tense
    if best is None and tense is None:
        return SummaryRow(
            criterion,
            "—",
            "Связей нет" if lang == "ru" else "No links",
            "neutral",
        )

    if best is not None and (tense is None or best.orb <= tense.orb):
        aspect = format_aspect_label(locale, best.aspect, style)
        rating = "Гармония" if lang == "ru" else "Harmony"
        return SummaryRow(criterion, aspect.capitalize(), rating, "harmony")

    assert tense is not None
    aspect = format_aspect_label(locale, tense.aspect, style)
    rating = "Напряжение" if lang == "ru" else "Tension"
    return SummaryRow(criterion, aspect.capitalize(), rating, "tension")


def _seal_indicator(locale: str, seal) -> str:
    lang = _lang(locale)
    source = SEAL_PLANET_LABELS[lang][seal.source_planet]
    target = SEAL_PLANET_LABELS[lang][seal.target_planet]
    aspect = _aspect_label(locale, seal.aspect)
    if lang == "ru":
        return f"{source} в {aspect} к {target}"
    return f"{source} {aspect} {target}"


def _happiness_seal_row(locale: str, seals: SynastrySeals, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Печать счастья" if lang == "ru" else "Seal of happiness"
    if not use_synastry_terms(style):
        criterion = "Поддержка" if lang == "ru" else "Support"
    if seals.best_happiness is None:
        return SummaryRow(
            criterion,
            "—",
            "Нет" if lang == "ru" else "None",
            "neutral",
        )
    return SummaryRow(
        criterion,
        _seal_indicator(locale, seals.best_happiness),
        "Есть" if lang == "ru" else "Yes",
        "harmony",
    )


def _unhappiness_seal_row(locale: str, seals: SynastrySeals) -> SummaryRow | None:
    if seals.best_unhappiness is None:
        return None
    lang = _lang(locale)
    criterion = "Печать несчастья" if lang == "ru" else "Seal of unhappiness"
    return SummaryRow(
        criterion,
        _seal_indicator(locale, seals.best_unhappiness),
        "Есть" if lang == "ru" else "Yes",
        "tension",
    )


def _planet_short(locale: str, planet: str) -> str:
    return HOUSE_PLANET_LABELS[_lang(locale)].get(planet, planet)


def _house7_row(locale: str, overlay: SynastryHouseOverlay) -> SummaryRow:
    lang = _lang(locale)
    criterion = "7‑й дом" if lang == "ru" else "7th house"

    if not overlay.available:
        return SummaryRow(
            criterion,
            "Нужны время и город" if lang == "ru" else "Need time and city",
            "—",
            "neutral",
        )

    partner_in_user = overlay.partner_in_user.get(7, ())
    user_in_partner = overlay.user_in_partner.get(7, ())

    if "SUN" in partner_in_user:
        indicator = (
            "Солнце партнёра в моём 7‑м"
            if lang == "ru"
            else "Partner's Sun in my 7th"
        )
        return SummaryRow(
            criterion,
            indicator,
            "Сильная связь" if lang == "ru" else "Strong bond",
            "harmony",
        )
    if "SUN" in user_in_partner:
        indicator = (
            "Моё Солнце в 7‑м партнёра"
            if lang == "ru"
            else "My Sun in partner's 7th"
        )
        return SummaryRow(
            criterion,
            indicator,
            "Сильная связь" if lang == "ru" else "Strong bond",
            "harmony",
        )

    planets = partner_in_user or user_in_partner
    if planets:
        names = ", ".join(_planet_short(locale, planet) for planet in planets[:2])
        if partner_in_user:
            indicator = (
                f"{names} партнёра в моём 7‑м"
                if lang == "ru"
                else f"Partner's {names} in my 7th"
            )
        else:
            indicator = (
                f"Мои {names} в 7‑м партнёра"
                if lang == "ru"
                else f"My {names} in partner's 7th"
            )
        strong = any(planet in LUMINARIES for planet in planets)
        rating = "Связь" if lang == "ru" else "Bond"
        return SummaryRow(criterion, indicator, rating, "harmony" if strong else "neutral")

    return SummaryRow(
        criterion,
        "—",
        "Слабая" if lang == "ru" else "Weak",
        "neutral",
    )


def _elements_row(locale: str, balance: ElementBalance, *, style: str = "terms") -> SummaryRow:
    lang = _lang(locale)
    criterion = "Стихии" if lang == "ru" else "Elements"
    if use_synastry_terms(style):
        user_elem = _element_label(locale, balance.user.dominant)
        partner_elem = _element_label(locale, balance.partner.dominant)
    else:
        user_elem = format_element_plain(locale, balance.user.dominant)
        partner_elem = format_element_plain(locale, balance.partner.dominant)
    indicator = f"{user_elem} + {partner_elem}"

    pair = (balance.user.dominant, balance.partner.dominant)
    if pair in COMPATIBLE_ELEMENT_PAIRS:
        rating = "Гармония" if lang == "ru" else "Harmony"
        tone = "harmony"
    elif balance.user.dominant == balance.partner.dominant:
        rating = "Гармония" if lang == "ru" else "Harmony"
        tone = "harmony"
    elif pair in CHALLENGING_ELEMENT_PAIRS:
        rating = "Напряжение" if lang == "ru" else "Tension"
        tone = "tension"
    else:
        rating = "Нейтрально" if lang == "ru" else "Neutral"
        tone = "neutral"

    return SummaryRow(criterion, indicator, rating, tone)


def _karma_row(locale: str, karma: KarmicAnalysis) -> SummaryRow | None:
    lang = _lang(locale)
    criterion = "Карма (узлы)" if lang == "ru" else "Karma (nodes)"

    if karma.best_destined is not None:
        link = karma.best_destined
        aspect = _aspect_label(locale, link.aspect)
        target = SEAL_PLANET_LABELS[lang].get(link.target_planet, link.target_planet)
        if lang == "ru":
            indicator = f"Раху ↔ {target} ({aspect})"
        else:
            indicator = f"Rahu ↔ {target} ({aspect})"
        return SummaryRow(
            criterion,
            indicator,
            "Предназначение" if lang == "ru" else "Destined",
            "harmony",
        )

    if karma.has_karmic_task and karma.karmic_tasks:
        link = karma.karmic_tasks[0]
        target = SEAL_PLANET_LABELS[lang].get(link.target_planet, link.target_planet)
        indicator = f"узел ↔ {target}" if lang == "ru" else f"node ↔ {target}"
        tone = "harmony" if link.aspect in HARMONIOUS_ASPECTS else "tension"
        rating = "Задача" if lang == "ru" else "Task"
        return SummaryRow(criterion, indicator, rating, tone)

    return None


def _transits_row(locale: str, transits: SynastryTransitAnalysis) -> SummaryRow:
    lang = _lang(locale)
    criterion = "Транзиты сейчас" if lang == "ru" else "Transits now"
    harmony = len(transits.current_harmony)
    tension = len(transits.current_tension)
    if harmony > tension:
        indicator = f"+{harmony}/−{tension}"
        rating = "Благоприятно" if lang == "ru" else "Favorable"
        tone = "harmony"
    elif tension > harmony:
        indicator = f"+{harmony}/−{tension}"
        rating = "Испытание" if lang == "ru" else "Testing"
        tone = "tension"
    else:
        indicator = "—"
        rating = "Спокойно" if lang == "ru" else "Calm"
        tone = "neutral"
    return SummaryRow(criterion, indicator, rating, tone)


def build_synastry_summary(
    *,
    locale: str,
    score: int,
    hits: list[SynastryHit],
    user_sign_key: str,
    partner_sign_key: str,
    seals: SynastrySeals,
    asc_dsc: AscDscAnalysis,
    composite: CompositeAnalysis,
    progressions: ProgressionsAnalysis,
    numerology: NumerologyCompat,
    tarot: TarotCompatSpread,
    house_overlay: SynastryHouseOverlay,
    element_balance: ElementBalance,
    moon_venus: MoonVenusAnalysis,
    karma: KarmicAnalysis,
    fictitious: FictitiousAnalysis,
    transits: SynastryTransitAnalysis,
    user_has_moon: bool,
    partner_has_moon: bool,
    style: str = "terms",
) -> SynastrySummary:
    sun_compat = analyze_sun_sign_compat(user_sign_key, partner_sign_key)
    rows: list[SummaryRow] = [
        _tag(_sun_sign_row(locale, sun_compat, style=style), AssessmentTier.BASIC),
        _tag(_asc_dsc_row(locale, asc_dsc, style=style), AssessmentTier.BASIC),
        _tag(_synastry_aspects_row(locale, hits, style=style), AssessmentTier.MEDIUM),
        _tag(_houses_row(locale, house_overlay, style=style), AssessmentTier.MEDIUM),
        _tag(_moon_venus_row(locale, moon_venus, style=style), AssessmentTier.MEDIUM),
        _tag(_happiness_seal_row(locale, seals, style=style), AssessmentTier.MEDIUM),
    ]
    unhappiness = _unhappiness_seal_row(locale, seals)
    if unhappiness is not None:
        rows.append(_tag(unhappiness, AssessmentTier.MEDIUM))

    rows.extend(
        [
            _tag(_composite_row(locale, composite, style=style), AssessmentTier.ADVANCED),
            _tag(_progressions_row(locale, progressions, style=style), AssessmentTier.ADVANCED),
            _tag(_fictitious_row(locale, fictitious, style=style), AssessmentTier.ADVANCED),
        ]
    )
    karma_row = _karma_row(locale, karma)
    if karma_row is not None:
        rows.append(_tag(karma_row, AssessmentTier.ADVANCED))
    rows.append(_tag(_transits_row(locale, transits), AssessmentTier.ADVANCED))

    rows.extend(
        [
            _tag(_numerology_row(locale, numerology, style=style), AssessmentTier.ESOTERIC),
            _tag(_tarot_row(locale, tarot, style=style), AssessmentTier.ESOTERIC),
            _tag(_energy_row(locale, element_balance, style=style), AssessmentTier.ESOTERIC),
        ]
    )

    tier_totals = _compute_tier_totals(locale, rows, style=style)
    net_balance = sum(row.points for row in rows)
    integrated_score = integrate_comprehensive_score(score, net_balance)

    harmonious_pct = round(_harmony_ratio(hits) * 100)
    level = classify_compatibility_level(
        hits,
        seals=seals,
        element_balance=element_balance,
        moon_venus=moon_venus,
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
        net_balance=net_balance,
    )
    sun_moon = _sun_moon_harmonious(
        hits,
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
    )
    moon_venus_ok = _moon_venus_harmonious(moon_venus)
    interpretation = _format_interpretation(
        locale,
        level,
        harmonious_pct=harmonious_pct,
        seals=seals,
        element_balance=element_balance,
        sun_moon=sun_moon,
        moon_venus_ok=moon_venus_ok,
        net_balance=net_balance,
        tier_totals=tier_totals,
    )

    return SynastrySummary(
        score=integrated_score,
        level=level,
        level_label=_level_label(locale, level),
        harmonious_pct=harmonious_pct,
        interpretation=interpretation,
        rows=tuple(rows),
        tier_totals=tier_totals,
        net_balance=net_balance,
    )

def _tone_icon(tone: str) -> str:
    if tone == "harmony":
        return "🟢"
    if tone == "tension":
        return "🔴"
    return "⚪"


def format_synastry_step10_section(
    locale: str,
    summary: SynastrySummary,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "📊 Шаг 10. Итоговая карта совместимости"
            if use_synastry_terms(style)
            else "📊 Шаг 10. Итог для пары"
        )
        lines.append(f"Общий балл: {summary.score}/100 — {summary.level_label}")
        lines.append(
            f"Суммарный баланс: {summary.net_balance:+d} "
            f"(гармония +1, напряжение −1)"
            if use_synastry_terms(style)
            else f"Balance: {summary.net_balance:+d}"
        )
        lines.append("")
        lines.append(
            "Критерий · Показатель · Балл"
            if use_synastry_terms(style)
            else "Criterion · Indicator · Score"
        )
    else:
        lines.append(
            "📊 Step 10. Compatibility scorecard"
            if use_synastry_terms(style)
            else "📊 Step 10. Pair summary"
        )
        lines.append(f"Overall: {summary.score}/100 — {summary.level_label}")
        lines.append(
            f"Net balance: {summary.net_balance:+d} (harmony +1, tension −1)"
            if use_synastry_terms(style)
            else f"Balance: {summary.net_balance:+d}"
        )
        lines.append("")
        lines.append(
            "Criterion · Indicator · Score"
            if use_synastry_terms(style)
            else "Item · Indicator · Score"
        )

    current_tier: AssessmentTier | None = None
    for row in summary.rows:
        if row.tier != current_tier:
            current_tier = row.tier
            lines.append("")
            tier_total = next(
                (item for item in summary.tier_totals if item.tier == current_tier),
                None,
            )
            header = _tier_label(locale, current_tier, style=style)
            if tier_total is not None:
                header = f"{header} · {tier_total.net:+d}"
            lines.append(f"— {header} —")

        icon = _tone_icon(row.tone)
        score_label = _points_label(row.tone)
        if use_synastry_terms(style):
            lines.append(f"{icon} {row.criterion} · {row.indicator} · {score_label}")
        else:
            lines.append(f"{icon} {row.criterion} · {row.indicator} · {row.rating} ({score_label})")

    lines.append("")
    if lang == "ru":
        lines.append("Итого по уровням:")
        for tier_total in summary.tier_totals:
            short = _tier_label(locale, tier_total.tier, style="plain")
            lines.append(
                f"• {short}: {tier_total.net:+d} "
                f"(+{tier_total.harmony}/−{tier_total.tension}/0×{tier_total.neutral})"
            )
    else:
        lines.append("Totals by level:")
        for tier_total in summary.tier_totals:
            short = _tier_label(locale, tier_total.tier, style="plain")
            lines.append(
                f"• {short}: {tier_total.net:+d} "
                f"(+{tier_total.harmony}/−{tier_total.tension}/0×{tier_total.neutral})"
            )

    lines.append("")
    lines.append("📝 " + ("Интерпретация" if lang == "ru" else "Interpretation"))
    lines.append(summary.interpretation)

    return "\n".join(lines)