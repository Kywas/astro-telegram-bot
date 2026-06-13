"""Synastry: composite chart (midpoint method) — the relationship as its own entity."""
from __future__ import annotations

from dataclasses import dataclass

from app.sun_sign_compat import SIGN_LABELS, ZODIAC_SIGNS
from app.synastry_houses import ANGULAR_HOUSES, HOUSE_SECTION, HOUSE_SECTION_PLAIN, PLANET_LABELS, planet_house

COMPOSITE_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")

SUN_HOUSE_HINT = {
    "ru": {
        1: "союз ярко проявляется — пара «видна» и задаёт тон",
        5: "романтика, игра и радость — сердце связи в любви и творчестве",
        7: "партнёрство — главная ось: вы как пара на первом плане",
        8: "интенсивная связь с элементами трансформации, близости и общих ресурсов",
        10: "статус, цели и репутация пары — союз заметен вовне",
        4: "дом, семья и корни — ядро в уюте и опоре",
    },
    "en": {
        1: "the bond shows clearly — the pair sets a visible tone",
        5: "romance, play, and joy — love and creativity at the core",
        7: "partnership is the main axis — you as a couple up front",
        8: "intense bond with transformation, intimacy, and shared resources",
        10: "status, goals, and reputation — the union is public-facing",
        4: "home, family, and roots — the core is in comfort and support",
    },
}

MOON_HOUSE_HINT = {
    "ru": {
        4: "эмоциональное ядро — дом, безопасность и «своё место»",
        5: "нежность, романтика и эмоциональная лёгость в паре",
        7: "чувства завязаны на образ партнёрства и «мы вдвоём»",
        8: "глубокая эмоциональная слияние и доверие",
        1: "настроение пары открыто — эмоции на виду",
    },
    "en": {
        4: "emotional core — home, safety, and belonging",
        5: "tenderness, romance, and emotional lightness",
        7: "feelings tie to the partnership image and “us”",
        8: "deep emotional merging and trust",
        1: "the pair's mood is open — feelings show",
    },
}

ASC_SIGN_HINT = {
    "ru": {
        "Aries": "прямой, энергичный стиль — пара действует быстро и смело",
        "Taurus": "спокойный, надёжный тон — союз ценит стабильность и комфорт",
        "Gemini": "лёгкость, разговоры и любопытство — пара живёт идеями и общением",
        "Cancer": "забота и эмоциональная близость — «мы» чувствуются как семья",
        "Leo": "яркость, тепло и признание — союз хочет сиять",
        "Virgo": "практичность и внимание к деталям — связь через помощь и порядок",
        "Libra": "гармония и партнёрский баланс — пара стремится к красоте и равновесию",
        "Scorpio": "глубина и интенсивность — союз не поверхностный",
        "Sagittarius": "свобода, рост и общие горизонты — пара смотрит вперёд",
        "Capricorn": "серьёзность и цели — союз строится на ответственности",
        "Aquarius": "нестандартность и дружба — пара ценит свободу и идеи",
        "Pisces": "мягкость и эмпатия — связь через чувствительность и мечту",
    },
    "en": {
        "Aries": "direct, energetic style — the pair acts fast and boldly",
        "Taurus": "calm, reliable tone — the union values stability and comfort",
        "Gemini": "lightness, talk, and curiosity — ideas and communication",
        "Cancer": "care and closeness — “we” feels like family",
        "Leo": "warmth and recognition — the bond wants to shine",
        "Virgo": "practicality and detail — connection through service and order",
        "Libra": "harmony and balance — beauty and equilibrium",
        "Scorpio": "depth and intensity — not a superficial bond",
        "Sagittarius": "freedom, growth, and horizons — looking forward together",
        "Capricorn": "seriousness and goals — built on responsibility",
        "Aquarius": "unconventionality and friendship — freedom and ideas",
        "Pisces": "softness and empathy — sensitivity and dream",
    },
}


@dataclass(frozen=True)
class CompositeAnalysis:
    planets: dict[str, float]
    cusps: list[float] | None
    sun_sign: str
    moon_sign: str | None
    asc_sign: str | None
    sun_house: int | None
    moon_house: int | None
    angular_planets: tuple[tuple[str, int], ...]
    has_moon: bool
    has_houses: bool

    @property
    def available(self) -> bool:
        return bool(self.planets)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _sign_name(locale: str, sign: str) -> str:
    return SIGN_LABELS[_lang(locale)][sign]


def _planet_name(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _longitude_to_sign(longitude: float) -> str:
    normalized = longitude % 360.0
    index = int(normalized // 30) % 12
    return ZODIAC_SIGNS[index]


def midpoint_longitude(first: float, second: float) -> float:
    diff = (second - first) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return (first + diff / 2.0) % 360.0


def _composite_planets(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    *,
    include_moon: bool,
) -> dict[str, float]:
    keys = [key for key in COMPOSITE_PLANETS if key != "MOON" or include_moon]
    composite: dict[str, float] = {}
    for key in keys:
        if key in user_planets and key in partner_planets:
            composite[key] = midpoint_longitude(user_planets[key], partner_planets[key])
    return composite


def _composite_cusps(
    user_cusps: list[float] | None,
    partner_cusps: list[float] | None,
) -> list[float] | None:
    if user_cusps is None or partner_cusps is None:
        return None
    if len(user_cusps) < 12 or len(partner_cusps) < 12:
        return None
    return [midpoint_longitude(user_cusps[i], partner_cusps[i]) for i in range(12)]


def build_composite_analysis(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    user_cusps: list[float] | None,
    partner_cusps: list[float] | None,
    *,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> CompositeAnalysis:
    include_moon = user_has_moon and partner_has_moon
    planets = _composite_planets(
        user_planets,
        partner_planets,
        include_moon=include_moon,
    )
    cusps = _composite_cusps(user_cusps, partner_cusps)
    sun_sign = _longitude_to_sign(planets["SUN"]) if "SUN" in planets else "Aries"
    moon_sign = _longitude_to_sign(planets["MOON"]) if "MOON" in planets else None
    asc_sign = _longitude_to_sign(cusps[0]) if cusps else None

    sun_house = planet_house(planets["SUN"], cusps) if cusps and "SUN" in planets else None
    moon_house = planet_house(planets["MOON"], cusps) if cusps and "MOON" in planets else None

    angular: list[tuple[str, int]] = []
    if cusps:
        for planet in COMPOSITE_PLANETS:
            if planet not in planets:
                continue
            house = planet_house(planets[planet], cusps)
            if house in ANGULAR_HOUSES:
                angular.append((planet, house))
        angular.sort(key=lambda item: (item[1], item[0]))

    return CompositeAnalysis(
        planets=planets,
        cusps=cusps,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        asc_sign=asc_sign,
        sun_house=sun_house,
        moon_house=moon_house,
        angular_planets=tuple(angular),
        has_moon=include_moon,
        has_houses=cusps is not None,
    )


def composite_score_delta(analysis: CompositeAnalysis) -> int:
    if not analysis.available:
        return 0
    delta = 0
    if analysis.sun_house in {5, 7, 8}:
        delta += 2
    elif analysis.sun_house in ANGULAR_HOUSES:
        delta += 1
    if analysis.moon_house in {4, 7}:
        delta += 1
    if len(analysis.angular_planets) >= 2:
        delta += 2
    elif analysis.angular_planets:
        delta += 1
    return min(delta, 4)


def _house_theme(locale: str, house: int) -> str:
    lang = _lang(locale)
    return HOUSE_SECTION[lang].get(house, (f"{house}-й дом", ""))[1]


def _house_area_label(locale: str, house: int, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    table = HOUSE_SECTION if use_synastry_terms(style) else HOUSE_SECTION_PLAIN
    entry = table[lang].get(house)
    if entry:
        return entry[0]
    if lang == "ru":
        return f"сфера {house}"
    return f"area {house}"


def _sun_house_line(locale: str, analysis: CompositeAnalysis, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    sign = _sign_name(locale, analysis.sun_sign)
    if analysis.sun_house is None:
        if lang == "ru":
            return f"• Солнце композита в {sign} — ядро целей и смысла союза."
        return f"• Composite Sun in {sign} — core purpose and meaning of the bond."

    house = analysis.sun_house
    hint = SUN_HOUSE_HINT[lang].get(
        house,
        _house_theme(locale, house),
    )
    if lang == "ru":
        if use_synastry_terms(style):
            return f"• Солнце композита в {sign}, {house}-й дом — {hint}."
        area = _house_area_label(locale, house, style=style)
        return f"• Главная цель союза — знак {sign}. Тема «{area}»: {hint}."
    if use_synastry_terms(style):
        return f"• Composite Sun in {sign}, {house}th house — {hint}."
    area = _house_area_label(locale, house, style=style)
    return f"• Main goal of the bond — {sign}. Theme «{area}»: {hint}."


def _moon_house_line(locale: str, analysis: CompositeAnalysis, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if not analysis.has_moon or analysis.moon_sign is None:
        if lang == "ru":
            return "• Луна композита: нужно время рождения у обоих для эмоционального ядра."
        return "• Composite Moon: birth time for both is needed for the emotional core."

    sign = _sign_name(locale, analysis.moon_sign)
    if analysis.moon_house is None:
        if lang == "ru":
            return f"• Луна композита в {sign} — эмоциональный тон союза."
        return f"• Composite Moon in {sign} — emotional tone of the bond."

    house = analysis.moon_house
    hint = MOON_HOUSE_HINT[lang].get(house, _house_theme(locale, house))
    if lang == "ru":
        if use_synastry_terms(style):
            return f"• Луна композита в {sign}, {house}-й дом — {hint}."
        area = _house_area_label(locale, house, style=style)
        return f"• Эмоции в паре — знак {sign}. Тема «{area}»: {hint}."
    if use_synastry_terms(style):
        return f"• Composite Moon in {sign}, {house}th house — {hint}."
    area = _house_area_label(locale, house, style=style)
    return f"• Pair feelings — {sign}. Theme «{area}»: {hint}."


def _asc_line(locale: str, analysis: CompositeAnalysis, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if analysis.asc_sign is None:
        if lang == "ru":
            return (
                "• ASC композита: для домов и стиля «в мире» нужны время и место рождения у обоих."
            )
        return "• Composite Ascendant: birth time and place for both are needed for houses and public style."

    sign = _sign_name(locale, analysis.asc_sign)
    hint = ASC_SIGN_HINT[lang].get(analysis.asc_sign, "")
    if lang == "ru":
        if use_synastry_terms(style):
            return f"• ASC композита в {sign} (1‑й дом) — {hint}."
        return f"• Как пара выглядит «в мире» — {sign}: {hint}."
    if use_synastry_terms(style):
        return f"• Composite Ascendant in {sign} (1st house) — {hint}."
    return f"• How the pair shows up in the world — {sign}: {hint}."


def format_synastry_composite_section(
    locale: str,
    analysis: CompositeAnalysis,
    *,
    style: str = "terms",
) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "🌐 Композитная карта"
            if use_synastry_terms(style)
            else "🌐 Карта вашего союза"
        )
        if use_synastry_terms(style):
            lines.append(
                "Композит — средняя точка между одинаковыми планетами двух карт. "
                "Это «карта отношений» как отдельного существа (метод midpoints)."
            )
        else:
            lines.append(
                "Это как общее «фото» вашего союза — как вы выглядите вместе и что для вас главное."
            )
    else:
        lines.append(
            "🌐 Composite chart"
            if use_synastry_terms(style)
            else "🌐 Your union chart"
        )
        if use_synastry_terms(style):
            lines.append(
                "The composite is the midpoint between matching planets in both charts — "
                "a “relationship chart” as its own entity (midpoint method)."
            )
        else:
            lines.append(
                "A snapshot of your bond: how you look together and what matters most."
            )

    lines.append("")
    lines.append("Ядро отношений" if lang == "ru" else "Core of the bond")
    lines.append(_sun_house_line(locale, analysis, style=style))
    lines.append(_moon_house_line(locale, analysis, style=style))

    lines.append("")
    lines.append(
        "Стиль пары в мире" if lang == "ru" else "How the pair meets the world"
    )
    lines.append(_asc_line(locale, analysis, style=style))

    lines.append("")
    if lang == "ru":
        header = (
            "Планеты в угловых домах (1, 4, 7, 10)"
            if use_synastry_terms(style)
            else "Ключевые темы союза (главные сферы)"
        )
    else:
        header = (
            "Planets in angular houses (1, 4, 7, 10)"
            if use_synastry_terms(style)
            else "Key union themes (main life areas)"
        )
    lines.append(header)

    if not analysis.has_houses:
        lines.append(
            "• Дома композита не рассчитаны — добавьте время и город у обоих."
            if lang == "ru"
            else "• Composite houses not calculated — add birth time and city for both."
        )
    elif not analysis.angular_planets:
        lines.append(
            "• В угловых домах композита нет планет — акценты в других сферах."
            if lang == "ru"
            else "• No planets in composite angular houses — themes lie elsewhere."
        )
    else:
        for planet, house in analysis.angular_planets:
            theme = _house_theme(locale, house)
            planet_name = _planet_name(locale, planet)
            if lang == "ru":
                if use_synastry_terms(style):
                    lines.append(f"• {planet_name} в {house}-м доме — {theme}. ⭐")
                else:
                    area = _house_area_label(locale, house, style=style)
                    lines.append(f"• {planet_name} в теме «{area}» — {theme}.")
            elif use_synastry_terms(style):
                lines.append(f"• {planet_name} in {house}th house — {theme}. ⭐")
            else:
                area = _house_area_label(locale, house, style=style)
                lines.append(f"• {planet_name} in «{area}» — {theme}.")

    return "\n".join(lines)
