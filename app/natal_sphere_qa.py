"""Natal chart Q&A by life sphere (house)."""
from __future__ import annotations

from dataclasses import dataclass

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement, build_jyotish_chart
from app.jyotish_text import (
    _house_theme,
    _lang,
    _pl,
    _render_planet,
    _use_terms,
)

HOUSE_BUTTON = {
    "ru": {
        1: "👤 Я",
        2: "💰 Ресурсы",
        3: "🚀 Действия",
        4: "🏠 Дом",
        5: "🎨 Творчество",
        6: "💪 Труд",
        7: "💞 Пара",
        8: "🔄 Перемены",
        9: "📚 Смысл",
        10: "🎯 Карьера",
        11: "🌟 Цели",
        12: "🌙 Глубина",
    },
    "en": {
        1: "👤 Self",
        2: "💰 Resources",
        3: "🚀 Action",
        4: "🏠 Home",
        5: "🎨 Creativity",
        6: "💪 Work",
        7: "💞 Love",
        8: "🔄 Change",
        9: "📚 Meaning",
        10: "🎯 Career",
        11: "🌟 Goals",
        12: "🌙 Depth",
    },
}


@dataclass(frozen=True)
class PopularBlock:
    id: str
    number: str
    emoji: str
    title: str
    hint: str
    question: str


POPULAR_BLOCKS: dict[str, tuple[PopularBlock, ...]] = {
    "ru": (
        PopularBlock(
            "theme", "1", "🌟", "Тема карты",
            "Лагна, стеллиум и главный сюжет жизни.",
            "Какая главная тема моей карты?",
        ),
        PopularBlock(
            "strength", "2", "💪", "Сильные стороны",
            "Где карта даёт опору и природный талант.",
            "Мои сильные стороны?",
        ),
        PopularBlock(
            "love", "3", "💞", "Отношения",
            "Венера, Луна и сфера партнёрства.",
            "Как складываются отношения?",
        ),
        PopularBlock(
            "career", "4", "🎯", "Карьера",
            "10-й дом, Солнце и путь реализации.",
            "Куда вести карьеру?",
        ),
        PopularBlock(
            "money", "5", "💰", "Деньги",
            "2-й дом, Венера и отношение к ресурсам.",
            "Как обстоят дела с деньгами?",
        ),
    ),
    "en": (
        PopularBlock(
            "theme", "1", "🌟", "Chart theme",
            "Lagna, stellium, and your life's main storyline.",
            "What is the main theme of my chart?",
        ),
        PopularBlock(
            "strength", "2", "💪", "Strengths",
            "Where the chart gives support and natural talent.",
            "What are my strengths?",
        ),
        PopularBlock(
            "love", "3", "💞", "Relationships",
            "Venus, Moon, and the partnership sphere.",
            "How do relationships work for me?",
        ),
        PopularBlock(
            "career", "4", "🎯", "Career",
            "House 10, Sun, and your path of realization.",
            "Where should I take my career?",
        ),
        PopularBlock(
            "money", "5", "💰", "Money",
            "House 2, Venus, and your relationship with resources.",
            "How does money work in my chart?",
        ),
    ),
}

FAMILY_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Как я строю романтические отношения?",
        "Кого я притягиваю и кто мне подходит?",
        "Что карта говорит о браке и союзе?",
        "Как складываются темы семьи и дома?",
        "Где типичные трения в паре и семье?",
    ),
    "en": (
        "How do I build romantic relationships?",
        "Who do I attract and who suits me?",
        "What does the chart say about marriage and union?",
        "How do family and home themes play out?",
        "Where do frictions show up in couple and family life?",
    ),
}

SPHERE_QUESTIONS: dict[str, dict[int, tuple[str, str, str]]] = {
    "ru": {
        1: (
            "Как меня видят при первой встрече?",
            "Где моя естественная сила?",
            "Что важно не подавлять в себе?",
        ),
        2: (
            "Как я отношусь к деньгам и ценностям?",
            "Откуда беру чувство опоры?",
            "Где легко терять или раздавать ресурсы?",
        ),
        3: (
            "Как я действую, когда нужно рискнуть?",
            "Как говорю и заявляю о себе?",
            "Где нужна смелость, а не осторожность?",
        ),
        4: (
            "Что для меня «дом» и безопасность?",
            "Как восстанавливаю силы?",
            "Где искать опору, когда тяжело?",
        ),
        5: (
            "Как выражаю радость и творчество?",
            "Где чувствую себя «собой»?",
            "Что приносит искреннее удовольствие?",
        ),
        6: (
            "Как отношусь к работе и рутине?",
            "Где типичное напряжение и борьба?",
            "Как заботиться о здоровье и теле?",
        ),
        7: (
            "Как я строю близость и партнёрство?",
            "Кого притягиваю и почему?",
            "Где типичные трения в отношениях?",
        ),
        8: (
            "Как переживаю кризисы и перемены?",
            "Что скрыто, но сильно влияет на жизнь?",
            "Где нужна честность с собой?",
        ),
        9: (
            "Во что верю и что даёт смысл?",
            "Как расширяю горизонт?",
            "Где ищу наставничество и закон?",
        ),
        10: (
            "Как реализуюсь и строю статус?",
            "Что хочу оставить после себя?",
            "Где амбиции помогают, а где мешают?",
        ),
        11: (
            "К каким целям иду и с кем?",
            "Где получаю поддержку и выгоду?",
            "Какие мечты реально достижимы?",
        ),
        12: (
            "Как отдыхаю и отпускаю?",
            "Что уходит «в тень»?",
            "Где нужна тишина и уединение?",
        ),
    },
    "en": {
        1: (
            "How do people see me at first meeting?",
            "Where is my natural strength?",
            "What should I not suppress in myself?",
        ),
        2: (
            "How do I relate to money and values?",
            "Where do I find a sense of support?",
            "Where do I easily lose or give away resources?",
        ),
        3: (
            "How do I act when I need to take a risk?",
            "How do I speak up and claim my space?",
            "Where do I need courage, not caution?",
        ),
        4: (
            "What is «home» and safety for me?",
            "How do I restore my energy?",
            "Where should I look for support when it's hard?",
        ),
        5: (
            "How do I express joy and creativity?",
            "Where do I feel most like myself?",
            "What brings genuine pleasure?",
        ),
        6: (
            "How do I handle work and routine?",
            "Where is typical tension and struggle?",
            "How should I care for health and body?",
        ),
        7: (
            "How do I build closeness and partnership?",
            "Who do I attract and why?",
            "Where do frictions usually appear in relationships?",
        ),
        8: (
            "How do I live through crises and change?",
            "What is hidden but strongly shapes my life?",
            "Where do I need honesty with myself?",
        ),
        9: (
            "What do I believe in and what gives meaning?",
            "How do I expand my horizon?",
            "Where do I seek guidance and inner law?",
        ),
        10: (
            "How do I realize myself and build status?",
            "What do I want to leave behind?",
            "Where do ambitions help and where do they hinder?",
        ),
        11: (
            "What goals do I pursue and with whom?",
            "Where do I get support and gain?",
            "Which dreams are realistically reachable?",
        ),
        12: (
            "How do I rest and let go?",
            "What goes into the «shadow»?",
            "Where do I need silence and solitude?",
        ),
    },
}


def popular_blocks(locale: str) -> tuple[PopularBlock, ...]:
    return POPULAR_BLOCKS[_lang(locale)]


def popular_block(locale: str, question_id: str) -> PopularBlock:
    for block in popular_blocks(locale):
        if block.id == question_id:
            return block
    return popular_blocks(locale)[0]


def popular_questions(locale: str) -> list[tuple[str, str]]:
    return [(block.id, block.question) for block in popular_blocks(locale)]


def popular_question_text(locale: str, question_id: str) -> str:
    return popular_block(locale, question_id).question


def popular_button_label(locale: str, question_id: str) -> str:
    block = popular_block(locale, question_id)
    return f"{block.number} {block.emoji} {block.title}"


def format_popular_block(block: PopularBlock) -> str:
    return (
        f"{block.number}️⃣ {block.emoji} {block.title}\n"
        f"{block.hint}\n"
        f"❓ {block.question}"
    )


def family_questions(locale: str) -> tuple[str, str, str, str, str]:
    return FAMILY_QUESTIONS[_lang(locale)]


def family_question_text(locale: str, index: int) -> str:
    questions = family_questions(locale)
    return questions[max(0, min(4, index))]


def family_block_teaser(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            "\n\n💍 Отношение / Брак / Семья\n"
            "Партнёрство, союз и семейный уклад — по 7-му и 4-му домам, Венере и Луне."
        )
    return (
        "\n\n💍 Relationship / Marriage / Family\n"
        "Partnership, union, and family life — houses 7 and 4, Venus and Moon."
    )


def family_picker_intro(locale: str) -> str:
    questions = family_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "💍 Отношение / Брак / Семья\n\n"
            "Партнёрство, брак и семья в твоей карте — "
            "7-й дом (союз), 4-й дом (дом и корни), Венера и Луна.\n"
        )
    else:
        header = (
            "💍 Relationship / Marriage / Family\n\n"
            "Partnership, marriage, and family in your chart — "
            "house 7 (union), house 4 (home and roots), Venus and Moon.\n"
        )
    lines = [
        f"{idx + 1}️⃣ ❓ {question}"
        for idx, question in enumerate(questions)
    ]
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return f"{title}\n\n{header}\n" + "\n\n".join(lines)


def popular_blocks_text(locale: str) -> str:
    blocks = popular_blocks(locale)
    if _lang(locale) == "ru":
        header = "🔥 Популярные вопросы\n\nВыбери вопрос — ответ строится по твоей карте.\n"
    else:
        header = "🔥 Popular questions\n\nPick a question — the answer comes from your chart.\n"
    body = "\n\n".join(format_popular_block(block) for block in blocks)
    return f"{header}\n{body}"


def popular_picker_intro(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            f"❓ Вопросы по натальной карте\n\n"
            f"{popular_blocks_text(locale)}"
            f"{family_block_teaser(locale)}"
        )
    return (
        f"❓ Natal chart questions\n\n"
        f"{popular_blocks_text(locale)}"
        f"{family_block_teaser(locale)}"
    )


def spheres_picker_intro(locale: str) -> str:
    if _lang(locale) == "ru":
        return f"❓ Вопросы по натальной карте\n\n{spheres_page_intro(locale)}"
    return f"❓ Natal chart questions\n\n{spheres_page_intro(locale)}"


def spheres_page_intro(locale: str) -> str:
    if _lang(locale) == "ru":
        return "📂 По сферам\n\nВыбери жизненную область:"
    return "📂 By life area\n\nPick a sphere:"


def house_button_label(locale: str, house: int) -> str:
    lang = _lang(locale)
    return HOUSE_BUTTON[lang].get(house, str(house))


def sphere_questions(locale: str, house: int) -> tuple[str, str, str]:
    lang = _lang(locale)
    return SPHERE_QUESTIONS[lang][house]


def question_button_label(question: str, *, max_len: int = 42) -> str:
    if len(question) <= max_len:
        return question
    return question[: max_len - 1].rstrip() + "…"


def build_chart_from_profile(profile) -> JyotishChart | None:
    if profile is None or profile.birth_date is None or profile.birth_time is None:
        return None
    city = profile.city or "-"
    if not city or city.strip() in {"-", ""}:
        return None
    return build_jyotish_chart(
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        city=city,
        timezone_name=profile.timezone or "UTC",
        locale=profile.language or "ru",
        lat=profile.birth_lat,
        lon=profile.birth_lon,
        birth_timezone=profile.birth_timezone,
    )


def _planets_in_house(chart: JyotishChart, house: int) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")
    return [chart.planets[key] for key in order if chart.planets[key].house == house]


def _lord_placement(chart: JyotishChart, house: int) -> PlanetPlacement:
    return chart.planets[chart.house_lords[house]]


def _sphere_label(locale: str, house: int, *, style: str) -> str:
    theme = _house_theme(locale, house)
    lang = _lang(locale)
    if _use_terms(style):
        if lang == "ru":
            return f"{house}-й дом — «{theme}»"
        return f"House {house} — {theme}"
    if lang == "ru":
        return f"«{theme}»"
    return theme.capitalize()


def _empty_house_answer(
    chart: JyotishChart,
    locale: str,
    house: int,
    *,
    style: str,
    focus: str,
) -> str:
    lang = _lang(locale)
    lord = _lord_placement(chart, house)
    lord_name = _pl(locale, lord.key)
    lord_sign = sign_label(locale, lord.sign)
    lord_theme = _house_theme(locale, lord.house)
    if lang == "ru":
        if _use_terms(style):
            lead = (
                f"В {house}-м доме («{_house_theme(locale, house)}») нет планет — "
                f"сфера звучит тише и идёт через управителя {lord_name} "
                f"в {lord.house}-м доме ({lord_theme})."
            )
        else:
            lead = (
                f"В сфере «{_house_theme(locale, house)}» нет ярких планет — "
                f"тема проявляется через {lord_name} в «{lord_theme}»."
            )
        focus_bits = {
            "strength": f"{lord_name} в {lord_sign} даёт опору: здесь проявляется сила этой темы.",
            "challenge": f"Следи за перекосом через {lord_name} в {lord_sign} — там же и типичное напряжение.",
            "default": f"Ключ — {lord_name} в {lord_sign}: через него эта сфера «оживает» в карте.",
        }
    else:
        if _use_terms(style):
            lead = (
                f"House {house} ({_house_theme(locale, house)}) has no planets — "
                f"the theme runs through lord {lord_name} in house {lord.house} ({lord_theme})."
            )
        else:
            lead = (
                f"The arena of {_house_theme(locale, house)} has no bright planets — "
                f"the theme runs through {lord_name} in {lord_theme}."
            )
        focus_bits = {
            "strength": f"{lord_name} in {lord_sign} is your anchor here.",
            "challenge": f"Watch distortions through {lord_name} in {lord_sign} — tension often starts there.",
            "default": f"The key is {lord_name} in {lord_sign}: this sphere lives through that placement.",
        }
    return f"{lead} {focus_bits.get(focus, focus_bits['default'])}"


def _house1_lagna_note(chart: JyotishChart, locale: str, *, style: str) -> str:
    lang = _lang(locale)
    lagna = sign_label(locale, chart.lagna_sign)
    if lang == "ru":
        if _use_terms(style):
            return f"Лагна в {lagna} — твой базовый образ входа в жизнь."
        return f"Вход в жизнь через {lagna} — так тебя читают с первого контакта."
    if _use_terms(style):
        return f"Lagna in {lagna} is your baseline way of entering life."
    return f"Rising through {lagna} is how people read you at first contact."


def build_sphere_answer(
    chart: JyotishChart,
    locale: str,
    house: int,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    questions = sphere_questions(locale, house)
    question = questions[max(0, min(2, question_index))]
    planets = _planets_in_house(chart, house)
    focus = ("default", "strength", "challenge")[max(0, min(2, question_index))]

    if not planets:
        body = _empty_house_answer(chart, locale, house, style=style, focus=focus)
    else:
        bits = [_render_planet(locale, pl, style=style) for pl in planets[:3]]
        joined = " ".join(bits)
        if lang == "ru":
            if focus == "strength":
                tail = "Здесь же и твоя опора — опирайся на эту энергию сознательно."
            elif focus == "challenge":
                tail = "Именно здесь чаще всплывают трения — замечай паттерн, не борись с собой вслепую."
            else:
                tail = "Это главный тон сферы в твоей карте."
        else:
            if focus == "strength":
                tail = "This is also your anchor — lean on this energy consciously."
            elif focus == "challenge":
                tail = "Friction often shows up here — notice the pattern instead of fighting blindly."
            else:
                tail = "This is the main tone of this sphere in your chart."
        body = f"{joined} {tail}"

    if house == 1 and question_index == 0:
        body = f"{_house1_lagna_note(chart, locale, style=style)} {body}"

    sphere = _sphere_label(locale, house, style=style)
    if lang == "ru":
        header = f"Сфера: {sphere}"
    else:
        header = f"Sphere: {sphere}"
    return f"{header}\n\n❓ {question}\n\n{body}"


def build_family_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = family_question_text(locale, question_index)
    venus = chart.planets["VENUS"]
    moon = chart.planets["MOON"]
    jupiter = chart.planets["JUPITER"]
    h7_planets = _planets_in_house(chart, 7)
    h4_planets = _planets_in_house(chart, 4)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h7_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 7), style=style)]
        if lang == "ru":
            intro = (
                "Романтика и притяжение — 7-й дом, Венера и Луна. "
                if _use_terms(style)
                else "Романтика и притяжение — сфера партнёрства, Венера и Луна. "
            )
        else:
            intro = (
                "Romance and attraction — house 7, Venus, and Moon. "
                if _use_terms(style)
                else "Romance and attraction — partnership, Venus, and Moon. "
            )
        body = (
            f"{intro}{_render_planet(locale, venus, style=style)} "
            f"{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 1:
        h7_sign = sign_label(locale, chart.house_signs[7])
        lord7 = _lord_placement(chart, 7)
        bits = [
            _render_planet(locale, venus, style=style),
            _render_planet(locale, lord7, style=style),
        ]
        if h7_planets:
            bits.append(_render_planet(locale, h7_planets[0], style=style))
        if lang == "ru":
            if _use_terms(style):
                intro = (
                    f"Притяжение и тип партнёра — знак 7-го дома ({h7_sign}), "
                    "Венера и управитель смотрят, кого ты выбираешь и кто выбирает тебя. "
                )
            else:
                intro = (
                    f"Притяжение и тип партнёра — тема «{_house_theme(locale, 7)}» "
                    f"({h7_sign}), Венера и ключевой показатель партнёрства. "
                )
        elif _use_terms(style):
            intro = (
                f"Attraction and partner type — 7th-house sign ({h7_sign}), "
                "Venus, and the house lord show who you choose and who chooses you. "
            )
        else:
            intro = (
                f"Attraction and partner type — {_house_theme(locale, 7)} "
                f"({h7_sign}), Venus, and the partnership key. "
            )
        body = f"{intro}{' '.join(bits)}".strip()

    elif question_index == 2:
        lord7 = _lord_placement(chart, 7)
        bits = [_render_planet(locale, lord7, style=style)]
        if h7_planets:
            bits.append(_render_planet(locale, h7_planets[0], style=style))
        if lang == "ru":
            intro = (
                "Брак и долгий союз смотрят на 7-й дом, его управителя и Юпитер как показатель зрелости союза. "
                if _use_terms(style)
                else "Брак и долгий союз — партнёрство, его «хозяина» в карте и Юпитер как зрелость союза. "
            )
            jup_line = _render_planet(locale, jupiter, style=style)
        else:
            intro = (
                "Marriage and lasting union — house 7, its lord, and Jupiter as maturity of partnership. "
                if _use_terms(style)
                else "Marriage and lasting union — partnership, its chart ruler, and Jupiter. "
            )
            jup_line = _render_planet(locale, jupiter, style=style)
        body = f"{intro}{' '.join(bits)} {jup_line}".strip()

    elif question_index == 3:
        bits = [_render_planet(locale, pl, style=style) for pl in h4_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 4), style=style)]
        if lang == "ru":
            intro = (
                "Семья и дом — 4-й дом и Луна как внутреннее чувство «своих». "
                if _use_terms(style)
                else "Семья и дом — сфера корней и Луна как чувство «своих». "
            )
        else:
            intro = (
                "Family and home — house 4 and the Moon as inner belonging. "
                if _use_terms(style)
                else "Family and home — roots and the Moon as belonging. "
            )
        body = (
            f"{intro}{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    else:
        mars = chart.planets["MARS"]
        saturn = chart.planets["SATURN"]
        bits: list[str] = []
        seen: set[str] = set()
        for pl in (*h7_planets, mars, saturn, chart.planets["RAHU"]):
            if pl.key in {"MARS", "SATURN", "RAHU"} and pl.key not in seen:
                seen.add(pl.key)
                bits.append(_render_planet(locale, pl, style=style))
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 7), style=style)]
        if lang == "ru":
            intro = (
                "Трения в паре и семье часто идут через Марс, Сатурн, Раху и напряжённые положения в 4-м и 7-м домах. "
                if _use_terms(style)
                else "Трения в паре и семье часто связаны с резкостью, границами и сложными темами партнёрства и дома. "
            )
            tail = " Замечай, где реагируешь резко или закрываешься — это точки роста, а не приговор."
        else:
            intro = (
                "Couple and family friction often runs through Mars, Saturn, Rahu, and tense 4th/7th-house themes. "
                if _use_terms(style)
                else "Friction often ties to sharp reactions, boundaries, and loaded partnership or home themes. "
            )
            tail = " Notice where you react sharply or shut down — growth points, not a verdict."
        body = f"{intro}{' '.join(bits[:3])}{tail}".strip()

    if lang == "ru":
        header = "💍 Отношение / Брак / Семья"
    else:
        header = "💍 Relationship / Marriage / Family"
    return f"{header}\n\n❓ {question}\n\n{body}"


def build_popular_answer(
    chart: JyotishChart,
    locale: str,
    question_id: str,
    *,
    style: str = "terms",
) -> str:
    from app.jyotish_text import LAGNA_ESSENCE, _derive_summary, _list_to_prose

    lang = _lang(locale)
    question = popular_question_text(locale, question_id)
    strengths, weaknesses, risks, opportunities = _derive_summary(chart, lang)

    if question_id == "theme":
        lagna = sign_label(locale, chart.lagna_sign)
        if lang == "ru":
            if _use_terms(style):
                lead = f"Лагна в {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            else:
                lead = f"Вход в жизнь через {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            if chart.stellium_house and chart.stellium_sign:
                st_sign = sign_label(locale, chart.stellium_sign)
                theme = _house_theme(locale, chart.stellium_house)
                if _use_terms(style):
                    body = (
                        f"{lead} Главный сюжет — стеллиум в {st_sign} "
                        f"в {chart.stellium_house}-м доме («{theme}»): эта тема судьбоносна."
                    )
                else:
                    body = (
                        f"{lead} Главный сюжет — несколько планет в {st_sign} "
                        f"в сфере «{theme}»: эта область жизни для тебя ключевая."
                    )
            elif chart.strong_houses:
                h = chart.strong_houses[0]
                theme = _house_theme(locale, h)
                cnt = chart.house_planet_count[h]
                if _use_terms(style):
                    body = (
                        f"{lead} Ярче всего звучит {h}-й дом («{theme}») — "
                        f"{cnt} планет(ы) собирают вокруг себя главный сюжет."
                    )
                else:
                    body = (
                        f"{lead} Ярче всего звучит сфера «{theme}» — "
                        f"{cnt} планет(ы) задают главный жизненный сюжет."
                    )
            else:
                body = lead
        else:
            if _use_terms(style):
                lead = f"Lagna in {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            else:
                lead = f"Rising through {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            if chart.stellium_house and chart.stellium_sign:
                st_sign = sign_label(locale, chart.stellium_sign)
                theme = _house_theme(locale, chart.stellium_house)
                body = (
                    f"{lead} The main storyline is a stellium in {st_sign} "
                    f"in the arena of {theme}."
                )
            elif chart.strong_houses:
                h = chart.strong_houses[0]
                theme = _house_theme(locale, h)
                body = (
                    f"{lead} House {h} ({theme}) stands out most — "
                    f"{chart.house_planet_count[h]} planet(s) set the main plot."
                )
            else:
                body = lead

    elif question_id == "strength":
        if lang == "ru":
            body = f"Сильные стороны — {_list_to_prose(strengths, lang)}."
            if chart.planets["SUN"].dignity == "exalted":
                body += " Солнце в силе даёт уверенный стержень и ощущение своего курса."
        else:
            body = f"Strengths — {_list_to_prose(strengths, lang)}."
            if chart.planets["SUN"].dignity == "exalted":
                body += " Exalted Sun adds a confident core and sense of direction."

    elif question_id == "weak":
        if lang == "ru":
            body = (
                f"Сложнее проявляются {_list_to_prose(weaknesses, lang)}. "
                f"Главный риск — {risks}."
            )
        else:
            body = (
                f"Growth edges — {_list_to_prose(weaknesses, lang)}. "
                f"Main risk — {risks}."
            )

    elif question_id == "love":
        venus = chart.planets["VENUS"]
        moon = chart.planets["MOON"]
        h7 = _planets_in_house(chart, 7)
        bits = [_render_planet(locale, pl, style=style) for pl in h7[:2]]
        if not bits:
            lord = _lord_placement(chart, 7)
            bits = [_render_planet(locale, lord, style=style)]
        if lang == "ru":
            intro = "В отношениях смотри на 7-й дом, Венеру и Луну. "
            if not _use_terms(style):
                intro = "В отношениях смотри на сферу партнёрства, Венеру и Луну. "
            body = (
                f"{intro}{_render_planet(locale, venus, style=style)} "
                f"{_render_planet(locale, moon, style=style)} "
                f"{' '.join(bits)}"
            ).strip()
        else:
            intro = "For relationships, read house 7, Venus, and Moon. "
            if not _use_terms(style):
                intro = "For relationships, read partnership, Venus, and Moon. "
            body = (
                f"{intro}{_render_planet(locale, venus, style=style)} "
                f"{_render_planet(locale, moon, style=style)} "
                f"{' '.join(bits)}"
            ).strip()

    elif question_id == "career":
        h10 = _planets_in_house(chart, 10)
        sun = chart.planets["SUN"]
        saturn = chart.planets["SATURN"]
        bits = [_render_planet(locale, pl, style=style) for pl in h10[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 10), style=style)]
        if lang == "ru":
            intro = "Карьера и реализация — 10-й дом, Солнце и Сатурн. "
            if not _use_terms(style):
                intro = "Карьера и реализация — сфера статуса, Солнце и Сатурн. "
            body = (
                f"{intro}{_render_planet(locale, sun, style=style)} "
                f"{_render_planet(locale, saturn, style=style)} "
                f"{' '.join(bits)}"
            ).strip()
            if chart.house_planet_count.get(10, 0) >= 2:
                body += " 10-й дом насыщен — профессиональная линия для тебя судьбоносна."
        else:
            intro = "Career runs through house 10, Sun, and Saturn. "
            if not _use_terms(style):
                intro = "Career runs through status, Sun, and Saturn. "
            body = (
                f"{intro}{_render_planet(locale, sun, style=style)} "
                f"{_render_planet(locale, saturn, style=style)} "
                f"{' '.join(bits)}"
            ).strip()

    elif question_id == "money":
        h2 = _planets_in_house(chart, 2)
        venus = chart.planets["VENUS"]
        jupiter = chart.planets["JUPITER"]
        bits = [_render_planet(locale, pl, style=style) for pl in h2[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 2), style=style)]
        if lang == "ru":
            intro = "Деньги и ценности — 2-й дом, Венера и Юпитер. "
            if not _use_terms(style):
                intro = "Деньги и ценности — сфера ресурсов, Венера и Юпитер. "
            body = (
                f"{intro}{_render_planet(locale, venus, style=style)} "
                f"{_render_planet(locale, jupiter, style=style)} "
                f"{' '.join(bits)}"
            ).strip()
        else:
            intro = "Money and values — house 2, Venus, and Jupiter. "
            if not _use_terms(style):
                intro = "Money and values — resources, Venus, and Jupiter. "
            body = (
                f"{intro}{_render_planet(locale, venus, style=style)} "
                f"{_render_planet(locale, jupiter, style=style)} "
                f"{' '.join(bits)}"
            ).strip()

    else:
        if lang == "ru":
            body = f"Главная возможность — {opportunities}."
        else:
            body = f"Main opportunity — {opportunities}."

    block = popular_block(locale, question_id)
    header = f"🔥 {block.emoji} {block.title}"
    return f"{header}\n\n❓ {question}\n\n{body}"


def questions_intro(locale: str, house: int, *, style: str) -> str:
    sphere = _sphere_label(locale, house, style=style)
    if _lang(locale) == "ru":
        return f"Сфера: {sphere}\n\nВыбери вопрос:"
    return f"Sphere: {sphere}\n\nPick a question:"
