"""Step 5 synastry: partner chart house overlays (Placidus)."""
from __future__ import annotations

from dataclasses import dataclass

# Relationship-relevant houses; 4 included as angular (1, 4, 7, 10).
FOCUS_HOUSES = (1, 2, 3, 4, 5, 7, 8, 9, 10)
ANGULAR_HOUSES = frozenset({1, 4, 7, 10})

OVERLAY_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
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

HOUSE_SECTION = {
    "ru": {
        1: ("1‑й дом — личность", "влияние на самоощущение друг друга"),
        2: ("2‑й дом — финансы", "совместное отношение к деньгам и ресурсам"),
        3: ("3‑й дом — общение", "стиль коммуникации и обмена идеями"),
        4: ("4‑й дом — семья и корни", "быт, дом и близкие"),
        5: ("5‑й дом — любовь", "романтика, флирт, творчество и дети"),
        7: ("7‑й дом — брак и партнёрство", "серьёзность намерений и образ пары"),
        8: ("8‑й дом — трансформация", "глубина связи, секс и общие ресурсы"),
        9: ("9‑й дом — мировоззрение", "философия, смысл и путешествия"),
        10: ("10‑й дом — карьера", "влияние на социальный статус и репутацию"),
    },
    "en": {
        1: ("1st house — identity", "how you affect each other's self-image"),
        2: ("2nd house — finances", "shared attitude to money and resources"),
        3: ("3rd house — communication", "style of talk and idea exchange"),
        4: ("4th house — family and roots", "home, daily life, and relatives"),
        5: ("5th house — love", "romance, flirtation, creativity, and children"),
        7: ("7th house — marriage and partnership", "serious intent and couple image"),
        8: ("8th house — transformation", "depth, intimacy, sex, and shared assets"),
        9: ("9th house — worldview", "philosophy, meaning, and travel"),
        10: ("10th house — career", "impact on status and public image"),
    },
}

HOUSE_SECTION_PLAIN = {
    "ru": {
        1: ("Личность", "как вы влияете на самоощущение друг друга"),
        2: ("Деньги", "отношение к финансам и ресурсам"),
        3: ("Общение", "стиль разговоров и обмена идеями"),
        4: ("Дом и семья", "быт, корни и близкие"),
        5: ("Любовь и романтика", "флирт, страсть, творчество и дети"),
        7: ("Союз и брак", "серьёзность намерений"),
        8: ("Глубина связи", "близость, секс и общие ресурсы"),
        9: ("Мировоззрение", "философия, смысл и путешествия"),
        10: ("Карьера и статус", "влияние на репутацию и амбиции"),
    },
    "en": {
        1: ("Identity", "how you shape each other's self-image"),
        2: ("Money", "attitude to finances and resources"),
        3: ("Communication", "how you talk and exchange ideas"),
        4: ("Home and family", "daily life, roots, and relatives"),
        5: ("Love and romance", "flirtation, passion, creativity, and children"),
        7: ("Union and marriage", "serious intent in the bond"),
        8: ("Depth of connection", "intimacy, sex, and shared assets"),
        9: ("Worldview", "philosophy, meaning, and travel"),
        10: ("Career and status", "impact on reputation and ambitions"),
    },
}
# (house, planet) -> meaning when *your* planet falls in *partner's* house
USER_IN_PARTNER = {
    (1, "SUN"): {
        "ru": "вы сильно влияете на его/её самоощущение и образ «я»",
        "en": "you strongly shape their sense of self and identity",
    },
    (1, "MOON"): {
        "ru": "рядом с вами партнёр чувствует себя эмоционально «собой»",
        "en": "beside you they feel emotionally like themselves",
    },
    (1, "MARS"): {
        "ru": "вы пробуждаете энергию, инициативу и напор",
        "en": "you awaken drive, initiative, and assertiveness",
    },
    (1, "VENUS"): {
        "ru": "вы добавляете притягательности и приятного отражения",
        "en": "you add attractiveness and a pleasing mirror",
    },
    (1, "MERCURY"): {
        "ru": "вы задаёте тон мышления и самопрезентации",
        "en": "you set the tone of their thinking and self-presentation",
    },
    (2, "VENUS"): {
        "ru": "вы смягчаете тему денег и удовольствий от ресурсов",
        "en": "you soften the money theme and pleasure from resources",
    },
    (2, "JUPITER"): {
        "ru": "рядом с вами расширяется чувство достатка и возможностей",
        "en": "beside you their sense of abundance and options grows",
    },
    (2, "SATURN"): {
        "ru": "вы напоминаете о бюджете, дисциплине и ответственности",
        "en": "you remind them of budget, discipline, and responsibility",
    },
    (2, "MERCURY"): {
        "ru": "финансовые решения идут через разговоры с вами",
        "en": "financial choices run through talks with you",
    },
    (3, "MERCURY"): {
        "ru": "общение с вами лёгкое, живое и насыщенное идеями",
        "en": "talk with you feels lively, quick, and idea-rich",
    },
    (3, "MOON"): {
        "ru": "вы делитесь эмоциями словами — разговор идёт от сердца",
        "en": "you share feelings in words — heart-led conversation",
    },
    (3, "VENUS"): {
        "ru": "диалог приятный, с комплиментами и лёгким флиртом",
        "en": "dialogue stays pleasant, with warmth and light flirtation",
    },
    (3, "MARS"): {
        "ru": "споры возможны, но и страстные обсуждения",
        "en": "debates flare, but so can passionate discussion",
    },
    (9, "JUPITER"): {
        "ru": "вы расширяете горизонты — планы, учёба, дальние поездки",
        "en": "you widen horizons — plans, learning, distant travel",
    },
    (9, "SUN"): {
        "ru": "вы вдохновляете его/её мировоззрение и жизненный путь",
        "en": "you inspire their worldview and life direction",
    },
    (9, "SATURN"): {
        "ru": "вы заземляете идеалы — меньше иллюзий, больше структуры",
        "en": "you ground ideals — less fantasy, more structure",
    },
    (10, "SUN"): {
        "ru": "вы заметны в его/её карьере и публичном образе",
        "en": "you show up in their career and public image",
    },
    (10, "SATURN"): {
        "ru": "вы связаны с амбициями, долгом и статусом партнёра",
        "en": "you tie into their ambitions, duty, and status",
    },
    (10, "JUPITER"): {
        "ru": "рядом с вами растут возможности и признание",
        "en": "beside you opportunities and recognition grow",
    },
    (10, "MARS"): {
        "ru": "вы мотивируете действовать и добиваться целей",
        "en": "you motivate action and reaching goals",
    },
    (7, "MOON"): {
        "ru": "вы для партнёра — символ эмоциональной опоры и надёжности в паре",
        "en": "you symbolize emotional anchor and reliability in partnership",
    },
    (7, "SUN"): {
        "ru": "вы отражаете его/её образ идеального партнёра",
        "en": "you mirror their image of an ideal partner",
    },
    (7, "VENUS"): {
        "ru": "легко видите друг друга «своей парой», есть притяжение",
        "en": "you easily read each other as a couple — natural attraction",
    },
    (7, "MARS"): {
        "ru": "в паре много искры — вы активируете друг друга",
        "en": "plenty of spark — you activate each other as partners",
    },
    (7, "MERCURY"): {
        "ru": "партнёрство строится через разговор и обмен идеями",
        "en": "partnership runs on talk and shared ideas",
    },
    (7, "JUPITER"): {
        "ru": "рядом с вами партнёр чувствует рост и оптимизм в союзе",
        "en": "beside you they feel growth and optimism in the union",
    },
    (7, "SATURN"): {
        "ru": "союз воспринимается серьёзно — есть тема ответственности",
        "en": "the bond feels serious — responsibility is in the air",
    },
    (5, "VENUS"): {
        "ru": "романтика, флирт и удовольствие от общения",
        "en": "romance, flirtation, and joy in being together",
    },
    (5, "MARS"): {
        "ru": "страсть, игра и охота друг за другом",
        "en": "passion, play, and the chase",
    },
    (5, "MOON"): {
        "ru": "нежная романтика и эмоциональная лёгкость",
        "en": "tender romance and emotional lightness",
    },
    (5, "SUN"): {
        "ru": "рядом хочется сиять и радоваться жизни",
        "en": "together you want to shine and enjoy life",
    },
    (4, "MOON"): {
        "ru": "уют, дом и чувство «своих» в быту",
        "en": "coziness, home, and a sense of belonging",
    },
    (4, "SUN"): {
        "ru": "вы — опора в вопросах дома и семьи",
        "en": "you are a pillar in home and family matters",
    },
    (4, "VENUS"): {
        "ru": "мягкая атмосфера дома и забота друг о друге",
        "en": "a soft home atmosphere and mutual care",
    },
    (4, "SATURN"): {
        "ru": "тема долга и структуры в быту — важны правила",
        "en": "duty and structure at home — rules matter",
    },
    (8, "MARS"): {
        "ru": "сильная сексуальная и эмоциональная интенсивность",
        "en": "strong sexual and emotional intensity",
    },
    (8, "MOON"): {
        "ru": "глубокая эмоциональная близость и доверие",
        "en": "deep emotional closeness and trust",
    },
    (8, "VENUS"): {
        "ru": "магнетизм и слияние на глубинном уровне",
        "en": "magnetism and merging on a deep level",
    },
}

PARTNER_IN_USER = {
    (1, "SUN"): {
        "ru": "партнёр сильно влияет на ваше самоощущение",
        "en": "your partner strongly shapes your sense of self",
    },
    (1, "MOON"): {
        "ru": "рядом с партнёром вы чувствуете себя эмоционально «собой»",
        "en": "beside your partner you feel emotionally like yourself",
    },
    (1, "MARS"): {
        "ru": "партнёр пробуждает вашу энергию и инициативу",
        "en": "your partner awakens your drive and initiative",
    },
    (2, "VENUS"): {
        "ru": "партнёр смягчает ваше отношение к деньгам и удовольствиям",
        "en": "your partner softens your attitude to money and pleasure",
    },
    (2, "SATURN"): {
        "ru": "партнёр напоминает о бюджете и финансовой дисциплине",
        "en": "your partner reminds you of budget and financial discipline",
    },
    (3, "MERCURY"): {
        "ru": "с партнёром легко говорить и обмениваться идеями",
        "en": "talk and idea exchange flow easily with your partner",
    },
    (3, "MOON"): {
        "ru": "партнёр говорит с вами на эмоциональном языке",
        "en": "your partner speaks to you in an emotional register",
    },
    (9, "JUPITER"): {
        "ru": "партнёр расширяет ваши горизонты и мировоззрение",
        "en": "your partner widens your horizons and worldview",
    },
    (10, "SUN"): {
        "ru": "партнёр заметен в вашей карьере и публичном образе",
        "en": "your partner shows up in your career and public image",
    },
    (10, "SATURN"): {
        "ru": "партнёр связан с вашими амбициями и статусом",
        "en": "your partner ties into your ambitions and status",
    },
    (7, "MOON"): {        "ru": "партнёр для вас — эмоциональная опора в союзе",
        "en": "your partner is an emotional anchor in the union",
    },
    (7, "VENUS"): {
        "ru": "партнёр естественно ложится в образ «вашей половинки»",
        "en": "your partner naturally fits your “other half” image",
    },
    (5, "MARS"): {
        "ru": "партнёр зажигает страсть и игривость",
        "en": "your partner sparks passion and play",
    },
    (5, "VENUS"): {
        "ru": "с партнёром легко романтизировать повседневность",
        "en": "romance comes easily with your partner",
    },
    (4, "MOON"): {
        "ru": "партнёр создаёт ощущение дома и семейного тепла",
        "en": "your partner creates a sense of home and family warmth",
    },
    (8, "MARS"): {
        "ru": "партнёр усиливает глубину и интенсивность связи",
        "en": "your partner deepens the intensity of the bond",
    },
    (8, "MOON"): {
        "ru": "партнёр открывает эмоциональные глубины",
        "en": "your partner opens emotional depths",
    },
}


@dataclass(frozen=True)
class SynastryHouseOverlay:
    user_in_partner: dict[int, tuple[str, ...]]
    partner_in_user: dict[int, tuple[str, ...]]
    user_has_houses: bool
    partner_has_houses: bool

    @property
    def available(self) -> bool:
        return self.user_has_houses or self.partner_has_houses

    @property
    def full_overlay(self) -> bool:
        return self.user_has_houses and self.partner_has_houses

    def angular_placements(self) -> int:
        """Count planet overlays in angular houses (1, 4, 7, 10) — strongest influence."""
        total = 0
        for house in ANGULAR_HOUSES:
            total += len(self.user_in_partner.get(house, ()))
            total += len(self.partner_in_user.get(house, ()))
        return total


def planet_house(planet_longitude: float, cusps: list[float]) -> int:
    """Return house 1–12 for a longitude given 12 Placidus cusps."""
    lon = planet_longitude % 360.0
    for house in range(1, 13):
        start = cusps[house - 1] % 360.0
        end = cusps[house % 12] % 360.0
        if start <= end:
            if start <= lon < end:
                return house
        elif lon >= start or lon < end:
            return house
    return 1


def map_planets_to_houses(
    planets: dict[str, float],
    cusps: list[float],
    *,
    planet_keys: tuple[str, ...] = OVERLAY_PLANETS,
) -> dict[str, int]:
    return {
        key: planet_house(planets[key], cusps)
        for key in planet_keys
        if key in planets
    }


def build_house_overlay(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    user_cusps: list[float] | None,
    partner_cusps: list[float] | None,
) -> SynastryHouseOverlay:
    user_in_partner: dict[int, tuple[str, ...]] = {h: () for h in FOCUS_HOUSES}
    partner_in_user: dict[int, tuple[str, ...]] = {h: () for h in FOCUS_HOUSES}

    if partner_cusps is not None:
        mapping = map_planets_to_houses(user_planets, partner_cusps)
        for house in FOCUS_HOUSES:
            user_in_partner[house] = tuple(
                p for p in OVERLAY_PLANETS if mapping.get(p) == house
            )

    if user_cusps is not None:
        mapping = map_planets_to_houses(partner_planets, user_cusps)
        for house in FOCUS_HOUSES:
            partner_in_user[house] = tuple(
                p for p in OVERLAY_PLANETS if mapping.get(p) == house
            )

    return SynastryHouseOverlay(
        user_in_partner=user_in_partner,
        partner_in_user=partner_in_user,
        user_has_houses=user_cusps is not None,
        partner_has_houses=partner_cusps is not None,
    )


def house_score_delta(overlay: SynastryHouseOverlay) -> int:
    if not overlay.full_overlay:
        return 0
    weighted = 0
    key_planets = {"MOON", "VENUS", "MARS", "SUN", "MERCURY", "JUPITER", "SATURN"}
    for house in FOCUS_HOUSES:
        house_weight = 2 if house in ANGULAR_HOUSES else 1
        for planet in overlay.user_in_partner.get(house, ()):
            if planet in key_planets:
                weighted += house_weight
        for planet in overlay.partner_in_user.get(house, ()):
            if planet in key_planets:
                weighted += house_weight
    if weighted >= 8:
        return 4
    if weighted >= 4:
        return 3
    if weighted >= 2:
        return 2
    if weighted >= 1:
        return 1
    return 0

def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _house_section(locale: str, house: int, *, style: str) -> tuple[str, str]:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if use_synastry_terms(style):
        return HOUSE_SECTION[lang][house]
    return HOUSE_SECTION_PLAIN[lang][house]


def _meaning(
    locale: str,
    house: int,
    planet: str,
    *,
    user_to_partner: bool,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    table = USER_IN_PARTNER if user_to_partner else PARTNER_IN_USER
    entry = table.get((house, planet))
    if entry and entry.get(lang):
        return entry[lang]
    _title, theme = _house_section(locale, house, style=style)
    planet_name = _planet_label(locale, planet)
    if user_to_partner:
        if lang == "ru":
            return f"ваша {planet_name} усиливает тему «{theme}» в карте партнёра"
        return f"your {planet_name} highlights “{theme}” in your partner's chart"
    if lang == "ru":
        return f"{planet_name} партнёра усиливает у вас тему «{theme}»"
    return f"partner's {planet_name} highlights “{theme}” in your chart"

def _format_placements(
    locale: str,
    house: int,
    planets: tuple[str, ...],
    *,
    user_to_partner: bool,
    style: str = "terms",
) -> list[str]:
    lang = _lang(locale)
    if not planets:
        if user_to_partner:
            return [
                "• Ваши планеты не попадают в этот дом партнёра — тема идёт через другие связи."
                if lang == "ru"
                else "• Your planets don't occupy this house in their chart — the theme runs elsewhere."
            ]
        return [
            "• Планеты партнёра не попадают в этот дом вашей карты."
            if lang == "ru"
            else "• Partner's planets don't occupy this house in your chart."
        ]

    lines: list[str] = []
    for planet in planets:
        meaning = _meaning(
            locale,
            house,
            planet,
            user_to_partner=user_to_partner,
            style=style,
        )
        planet_name = _planet_label(locale, planet)
        if lang == "ru":
            if user_to_partner:
                lines.append(
                    f"• Ваша {planet_name} в {house}-м доме партнёра — {meaning}."
                )
            else:
                lines.append(
                    f"• {planet_name} партнёра в {house}-м доме вашей карты — {meaning}."
                )
        elif user_to_partner:
            lines.append(
                f"• Your {planet_name} in partner's {house}th house — {meaning}."
            )
        else:
            lines.append(
                f"• Partner's {planet_name} in your {house}th house — {meaning}."
            )
    return lines

def format_synastry_step5_section(locale: str, overlay: SynastryHouseOverlay, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "🏠 Шаг 5. Синастрия по домам"
            if use_synastry_terms(style)
            else "🏠 Шаг 5. Сферы жизни в паре"
        )
        if use_synastry_terms(style):
            lines.append(
                "Смотрим, какие планеты одного партнёра попадают в дома другого "
                "(и наоборот). Система домов: Placidus."
            )
            lines.append(
                "Ключевое правило: планеты в угловых домах (1, 4, 7, 10) "
                "дают наиболее сильное влияние."
            )
        else:
            lines.append(
                "Смотрим, в каких сферах жизни партнёра вы оказываетесь «на виду» "
                "и что это значит для пары."
            )
            lines.append(
                "Самое заметное влияние — когда планета попадает в ключевые сферы: "
                "личность, дом, союз и карьера."
            )
    else:
        lines.append(
            "🏠 Step 5. House synastry"
            if use_synastry_terms(style)
            else "🏠 Step 5. Life areas in the pair"
        )
        if use_synastry_terms(style):
            lines.append(
                "We check which planets of one partner fall into the other's houses "
                "(and vice versa). House system: Placidus."
            )
            lines.append(
                "Key rule: planets in angular houses (1, 4, 7, 10) "
                "have the strongest influence."
            )
        else:
            lines.append(
                "We look at which life areas of your partner's world you show up in "
                "and what that means for the bond."
            )
            lines.append(
                "Strongest impact when a planet lands in core areas: "
                "identity, home, union, and career."
            )
    if not overlay.available:
        lines.append("")
        if lang == "ru":
            lines.append(
                "• Для домов нужны время рождения и город у обоих — "
                "иначе дома не рассчитать."
            )
        else:
            lines.append(
                "• Houses need birth time and city for both partners."
            )
        return "\n".join(lines)

    if not overlay.full_overlay:
        lines.append("")
        missing: list[str] = []
        if not overlay.partner_has_houses:
            missing.append(
                "у партнёра нет времени/города для домов"
                if lang == "ru"
                else "partner is missing birth time/city for houses"
            )
        if not overlay.user_has_houses:
            missing.append(
                "у вас нет времени/города для домов"
                if lang == "ru"
                else "you are missing birth time/city for houses"
            )
        note = "; ".join(missing)
        lines.append(f"• Частичный расчёт: {note}." if lang == "ru" else f"• Partial overlay: {note}.")

    if overlay.full_overlay and overlay.angular_placements():
        if lang == "ru":
            lines.append(
                f"• Угловые дома (1, 4, 7, 10): {overlay.angular_placements()} "
                "активных попаданий — влияние усилено."
            )
        else:
            lines.append(
                f"• Angular houses (1, 4, 7, 10): {overlay.angular_placements()} "
                "active placements — influence is amplified."
            )

    for house in FOCUS_HOUSES:
        header, subtitle = _house_section(locale, house, style=style)
        prefix = "⭐ " if house in ANGULAR_HOUSES and use_synastry_terms(style) else ""
        lines.append("")
        lines.append(f"🏡 {prefix}{header}")
        lines.append(subtitle.capitalize() + ".")

        if overlay.partner_has_houses:
            arrow = "→ Вы у партнёра:" if lang == "ru" else "→ You in partner's chart:"
            lines.append(arrow)
            lines.extend(
                _format_placements(
                    locale,
                    house,
                    overlay.user_in_partner.get(house, ()),
                    user_to_partner=True,
                    style=style,
                )
            )

        if overlay.user_has_houses:
            arrow = "→ Партнёр у вас:" if lang == "ru" else "→ Partner in your chart:"
            lines.append(arrow)
            lines.extend(
                _format_placements(
                    locale,
                    house,
                    overlay.partner_in_user.get(house, ()),
                    user_to_partner=False,
                    style=style,
                )
            )
    return "\n".join(lines)
