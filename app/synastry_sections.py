"""Synastry report split into themed blocks for paginated UI."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.compatibility import compatibility_summary
from app.sun_sign_compat import analyze_sun_sign_compat, format_sun_sign_compat_section
from app.synastry_asc import AscDscAnalysis, format_synastry_step2_section
from app.synastry_composite import CompositeAnalysis, format_synastry_composite_section
from app.synastry_elements import ElementBalance, format_synastry_step6_section
from app.synastry_fictitious import FictitiousAnalysis, format_synastry_fictitious_section
from app.synastry_houses import SynastryHouseOverlay, format_synastry_step5_section
from app.synastry_karma import KarmicAnalysis, format_synastry_step8_section
from app.synastry_moon_venus import MoonVenusAnalysis, format_synastry_step7_section
from app.synastry_numerology import NumerologyCompat, format_synastry_numerology_section
from app.synastry_overlay import format_synastry_step3_section
from app.synastry_progressions import ProgressionsAnalysis, format_synastry_progressions_section
from app.synastry_seals import SynastrySeals, filter_hits_for_step3, format_synastry_step4_section
from app.synastry_style import format_comprehensive_scope_intro, format_report_header, use_synastry_terms
from app.synastry_summary import SynastrySummary, build_synastry_summary, format_synastry_step10_section
from app.synastry_tarot import TarotCompatSpread, format_synastry_tarot_section
from app.synastry_text import (
    MODE_LABELS,
    SynastryHit,
    format_synastry_advice,
    format_synastry_aspect_line,
    format_synastry_disclaimers,
    _aspect_tone,
    _lang,
)
from app.synastry_transits import SynastryTransitAnalysis, format_synastry_step9_section

THEME_ORDER: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("overview", ("intro", "sun", "elements")),
    ("attraction", ("asc", "aspects", "moon_venus")),
    ("bond", ("composite", "houses", "progressions")),
    ("depth", ("fictitious", "karma", "seals", "transits")),
    ("symbols", ("numerology", "tarot")),
    ("result", ("summary", "advice", "disclaimers", "compat_summary")),
)

# Shorter themed pages for plain-language partner compat (Telegram UI).
THEME_ORDER_PLAIN: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("overview", ("sun", "elements")),
    ("attraction", ("asc", "aspects")),
    ("bond", ("composite",)),
    ("depth", ("karma",)),
    ("symbols", ("numerology", "tarot")),
    ("result", ("summary", "advice")),
)

THEME_LABELS = {
    "ru": {
        "overview": "📋 Обзор пары",
        "attraction": "💞 Притяжение",
        "bond": "🤝 Союз",
        "depth": "🌑 Глубина и карма",
        "symbols": "🔢 Числа и Таро",
        "result": "💬 Итог и совет",
    },
    "en": {
        "overview": "📋 Pair overview",
        "attraction": "💞 Attraction",
        "bond": "🤝 Bond",
        "depth": "🌑 Depth and karma",
        "symbols": "🔢 Numbers and Tarot",
        "result": "📊 Summary and advice",
    },
}

THEME_LABELS_TERMS = {
    "ru": {
        "overview": "📋 Шаги 1–6: знаки и элементы",
        "attraction": "💞 ASC, синастрия, Луна/Венера",
        "bond": "🤝 Композит, дома, прогрессии",
        "depth": "🌑 Лилит, карма, печати, транзиты",
        "symbols": "🔢 Нумерология и Таро",
        "result": "📊 Сводка и рекомендации",
    },
    "en": {
        "overview": "📋 Steps 1–6: signs and elements",
        "attraction": "💞 ASC, synastry, Moon/Venus",
        "bond": "🤝 Composite, houses, progressions",
        "depth": "🌑 Lilith, karma, seals, transits",
        "symbols": "🔢 Numerology and Tarot",
        "result": "📊 Summary and recommendations",
    },
}


@dataclass(frozen=True)
class SynastrySection:
    key: str
    body: str


@dataclass(frozen=True)
class SynastryTheme:
    key: str
    title: str
    body: str


THEME_LABELS_PLAIN = {
    "ru": {
        "overview": "📋 Кто вы как пара",
        "attraction": "💞 Что вас тянет",
        "bond": "🤝 Как живёте «мы»",
        "depth": "🌑 О чём молчат",
        "symbols": "🔢 Числа и карты",
        "result": "💬 Итог и совет",
    },
    "en": {
        "overview": "📋 Who you are together",
        "attraction": "💞 What pulls you in",
        "bond": "🤝 Living as «we»",
        "depth": "🌑 What's unsaid",
        "symbols": "🔢 Numbers and cards",
        "result": "💬 Wrap-up and tip",
    },
}


def theme_label(locale: str, theme_key: str, *, style: str = "plain") -> str:
    lang = _lang(locale)
    if use_synastry_terms(style):
        table = THEME_LABELS_TERMS[lang]
    elif style == "plain":
        table = THEME_LABELS_PLAIN[lang]
    else:
        table = THEME_LABELS[lang]
    return table.get(theme_key, THEME_LABELS[lang].get(theme_key, theme_key))


def build_synastry_sections(
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
    compat_summary_text: str = "",
) -> tuple[list[SynastrySection], SynastrySummary]:
    lang = _lang(locale)
    mode_key = mode if mode in MODE_LABELS[lang] else "love"
    sections: list[SynastrySection] = []

    intro_lines = [
        *format_report_header(
            locale,
            mode_label=MODE_LABELS[lang][mode_key],
            user_sign=user_sign,
            partner_sign=partner_sign,
            style=style,
        ),
        "",
        format_comprehensive_scope_intro(locale, style=style),
    ]
    sections.append(SynastrySection("intro", "\n".join(intro_lines)))

    sun_compat = analyze_sun_sign_compat(user_sign_key, partner_sign_key)
    if sun_compat is not None:
        sections.append(
            SynastrySection("sun", format_sun_sign_compat_section(locale, sun_compat, style=style))
        )

    sections.append(
        SynastrySection(
            "numerology",
            format_synastry_numerology_section(
                locale,
                numerology,
                user_birth_date=user_birth_date,
                partner_birth_date=partner_birth_date,
                style=style,
            ),
        )
    )
    sections.append(SynastrySection("tarot", format_synastry_tarot_section(locale, tarot, style=style)))
    sections.append(
        SynastrySection("asc", format_synastry_step2_section(locale, asc_dsc, style=style))
    )

    step3_hits = filter_hits_for_step3(hits, seals)
    sections.append(
        SynastrySection(
            "aspects",
            format_synastry_step3_section(
                locale,
                mode=mode_key,
                hits=step3_hits,
                user_has_moon=user_has_moon,
                partner_has_moon=partner_has_moon,
                format_aspect_line=format_synastry_aspect_line,
                aspect_tone=_aspect_tone,
                style=style,
            ),
        )
    )
    sections.append(
        SynastrySection("fictitious", format_synastry_fictitious_section(locale, fictitious, style=style))
    )
    sections.append(
        SynastrySection("composite", format_synastry_composite_section(locale, composite, style=style))
    )
    sections.append(
        SynastrySection(
            "progressions",
            format_synastry_progressions_section(locale, progressions, style=style),
        )
    )
    sections.append(SynastrySection("seals", format_synastry_step4_section(locale, seals, style=style)))
    sections.append(
        SynastrySection("houses", format_synastry_step5_section(locale, house_overlay, style=style))
    )
    sections.append(
        SynastrySection("elements", format_synastry_step6_section(locale, element_balance, style=style))
    )
    sections.append(
        SynastrySection("moon_venus", format_synastry_step7_section(locale, moon_venus, style=style))
    )
    sections.append(
        SynastrySection("karma", format_synastry_step8_section(locale, karma, style=style))
    )
    sections.append(
        SynastrySection("transits", format_synastry_step9_section(locale, transits, style=style))
    )

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
    sections.append(
        SynastrySection("summary", format_synastry_step10_section(locale, summary, style=style))
    )
    sections.append(
        SynastrySection(
            "advice",
            (
                ("💡 Что бы я на вашем месте учёл\n" if lang == "ru" and not use_synastry_terms(style) else "💡 " + ("Совет" if lang == "ru" else "Advice") + "\n")
                + format_synastry_advice(locale, mode_key, score, style=style)
            ),
        )
    )
    sections.append(
        SynastrySection("disclaimers", format_synastry_disclaimers(locale, style=style))
    )
    if compat_summary_text.strip():
        sections.append(SynastrySection("compat_summary", compat_summary_text.strip()))

    return sections, summary


def group_synastry_themes(
    locale: str,
    sections: list[SynastrySection],
    *,
    style: str = "plain",
) -> list[SynastryTheme]:
    by_key = {section.key: section.body for section in sections}
    order = THEME_ORDER if use_synastry_terms(style) else THEME_ORDER_PLAIN
    themes: list[SynastryTheme] = []
    for theme_key, section_keys in order:
        bodies = [by_key[key] for key in section_keys if key in by_key and by_key[key].strip()]
        if not bodies:
            continue
        themes.append(
            SynastryTheme(
                key=theme_key,
                title=theme_label(locale, theme_key, style=style),
                body="\n\n".join(bodies),
            )
        )
    return themes


def join_synastry_sections(sections: list[SynastrySection]) -> str:
    return "\n\n".join(section.body for section in sections if section.body.strip())


def basic_synastry_sections(locale: str, body: str) -> list[SynastrySection]:
    return [SynastrySection("basic", body)]
