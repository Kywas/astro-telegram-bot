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


ASPECT_TONE_PLAIN = {
    "ru": {
        "love": {
            "trine": "рядом с этим человеком спокойно и хочется остаться",
            "sextile": "легко сближаетесь, без натянутости",
            "conjunction": "тема отношений звучит громко — не проходит мимо",
            "square": "может зажигать, но и задевать — лучше не копить молча",
            "opposition": "тянет, даже когда бесит — типичная история «противоположности»",
        },
        "friendship": {
            "trine": "понимаете друг друга почти с полуслова",
            "sextile": "общаться легко, без лишних объяснений",
            "conjunction": "общие интересы сильно сближают",
            "square": "темп разный — договоритесь, как общаться",
            "opposition": "вы разные, но это может дополнять",
        },
        "work": {
            "trine": "вместе продуктивно, без лишней суеты",
            "sextile": "идеи обмениваются легко",
            "conjunction": "общая цель чувствуется сильнее",
            "square": "подходы разные — распределите роли",
            "opposition": "напряжение есть, но может толкать вперёд",
        },
    },
    "en": {
        "love": {
            "trine": "you feel calm around each other and want to stay",
            "sextile": "you warm up fast, without awkwardness",
            "conjunction": "the relationship theme is loud — hard to ignore",
            "square": "it can spark and sting — don't swallow it in silence",
            "opposition": "it pulls even when it annoys — classic opposites",
        },
        "friendship": {
            "trine": "you get each other almost without words",
            "sextile": "talking feels easy, no over-explaining",
            "conjunction": "shared interests pull you close",
            "square": "different pace — agree how you connect",
            "opposition": "you're different, but that can complement",
        },
        "work": {
            "trine": "productive together, without extra noise",
            "sextile": "ideas flow easily",
            "conjunction": "the shared goal feels stronger",
            "square": "different styles — split roles clearly",
            "opposition": "tension is there, but it can push you forward",
        },
    },
}


def _aspect_tone(locale: str, aspect: str, mode: str, *, style: str = "terms") -> str:
    lang = _lang(locale)
    mode_key = mode if mode in ASPECT_TONE[lang] else "love"
    table = ASPECT_TONE if use_synastry_terms(style) else ASPECT_TONE_PLAIN
    return table[lang][mode_key][aspect]


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
    tone = _aspect_tone(locale, aspect, mode, style=style)
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


def format_synastry_advice(locale: str, mode: str, score: int, *, style: str = "terms") -> str:
    lang = _lang(locale)
    plain = not use_synastry_terms(style)
    if lang == "ru":
        if mode == "love":
            if score >= 75:
                return (
                    "Я бы опирался на то, что у вас уже получается. Ссоры не всегда про «не люблю» — "
                    "иногда просто устали или не договорились."
                    if plain
                    else "Опирайтесь на сильные связи и не принимайте напряжение на личный счёт."
                )
            if score >= 55:
                return (
                    "Говорите о чувствах вслух, без намёков. Притяжение есть, но и точки, "
                    "где легко не понять друг друга."
                    if plain
                    else "Говорите прямо о чувствах — карты показывают и притяжение, и точки трения."
                )
            return (
                "Не форсируйте близость. Сначала разберитесь, кто вы друг для друга — потом решения."
                if plain
                else "Не форсируйте близость: сначала ясность, потом решения."
            )
        if mode == "friendship":
            if score >= 75:
                return (
                    "Не теряйте контакт — у вас это складывается естественно."
                    if plain
                    else "Поддерживайте регулярный контакт — связь легко складывается."
                )
            return (
                "Если друг другу пишете в разном темпе — это нормально, просто проговорите."
                if plain
                else "Уважайте разный темп и формат общения."
            )
        if score >= 75:
            return (
                "Распределите, кто за что отвечает — так меньше нервов на ровном месте."
                if plain
                else "Закрепите роли и дедлайны — взаимодействие продуктивное."
            )
        return (
            "Сначала договоритесь о задачах. Потом уже скорость."
            if plain
            else "Сначала договоритесь о задачах, потом ускоряйтесь."
        )

    if mode == "love":
        if score >= 75:
            return (
                "Lean on what works between you. Don't take fights personally."
                if plain
                else "Lean on your strong links and don't take tension personally."
            )
        if score >= 55:
            return (
                "Talk openly about feelings — there's pull and spots to negotiate."
                if plain
                else "Talk openly about feelings — the chart shows both pull and friction."
            )
        return (
            "Don't rush closeness. Understand each other first, then decide."
            if plain
            else "Don't force closeness: clarity first, decisions second."
        )
    if mode == "friendship":
        if score >= 75:
            return (
                "Keep in touch — friendship comes easily."
                if plain
                else "Keep regular contact — the connection flows easily."
            )
        return (
            "Respect different communication pace."
            if plain
            else "Respect different rhythms and communication styles."
        )
    if score >= 75:
        return (
            "Agree who does what — work goes smoother."
            if plain
            else "Define roles and deadlines — interaction is productive."
        )
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
                "💡 На что обратить внимание",
                "• «Плохие» строки — не приговор. Через них пары часто и сближаются.",
                "• Если внутри тревожно — верьте себе больше, чем любому тексту, даже этому.",
                "• Это повод поговорить, не инструкция «как жить правильно».",
                "• Люди меняются — через пару лет можно перечитать, если захочется.",
            ]
        )
    return "\n".join(
        [
            "💡 Good to remember",
            "• «Bad» lines aren't a verdict. Couples often grow through friction.",
            "• If something feels wrong inside — trust yourself, not only the text.",
            "• This is a talking prompt, not fate.",
            "• Re-read the report every few years.",
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
) -> tuple[str, SynastrySummary, list]:
    from app.synastry_sections import SynastrySection, build_synastry_sections, join_synastry_sections

    sections, summary = build_synastry_sections(
        locale,
        mode=mode,
        score=score,
        hits=hits,
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
        user_sign=user_sign,
        partner_sign=partner_sign,
        user_sign_key=user_sign_key,
        partner_sign_key=partner_sign_key,
        user_birth_date=user_birth_date,
        partner_birth_date=partner_birth_date,
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
        style=style,
    )
    return join_synastry_sections(sections), summary, sections
