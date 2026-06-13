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
from app.text_format import format_report

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
            "default": "окрашивает самовыражение и стиль действия",
        },
        "MOON": {
            "Virgo": "ум наблюдателя: замечаешь детали, ошибки, несостыковки",
            "Taurus": "эмоциональная устойчивость и потребность в простом комфорте",
            "Cancer": "глубокая чувствительность и потребность в заботе",
            "default": "окрашивает чувства и внутренний ритм",
        },
        "MARS": {
            "Leo": "гордость, резкость речи, желание стоять за своё",
            "default": "даёт волю и способ действовать",
        },
        "MERCURY": {
            "Aries": "ум быстрый, острый, порой поспешный и нетерпеливый",
            "default": "формирует мышление и речь",
        },
        "VENUS": {
            "Aries": "вкус яркий: в чувствах нужна искра, в делах — вдохновение",
            "default": "задаёт ценности и притяжение",
        },
        "JUPITER": {
            "Capricorn": "вера и смысл приходят через испытания, а не «по умолчанию»",
            "default": "расширяет горизонт и смысл",
        },
        "SATURN": {
            "Pisces": "серьёзное отношение к знаниям, судьбе и истине",
            "default": "учит дисциплине и терпению",
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


def _use_terms(style: str) -> bool:
    return style != "plain"


def _house_lead(locale: str, house: int, theme: str, *, style: str) -> str:
    lang = _lang(locale)
    if _use_terms(style):
        if lang == "ru":
            return f"В {house}-м доме, где звучит тема «{theme}», "
        return f"In house {house}, the arena of {theme}, "
    if lang == "ru":
        return f"В сфере «{theme}», "
    return f"In the arena of {theme}, "


def _pl(locale: str, key: str) -> str:
    return PLANET_LABEL[_lang(locale)].get(key, key)


def _house_theme(locale: str, house: int) -> str:
    return HOUSE_THEME[_lang(locale)][house]


def _dignity_clause(locale: str, pl: PlanetPlacement, *, style: str = "terms") -> str:
    lang = _lang(locale)
    clauses: list[str] = []
    if not _use_terms(style):
        if pl.dignity == "exalted":
            return (
                "Здесь эта тема даётся легко и естественно."
                if lang == "ru"
                else "This theme comes easily and naturally."
            )
        if pl.dignity == "debilitated":
            return (
                "Здесь важна сознательная работа с этой темой."
                if lang == "ru"
                else "This theme asks for conscious work."
            )
        if pl.dignity == "own":
            return (
                "Планета здесь чувствует себя «дома»."
                if lang == "ru"
                else "The planet feels at home here."
            )
        if pl.retrograde and pl.key not in {"RAHU", "KETU"}:
            return (
                "Энергия идёт внутрь — эффект глубже, чем кажется снаружи."
                if lang == "ru"
                else "The energy turns inward — the effect runs deeper than it looks."
            )
        return ""
    if pl.dignity == "exalted":
        clauses.append(
            "планета в знаке силы, и тема раскрывается ярко и естественно"
            if lang == "ru"
            else "the planet is in a sign of strength and expresses itself naturally"
        )
    elif pl.dignity == "debilitated":
        clauses.append(
            "положение требует сознательной работы с этой темой"
            if lang == "ru"
            else "the placement asks for conscious work with this theme"
        )
    elif pl.dignity == "own":
        clauses.append(
            "планета «дома» в своём знаке"
            if lang == "ru"
            else "the planet is at home in its own sign"
        )
    if pl.dig_bala:
        clauses.append(
            "есть направленная сила — планета на своей естественной «сцене»"
            if lang == "ru"
            else "directional strength puts the planet on its natural stage"
        )
    if pl.retrograde and pl.key not in {"RAHU", "KETU"}:
        clauses.append(
            "ретроградность уводит энергию внутрь, эффект глубже и не прямолинейнее"
            if lang == "ru"
            else "retrograde motion turns the energy inward for a deeper, less linear effect"
        )
    if not clauses:
        return ""
    if lang == "ru":
        return "При этом " + ", ".join(clauses) + "."
    return "This comes with " + ", ".join(clauses) + "."


def _nakshatra_clause(locale: str, nakshatra: str, *, style: str = "terms") -> str:
    if not _use_terms(style):
        return ""
    lang = _lang(locale)
    if lang == "ru":
        return f"Тон задаёт накшатра {nakshatra}."
    return f"The tone is shaped by nakshatra {nakshatra}."


def _sign_line(locale: str, planet: str, sign: str) -> str:
    lang = _lang(locale)
    sign_name = sign_label(locale, sign)
    custom = SIGN_IN_SIGN.get(lang, {}).get(planet, {})
    text = custom.get(sign) or custom.get("default", "").format(sign=sign_name)
    if not text:
        if lang == "ru":
            text = f"раскрывает свой характер"
        else:
            text = f"{_pl(locale, planet)} expresses through {sign_name}"
    return text


def _planet_prose(
    locale: str,
    pl: PlanetPlacement,
    *,
    omit_house: bool = False,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    sign_name = sign_label(locale, pl.sign)
    theme = _house_theme(locale, pl.house)
    core = _sign_line(locale, pl.key, pl.sign).rstrip(".")
    dignity = _dignity_clause(locale, pl, style=style)
    nak = _nakshatra_clause(locale, pl.nakshatra, style=style)
    pname = _pl(locale, pl.key)

    if lang == "ru":
        if omit_house:
            lead = f"{pname} в {sign_name} — {core}."
        else:
            lead = (
                f"{_house_lead(locale, pl.house, theme, style=style)}"
                f"{pname} в {sign_name} — {core}."
            )
    elif omit_house:
        lead = f"{pname} in {sign_name} — {core}."
    else:
        lead = (
            f"{_house_lead(locale, pl.house, theme, style=style)}"
            f"{pname} in {sign_name} — {core}."
        )

    parts = [lead]
    if dignity:
        parts.append(dignity)
    if nak:
        parts.append(nak)
    return " ".join(parts)


def _planet_prose_special(
    locale: str,
    pl: PlanetPlacement,
    *,
    omit_house: bool = False,
    style: str = "terms",
) -> str | None:
    """Rich one-off phrasing for well-known combinations; None → use generic prose."""
    lang = _lang(locale)
    sign_name = sign_label(locale, pl.sign)
    theme = _house_theme(locale, pl.house)
    house = pl.house
    dignity = _dignity_clause(locale, pl, style=style)
    nak = _nakshatra_clause(locale, pl.nakshatra, style=style)
    nak_bit = f" {nak}" if nak else ""

    if lang == "ru":
        if pl.key == "SUN" and pl.dignity == "exalted":
            if _use_terms(style):
                house_bit = (
                    f"В {house}-м доме ({theme}) "
                    if not omit_house
                    else ""
                )
                text = (
                    f"{house_bit}Солнце в {sign_name} — в знаке силы, в положении «царя»: "
                    "ядро личности тянет к реализации, статусу и собственному курсу, "
                    "а не к роли серого исполнителя."
                )
            elif omit_house:
                text = (
                    f"Солнце в {sign_name} — сильное ядро личности: "
                    "тянет к реализации, статусу и собственному курсу."
                )
            else:
                text = (
                    f"В сфере «{theme}» Солнце в {sign_name} — сильное ядро личности: "
                    "тянет к реализации, статусу и собственному курсу."
                )
            return f"{text} {dignity}{nak_bit}".replace("  ", " ").strip()
        if pl.key == "MERCURY" and pl.sign == "Aries":
            retro = (
                " Мысли часто идут внутрь, а не наружу."
                if pl.retrograde and not _use_terms(style)
                else (
                    " Ретроградность усиливает внутреннюю переработку мыслей."
                    if pl.retrograde
                    else ""
                )
            )
            return (
                f"Меркурий в {sign_name} даёт быстрый, острый ум — "
                f"слово здесь настоящий инструмент, хотя порой звучит резко и нетерпеливо.{retro}{nak_bit}"
            ).strip()
        if pl.key == "VENUS" and pl.sign == "Aries":
            return (
                f"Венера в {sign_name} окрашивает вкус ярко: в чувствах нужна искра, "
                f"в делах — вдохновение, и иногда внимание уходит в цели, как только «загорелось».{nak_bit}"
            ).strip()
        return None

    if pl.key == "SUN" and pl.dignity == "exalted":
        if _use_terms(style):
            return (
                f"Sun in {sign_name} sits in a sign of strength — a royal placement "
                f"that pulls toward realization, status, and your own course. {dignity}{nak_bit}"
            ).strip()
        if omit_house:
            text = (
                f"Sun in {sign_name} is a strong core — "
                "it pulls toward realization, status, and your own course."
            )
        else:
            text = (
                f"In the arena of {theme}, Sun in {sign_name} is a strong core — "
                "it pulls toward realization, status, and your own course."
            )
        return f"{text} {dignity}{nak_bit}".strip()
    return None


def _truncate(text: str, limit: int = 3900) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _render_planet(
    locale: str,
    pl: PlanetPlacement,
    *,
    omit_house: bool = False,
    style: str = "terms",
) -> str:
    special = _planet_prose_special(locale, pl, omit_house=omit_house, style=style)
    if special:
        return special
    return _planet_prose(locale, pl, omit_house=omit_house, style=style)


def build_jyotish_part(chart: JyotishChart, locale: str, part: int, *, style: str = "terms") -> str:
    if part == 1:
        return format_report(_truncate(_part1(chart, locale, style=style)))
    if part == 2:
        return format_report(_truncate(_part2(chart, locale, style=style)))
    return format_report(_truncate(_part3(chart, locale, style=style)))


def _part1(chart: JyotishChart, locale: str, *, style: str = "terms") -> str:
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
        if _use_terms(style):
            intro = (
                "🌙 Ведический разбор натальной карты\n\n"
                "Это разбор в духе ведической астрологии (Джйотиш): здесь смотрят не только знак планеты, "
                "но и дом, накшатру, силу положения и общий узор карты."
            )
            core = (
                f"Твоя Лагна — {lagna}: так ты входишь в жизнь и так тебя читают снаружи. "
                f"Луна в {moon_sign} окрашивает ум и чувства, Солнце в {sun_sign} — ядро личности."
            )
        else:
            intro = (
                "🌙 Твоя натальная карта\n\n"
                "Это персональный разбор по дате, времени и месту рождения — "
                "простым языком, без астрологического жаргона."
            )
            core = (
                f"Твоё восходящее сочетание — {lagna}: так ты входишь в жизнь и как тебя обычно воспринимают. "
                f"Луна в {moon_sign} окрашивает ум и чувства, Солнце в {sun_sign} — ядро личности."
            )
        paragraphs = [intro, core]
        if chart.stellium_sign and chart.stellium_planets:
            names = ", ".join(_pl(locale, p) for p in chart.stellium_planets)
            st_sign = sign_label(locale, chart.stellium_sign)
            if _use_terms(style):
                paragraphs[-1] += (
                    f" Особый акцент карты — стеллиум в {st_sign} "
                    f"({names}) в {chart.stellium_house}-м доме: тема этого дома для тебя судьбоносна."
                )
            else:
                theme = _house_theme(locale, chart.stellium_house)
                paragraphs[-1] += (
                    f" Особый акцент — несколько планет в {st_sign} ({names}) "
                    f"в сфере «{theme}»: эта жизненная область для тебя судьбоносна."
                )

        paragraphs.append(
            f"В карте преобладает стихия {elem} — {_element_prose(chart.dominant_element, lang)}."
        )

        if _use_terms(style):
            lagna_text = f"Лагна в {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
        else:
            lagna_text = f"Вход в жизнь через {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
        if lagna_elem != chart.dominant_element:
            lagna_text += (
                f" Поэтому снаружи может ощущаться больше «{lagna_elem_label}», "
                f"а внутри — «{elem}»: один образ для мира, другой — для себя."
            )
        paragraphs.append(lagna_text)

        rhythm = _mobility_prose(chart, lang)
        extras: list[str] = []
        if chart.retrograde_planets:
            rp = ", ".join(_pl(locale, p) for p in chart.retrograde_planets)
            if _use_terms(style):
                extras.append(
                    f"Ретроградные {rp} дают не прямолинейный, а более глубокий способ думать и действовать."
                )
            else:
                extras.append(
                    f"{rp} работают более внутренне — "
                    "дают не прямолинейный, а более глубокий способ думать и действовать."
                )
        if chart.moon_waxing:
            extras.append("Луна растущая — внутренний ресурс легче наращивать и удерживать.")
        else:
            extras.append("Луна убывающая — сильнее потребность в отпускании и завершении циклов.")
        paragraphs.append(f"{rhythm} {' '.join(extras)}".strip())
        return "\n\n".join(paragraphs)

    if _use_terms(style):
        intro = (
            "🌙 Vedic natal chart reading\n\n"
            "This is a Jyotish-style reading: sign, house, nakshatra, dignity, and the chart pattern."
        )
        core = (
            f"Your Lagna is {lagna} — how you enter life and how others read you. "
            f"The Moon in {moon_sign} colors mind and feeling; the Sun in {sun_sign} is your core."
        )
    else:
        intro = (
            "🌙 Your natal chart\n\n"
            "A personal reading from your birth data — in plain language, without astrological jargon."
        )
        core = (
            f"Your rising sign is {lagna} — how you enter life and how others usually see you. "
            f"The Moon in {moon_sign} colors mind and feeling; the Sun in {sun_sign} is your core."
        )
    paragraphs = [intro, core]
    if chart.stellium_sign and chart.stellium_planets:
        names = ", ".join(_pl(locale, p) for p in chart.stellium_planets)
        st_sign = sign_label(locale, chart.stellium_sign)
        if _use_terms(style):
            paragraphs[-1] += (
                f" A stellium in {st_sign} ({names}), house {chart.stellium_house}, "
                "marks one of the chart's fated themes."
            )
        else:
            theme = _house_theme(locale, chart.stellium_house)
            paragraphs[-1] += (
                f" Several planets in {st_sign} ({names}), in the arena of {theme}, "
                "mark one of your fated life themes."
            )
    paragraphs.append(
        f"The dominant element is {elem} — {_element_prose(chart.dominant_element, lang)}."
    )
    if _use_terms(style):
        paragraphs.append(f"Lagna in {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}.")
    else:
        paragraphs.append(f"Rising through {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}.")
    paragraphs.append(_mobility_prose(chart, lang))
    return "\n\n".join(paragraphs)


def _element_prose(element: str, lang: str) -> str:
    if lang == "ru":
        mapping = {
            "fire": "она даёт напор, скорость и желание действовать, а не жить «вполсилы»",
            "earth": "она даёт практичность, терпение и опору на реальные результаты",
            "air": "она даёт мысли, контакты и потребность обмениваться идеями",
            "water": "она даёт чувствительность, интуицию и глубину переживаний",
        }
        return mapping.get(element, "")
    mapping = {
        "fire": "it adds drive, speed, and the wish to act fully",
        "earth": "it adds practicality, patience, and tangible results",
        "air": "it adds thought, contact, and exchange of ideas",
        "water": "it adds sensitivity, intuition, and emotional depth",
    }
    return mapping.get(element, "")


def _mobility_prose(chart: JyotishChart, lang: str) -> str:
    mutable = sum(
        1
        for pl in chart.planets.values()
        if pl.sign in {"Gemini", "Virgo", "Sagittarius", "Pisces"}
        and pl.key not in {"RAHU", "KETU"}
    )
    if lang == "ru":
        if mutable >= 3:
            return (
                "В карте сильны подвижные знаки — жизнь редко терпит застой, "
                "многое меняется через движение и смену обстановки."
            )
        return (
            "Карта сочетает стабильность и перемены — важно не застревать в одном режиме, "
            "но и не разрушать опору ради суеты."
        )
    if mutable >= 3:
        return "Mutable signs are strong — life changes through movement and fresh scenery."
    return "The chart mixes stability and change — neither stagnation nor chaos serves you well."


def _focus_house_prose(chart: JyotishChart, locale: str, house: int, *, style: str = "terms") -> str:
    lang = _lang(locale)
    planets = [
        chart.planets[k]
        for k in ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
        if chart.planets[k].house == house
    ]
    if not planets:
        return ""

    theme = _house_theme(locale, house)
    if len(planets) == 1:
        return _render_planet(locale, planets[0], style=style)

    names = ", ".join(_pl(locale, pl.key) for pl in planets)
    if lang == "ru":
        if _use_terms(style):
            intro = (
                f"В {house}-м доме, где звучит тема «{theme}», сходятся {names} — "
                "один из главных сюжетов твоей карты. "
            )
        else:
            intro = (
                f"В сфере «{theme}» сходятся {names} — "
                "один из главных сюжетов твоей карты. "
            )
    elif _use_terms(style):
        intro = (
            f"In house {house}, the arena of {theme}, {names} meet — "
            "one of the chart's main storylines. "
        )
    else:
        intro = (
            f"In the arena of {theme}, {names} meet — "
            "one of the chart's main storylines. "
        )

    planet_bits = [_render_planet(locale, pl, omit_house=True, style=style) for pl in planets]
    return intro + " ".join(planet_bits)


def _houses_summary_prose(chart: JyotishChart, locale: str, *, style: str = "terms") -> str:
    lang = _lang(locale)
    if lang == "ru":
        if _use_terms(style):
            parts = [
                "Дома в Джйотиш — сцены жизни: важно не только где стоят планеты, "
                "но и какие сцены освещены ярче всего."
            ]
            house_bits = []
            for h in chart.strong_houses[:4]:
                cnt = chart.house_planet_count[h]
                house_bits.append(
                    f"в {h}-м доме ({_house_theme(locale, h)}) — {cnt} планет(ы)"
                )
            if house_bits:
                parts.append("Особенно отчётливо звучат " + ", ".join(house_bits) + ".")
            if chart.kendra_planet_count >= 3:
                parts.append(
                    "Кендры (1, 4, 7, 10) насыщены — судьба строится на реальных событиях, а не на мечтах."
                )
            if chart.dusthana_planet_count <= 2:
                parts.append(
                    "Сложные дома (6, 8, 12) не перегружены — трудности есть, "
                    "но карта не выглядит разрушительной."
                )
            return " ".join(parts)

        parts = [
            "В карте особенно ярко звучат несколько жизненных сфер — "
            "не только знаки планет, но и темы, где они складываются вместе."
        ]
        house_bits = []
        for h in chart.strong_houses[:4]:
            cnt = chart.house_planet_count[h]
            house_bits.append(f"«{_house_theme(locale, h)}» — {cnt} планет(ы)")
        if house_bits:
            parts.append("Сильнее всего: " + ", ".join(house_bits) + ".")
        if chart.kendra_planet_count >= 3:
            parts.append(
                "Центральные темы жизни (личность, дом, отношения, реализация) насыщены — "
                "судьба строится на реальных событиях, а не на мечтах."
            )
        if chart.dusthana_planet_count <= 2:
            parts.append(
                "Сложные периоды возможны, но карта не выглядит перегруженной напряжением."
            )
        return " ".join(parts)

    if _use_terms(style):
        parts = ["Houses are life's stages — some are lit more brightly than others."]
        for h in chart.strong_houses[:4]:
            cnt = chart.house_planet_count[h]
            parts.append(f"House {h} ({_house_theme(locale, h)}) holds {cnt} planet(s).")
        return " ".join(parts)

    parts = [
        "Several life arenas stand out — not just planet signs, but themes where they cluster."
    ]
    for h in chart.strong_houses[:4]:
        cnt = chart.house_planet_count[h]
        parts.append(f"{_house_theme(locale, h).capitalize()} — {cnt} planet(s).")
    return " ".join(parts)


def _list_to_prose(items: list[str], lang: str) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if lang == "ru":
        return ", ".join(items[:-1]) + " и " + items[-1]
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _part2(chart: JyotishChart, locale: str, *, style: str = "terms") -> str:
    lang = _lang(locale)
    focus_house = chart.stellium_house or (chart.strong_houses[0] if chart.strong_houses else 10)
    paragraphs: list[str] = []

    if lang == "ru":
        if _use_terms(style):
            paragraphs.append(
                "🌌 Планеты и накшатры\n\n"
                "Накшатры — тонкие «комнаты» неба: они показывают не только что делает планета, "
                "но и как именно это проявляется в жизни."
            )
        else:
            paragraphs.append(
                "🌌 Планеты\n\n"
                "Здесь — как каждая планета окрашивает характер и жизненные темы."
            )
    elif _use_terms(style):
        paragraphs.append(
            "🌌 Planets and nakshatras\n\n"
            "Nakshatras are subtle sky-sectors that show how a planet expresses itself in life."
        )
    else:
        paragraphs.append(
            "🌌 Planets\n\n"
            "How each planet colors character and life themes."
        )

    focus_prose = _focus_house_prose(chart, locale, focus_house, style=style)
    if lang == "ru":
        if _use_terms(style):
            header = (
                f"🔥 Главный нерв карты — {focus_house}-й дом "
                f"({_house_theme(locale, focus_house)})"
            )
        else:
            header = f"🔥 Главный нерв карты — «{_house_theme(locale, focus_house)}»"
    elif _use_terms(style):
        header = f"🔥 Main chart nerve — house {focus_house}"
    else:
        header = f"🔥 Main chart nerve — {_house_theme(locale, focus_house)}"

    if focus_prose:
        paragraphs.append(f"{header}\n\n{focus_prose}")
        covered = {pl.key for pl in chart.planets.values() if pl.house == focus_house}
    else:
        covered = set()
        sun_moon = (
            f"{_render_planet(locale, chart.planets['SUN'], style=style)} "
            f"{_render_planet(locale, chart.planets['MOON'], style=style)}"
        ).strip()
        sun_moon_header = "🌞 Солнце и Луна" if lang == "ru" else "🌞 Sun and Moon"
        paragraphs.append(f"{sun_moon_header}\n\n{sun_moon}")
        covered.update({"SUN", "MOON"})

    other_planets = [
        _render_planet(locale, chart.planets[key], style=style)
        for key in ("MARS", "JUPITER", "SATURN")
        if key not in covered
    ]
    if other_planets:
        if lang == "ru":
            outer_header = (
                f"⚔️ {_pl(locale, 'MARS')}, {_pl(locale, 'JUPITER')} и {_pl(locale, 'SATURN')}"
            )
        else:
            outer_header = "⚔️ Mars, Jupiter, and Saturn"
        paragraphs.append(f"{outer_header}\n\n{' '.join(other_planets)}")

    rahu = chart.planets["RAHU"]
    ketu = chart.planets["KETU"]
    moon = chart.planets["MOON"]
    nodes_text = (
        f"{_render_planet(locale, rahu, style=style)} "
        f"{_render_planet(locale, ketu, style=style)}"
    ).strip()
    if lang == "ru":
        moon_rahu = ""
        if moon.house == rahu.house or abs(moon.house - rahu.house) == 11:
            if _use_terms(style):
                moon_rahu = (
                    "Луна и Раху связаны по дому — ум восприимчив к деталям и нестандартным идеям, "
                    "но порой труднее сохранить покой. "
                )
            else:
                moon_rahu = (
                    "Луна и узел карты связаны — ум восприимчив к деталям и нестандартным идеям, "
                    "но порой труднее сохранить покой. "
                )
        nodes_header = (
            "🌫 Узлы карты (Раху / Кету)" if _use_terms(style) else "🌫 Узлы карты"
        )
        houses_header = "🏠 Дома" if _use_terms(style) else "🏠 Жизненные сферы"
        paragraphs.append(f"{nodes_header}\n\n{moon_rahu}{nodes_text}")
        paragraphs.append(f"{houses_header}\n\n{_houses_summary_prose(chart, locale, style=style)}")
    else:
        nodes_header = (
            "🌫 Lunar nodes (Rahu / Ketu)" if _use_terms(style) else "🌫 Chart nodes"
        )
        houses_header = "🏠 Houses" if _use_terms(style) else "🏠 Life arenas"
        paragraphs.append(f"{nodes_header}\n\n{nodes_text}")
        paragraphs.append(f"{houses_header}\n\n{_houses_summary_prose(chart, locale, style=style)}")

    return "\n\n".join(part for part in paragraphs if part.strip())


def _part3(chart: JyotishChart, locale: str, *, style: str = "terms") -> str:
    lang = _lang(locale)
    strengths, weaknesses, risks, opportunities = _derive_summary(chart, lang)

    if lang == "ru":
        paragraphs = ["🌟 Итог"]
        if chart.gandanta_lagna or chart.gandanta_moon:
            if _use_terms(style):
                paragraphs.append(
                    "Лагна или Луна в ганданте — знак внутренней крайности и глубины. "
                    "Такой человек чувствует сильнее обычного, но дольше учится устойчивости."
                )
            else:
                paragraphs.append(
                    "Вход в жизнь или Луна в особой точке карты — знак внутренней глубины и крайних переживаний. "
                    "Такой человек чувствует сильнее обычного, но дольше учится устойчивости."
                )
        paragraphs.append(f"Сильные стороны — {_list_to_prose(strengths, lang)}.")
        paragraphs.append(f"Слабее проявляются {_list_to_prose(weaknesses, lang)}.")
        paragraphs.append(f"Главный риск — {risks}.")
        paragraphs.append(f"Главная возможность — {opportunities}.")
        return "\n\n".join(paragraphs)

    paragraphs = [
        "🌟 Summary",
    ]
    if chart.gandanta_lagna or chart.gandanta_moon:
        if _use_terms(style):
            paragraphs.append(
                "Lagna or Moon in gandanta marks inner depth and intensity — "
                "feelings run strong, stability takes longer to build."
            )
        else:
            paragraphs.append(
                "Rising sign or Moon in a sensitive chart point marks inner depth — "
                "feelings run strong, stability takes longer to build."
            )
    paragraphs.extend([
        f"Strengths — {_list_to_prose(strengths, lang)}.",
        f"Growth edges — {_list_to_prose(weaknesses, lang)}.",
        f"Main risk — {risks}.",
        f"Main opportunity — {opportunities}.",
    ])
    return "\n\n".join(paragraphs)


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
    style: str = "terms",
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
    return build_jyotish_part(chart, locale, part, style=style)
