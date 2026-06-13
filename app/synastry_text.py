from __future__ import annotations

from datetime import date

from app.forecast_text import _aspect_label
from app.sun_sign_compat import analyze_sun_sign_compat, format_sun_sign_compat_section
from app.synastry_numerology import NumerologyCompat, format_synastry_numerology_section
from app.synastry_tarot import TarotCompatSpread, format_synastry_tarot_section
from app.synastry_asc import AscDscAnalysis, format_synastry_step2_section
from app.synastry_composite import CompositeAnalysis, format_synastry_composite_section
from app.synastry_progressions import ProgressionsAnalysis, format_synastry_progressions_section
from app.synastry_fictitious import FictitiousAnalysis, format_synastry_fictitious_section
from app.synastry_style import (
    format_comprehensive_scope_intro,
    format_cross_link_line,
    format_report_header,
    use_synastry_terms,
)
from app.synastry_overlay import format_synastry_step3_section
from app.synastry_karma import KarmicAnalysis, format_synastry_step8_section
from app.synastry_moon_venus import MoonVenusAnalysis, format_synastry_step7_section
from app.synastry_summary import build_synastry_summary, format_synastry_step10_section, SynastrySummary
from app.synastry_transits import SynastryTransitAnalysis, format_synastry_step9_section
from app.synastry_elements import ElementBalance, format_synastry_step6_section
from app.synastry_houses import SynastryHouseOverlay, format_synastry_step5_section
from app.synastry_seals import SynastrySeals, filter_hits_for_step3, format_synastry_step4_section

SynastryHit = tuple[float, str, str, str]

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
    },
}

MODE_LABELS = {
    "ru": {"love": "любовь", "friendship": "дружба", "work": "работа"},
    "en": {"love": "love", "friendship": "friendship", "work": "work"},
}

ASPECT_TONE = {
    "ru": {
        "love": {
            "trine": "сильная поддержка и притяжение",
            "sextile": "лёгкий контакт и взаимный интерес",
            "conjunction": "мощное усиление темы отношений",
            "square": "страсть и напряжение — нужен диалог",
            "opposition": "магнетизм через контраст",
        },
        "friendship": {
            "trine": "лёгкое взаимопонимание",
            "sextile": "комфортное общение",
            "conjunction": "сильная связь интересов",
            "square": "разные темпы — договаривайтесь",
            "opposition": "дополняете друг друга",
        },
        "work": {
            "trine": "продуктивное взаимодействие",
            "sextile": "удачный обмен идеями",
            "conjunction": "усиление общей цели",
            "square": "разные подходы — нужны роли",
            "opposition": "конструктивное напряжение",
        },
    },
    "en": {
        "love": {
            "trine": "strong support and attraction",
            "sextile": "easy contact and mutual interest",
            "conjunction": "powerful intensification of the bond",
            "square": "passion and tension — talk it through",
            "opposition": "magnetism through contrast",
        },
        "friendship": {
            "trine": "easy understanding",
            "sextile": "comfortable communication",
            "conjunction": "strong link of interests",
            "square": "different rhythms — negotiate",
            "opposition": "you complement each other",
        },
        "work": {
            "trine": "productive interaction",
            "sextile": "smooth idea exchange",
            "conjunction": "shared goal intensifies",
            "square": "different approaches — define roles",
            "opposition": "constructive tension",
        },
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _aspect_tone(locale: str, aspect: str, mode: str) -> str:
    lang = _lang(locale)
    mode_key = mode if mode in ASPECT_TONE[lang] else "love"
    return ASPECT_TONE[lang][mode_key][aspect]


def format_synastry_aspect_line(
    locale: str,
    user_planet: str,
    partner_planet: str,
    aspect: str,
    mode: str,
    orb: float,
    *,
    bullet: str = "",
    style: str = "terms",
) -> str:
    tone = _aspect_tone(locale, aspect, mode)
    core = format_cross_link_line(
        locale,
        user_planet,
        partner_planet,
        aspect,
        tone,
        orb,
        style,
    )
    if not bullet:
        return core
    return f"{bullet} {core}"


def format_synastry_advice(locale: str, mode: str, score: int) -> str:
    lang = _lang(locale)
    if lang == "ru":
        if mode == "love":
            if score >= 75:
                return "Опирайтесь на сильные связи и не принимайте напряжение на личный счёт."
            if score >= 55:
                return "Говорите прямо о чувствах — карты показывают и притяжение, и точки трения."
            return "Не форсируйте близость: сначала ясность, потом решения."
        if mode == "friendship":
            if score >= 75:
                return "Поддерживайте регулярный контакт — связь легко складывается."
            return "Уважайте разный темп и формат общения."
        if score >= 75:
            return "Закрепите роли и дедлайны — взаимодействие продуктивное."
        return "Сначала договоритесь о задачах, потом ускоряйтесь."

    if mode == "love":
        if score >= 75:
            return "Lean on your strong links and don't take tension personally."
        if score >= 55:
            return "Talk openly about feelings — the chart shows both pull and friction."
        return "Don't force closeness: clarity first, decisions second."
    if mode == "friendship":
        if score >= 75:
            return "Keep regular contact — the connection flows easily."
        return "Respect different rhythms and communication styles."
    if score >= 75:
        return "Define roles and deadlines — interaction is productive."
    return "Agree on tasks first, then pick up the pace."


def format_synastry_disclaimers(locale: str, *, style: str = "terms") -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        if lang == "ru":
            return "\n".join(
                [
                    "📌 Важные рекомендации",
                    "• Не зацикливайтесь на «плохих» показателях. Напряжённые аспекты дают рост, "
                    "а идеальные карты без вызовов могут привести к застою.",
                    "• Проверяйте интуицию. Если астрология говорит «да», а внутри дискомфорт — "
                    "доверьтесь себе.",
                    "• Избегайте фатализма. Карты показывают потенциал, а не судьбу.",
                    "• Обновляйте анализ. Раз в 5–7 лет перепроверяйте синастрию — люди меняются.",
                    "• Используйте методы как подсказки, а не догму. Эзотерика — инструмент "
                    "самопознания, а не приговор.",
                    "• Точность времени рождения сильно влияет на дома, Луну и ASC.",
                ]
            )
        return "\n".join(
            [
                "📌 Important recommendations",
                "• Don't fixate on «bad» scores. Tense aspects foster growth; "
                "a perfect chart without challenges can lead to stagnation.",
                "• Check your intuition. If astrology says «yes» but you feel uneasy — trust yourself.",
                "• Avoid fatalism. The chart shows potential, not fate.",
                "• Refresh the analysis. Revisit synastry every 5–7 years — people change.",
                "• Use these methods as hints, not dogma. Esoteric tools are for self-knowledge, "
                "not a verdict.",
                "• Birth-time accuracy strongly affects houses, the Moon, and the Ascendant.",
            ]
        )
    if lang == "ru":
        return "\n".join(
            [
                "💡 Важные рекомендации",
                "• Не цепляйтесь за «плохие» пункты — напряжение часто даёт рост.",
                "• Если внутри дискомфорт — слушайте себя, а не только текст.",
                "• Это не приговор и не судьба — только возможные сценарии.",
                "• Имеет смысл пересматривать разбор раз в 5–7 лет.",
                "• Используйте как подсказку для разговора с собой и партнёром.",
            ]
        )
    return "\n".join(
        [
            "💡 Important recommendations",
            "• Don't cling to «bad» lines — tension often means growth.",
            "• If something feels off inside — listen to yourself, not only the text.",
            "• This isn't fate — only possible scenarios.",
            "• Revisit the reading every 5–7 years.",
            "• Use it as a prompt for honest talk with yourself and your partner.",
        ]
    )


def format_synastry_report(
    locale: str,
    *,
    mode: str,
    score: int,
    hits: list[SynastryHit],
    seals: SynastrySeals,
    asc_dsc: AscDscAnalysis,
    composite: CompositeAnalysis,
    house_overlay: SynastryHouseOverlay,
    element_balance: ElementBalance,
    moon_venus: MoonVenusAnalysis,
    karma: KarmicAnalysis,
    fictitious: FictitiousAnalysis,
    progressions: ProgressionsAnalysis,
    numerology: NumerologyCompat,
    tarot: TarotCompatSpread,
    transits: SynastryTransitAnalysis,
    user_sign: str,
    partner_sign: str,
    user_sign_key: str,
    partner_sign_key: str,
    user_birth_date: date,
    partner_birth_date: date,
    user_has_moon: bool,
    partner_has_moon: bool,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    mode_key = mode if mode in MODE_LABELS[lang] else "love"
    lines: list[str] = []

    lines.extend(
        format_report_header(
            locale,
            mode_label=MODE_LABELS[lang][mode_key],
            user_sign=user_sign,
            partner_sign=partner_sign,
            style=style,
        )
    )

    lines.append("")
    lines.append(format_comprehensive_scope_intro(locale, style=style))

    sun_compat = analyze_sun_sign_compat(user_sign_key, partner_sign_key)
    if sun_compat is not None:
        lines.append("")
        lines.append(format_sun_sign_compat_section(locale, sun_compat, style=style))

    lines.append("")
    lines.append(
        format_synastry_numerology_section(
            locale,
            numerology,
            user_birth_date=user_birth_date,
            partner_birth_date=partner_birth_date,
            style=style,
        )
    )

    lines.append("")
    lines.append(format_synastry_tarot_section(locale, tarot, style=style))

    lines.append("")
    lines.append(format_synastry_step2_section(locale, asc_dsc, style=style))

    step3_hits = filter_hits_for_step3(hits, seals)
    lines.append("")
    lines.append(
        format_synastry_step3_section(
            locale,
            mode=mode_key,
            hits=step3_hits,
            user_has_moon=user_has_moon,
            partner_has_moon=partner_has_moon,
            format_aspect_line=format_synastry_aspect_line,
            aspect_tone=_aspect_tone,
            style=style,
        )
    )

    lines.append("")
    lines.append(format_synastry_fictitious_section(locale, fictitious, style=style))

    lines.append("")
    lines.append(format_synastry_composite_section(locale, composite, style=style))

    lines.append("")
    lines.append(format_synastry_progressions_section(locale, progressions, style=style))

    lines.append("")
    lines.append(format_synastry_step4_section(locale, seals, style=style))

    lines.append("")
    lines.append(format_synastry_step5_section(locale, house_overlay, style=style))

    lines.append("")
    lines.append(format_synastry_step6_section(locale, element_balance, style=style))

    lines.append("")
    lines.append(format_synastry_step7_section(locale, moon_venus, style=style))

    lines.append("")
    lines.append(format_synastry_step8_section(locale, karma, style=style))

    lines.append("")
    lines.append(format_synastry_step9_section(locale, transits, style=style))

    summary = build_synastry_summary(
        locale=locale,
        score=score,
        hits=hits,
        user_sign_key=user_sign_key,
        partner_sign_key=partner_sign_key,
        seals=seals,
        asc_dsc=asc_dsc,
        composite=composite,
        house_overlay=house_overlay,
        element_balance=element_balance,
        moon_venus=moon_venus,
        karma=karma,
        fictitious=fictitious,
        progressions=progressions,
        numerology=numerology,
        tarot=tarot,
        transits=transits,
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
        style=style,
    )
    lines.append("")
    lines.append(format_synastry_step10_section(locale, summary, style=style))

    lines.append("")
    lines.append("💡 " + ("Совет" if lang == "ru" else "Advice"))
    lines.append(format_synastry_advice(locale, mode_key, score))

    lines.append("")
    lines.append(format_synastry_disclaimers(locale, style=style))

    return "\n".join(lines), summary
