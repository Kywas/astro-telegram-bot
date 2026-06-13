"""Concrete family/relationship Q&A from 7th house, lords, and karakas.

Logic follows common Jyotish marriage indicators (7th sign, 7th lord placement,
planets in 7th, Venus/Moon/Jupiter karakas, 4th for home) — see open references
on 7th-lord-in-houses and partner typing (e.g. Jagannath Hora, VediqAstro).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import _house_theme, _lang, _pl, _use_terms
from app.natal_qa_synthesis import _classify_question, _question_frame
from app.natal_qa_voice import humanize_natal_plain, plain_area, plain_placement_line, plain_role
from app.text_format import b, h, p

# Partner flavour by sign on the 7th cusp (classical 7th-house spouse typing).
_H7_PARTNER: dict[str, dict[str, str]] = {
    "ru": {
        "Aries": "энергичный, прямой, с собственным темпом — не терпит давления",
        "Taurus": "устойчивый, чувственный, ценит комфорт и предсказуемость",
        "Gemini": "общительный, любопытный — важен разговор и лёгкость контакта",
        "Cancer": "заботливый, домашний — нужна эмоциональная безопасность",
        "Leo": "яркий, с достоинством — важны уважение и тепло",
        "Virgo": "практичный, внимательный к деталям — любит порядок и пользу",
        "Libra": "гармоничный, дипломатичный — тянет к равенству и красоте пары",
        "Scorpio": "глубокий, интенсивный — отношения «всё или ничего»",
        "Sagittarius": "свободолюбивый, оптимистичный — нужен простор и смысл",
        "Capricorn": "серьёзный, ответственный — союз как дело и опора",
        "Aquarius": "самостоятельный, нестандартный — дружба и идеи важнее романтики",
        "Pisces": "мягкий, эмпатичный — нужна душевная близость и принятие",
    },
    "en": {
        "Aries": "energetic and direct — resists pressure",
        "Taurus": "steady and sensual — values comfort and predictability",
        "Gemini": "talkative and curious — needs conversation and lightness",
        "Cancer": "caring and homely — needs emotional safety",
        "Leo": "warm and proud — needs respect and warmth",
        "Virgo": "practical and detail-minded — likes order and usefulness",
        "Libra": "harmonious and diplomatic — drawn to balance and beauty",
        "Scorpio": "deep and intense — all-or-nothing bonding",
        "Sagittarius": "freedom-loving and optimistic — needs space and meaning",
        "Capricorn": "serious and responsible — union as duty and support",
        "Aquarius": "independent and unconventional — friendship and ideas over romance",
        "Pisces": "soft and empathetic — needs soul-level closeness",
    },
}

# Where/how partnership themes activate when the 7th lord sits in each house.
_LORD7_IN_HOUSE: dict[str, dict[int, str]] = {
    "ru": {
        1: "партнёрство сливается с твоим образом — союз меняет то, как ты себя видишь",
        2: "брак связан с деньгами и ценностями — партнёр может влиять на доход и стиль трат",
        3: "знакомство через общение, соседей, поездки — часто молодой или разговорчивый тип",
        4: "союз завязан на дом и семью — партнёр даёт чувство «своих» или из твоей среды",
        5: "романтика, творчество, досуг — встреча через увлечения, праздники, детей",
        6: "через работу/службу — возможны задержки, бытовые споры, тема здоровья в паре",
        7: "брак — одна из главных тем, не «фоновая» история",
        8: "глубокая трансформация — совместные кризисы, тайны, наследство или общие ресурсы",
        9: "иностранец, другая культура, наставник — брак расширяет мировоззрение",
        10: "партнёр виден публично — карьера, статус, встреча на работе или через репутацию",
        11: "через друзей и сообщества — желания реализуются после союза",
        12: "дистанция, уединение, заграница — нужна приватность; возможны жертвы ради пары",
    },
    "en": {
        1: "partnership merges with identity — union reshapes self-image",
        2: "marriage ties to money and values — spouse may affect income and spending",
        3: "meeting through talk, neighbors, short trips — often a younger or chatty type",
        4: "union anchors in home and family — partner brings belonging or comes from your roots",
        5: "romance, creativity, leisure — meeting through hobbies, events, children",
        6: "through work/service — delays, daily friction, health themes in the pair",
        7: "strong marriage focus — spouse embodies the 7th sign; partnership is central",
        8: "deep transformation — joint crises, secrets, inheritance or shared resources",
        9: "foreigner, other culture, teacher — marriage widens worldview",
        10: "partner is public — career, status, meeting at work or through reputation",
        11: "through friends and groups — wishes often land after union",
        12: "distance, solitude, abroad — privacy needed; possible sacrifice for the pair",
    },
}

# Planets occupying the 7th (classical spouse/relationship modifiers).
_PLANET_IN_7: dict[str, dict[str, str]] = {
    "ru": {
        "SUN": "партнёр с сильным характером — лидер или человек, который «светит» в паре",
        "MOON": "эмоциональный партнёр — настроение пары меняется вместе с Луной",
        "MARS": "страсть и споры — химия сильная, но нужен выход энергии без войны",
        "MERCURY": "умный, молодой духом партнёр — связь через слова и обмен идеями",
        "JUPITER": "зрелый, благожелательный партнёр — хороший знак для устойчивого союза",
        "VENUS": "любовь и брак важны сами по себе — притяжение к красивому и гармоничному",
        "SATURN": "зрелый или старший партнёр — поздний старт, но серьёзные обязательства",
        "RAHU": "нестандартный тип — иностранец, контраст, сильная тяга к «другому»",
        "KETU": "отстранённость или духовный партнёр — тема «отпустить ожидания»",
    },
    "en": {
        "SUN": "strong-willed partner — a leader or someone who shines in the pair",
        "MOON": "emotional partner — the pair's mood shifts with the Moon",
        "MARS": "passion and arguments — strong chemistry, needs a non-destructive outlet",
        "MERCURY": "clever, youthful partner — bond through words and ideas",
        "JUPITER": "mature, benevolent partner — good sign for a stable union",
        "VENUS": "love and marriage matter on their own — pull toward beauty and harmony",
        "SATURN": "mature or older partner — late start, serious commitments",
        "RAHU": "unusual type — foreign, contrast, strong pull toward the «other»",
        "KETU": "detached or spiritual partner — theme of releasing expectations",
    },
}

_DIGNITY: dict[str, dict[str, str]] = {
    "ru": {
        "exalted": "в знаке силы — тема работает ярко",
        "own": "в своём знаке — устойчиво и надёжно",
        "debilitated": "в слабом положении — нужна осознанность, не давить на тему",
        "neutral": "",
    },
    "en": {
        "exalted": "exalted — theme works brightly",
        "own": "in own sign — steady and reliable",
        "debilitated": "debilitated — needs conscious care, don't force the theme",
        "neutral": "",
    },
}


@dataclass(frozen=True)
class FamilyStructuredAnswer:
    brief: str
    markers: tuple[str, ...]
    practice: str


def _planets_in_house(chart: JyotishChart, house: int) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")
    return [chart.planets[key] for key in order if chart.planets[key].house == house]


def _lord(chart: JyotishChart, house: int) -> PlanetPlacement:
    return chart.planets[chart.house_lords[house]]


def _dignity_note(locale: str, pl: PlanetPlacement) -> str:
    return _DIGNITY[_lang(locale)].get(pl.dignity, "")


def _placement_label(
    locale: str,
    pl: PlanetPlacement,
    *,
    style: str,
    role: str = "",
) -> str:
    lang = _lang(locale)
    pname = _pl(locale, pl.key)
    sign = sign_label(locale, pl.sign)
    dig = _dignity_note(locale, pl)
    if _use_terms(style):
        theme = _house_theme(locale, pl.house)
        base = f"{pname} в {sign}, {pl.house}-й дом («{theme}»)"
        return f"{base} · {dig}" if dig else base
    return plain_placement_line(locale, pl)


# Where home/family themes go when the 4th lord sits in each house.
_LORD4_IN_HOUSE: dict[str, dict[int, str]] = {
    "ru": {
        1: "семейный фон влияет на образ — «дом» начинается с того, как ты себя чувствуешь",
        2: "дом связан с ресурсами — опора через достаток, еду, ценности семьи",
        3: "дом через общение — близкие рядом, когда есть разговор и короткие поездки",
        4: "сильная тема корней — семья и жильё в центре жизни",
        5: "дом радостный — уют через творчество, детей, праздники",
        6: "дом через быт и заботу — много дел, иногда усталость от «хозяйства»",
        7: "дом строится через партнёра — «свои» часто приходят с союзом",
        8: "глубокие семейные тайны — дом переживает кризисы и обновления",
        9: "дом далеко от родины или через веру/учёбу — расширение через традицию",
        10: "дом на виду — семья связана с работой, статусом, репутацией",
        11: "дом через друзей и сообщество — «свои» шире кровных",
        12: "дом в уединении — нужна тишина; корни могут быть «за морем» или в духовности",
    },
    "en": {
        1: "family background shapes identity — «home» starts with self-feeling",
        2: "home ties to resources — support through means and family values",
        3: "home through talk — closeness when there is conversation",
        4: "strong roots theme — family and dwelling are central",
        5: "joyful home — comfort through creativity and celebration",
        6: "home through routine — chores and care, sometimes tiring",
        7: "home built through partner — «your people» often arrive with union",
        8: "deep family secrets — home goes through crises and renewal",
        9: "home far from birthplace or through faith/study",
        10: "visible home — family linked to work and status",
        11: "home through friends and community",
        12: "home in solitude — quiet needed; roots may be abroad or spiritual",
    },
}


def _lord4_circumstance(locale: str, house: int) -> str:
    return _LORD4_IN_HOUSE[_lang(locale)].get(house, _LORD4_IN_HOUSE[_lang(locale)][4])


def _h7_partner_type(locale: str, sign: str) -> str:
    return _H7_PARTNER[_lang(locale)].get(sign, _H7_PARTNER[_lang(locale)]["Libra"])


def _lord7_circumstance(locale: str, house: int, *, style: str = "terms") -> str:
    lang = _lang(locale)
    if not _use_terms(style) and lang == "ru" and house == 7:
        return "партнёрство — центральная тема, не фон"
    if not _use_terms(style) and lang == "en" and house == 7:
        return "partnership is central, not background"
    return _LORD7_IN_HOUSE[lang].get(house, _LORD7_IN_HOUSE[lang][7])


def _planet_in_7_note(locale: str, key: str) -> str:
    return _PLANET_IN_7[_lang(locale)].get(key, "")


def _moon_relationship_mode(locale: str, moon: PlanetPlacement, *, style: str) -> str:
    lang = _lang(locale)
    sign = sign_label(locale, moon.sign)
    if not _use_terms(style):
        area = plain_area(locale, moon.house)
        if moon.house == 7:
            if lang == "ru":
                return "эмоции сразу в паре — чувствуешь партнёра настроением, не только словами"
            return "feelings live in the pair — you read your partner through mood"
        if lang == "ru":
            return f"чувства идут через {area} ({sign}) — сначала настроение, потом слова"
        return f"feelings run through {area} ({sign}) — mood before words"
    if moon.house == 7:
        if lang == "ru":
            return "эмоции сразу в паре — чувствуешь партнёра телом и настроением"
        return "emotions live in the pair — you feel the partner through mood and body"
    if moon.house in (3, 5):
        if lang == "ru":
            return f"сначала слова и игра ({sign}, {moon.house}-й дом) — потом доверие и близость"
        return f"words and play first ({sign}, house {moon.house}) — trust and closeness follow"
    if moon.house == 4:
        if lang == "ru":
            return "близость через дом и «своих» — без ощущения семьи интерес падает"
        return "closeness through home and «your people» — without family feeling, interest drops"
    if lang == "ru":
        return f"эмоции в {moon.house}-м доме ({sign}) — чувства приходят через {_house_theme(locale, moon.house).lower()}"
    return f"emotions in house {moon.house} ({sign}) — feelings arrive via {_house_theme(locale, moon.house)}"


def _venus_love_filter(locale: str, venus: PlanetPlacement, *, style: str) -> str:
    lang = _lang(locale)
    sign = sign_label(locale, venus.sign)
    in7 = venus.house == 7
    if not _use_terms(style):
        where = "прямо в паре" if in7 else f"через {plain_area(locale, venus.house)}"
        if lang == "ru":
            return f"В любви выбираешь, где {where} — приятно и по-настоящему ({sign})"
        return f"In love you pick where {where} feels real and warm ({sign})"
    dig = _dignity_note(locale, venus)
    if lang == "ru":
        where = "прямо в теме партнёрства" if in7 else f"через {_house_theme(locale, venus.house).lower()}"
        tail = f" ({dig})" if dig else ""
        return f"Венера в {sign}{tail}: выбираешь, где {where} — приятно, красиво и по-настоящему"
    where = "directly in partnership" if in7 else f"via {_house_theme(locale, venus.house)}"
    tail = f" ({dig})" if dig else ""
    return f"Venus in {sign}{tail}: you choose where {where} feels pleasant and real"


def _jupiter_union_maturity(locale: str, jupiter: PlanetPlacement, *, style: str = "terms") -> str:
    lang = _lang(locale)
    sign = sign_label(locale, jupiter.sign)
    house = jupiter.house
    theme = _house_theme(locale, house)
    if not _use_terms(style):
        area = plain_area(locale, house)
        if lang == "ru":
            if house == 7:
                return "Союз даёт рост, если оба не сливаются в «я одна/один тащу»"
            return f"Пара крепнет через {area} ({sign}) — не только романтика на старте"
        if house == 7:
            return "Union grows when neither of you carries everything alone"
        return f"Pair strengthens through {area} ({sign}) — not just honeymoon vibes"
    if lang == "ru":
        if house == 7:
            return "Юпитер в 7-м — союз приносит рост и благословение, если оба берут ответственность"
        if house == 4:
            return f"Юпитер в 4-м ({sign}) — брак крепнет, когда дом доверяет и держит глубину, а не только уют"
        if house in (9, 11):
            return f"Юпитер в {house}-м — союз расширяет горизонт и даёт общий смысл ({theme})"
        return f"Юпитер в {house}-м ({sign}) — зрелость пары через тему «{theme}»"
    if house == 7:
        return "Jupiter in the 7th — union brings growth when both take responsibility"
    if house == 4:
        return f"Jupiter in the 4th ({sign}) — marriage strengthens when home holds depth and trust"
    return f"Jupiter in house {house} ({sign}) — pair matures through {theme}"


def _home_family_core(locale: str, chart: JyotishChart, *, style: str) -> str:
    lang = _lang(locale)
    moon = chart.planets["MOON"]
    lord4 = _lord(chart, 4)
    h4_sign = sign_label(locale, chart.house_signs[4])
    in4 = _planets_in_house(chart, 4)
    lord4_note = (
        _lord4_circumstance(locale, lord4.house)
        if lord4.house != 4
        else (
            "управитель 4-го в своём доме — тема семьи и корней звучит сильно"
            if lang == "ru"
            else "4th lord in its own house — family and roots are loud"
        )
    )
    if not _use_terms(style):
        if lang == "ru":
            base = f"Дом и «свои» — про {plain_area(locale, 4)}. "
            moon_bit = _moon_relationship_mode(locale, moon, style=style)
            lord_bit = _lord4_circumstance(locale, lord4.house)
            extra = ""
            if in4:
                extra = " Дома много энергии — семейная атмосфера яркая."
            return base + f"Эмоции: {moon_bit}. {lord_bit.capitalize()}.{extra}"
        base = f"Home and «your people» — about {plain_area(locale, 4)}. "
        return base + _moon_relationship_mode(locale, moon, style=style) + f" {_lord4_circumstance(locale, lord4.house)}."
    if lang == "ru":
        base = f"4-й дом в {h4_sign}: дом — про {_house_theme(locale, 4).lower()}. "
        moon_bit = _moon_relationship_mode(locale, moon, style=style)
        lord_bit = f"Управитель 4-го ({_pl(locale, lord4.key)} в {sign_label(locale, lord4.sign)}): {lord4_note}."
        extra = ""
        if in4:
            names = ", ".join(_pl(locale, p.key) for p in in4[:2])
            extra = f" В 4-м также {names} — семейная атмосфера окрашена их качествами."
        return base + f"Луна: {moon_bit}. " + lord_bit + extra
    base = f"4th house in {h4_sign}: home is about {_house_theme(locale, 4)}. "
    return base + _moon_relationship_mode(locale, moon, style=style) + f" 4th lord: {lord4_note}."


def _friction_points(locale: str, chart: JyotishChart, *, style: str) -> list[str]:
    lang = _lang(locale)
    points: list[str] = []
    mars = chart.planets["MARS"]
    saturn = chart.planets["SATURN"]
    rahu = chart.planets["RAHU"]
    venus = chart.planets["VENUS"]
    lord7 = _lord(chart, 7)

    if mars.house in (4, 7) or mars.dignity == "debilitated":
        if lang == "ru":
            if not _use_terms(style):
                if mars.house == 12:
                    points.append("Злость уходит внутрь — молчишь, уходишь, копишь обиду вместо разговора")
                elif mars.house == 7:
                    points.append("В паре бывают вспышки — кто главный, кто уступает; нужны правила ссоры")
                else:
                    points.append(f"Напряжение в {plain_area(locale, mars.house)} — не всегда про «не люблю»")
            elif mars.house == 12:
                points.append(
                    "Марс в 12-м (ослаблен) — злость уходит внутрь: молчание, уход, пассивная обида вместо разговора"
                )
            elif mars.house == 7:
                points.append("Марс в 7-м — вспышки и борьба за лидерство в паре; нужны правила спора")
            else:
                points.append(f"Марс в {mars.house}-м — напряжение в теме {_house_theme(locale, mars.house).lower()}")
        elif mars.house == 12:
            points.append("Mars in the 12th (weak) — anger goes inward: silence and passive hurt")
        elif mars.house == 7:
            points.append("Mars in the 7th — flare-ups and leadership fights; need conflict rules")
        else:
            points.append(f"Mars in house {mars.house} — tension in {_house_theme(locale, mars.house)}")

    if saturn.house in (4, 7) or saturn.dignity in {"debilitated", "own", "exalted"}:
        if saturn.house == 7:
            if lang == "ru":
                if not _use_terms(style):
                    if saturn.dignity == "own":
                        points.append(
                            "Союз серьёзный, но без тепла легко превратиться в «мы соседи по договору»"
                        )
                    else:
                        points.append("Дистанция и проверки на прочность — страшно обещать, пока не уверен")
                elif saturn.dignity == "own":
                    points.append(
                        "Сатурн-управитель 7-го в 7-м (свой знак) — союз серьёзный, но холод или дистанция возможны без тепла"
                    )
                else:
                    points.append("Сатурн в 7-м — дистанция, проверки на прочность, страх обязательств")
            elif not _use_terms(style):
                if saturn.dignity == "own":
                    points.append("Serious union — without warmth it can feel like «roommates by contract»")
                else:
                    points.append("Distance and durability tests — hard to promise until sure")
            elif saturn.dignity == "own":
                points.append("Saturn as 7th lord in the 7th (own sign) — serious union, risk of cold distance")
            else:
                points.append("Saturn in the 7th — distance, tests of durability, fear of commitment")

    if rahu.house in (3, 4, 7):
        if lang == "ru":
            if not _use_terms(style):
                points.append(
                    f"Идеализация и ревность в {plain_area(locale, rahu.house)} — "
                    "ожидания иногда выше реальности (классика «я думал, будет иначе»)"
                )
            else:
                points.append(
                    f"Раху в {rahu.house}-м — идеализация и ревность в {_house_theme(locale, rahu.house).lower()}; "
                    "ожидания могут быть выше реальности"
                )
        else:
            points.append(
                f"Rahu in house {rahu.house} — idealization/jealousy in {_house_theme(locale, rahu.house)}"
            )

    if venus.house == 7 and lord7.key == "SATURN":
        if not _use_terms(style):
            if lang == "ru":
                points.append("Любовь vs долг: «хочу близости» и «надо держать рамки» — оба голоса громкие")
            else:
                points.append("Love vs duty — both voices are loud")
        elif lang == "ru":
            points.append("Венера и Сатурн вместе в 7-м — любовь vs долг: «хочу близости» и «надо держать рамки»")
        else:
            points.append("Venus and Saturn together in the 7th — love vs duty tension")

    if not points:
        if lang == "ru":
            points.append("Явных «тяжёлых» планет в 4/7 мало — трения скорее бытовые; смотри повторяющиеся ссоры")
        else:
            points.append("Few heavy planets in 4/7 — friction is likely daily; watch repeating arguments")
    return points[:3]


def _brief_q0(locale: str, chart: JyotishChart, question: str, *, style: str) -> str:
    lang = _lang(locale)
    intent = _classify_question(question, lang)
    frame = _question_frame(locale, question, intent if intent == "how_relationship" else "how_relationship", style=style)
    venus = chart.planets["VENUS"]
    moon = chart.planets["MOON"]
    h7 = _planets_in_house(chart, 7)
    lord7 = _lord(chart, 7)

    if lang == "ru":
        steps = [
            _venus_love_filter(locale, venus, style=style),
            f"Эмоционально: {_moon_relationship_mode(locale, moon, style=style)}.",
        ]
        if h7:
            for pl in h7[:2]:
                note = _planet_in_7_note(locale, pl.key)
                if note:
                    if _use_terms(style):
                        steps.append(f"{_pl(locale, pl.key)} в 7-м: {note}.")
                    else:
                        steps.append(f"В паре усиливает: {note}.")
        elif lord7.house != 7:
            if _use_terms(style):
                steps.append(
                    f"7-й пуст — стиль пары задаёт управитель ({_pl(locale, lord7.key)} в {lord7.house}-м): "
                    f"{_lord7_circumstance(locale, lord7.house, style=style)}."
                )
            else:
                steps.append(
                    f"Пара складывается через {plain_area(locale, lord7.house)}: "
                    f"{_lord7_circumstance(locale, lord7.house, style=style)}."
                )
        body = " ".join(steps)
        return p(b(frame), h(body))

    steps = [
        _venus_love_filter(locale, venus, style=style),
        f"Emotionally: {_moon_relationship_mode(locale, moon, style=style)}.",
    ]
    for pl in h7[:2]:
        note = _planet_in_7_note(locale, pl.key)
        if note:
            steps.append(f"{_pl(locale, pl.key)} in the 7th: {note}.")
    return p(b(frame), h(" ".join(steps)))


def _brief_q1(locale: str, chart: JyotishChart, question: str, *, style: str) -> str:
    lang = _lang(locale)
    frame = _question_frame(locale, question, "who_partner", style=style)
    h7_sign_key = chart.house_signs[7]
    h7_sign = sign_label(locale, h7_sign_key)
    partner = _h7_partner_type(locale, h7_sign_key)
    lord7 = _lord(chart, 7)
    venus = chart.planets["VENUS"]
    in7 = _planets_in_house(chart, 7)

    if lang == "ru":
        if _use_terms(style):
            lines = [
                f"Знак 7-го ({h7_sign}) тянет к типу: {b(partner)}.",
                f"Обстоятельства и «как встречаешь» — управитель 7-го "
                f"({_pl(locale, lord7.key)} в {lord7.house}-м доме): {_lord7_circumstance(locale, lord7.house, style=style)}.",
                _venus_love_filter(locale, venus, style=style) + ".",
            ]
            for pl in in7:
                note = _planet_in_7_note(locale, pl.key)
                if note and pl.key not in {lord7.key}:
                    lines.append(f"В 7-м {_pl(locale, pl.key)} усиливает: {note}")
        else:
            lines = [
                f"Тебя тянет к типу: {b(partner)} (оттенок {h7_sign}).",
                f"Встречаешь людей через {plain_area(locale, lord7.house)}: "
                f"{_lord7_circumstance(locale, lord7.house, style=style)}.",
                _venus_love_filter(locale, venus, style=style) + ".",
            ]
            for pl in in7:
                note = _planet_in_7_note(locale, pl.key)
                if note and pl.key not in {lord7.key}:
                    lines.append(f"В паре добавляет: {note}")
        return p(b(frame), h(" ".join(lines)))

    lines = [
        f"7th sign ({h7_sign}) pulls toward: {b(partner)}.",
        f"How you meet — 7th lord {_pl(locale, lord7.key)} in house {lord7.house}: "
        f"{_lord7_circumstance(locale, lord7.house, style=style)}.",
        _venus_love_filter(locale, venus, style=style) + ".",
    ]
    return p(b(frame), h(" ".join(lines)))


def _brief_q2(locale: str, chart: JyotishChart, question: str, *, style: str) -> str:
    lang = _lang(locale)
    frame = _question_frame(locale, question, "what", style=style)
    lord7 = _lord(chart, 7)
    jupiter = chart.planets["JUPITER"]
    in7 = _planets_in_house(chart, 7)
    dig = _dignity_note(locale, lord7)

    if lang == "ru":
        if _use_terms(style):
            marriage = (
                f"Управитель брака — {_pl(locale, lord7.key)} в {sign_label(locale, lord7.sign)}, "
                f"{lord7.house}-й дом: {_lord7_circumstance(locale, lord7.house, style=style)}."
            )
            if dig:
                marriage += f" {dig.capitalize()}."
            jup = _jupiter_union_maturity(locale, jupiter, style=style)
            extra = ""
            if lord7.house == 7:
                extra = " Союз — одна из центральных тем жизни, не «фоновая» история."
            elif lord7.house in (6, 8, 12):
                extra = " Возможны задержки или испытания — качество зависит от осознанности, не от «запрета»."
            if in7:
                names = ", ".join(_pl(locale, p.key) for p in in7)
                extra += f" В 7-м: {names} — они окрашивают повседневность брака."
            return p(b(frame), h(f"{marriage} {jup}.{extra}"))
        marriage = (
            f"Серьёзный союз у тебя через {plain_area(locale, lord7.house)} "
            f"({sign_label(locale, lord7.sign)}): {_lord7_circumstance(locale, lord7.house, style=style)}."
        )
        jup = _jupiter_union_maturity(locale, jupiter, style=style)
        extra = ""
        if lord7.house == 7:
            extra = " Пара — не «фон», а одна из главных тем."
        elif lord7.house in (6, 8, 12):
            extra = " Может тянуть время — не приговор, а «не спеши с подписью»."
        return p(b(frame), h(f"{marriage} {jup}.{extra}"))

    marriage = (
        f"Marriage lord — {_pl(locale, lord7.key)} in {sign_label(locale, lord7.sign)}, "
        f"house {lord7.house}: {_lord7_circumstance(locale, lord7.house, style=style)}."
    )
    return p(b(frame), h(f"{marriage} {_jupiter_union_maturity(locale, jupiter, style=style)}."))


def _brief_q3(locale: str, chart: JyotishChart, question: str, *, style: str) -> str:
    lang = _lang(locale)
    if _use_terms(style):
        topic = question.strip().rstrip("?.!")
        frame = f"На «{topic}» — по 4-му дому, Луне и управителю 4-го:" if lang == "ru" else f"On «{topic}» — from house 4, the Moon, and the 4th lord:"
    else:
        frame = _question_frame(locale, question, "general", style=style)
    core = _home_family_core(locale, chart, style=style)
    return p(b(frame), h(core))


def _brief_q4(locale: str, chart: JyotishChart, question: str, *, style: str) -> str:
    lang = _lang(locale)
    frame = _question_frame(locale, question, "challenge", style=style)
    frictions = _friction_points(locale, chart, style=style)
    if lang == "ru":
        body = " ".join(frictions) + " Это не приговор — лучше сказать «мне обидно», чем молчать до взрыва."
    else:
        body = " ".join(frictions) + " Not a verdict — say «I'm hurt» before it blows up."
    return p(b(frame), h(body))


def _markers_q0(locale: str, chart: JyotishChart, *, style: str) -> tuple[str, ...]:
    venus = chart.planets["VENUS"]
    moon = chart.planets["MOON"]
    lord7 = _lord(chart, 7)
    h7_sign = sign_label(locale, chart.house_signs[7])
    lines = [
        _placement_label(locale, venus, style=style, role="Венера" if _lang(locale) == "ru" else "Venus"),
        _placement_label(locale, moon, style=style, role="Луна" if _lang(locale) == "ru" else "Moon"),
    ]
    in7 = _planets_in_house(chart, 7)
    seen: set[str] = {"VENUS", "MOON"}
    if in7:
        for pl in in7[:2]:
            if pl.key in seen:
                continue
            seen.add(pl.key)
            note = _planet_in_7_note(locale, pl.key)
            line = _placement_label(locale, pl, style=style)
            lines.append(f"{line} — {note}" if note else line)
    else:
        if _lang(locale) == "ru":
            if _use_terms(style):
                lines.append(
                    f"7-й дом ({h7_sign}) без планет — стиль пары через {_pl(locale, lord7.key)} "
                    f"в {lord7.house}-м: {_lord7_circumstance(locale, lord7.house, style=style)}"
                )
            else:
                lines.append(
                    f"В паре мало «громких» маркеров — стиль через {plain_area(locale, lord7.house)}: "
                    f"{_lord7_circumstance(locale, lord7.house, style=style)}"
                )
        else:
            lines.append(
                f"Empty 7th ({h7_sign}) — pair style via {_pl(locale, lord7.key)} "
                f"in house {lord7.house}: {_lord7_circumstance(locale, lord7.house, style=style)}"
            )
    return tuple(lines[:3])


def _markers_q1(locale: str, chart: JyotishChart, *, style: str) -> tuple[str, ...]:
    h7_sign = sign_label(locale, chart.house_signs[7])
    partner = _h7_partner_type(locale, chart.house_signs[7])
    lord7 = _lord(chart, 7)
    venus = chart.planets["VENUS"]
    lang = _lang(locale)
    if lang == "ru":
        if _use_terms(style):
            lines = [
                f"Знак 7-го · {h7_sign} · тип: {partner}",
                _placement_label(locale, lord7, style=style, role="Управитель 7-го")
                + f" — {_lord7_circumstance(locale, lord7.house, style=style)}",
                _placement_label(locale, venus, style=style, role="Фильтр Венеры"),
            ]
        else:
            lines = [
                f"Тип притяжения · {h7_sign} · {partner}",
                plain_placement_line(locale, lord7) + f" — {_lord7_circumstance(locale, lord7.house, style=style)}",
                plain_placement_line(locale, venus),
            ]
    else:
        lines = [
            f"7th sign · {h7_sign} · type: {partner}",
            _placement_label(locale, lord7, style=style, role="7th lord")
            + f" — {_lord7_circumstance(locale, lord7.house, style=style)}",
            _placement_label(locale, venus, style=style, role="Venus filter"),
        ]
    return tuple(lines)


def _markers_q2(locale: str, chart: JyotishChart, *, style: str) -> tuple[str, ...]:
    lord7 = _lord(chart, 7)
    jupiter = chart.planets["JUPITER"]
    lang = _lang(locale)
    lord_line = _placement_label(
        locale, lord7, style=style, role="Управитель брака" if lang == "ru" else "Marriage lord"
    )
    jup_line = _placement_label(locale, jupiter, style=style, role="Юпитер" if lang == "ru" else "Jupiter")
    h7 = sign_label(locale, chart.house_signs[7])
    if lang == "ru":
        third = f"7-й дом · {h7} · тема союза и договорённостей один на один"
    else:
        third = f"7th house · {h7} · one-to-one union and contracts"
    return (lord_line, jup_line, third)


def _markers_q3(locale: str, chart: JyotishChart, *, style: str) -> tuple[str, ...]:
    moon = chart.planets["MOON"]
    lord4 = _lord(chart, 4)
    h4_sign = sign_label(locale, chart.house_signs[4])
    in4 = _planets_in_house(chart, 4)
    lang = _lang(locale)
    lines = [
        _placement_label(locale, moon, style=style, role="Луна" if lang == "ru" else "Moon"),
        _placement_label(locale, lord4, style=style, role="Управитель 4-го" if lang == "ru" else "4th lord"),
    ]
    if in4:
        pl = in4[0]
        lines.append(_placement_label(locale, pl, style=style, role="В 4-м" if lang == "ru" else "In 4th"))
    else:
        lines.append(
            f"4-й дом · {h4_sign} · {_house_theme(locale, 4)}"
            if lang == "ru"
            else f"4th house · {h4_sign} · {_house_theme(locale, 4)}"
        )
    return tuple(lines)


def _markers_q4(locale: str, chart: JyotishChart, *, style: str) -> tuple[str, ...]:
    points = _friction_points(locale, chart, style=style)
    markers: list[str] = []
    for key in ("MARS", "SATURN", "RAHU"):
        pl = chart.planets[key]
        if pl.house in (3, 4, 7, 12) or pl.dignity == "debilitated":
            markers.append(_placement_label(locale, pl, style=style))
    for pt in points:
        if len(markers) >= 3:
            break
        markers.append(pt)
    return tuple(markers[:3])


def _practice_for(locale: str, question_index: int, chart: JyotishChart) -> str:
    lang = _lang(locale)
    moon = chart.planets["MOON"]
    lord7 = _lord(chart, 7)

    if question_index == 0:
        if lang == "ru":
            if moon.house in (3, 5):
                return "На неделю: сначала проговаривай, что чувствуешь, — потом жди близости; так твоя Луна успевает довериться."
            return "На неделю: заметь, при каком «приятно и красиво» (Венера) ты открываешься — это твой романтический код."
        return "For one week: notice when Venus conditions feel met — that's your romance code."

    if question_index == 1:
        if lang == "ru":
            return (
                f"Спроси себя: человек типа «{_h7_partner_type(locale, chart.house_signs[7])[:40]}…» "
                f"и обстоятельства {lord7.house}-го дома — это то, куда ты реально идёшь?"
            )
        return "Ask: is the 7th-sign type and lord's house circumstance where you actually go?"

    if question_index == 2:
        if lang == "ru":
            if lord7.house in (6, 8, 12):
                return "Не торопи «штамп» — проверь, выдерживает ли союз быт и кризис; карта про качество, не про запрет."
            return "Обсуди с партнёром (или с собой) правила союза: что для тебя «брак», а что — просто привычка."
        return "Discuss union rules: what is «marriage» for you vs habit?"

    if question_index == 3:
        if lang == "ru":
            return "Создай один ритуал «дома» — еда, звонок близким, уют — и понаблюдай, как меняется настроение Луны."
        return "Create one home ritual and watch how your Moon mood shifts."

    if lang == "ru":
        return "Когда чувствуешь сжатие — назови вслух одну эмоцию до того, как уйдёшь в молчание или вспышку."
    return "When tension rises, name one emotion aloud before silence or a flare-up."


def build_family_structured(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    question: str,
    *,
    style: str = "terms",
) -> FamilyStructuredAnswer:
    idx = max(0, min(4, question_index))
    brief_fns = (_brief_q0, _brief_q1, _brief_q2, _brief_q3, _brief_q4)
    marker_fns = (_markers_q0, _markers_q1, _markers_q2, _markers_q3, _markers_q4)
    return FamilyStructuredAnswer(
        brief=brief_fns[idx](locale, chart, question, style=style),
        markers=marker_fns[idx](locale, chart, style=style),
        practice=_practice_for(locale, idx, chart),
    )
