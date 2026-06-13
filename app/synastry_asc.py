"""Step 2 synastry: Ascendant (ASC) and Descendant (DSC) angle pairing."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.sun_sign_compat import SIGN_LABELS, ZODIAC_SIGNS, are_opposite_signs

ASC_CUSP_INDEX = 0
DSC_CUSP_INDEX = 6

SCORE_DELTA = {
    "user_asc_partner_dsc": 6,
    "partner_asc_user_dsc": 6,
    "same_asc": 3,
    "opposite_asc_dsc": 5,
    "opposite_asc": 4,
}


class AngleMatchKind(StrEnum):
    USER_ASC_PARTNER_DSC = "user_asc_partner_dsc"
    PARTNER_ASC_USER_DSC = "partner_asc_user_dsc"
    SAME_ASC = "same_asc"
    OPPOSITE_ASC_DSC = "opposite_asc_dsc"
    OPPOSITE_ASC = "opposite_asc"


@dataclass(frozen=True)
class AscDscAnalysis:
    user_asc_sign: str | None
    user_dsc_sign: str | None
    partner_asc_sign: str | None
    partner_dsc_sign: str | None
    user_has_angles: bool
    partner_has_angles: bool
    matches: tuple[AngleMatchKind, ...]
    score_delta: int

    @property
    def available(self) -> bool:
        return self.user_has_angles or self.partner_has_angles

    @property
    def full_analysis(self) -> bool:
        return self.user_has_angles and self.partner_has_angles


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _longitude_to_sign(longitude: float) -> str:
    normalized = longitude % 360.0
    index = int(normalized // 30) % 12
    return ZODIAC_SIGNS[index]


def _angle_sign(cusps: list[float] | None, index: int) -> str | None:
    if not cusps or len(cusps) < 12:
        return None
    return _longitude_to_sign(cusps[index])


def _detect_matches(
    user_asc: str | None,
    user_dsc: str | None,
    partner_asc: str | None,
    partner_dsc: str | None,
) -> tuple[AngleMatchKind, ...]:
    if not all((user_asc, user_dsc, partner_asc, partner_dsc)):
        return ()

    matches: list[AngleMatchKind] = []
    assert user_asc and user_dsc and partner_asc and partner_dsc

    if user_asc == partner_dsc:
        matches.append(AngleMatchKind.USER_ASC_PARTNER_DSC)
    if partner_asc == user_dsc:
        matches.append(AngleMatchKind.PARTNER_ASC_USER_DSC)
    if user_asc == partner_asc:
        matches.append(AngleMatchKind.SAME_ASC)
    if user_asc != partner_dsc and are_opposite_signs(user_asc, partner_dsc):
        matches.append(AngleMatchKind.OPPOSITE_ASC_DSC)
    if user_asc != partner_asc and are_opposite_signs(user_asc, partner_asc):
        matches.append(AngleMatchKind.OPPOSITE_ASC)

    # Prefer strongest unique signals; drop redundant opposite when exact cross exists.
    if AngleMatchKind.USER_ASC_PARTNER_DSC in matches and AngleMatchKind.OPPOSITE_ASC_DSC in matches:
        matches = [m for m in matches if m != AngleMatchKind.OPPOSITE_ASC_DSC]
    if AngleMatchKind.PARTNER_ASC_USER_DSC in matches and AngleMatchKind.OPPOSITE_ASC_DSC in matches:
        matches = [m for m in matches if m != AngleMatchKind.OPPOSITE_ASC_DSC]

    return tuple(matches)


def analyze_asc_dsc_synastry(
    user_cusps: list[float] | None,
    partner_cusps: list[float] | None,
) -> AscDscAnalysis:
    user_asc = _angle_sign(user_cusps, ASC_CUSP_INDEX)
    user_dsc = _angle_sign(user_cusps, DSC_CUSP_INDEX)
    partner_asc = _angle_sign(partner_cusps, ASC_CUSP_INDEX)
    partner_dsc = _angle_sign(partner_cusps, DSC_CUSP_INDEX)

    user_has = user_asc is not None and user_dsc is not None
    partner_has = partner_asc is not None and partner_dsc is not None
    matches = _detect_matches(user_asc, user_dsc, partner_asc, partner_dsc)
    score_delta = sum(SCORE_DELTA[kind.value] for kind in matches)
    score_delta = min(score_delta, 12)

    return AscDscAnalysis(
        user_asc_sign=user_asc,
        user_dsc_sign=user_dsc,
        partner_asc_sign=partner_asc,
        partner_dsc_sign=partner_dsc,
        user_has_angles=user_has,
        partner_has_angles=partner_has,
        matches=matches,
        score_delta=score_delta,
    )


def asc_dsc_score_delta(analysis: AscDscAnalysis) -> int:
    return analysis.score_delta if analysis.full_analysis else 0


def _sign_name(locale: str, sign: str | None) -> str:
    if sign is None:
        return "—"
    return SIGN_LABELS[_lang(locale)][sign]


def _match_line(locale: str, kind: AngleMatchKind, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    terms = use_synastry_terms(style)

    if kind == AngleMatchKind.USER_ASC_PARTNER_DSC:
        if lang == "ru":
            if terms:
                return (
                    "• Ваш ASC совпадает с DSC партнёра — сильное притяжение: "
                    "вы близки к его/её образу идеального партнёра."
                )
            return (
                "• Вы — как раз тот тип, которого партнёр ищет «на автомате». "
                "Магнит включён."
            )
        if terms:
            return (
                "• Your Ascendant matches your partner's Descendant — strong pull: "
                "you mirror their ideal partner image."
            )
        return (
            "• How you show up in the world matches what your partner subconsciously seeks — "
            "strong attraction."
        )

    if kind == AngleMatchKind.PARTNER_ASC_USER_DSC:
        if lang == "ru":
            if terms:
                return (
                    "• ASC партнёра совпадает с вашим DSC — он/она попадает в ваш образ "
                    "идеального партнёра."
                )
            return (
                "• Партнёр попадает в ваш «идеальный тип» — как будто заказывали."
            )
        if terms:
            return (
                "• Partner's Ascendant matches your Descendant — they fit your ideal partner image."
            )
        return "• Your partner's outward style matches what you subconsciously seek in a bond."

    if kind == AngleMatchKind.SAME_ASC:
        if lang == "ru":
            if terms:
                return (
                    "• ASC совпадают — похожие темпераменты и манера проявляться, "
                    "но возможны конфликты из‑за одинаковых слабых сторон."
                )
            return (
                "• Вы похожи снаружи — понимаете друг друга быстро. "
                "Минус: одни и те же косяки можете умножить на два."
            )
        if terms:
            return (
                "• Matching Ascendants — similar temperaments and self-presentation; "
                "shared blind spots may clash."
            )
        return (
            "• You present yourselves similarly — easy rapport, but shared weak spots can amplify."
        )

    if kind == AngleMatchKind.OPPOSITE_ASC_DSC:
        if lang == "ru":
            if terms:
                return (
                    "• Ваш ASC и DSC партнёра — противоположные знаки: "
                    "классическое притяжение «я ↔ идеальный партнёр»."
                )
            return (
                "• Вы — как плюс и минус на магните: тянет, хотя снаружи всё наоборот."
            )
        if terms:
            return (
                "• Your Ascendant and partner's Descendant are opposite signs — "
                "classic “self ↔ ideal partner” magnetism."
            )
        return (
            "• How you show up and what your partner seeks are opposites — "
            "magnetic complementary attraction."
        )

    if kind == AngleMatchKind.OPPOSITE_ASC:
        if lang == "ru":
            if terms:
                return (
                    "• ASC в противоположных знаках — сильный контраст темпераментов "
                    "и взаимное дополнение."
                )
            return "• Снаружи вы — полные противоположности. Классика «меня тянет, хотя мы не похожи»."
        if terms:
            return (
                "• Ascendants in opposite signs — strong temperamental contrast "
                "and complementarity."
            )
        return "• Opposite outward styles — contrast creates pull."

    return ""


def format_synastry_step2_section(locale: str, analysis: AscDscAnalysis, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "↗️ Шаг 2. ASC и DSC"
            if use_synastry_terms(style)
            else "↗️ Как выглядите и кого ищете"
        )
        if use_synastry_terms(style):
            lines.append(
                "ASC — восходящий знак (как вы проявляетесь); "
                "DSC — куспид 7‑го дома (какого партнёра ищете). Система домов: Placidus."
            )
        else:
            lines.append(
                "Первое впечатление и «мой тип» — нужны время и город рождения у обоих. "
                "Без этого блок пропускаем."
            )
    else:
        lines.append(
            "↗️ Step 2. ASC and DSC"
            if use_synastry_terms(style)
            else "↗️ First impression and «my type»"
        )
        if use_synastry_terms(style):
            lines.append(
                "Ascendant — rising sign (how you show up); "
                "Descendant — 7th-house cusp (partner type you seek). House system: Placidus."
            )
        else:
            lines.append(
                "How each of you shows up in the world and the partner type you subconsciously seek — "
                "from birth time and place."
            )

    if not analysis.available:
        lines.append("")
        if lang == "ru":
            lines.append(
                "• Нужны время рождения и город (или координаты) у обоих — "
                "иначе ASC и DSC не рассчитать."
            )
        else:
            lines.append(
                "• Birth time and city (or coordinates) for both are required — "
                "otherwise Ascendant and Descendant cannot be calculated."
            )
        return "\n".join(lines)

    lines.append("")
    if analysis.user_has_angles:
        if lang == "ru":
            if use_synastry_terms(style):
                lines.append(
                    f"• Вы: ASC {_sign_name(locale, analysis.user_asc_sign)}, "
                    f"DSC {_sign_name(locale, analysis.user_dsc_sign)}."
                )
            else:
                lines.append(
                    f"• Вы: образ «в мире» — {_sign_name(locale, analysis.user_asc_sign)}; "
                    f"ищете партнёра в ключе {_sign_name(locale, analysis.user_dsc_sign)}."
                )
        elif use_synastry_terms(style):
            lines.append(
                f"• You: ASC {_sign_name(locale, analysis.user_asc_sign)}, "
                f"DSC {_sign_name(locale, analysis.user_dsc_sign)}."
            )
        else:
            lines.append(
                f"• You: outward style — {_sign_name(locale, analysis.user_asc_sign)}; "
                f"seek a partner like {_sign_name(locale, analysis.user_dsc_sign)}."
            )
    elif lang == "ru":
        lines.append("• Ваши ASC/DSC: укажите время рождения и город в профиле.")
    else:
        lines.append("• Your ASC/DSC: add birth time and city in profile.")

    if analysis.partner_has_angles:
        if lang == "ru":
            if use_synastry_terms(style):
                lines.append(
                    f"• Партнёр: ASC {_sign_name(locale, analysis.partner_asc_sign)}, "
                    f"DSC {_sign_name(locale, analysis.partner_dsc_sign)}."
                )
            else:
                lines.append(
                    f"• Партнёр: образ «в мире» — {_sign_name(locale, analysis.partner_asc_sign)}; "
                    f"ищет партнёра в ключе {_sign_name(locale, analysis.partner_dsc_sign)}."
                )
        elif use_synastry_terms(style):
            lines.append(
                f"• Partner: ASC {_sign_name(locale, analysis.partner_asc_sign)}, "
                f"DSC {_sign_name(locale, analysis.partner_dsc_sign)}."
            )
        else:
            lines.append(
                f"• Partner: outward style — {_sign_name(locale, analysis.partner_asc_sign)}; "
                f"seeks a partner like {_sign_name(locale, analysis.partner_dsc_sign)}."
            )
    elif lang == "ru":
        lines.append("• ASC/DSC партнёра: нужны его время рождения и город.")
    else:
        lines.append("• Partner ASC/DSC: their birth time and city are required.")

    if analysis.full_analysis and analysis.matches:
        lines.append("")
        if lang == "ru":
            lines.append("Связки углов:" if use_synastry_terms(style) else "Почему тянет:")
        else:
            lines.append("Angle links:" if use_synastry_terms(style) else "What this means for the pair:")
        for kind in analysis.matches:
            line = _match_line(locale, kind, style=style)
            if line:
                lines.append(line)
    elif analysis.full_analysis:
        if lang == "ru":
            lines.append("")
            lines.append(
                "• Ярких «идеальных пар» тут нет — зато притяжение может быть в других местах."
            )
        else:
            lines.append("")
            lines.append("• No strong ASC↔DSC matches — the theme runs through other chart layers.")

    return "\n".join(lines)
