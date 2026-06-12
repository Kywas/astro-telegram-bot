"""Narrative Vedic natal chart readings in plain language."""
from __future__ import annotations

from app.astro_engine import SIGN_ELEMENTS, sign_label
from app.jyotish_engine import (
    DUSTHANA_HOUSES,
    JyotishChart,
    KENDRA_HOUSES,
    PlanetPlacement,
    build_jyotish_chart,
)

PLANET_LABEL = {
    "ru": {
        "SUN": "Солнце", "MOON": "Луна", "MERCURY": "Меркурий", "VENUS": "Венера",
        "MARS": "Марс", "JUPITER": "Юпитер", "SATURN": "Сатурн", "RAHU": "Раху", "KETU": "Кету",
        "LAGNA": "Лагна",
    },
    "en": {
        "SUN": "Sun", "MOON": "Moon", "MERCURY": "Mercury", "VENUS": "Venus",
        "MARS": "Mars", "JUPITER": "Jupiter", "SATURN": "Saturn", "RAHU": "Rahu", "KETU": "Ketu",
        "LAGNA": "Lagna",
    },
}

ELEMENT_LABEL = {
    "ru": {"fire": "огонь", "earth": "земля", "air": "воздух", "water": "вода"},
    "en": {"fire": "fire", "earth": "earth", "air": "air", "water": "water"},
}

HOUSE_THEME = {
    "ru": {
        1: "личность и способ входить в жизнь",
        2: "ресурсы, речь и ценности",
        3: "усилия, смелость и самостоятельные шаги",
        4: "дом, опора и внутренний покой",
        5: "творчество, радость и самовыражение",
        6: "служение, труд и преодоление",
        7: "партнёрство и зеркала через других",
        8: "глубинные перемены и кризисы роста",
        9: "мировоззрение, смысл и внутренний закон",
        10: "реализация, статус и след в мире",
        11: "цели, круг поддержки и плоды усилий",
        12: "уединение, отпускание и духовная глубина",
    },
    "en": {
        1: "identity and how you enter life",
        2: "resources, speech, and values",
        3: "effort, courage, and independent steps",
        4: "home, foundation, and inner peace",
        5: "creativity, joy, and self-expression",
        6: "service, work, and overcoming",
        7: "partnership and mirrors through others",
        8: "deep change and growth crises",
        9: "worldview, meaning, and inner law",
        10: "realization, status, and your mark on the world",
        11: "goals, support circle, and fruits of effort",
        12: "solitude, release, and spiritual depth",
    },
}

LAGNA_ESSENCE = {
    "ru": {
        "Aries": "прямой, быстрый, инициативный образ — ты входишь в жизнь через действие",
        "Taurus": "спокойный, устойчивый образ — ценишь надёжность и телесный комфорт",
        "Gemini": "лёгкий, любознательный образ — многое познаёшь через слово и контакт",
        "Cancer": "мягкий, чувствительный образ — важны близость, память и защищённость",
        "Leo": "яркий, гордый образ — потребность быть заметным и жить щедро",
        "Virgo": "собранный, внимательный образ — замечаешь детали и стремишься к пользе",
        "Libra": "гармоничный, тактичный образ — ищешь баланс и красоту в отношениях",
        "Scorpio": "глубокий, сдержанный образ — чувствуешь больше, чем показываешь",
        "Sagittarius": "открытый, ищущий образ — тянет к смыслу, свободе и росту",
        "Capricorn": "серьёзный, собранный образ — ответственность и цель важнее суеты",
        "Aquarius": "своеобразный, отстранённый образ — мыслишь шире привычных рамок",
        "Pisces": "мягкий, интуитивный образ — границы между собой и миром размыты",
    },
    "en": {
        "Aries": "a direct, fast, initiative-first presence",
        "Taurus": "a calm, steady presence that values reliability",
        "Gemini": "a light, curious presence that learns through words and contact",
        "Cancer": "a soft, sensitive presence that needs closeness and safety",
        "Leo": "a bright, proud presence that wants to be seen",
        "Virgo": "a precise, useful presence that notices details",
        "Libra": "a harmonious presence that seeks balance in relationships",
        "Scorpio": "a deep, reserved presence that feels more than it shows",
        "Sagittarius": "an open, seeking presence drawn to meaning and freedom",
        "Capricorn": "a serious presence where duty outweighs fuss",
        "Aquarius": "an original, detached presence that thinks outside the box",
        "Pisces": "a soft, intuitive presence with thin boundaries",
    },
}

SIGN_IN_SIGN = {
    "ru": {
        "SUN": {
            "Aries": "ядро личности горит импульсом и инициативой",
            "Leo": "сильное солнечное ядро — потребность сиять и вести",
            "default": "солнце задаёт тон самовыражению через знак {sign}",
        },
        "MOON": {
            "Virgo": "ум наблюдателя: замечаешь детали, ошибки, несостыковки",
            "Taurus": "эмоциональная устойчивость и потребность в простом комфорте",
            "Cancer": "глубокая чувствительность и потребность в заботе",
            "default": "луна окрашивает чувства через знак {sign}",
        },
        "MARS": {
            "Leo": "гордость, резкость речи, желание стоять за своё",
            "default": "марс даёт волю и способ действовать через знак {sign}",
        },
        "MERCURY": {
            "Aries": "ум быстрый, острый, порой поспешный и нетерпеливый",
            "default": "меркурий формирует мышление через знак {sign}",
        },
        "VENUS": {
            "Aries": "вкус яркий: в чувствах нужна искра, в делах — вдохновение",
            "default": "венера задаёт ценности и притяжение через знак {sign}",
        },
        "JUPITER": {
            "Capricorn": "вера и смысл приходят через испытания, а не «по умолчанию»",
            "default": "юпитер расширяет горизонт через знак {sign}",
        },
        "SATURN": {
            "Pisces": "серьёзное отношение к знаниям, судьбе и истине",
            "default": "сатурн учит дисциплине через знак {sign}",
        },
    },
}

DIGNITY_PHRASE = {
    "ru": {
        "exalted": "в знаке силы — планета раскрывается ярко и естественно",
        "debilitated": "в неудобном положении — тема планеты требует сознательной работы",
        "own": "в своём знаке — планета чувствует себя «дома»",
        "neutral": "",
    },
    "en": {
        "exalted": "in a sign of strength — the planet expresses itself naturally",
        "debilitated": "in a weaker placement — the theme asks for conscious work",
        "own": "in its own sign — the planet feels at home",
        "neutral": "",
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _pl(locale: str, key: str) -> str:
    return PLANET_LABEL[_lang(locale)].get(key, key)


def _house_theme(locale: str, house: int) -> str:
    return HOUSE_THEME[_lang(locale)][house]


def _dignity_note(locale: str, pl: PlanetPlacement) -> str:
    lang = _lang(locale)
    base = DIGNITY_PHRASE[lang].get(pl.dignity, "")
    parts = [base] if base else []
    if pl.dig_bala:
        if lang == "ru":
            parts.append("есть направленная сила (dig bala) — планета «на своей сцене»")
        else:
            parts.append("directional strength (dig bala) — the planet is on its natural stage")
    if pl.retrograde and pl.key not in {"RAHU", "KETU"}:
        if lang == "ru":
            parts.append("ретроградность — энергия обращена внутрь, эффект глубже и не прямолинейнее")
        else:
            parts.append("retrograde — energy turns inward, the effect runs deeper")
    return ". ".join(parts)


def _sign_line(locale: str, planet: str, sign: str) -> str:
    lang = _lang(locale)
    sign_name = sign_label(locale, sign)
    custom = SIGN_IN_SIGN.get(lang, {}).get(planet, {})
    text = custom.get(sign) or custom.get("default", "").format(sign=sign_name)
    if not text:
        if lang == "ru":
            text = f"{_pl(locale, planet)} проявляется через знак {sign_name}"
        else:
            text = f"{_pl(locale, planet)} expresses through {sign_name}"
    return text


def _planet_block(locale: str, pl: PlanetPlacement) -> str:
    lang = _lang(locale)
    sign_name = sign_label(locale, pl.sign)
    house = pl.house
    theme = _house_theme(locale, house)
    core = _sign_line(locale, pl.key, pl.sign)
    dignity = _dignity_note(locale, pl)
    nak = pl.nakshatra

    if lang == "ru":
        lines = [
            f"{_pl(locale, pl.key)} в {sign_name}, {house}-й дом ({theme}).",
            core.capitalize() + ".",
        ]
        if dignity:
            lines.append(dignity.capitalize() + ".")
        lines.append(f"Накшатра: {nak}.")
        return "\n".join(lines)

    lines = [
        f"{_pl(locale, pl.key)} in {sign_name}, house {house} ({theme}).",
        core.capitalize() + ".",
    ]
    if dignity:
        lines.append(dignity.capitalize() + ".")
    lines.append(f"Nakshatra: {nak}.")
    return "\n".join(lines)


def _truncate(text: str, limit: int = 3900) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def build_jyotish_part(chart: JyotishChart, locale: str, part: int) -> str:
    if part == 1:
        return _truncate(_part1(chart, locale))
    if part == 2:
        return _truncate(_part2(chart, locale))
    return _truncate(_part3(chart, locale))


def _part1(chart: JyotishChart, locale: str) -> str:
    lang = _lang(locale)
    lagna = sign_label(locale, chart.lagna_sign)
    moon = chart.planets["MOON"]
    sun = chart.planets["SUN"]
    moon_sign = sign_label(locale, moon.sign)
    sun_sign = sign_label(locale, sun.sign)
    elem = ELEMENT_LABEL[lang][chart.dominant_element]
    lagna_elem = SIGN_ELEMENTS.get(chart.lagna_sign, "air")
    lagna_elem_label = ELEMENT_LABEL[lang][lagna_elem]

    if lang == "ru":
        lines = [
            "🌙 Ведический разбор натальной карты",
            "",
            "Это разбор в духе ведической астрологии (Джйотиш). Здесь смотрят не только знак планеты, "
            "но и дом, накшатру, силу положения и общий узор карты.",
            "",
            "✨ Твои основные положения",
            f"• Лагна (внешний образ, способ идти по жизни) — {lagna}",
            f"• Луна (ум, чувства) — {moon_sign}",
            f"• Солнце (ядро личности) — {sun_sign}",
        ]
        if chart.stellium_sign and chart.stellium_planets:
            names = ", ".join(_pl(locale, p) for p in chart.stellium_planets)
            st_sign = sign_label(locale, chart.stellium_sign)
            lines.append(
                f"• Стеллиум в {st_sign}, в {chart.stellium_house}-м доме: {names}. "
                "Это очень заметный акцент карты — тема этого дома для тебя судьбоносна."
            )
        lines.extend([
            "",
            f"🔥 Выделенная стихия — {elem}.",
            _element_fire_earth_air_water(chart.dominant_element, lang),
            "",
            f"🌊 Лагна в {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}.",
        ])
        if lagna_elem != chart.dominant_element:
            lines.append(
                f"Поэтому внешне может быть больше «{lagna_elem_label}», "
                f"а внутри — «{elem}»: снаружи одна стихия, внутри другая."
            )
        lines.extend(["", "✨ Что преобладает"])
        lines.append(_mobility_line(chart, lang))
        if chart.retrograde_planets:
            rp = ", ".join(_pl(locale, p) for p in chart.retrograde_planets)
            lines.append(
                f"• Есть ретроградные планеты: {rp}. "
                "Это даёт не прямолинейный, а более глубокий способ действовать и думать."
            )
        if chart.moon_waxing:
            lines.append("• Луна растущая — внутренний ресурс легче наращивается.")
        else:
            lines.append("• Луна убывающая — больше потребность в отпускании и завершении циклов.")
        return "\n".join(lines)

    lines = [
        "🌙 Vedic natal chart reading",
        "",
        "This is a Jyotish-style reading: sign, house, nakshatra, dignity, and the chart pattern.",
        "",
        "✨ Core placements",
        f"• Lagna — {lagna}",
        f"• Moon — {moon_sign}",
        f"• Sun — {sun_sign}",
    ]
    if chart.stellium_sign:
        names = ", ".join(_pl(locale, p) for p in chart.stellium_planets)
        lines.append(f"• Stellium in {sign_label(locale, chart.stellium_sign)}, house {chart.stellium_house}: {names}.")
    lines.extend([
        "",
        f"🔥 Dominant element — {elem}.",
        _element_fire_earth_air_water(chart.dominant_element, lang),
        "",
        f"🌊 Lagna in {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}.",
    ])
    return "\n".join(lines)


def _element_fire_earth_air_water(element: str, lang: str) -> str:
    if lang == "ru":
        mapping = {
            "fire": "Даёт напор, скорость, желание действовать и не жить «вполсилы».",
            "earth": "Даёт практичность, терпение и опору на реальные результаты.",
            "air": "Даёт мысли, контакты и потребность обмениваться идеями.",
            "water": "Даёт чувствительность, интуицию и глубину переживаний.",
        }
        return mapping.get(element, "")
    mapping = {
        "fire": "It adds drive, speed, and the wish to act fully.",
        "earth": "It adds practicality, patience, and tangible results.",
        "air": "It adds thought, contact, and exchange of ideas.",
        "water": "It adds sensitivity, intuition, and emotional depth.",
    }
    return mapping.get(element, "")


def _mobility_line(chart: JyotishChart, lang: str) -> str:
    mutable = sum(1 for pl in chart.planets.values() if pl.sign in {"Gemini", "Virgo", "Sagittarius", "Pisces"} and pl.key not in {"RAHU", "KETU"})
    if lang == "ru":
        if mutable >= 3:
            return "• Сильны подвижные знаки — жизнь не любит застоя, многое меняется через движение."
        return "• Карта сочетает стабильность и перемены — важно не застревать в одном режиме."
    if mutable >= 3:
        return "• Mutable signs are strong — life changes through movement."
    return "• The chart mixes stability and change."


def _focus_house_narrative(chart: JyotishChart, locale: str, house: int) -> list[str]:
    lang = _lang(locale)
    planets = [
        chart.planets[k]
        for k in ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
        if chart.planets[k].house == house
    ]
    if not planets:
        return []

    lines: list[str] = []
    if lang == "ru":
        lines.append(
            f"В {house}-м доме ({_house_theme(locale, house)}) собрано несколько планет — "
            "это один из главных сюжетов твоей карты."
        )
    else:
        lines.append(f"House {house} holds several planets — a main storyline of your chart.")

    for pl in planets:
        sign_name = sign_label(locale, pl.sign)
        if pl.key == "SUN" and pl.dignity == "exalted":
            if lang == "ru":
                lines.append(
                    f"Солнце в {sign_name} — в знаке силы, в положении «царя». "
                    f"В {house}-м доме оно тянет к реализации, статусу и собственному курсу. "
                    "Ты не создан для роли серого исполнителя."
                )
                continue
        if pl.key == "MERCURY" and pl.sign == "Aries":
            if lang == "ru":
                extra = " Ретроградность усиливает внутреннюю переработку мыслей." if pl.retrograde else ""
                lines.append(
                    f"Меркурий в {sign_name} — ум быстрый и острый, но порой резкий и нетерпеливый. "
                    f"Слово может быть инструментом.{extra}"
                )
                continue
        if pl.key == "VENUS" and pl.sign == "Aries":
            if lang == "ru":
                lines.append(
                    f"Венера в {sign_name} — вкус яркий: в чувствах нужна искра, в делах — вдохновение. "
                    "Иногда: загорелся — и внимание уходит в цели."
                )
                continue
        lines.append(_planet_block(locale, pl))
        lines.append("")
    return lines


def _part2(chart: JyotishChart, locale: str) -> str:
    lang = _lang(locale)
    focus_house = chart.stellium_house or (chart.strong_houses[0] if chart.strong_houses else 10)

    if lang == "ru":
        lines = [
            "🌌 О накшатрах",
            "Накшатры — тонкие «комнаты» неба: они показывают не только что делает планета, но и *как*.",
            "",
            f"🔥 Главный нерв карты — {focus_house}-й дом",
            f"Тема: {_house_theme(locale, focus_house)}.",
            "",
        ]
    else:
        lines = [
            "🌌 About nakshatras",
            "Nakshatras are subtle sky-sectors that show how a planet expresses itself.",
            "",
            f"🔥 Main chart nerve — house {focus_house}",
            "",
        ]

    focus_lines = _focus_house_narrative(chart, locale, focus_house)
    if focus_lines:
        lines.extend(focus_lines)
        covered = {pl.key for pl in chart.planets.values() if pl.house == focus_house}
    else:
        focus_planets = [chart.planets["SUN"], chart.planets["MOON"]]
        covered = set()
        for pl in focus_planets:
            lines.append(_planet_block(locale, pl))
            lines.append("")

    for key in ("MARS", "JUPITER", "SATURN"):
        if key in covered:
            continue
        lines.append(_planet_block(locale, chart.planets[key]))
        lines.append("")

    rahu = chart.planets["RAHU"]
    ketu = chart.planets["KETU"]
    moon = chart.planets["MOON"]
    if lang == "ru":
        if moon.house == rahu.house or abs(moon.house - rahu.house) == 11:
            lines.append(
                "🌙 Луна и Раху связаны по дому — ум восприимчив к деталям и нестандартным идеям, "
                "но порой труднее сохранить покой."
            )
        lines.append("🌫 Узлы карты (Раху / Кету)")
        lines.append(_planet_block(locale, rahu))
        lines.append("")
        lines.append(_planet_block(locale, ketu))
        lines.extend(["", "🏠 О домах в Джйотиш"])
        lines.append(
            "Дома — сцены жизни. Важно не только где стоят планеты, но и какие сцены освещены сильнее."
        )
        for h in chart.strong_houses[:4]:
            cnt = chart.house_planet_count[h]
            lines.append(f"• {h}-й дом — {cnt} планет(ы): {_house_theme(locale, h)}.")
        if chart.kendra_planet_count >= 3:
            lines.append(
                "• Кендры (1, 4, 7, 10) насыщены — судьба строится на реальных событиях, а не на фантазиях."
            )
        if chart.dusthana_planet_count <= 2:
            lines.append(
                "• Сложные дома (6, 8, 12) не перегружены — трудности есть, но карта не выглядит разрушительной."
            )
    else:
        lines.append(_planet_block(locale, rahu))
        lines.append(_planet_block(locale, ketu))

    return "\n".join(lines)
def _part3(chart: JyotishChart, locale: str) -> str:
    lang = _lang(locale)
    strengths, weaknesses, risks, opportunities = _derive_summary(chart, lang)

    if lang == "ru":
        lines = ["🌟 Итог", ""]
        if chart.gandanta_lagna or chart.gandanta_moon:
            lines.extend([
                "⚡ Особенность карты",
                "Лагна или Луна в ганданте — знак внутренней крайности и глубины. "
                "Такой человек чувствует сильнее обычного, но дольше учится устойчивости.",
                "",
            ])
        lines.append("Сильные стороны:")
        lines.extend(f"• {s}" for s in strengths)
        lines.append("")
        lines.append("Слабые стороны:")
        lines.extend(f"• {w}" for w in weaknesses)
        lines.append("")
        lines.append("Главные риски:")
        lines.append(f"• {risks}")
        lines.append("")
        lines.append("Главные возможности:")
        lines.append(f"• {opportunities}")
        return "\n".join(lines)

    lines = ["🌟 Summary", "", "Strengths:"]
    lines.extend(f"• {s}" for s in strengths)
    lines.extend(["", "Growth edges:"])
    lines.extend(f"• {w}" for w in weaknesses)
    lines.extend(["", f"Main risk: {risks}", "", f"Main opportunity: {opportunities}"])
    return "\n".join(lines)


def _derive_summary(chart: JyotishChart, lang: str) -> tuple[list[str], list[str], str, str]:
    strengths: list[str] = []
    weaknesses: list[str] = []

    for key, pl in chart.planets.items():
        if key in {"RAHU", "KETU"}:
            continue
        if pl.dignity == "exalted":
            strengths.append(_summary_strength(key, pl, lang))
        if pl.dignity == "debilitated":
            weaknesses.append(_summary_weakness(key, pl, lang))

    if chart.stellium_house == 10 or chart.house_planet_count.get(10, 0) >= 2:
        strengths.append(
            "яркая профессиональная энергия и потенциал заметности"
            if lang == "ru"
            else "strong professional energy and visibility"
        )
    if chart.retrograde_planets:
        if lang == "ru":
            strengths.append("способность глубоко переваривать опыт и бить точно после паузы")
        else:
            strengths.append("depth of processing and precision after pause")
    if chart.planets["MOON"].dignity in {"exalted", "own"} and chart.moon_waxing:
        strengths.append(
            "хороший внутренний ресурс и способность восстанавливаться"
            if lang == "ru"
            else "solid inner resource and recovery capacity"
        )
    if chart.planets["MERCURY"].retrograde or chart.planets["MARS"].retrograde:
        weaknesses.append(
            "тревожная перегрузка ума или внутренние споры"
            if lang == "ru"
            else "mental overload or inner arguments"
        )
    if chart.planets["MARS"].house in {2, 3, 8}:
        weaknesses.append(
            "резкость в слове и реакции, когда задевают достоинство"
            if lang == "ru"
            else "sharp speech when dignity is touched"
        )
    if chart.planets["JUPITER"].dignity == "debilitated":
        weaknesses.append(
            "завышенные ожидания и уроки через отношения"
            if lang == "ru"
            else "high expectations and lessons through relationships"
        )
    if chart.dusthana_planet_count >= 3:
        weaknesses.append(
            "склонность к внутреннему напряжению в сложных периодах"
            if lang == "ru"
            else "inner tension during hard periods"
        )

    if not strengths:
        strengths = [
            "воля и способность собраться",
            "умение учиться через опыт",
            "многослойность характера",
        ] if lang == "ru" else ["willpower", "learning through experience", "character depth"]
    if not weaknesses:
        weaknesses = [
            "склонность перегружать себя",
            "сложность с расслаблением",
        ] if lang == "ru" else ["overloading yourself", "difficulty relaxing"]

    strengths = strengths[:5]
    weaknesses = weaknesses[:5]

    if lang == "ru":
        risks = (
            "сжигать себя амбициями, спорить там, где нужна гибкость, "
            "и жить во внутреннем напряжении, даже когда внешне всё под контролем"
        )
        opportunities = (
            "сильная реализация, заметность, авторитет — "
            "умение стать человеком, которого слушают и за которым идут"
        )
    else:
        risks = "burnout from ambition and arguing where flexibility is needed"
        opportunities = "realization, visibility, and earned authority"

    return strengths, weaknesses, risks, opportunities


def _summary_strength(key: str, pl: PlanetPlacement, lang: str) -> str:
    if lang == "ru":
        mapping = {
            "SUN": "лидерский стержень и уверенность в своём курсе",
            "MOON": "эмоциональная устойчивость и психологическая чуткость",
            "MARS": "смелость и способность зарабатывать через инициативу",
            "MERCURY": "острый ум и способность быстро схватывать",
            "VENUS": "яркий вкус и притяжение",
            "JUPITER": "мудрость и тяга к росту",
            "SATURN": "дисциплина и зрелость",
        }
        return mapping.get(key, f"сила {_pl('ru', key).lower()}")
    return f"strength of {_pl('en', key).lower()}"


def _summary_weakness(key: str, pl: PlanetPlacement, lang: str) -> str:
    if lang == "ru":
        mapping = {
            "SUN": "гордость и трудность уступать",
            "MOON": "тревожность и цепляние за детали",
            "MARS": "импульсивность и резкость",
            "MERCURY": "поспешность в словах",
            "VENUS": "перепады в желаниях",
            "JUPITER": "разочарование в ожиданиях",
            "SATURN": "жёсткость и недоверие",
        }
        return mapping.get(key, f"напряжение {_pl('ru', key).lower()}")
    return f"tension in {_pl('en', key).lower()}"


def build_jyotish_reading(
    *,
    locale: str,
    birth_date,
    birth_time,
    city: str,
    timezone: str = "UTC",
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
    part: int = 1,
) -> str | None:
    chart = build_jyotish_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        timezone_name=timezone,
        locale=locale,
        lat=lat,
        lon=lon,
        birth_timezone=birth_timezone,
    )
    if chart is None:
        return None
    return build_jyotish_part(chart, locale, part)
