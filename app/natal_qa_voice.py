"""Plain-language voice for natal chart Q&A — Joyti-style narrative, no jargon."""
from __future__ import annotations

import re
from html import unescape

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import _house_theme, _lang
from app.text_format import b, h, p, sentence_paragraphs

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")

_PLAIN_ROLE = {
    "ru": {
        "SUN": "твоя суть",
        "MOON": "твои эмоции",
        "MERCURY": "мышление и речь",
        "VENUS": "твоя нежность и вкус",
        "MARS": "твой напор",
        "JUPITER": "твоя надежда и рост",
        "SATURN": "твои границы",
        "RAHU": "тяга к новому",
        "KETU": "умение отпускать",
    },
    "en": {
        "SUN": "your core",
        "MOON": "your feelings",
        "MERCURY": "thinking and speech",
        "VENUS": "your warmth and taste",
        "MARS": "your drive",
        "JUPITER": "your hope and growth",
        "SATURN": "your boundaries",
        "RAHU": "craving for the new",
        "KETU": "letting go",
    },
}

_PLAIN_AREA = {
    "ru": {
        1: "как ты себя показываешь",
        2: "деньги и ценности",
        3: "разговоры и будни",
        4: "дом и близкие",
        5: "радость и романтика",
        6: "работа и быт",
        7: "партнёр и пара",
        8: "кризисы и общие деньги",
        9: "смысл и путешествия",
        10: "работа и статус",
        11: "друзья и цели",
        12: "отдых и уединение",
    },
    "en": {
        1: "how you show up",
        2: "money and values",
        3: "talk and daily life",
        4: "home and close ones",
        5: "joy and romance",
        6: "work and routine",
        7: "partner and couple",
        8: "crisis and shared money",
        9: "meaning and travel",
        10: "work and status",
        11: "friends and goals",
        12: "rest and solitude",
    },
}

_HUMANIZE_RU = (
    (r"\bуправител\w*\s+\d+-?\s*(?:го|й)\b", "ключ к теме"),
    (r"\b\d+-?\s*(?:й|й)\s+дом\b", "эта сфера"),
    (r"\b\d+-?\s*(?:th|st|nd|rd)\s+house\b", "this area"),
    (r"\bЛагн\w*\b", "как тебя видят"),
    (r"\bЛун\w*\b", "эмоции"),
    (r"\bВенер\w*\b", "нежность"),
    (r"\bСолнц\w*\b", "суть"),
    (r"\bМарс\w*\b", "напор"),
    (r"\bМеркури\w*\b", "мышление"),
    (r"\bЮпитер\w*\b", "рост"),
    (r"\bСатурн\w*\b", "границы"),
    (r"\bРах\w*\b", "амбиции"),
    (r"\bКет\w*\b", "отпускание"),
    (r"\bкарм\w*\b", "урок"),
    (r"\bнакшатр\w*\b", ""),
    (r"\bдхарм\w*\b", "смысл"),
    (r"\bупай\w*\b", "практика"),
    (r"в знаке силы", "очень сильно"),
    (r"в слабом положении", "нужна бережность"),
    (r"в своём знаке", "устойчиво"),
    (r"  +", " "),
)

_HUMANIZE_EN = (
    (r"\b\d+(?:st|nd|rd|th)\s+house\b", "this area"),
    (r"\bhouse\s+\d+\b", "this area"),
    (r"\blord of house\b", "key to"),
    (r"\bLagna\b", "first impression"),
    (r"\bMoon\b", "feelings"),
    (r"\bVenus\b", "warmth"),
    (r"\bSun\b", "core"),
    (r"\bMars\b", "drive"),
    (r"\bMercury\b", "thinking"),
    (r"\bJupiter\b", "growth"),
    (r"\bSaturn\b", "boundaries"),
    (r"\bRahu\b", "ambition"),
    (r"\bKetu\b", "release"),
    (r"\bkarm\w*\b", "lesson"),
    (r"\bnakshatr\w*\b", ""),
    (r"exalted", "very strong"),
    (r"debilitated", "needs care"),
    (r"  +", " "),
)


def plain_role(locale: str, planet_key: str) -> str:
    return _PLAIN_ROLE[_lang(locale)].get(planet_key, planet_key.lower())


def plain_area(locale: str, house: int) -> str:
    lang = _lang(locale)
    return _PLAIN_AREA[lang].get(house, _house_theme(locale, house).lower())


def plain_placement_line(locale: str, pl: PlanetPlacement, *, hint: str = "") -> str:
    lang = _lang(locale)
    sign = sign_label(locale, pl.sign)
    role = plain_role(locale, pl.key)
    area = plain_area(locale, pl.house)
    dig = ""
    if pl.dignity == "exalted":
        dig = " — тут сильная опора" if lang == "ru" else " — strong anchor here"
    elif pl.dignity == "own":
        dig = " — устойчиво" if lang == "ru" else " — steady"
    elif pl.dignity == "debilitated":
        dig = " — нужна бережность, не давить на себя" if lang == "ru" else " — needs care, don't force it"
    if lang == "ru":
        line = f"{role.capitalize()} ({sign}) — про {area}{dig}."
    else:
        line = f"{role.capitalize()} ({sign}) — about {area}{dig}."
    if hint:
        line = f"{line} {hint}"
    return line


def plain_lord_line(locale: str, chart: JyotishChart, from_house: int) -> str:
    lang = _lang(locale)
    lord_key = chart.house_lords[from_house]
    lord = chart.planets[lord_key]
    source = plain_area(locale, from_house)
    target = plain_area(locale, lord.house)
    sign = sign_label(locale, lord.sign)
    role = plain_role(locale, lord.key)
    if lord.house == from_house:
        if lang == "ru":
            return f"Тема «{source}» у тебя звучит громко — {role} ({sign}) держит её в центре."
        return f"«{source}» is loud for you — {role} ({sign}) keeps it front and center."
    if lang == "ru":
        return f"Тема «{source}» идёт через {target} — обрати внимание на {role} ({sign})."
    return f"«{source}» runs through {target} — watch {role} ({sign})."


def strip_telegram_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"</?(?:b|i|u|code|pre)>", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return unescape(cleaned).strip()


def life_manifestation_echo(locale: str, question: str, *, style: str = "terms") -> str:
    """One sentence linking chart themes to everyday life."""
    from app.jyotish_text import _use_terms
    from app.natal_qa_synthesis import _classify_question

    lang = _lang(locale)
    intent = _classify_question(question, lang)
    plain = not _use_terms(style)
    if lang == "ru":
        table = {
            "money": (
                "В быту это часто видно в привычных тратах и решениях «стоит / не стоит» — не в разовой удаче "
                "и не в «я нашёл криптовалюту в подвале»."
                if plain
                else "В повседневности смотри на повторяющиеся финансовые решения: что покупаешь, на что копишь, от чего отказываешься."
            ),
            "career": (
                "На работе это проявляется в том, где ты оживаешь, а где тихо выгораешь — не только в должности."
                if plain
                else "На практике отслеживай рабочие циклы: где растёшь, где тормозишь, где берёшь ответственность без выгорания."
            ),
            "health": (
                "С телом это обычно про режим, сон и нагрузку — не про «закалку характера» и не про "
                "«просто соберись, ты же взрослый». Организм не читает мотивационные посты."
                if plain
                else "С телом связка проявляется через режим, сон, питание и реакцию на стресс — смотри повторяющиеся сбои."
            ),
            "how_relationship": (
                "В паре это слышно в бытовых сценариях: как миритесь, как просите о близости, как молчите "
                "и кто первый делает вид, что «ничего не случилось»."
                if plain
                else "В отношениях ищи повторяющиеся сценарии: сближение, дистанция, споры, примирение — там живёт карта."
            ),
            "who_partner": (
                "Обрати внимание, кого ты реально выбираешь — не только кого «хочешь по списку»."
                if plain
                else "Сравни идеальный тип с реальными партнёрами из прошлого — карта часто повторяет один мотив."
            ),
            "challenge": (
                "Затык обычно не в одном дне, а в привычке, которая возвращается снова и снова."
                if plain
                else "Узел чаще в повторяющемся паттерне реакции, а не в одном событии — заметь, что возвращается."
            ),
            "when": (
                "Сроки в карте — про внутреннюю готовность, а не про дату в календаре."
                if plain
                else "Время приходит, когда тема перестаёт быть фоном и требует решения — смотри на внутренний «да, готов»."
            ),
            "why": (
                "«Почему» обычно раскрывается через повторяющиеся чувства, а не через одну фразу из гороскопа."
                if plain
                else "Причина чаще в связке эмоций, ценностей и привычек — не в одном изолированном факторе."
            ),
            "purpose": (
                "Предназначение здесь — не одна профессия, а направление, куда снова тянет, даже после пауз."
                if plain
                else "Предназначение проявляется в темах, куда возвращаешься годами — даже если меняешь форму работы."
            ),
            "strength": (
                "Сила работает, когда ты её сознательно используешь — иначе она просто «есть в фоне»."
                if plain
                else "Опора усиливается, когда опираешься на неё в реальных задачах, а не только узнаёшь себя в тексте."
            ),
            "general": (
                "Смотри, где в жизни это повторяется — там ответ перестаёт быть «умной фразой из интернета» "
                "и становится узнаваемым сценарием."
                if plain
                else "Проверяй тему на повторяющихся жизненных ситуациях — так карта становится опытом, а не теорией."
            ),
        }
        return table.get(intent, table["general"])
    table = {
        "money": (
            "In daily life this shows in spending habits and «worth it / not worth it» calls — not one lucky break."
            if plain
            else "Track repeating money choices: what you buy, save for, and refuse — that's the live pattern."
        ),
        "career": (
            "At work it shows where you come alive vs quietly burn out — not just your job title."
            if plain
            else "Watch work cycles: where you grow, stall, or take responsibility without burning out."
        ),
        "health": (
            "With the body it's usually routine, sleep, and load — not willpower stunts."
            if plain
            else "Body themes show through routine, sleep, food, and stress response — note what repeats."
        ),
        "how_relationship": (
            "In pairs it sounds like daily scripts: making up, asking for closeness, going silent."
            if plain
            else "In relationships look for repeating scripts: closeness, distance, fights, repair."
        ),
        "who_partner": (
            "Notice who you actually choose — not only who you «want on paper»."
            if plain
            else "Compare the ideal type with real past partners — the chart often repeats one motif."
        ),
        "challenge": (
            "The block is usually a habit that returns — not a single bad day."
            if plain
            else "The knot is often a repeating reaction pattern, not one isolated event."
        ),
        "when": (
            "Timing in the chart is about inner readiness, not a calendar date."
            if plain
            else "Time arrives when the theme stops being background and asks for a decision."
        ),
        "why": (
            "«Why» usually unfolds through repeating feelings, not one horoscope line."
            if plain
            else "Causes often sit in emotions, values, and habits — not one isolated factor."
        ),
        "purpose": (
            "Purpose here isn't one job title — it's a direction you return to after pauses."
            if plain
            else "Purpose shows in themes you return to for years — even if the work form changes."
        ),
        "strength": (
            "Strength works when you use it on purpose — otherwise it stays background noise."
            if plain
            else "Anchors grow when you lean on them in real tasks, not only recognize them in text."
        ),
        "general": (
            "Watch where this repeats in life — that's where the answer stops being abstract."
            if plain
            else "Test the theme on repeating life situations — then the chart becomes experience."
        ),
    }
    return table.get(intent, table["general"])


def plain_disclaimer(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            "Важно помнить: карта показывает потенциал, а не приговор. "
            "Итог зависит от твоего выбора, зрелости и того, как ты ведёшь себя в жизни."
        )
    return (
        "Remember: the chart shows potential, not a verdict. "
        "The outcome depends on your choices, maturity, and how you act."
    )


def _marker_to_prose(locale: str, line: str) -> str:
    text = humanize_natal_plain(strip_telegram_html(line), locale)
    text = text.lstrip("•·- ").strip()
    if not text:
        return ""
    if text[0].islower():
        text = text[0].upper() + text[1:]
    if not text.endswith((".", "!", "?", "…")):
        text += "."
    return text


def _plain_detail_intro(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            "Разложу спокойно и без зауми — как разговор с подругой, "
            "которая в теме, но не мучает лекцией на три часа:"
        )
    return (
        "I'll unpack this without jargon — like a friend who knows astrology "
        "but won't lecture you for three hours:"
    )


def _plain_eli5_bridge(locale: str, first_sentence: str) -> str:
    """Restate the main point in even simpler words."""
    lang = _lang(locale)
    core = first_sentence.strip().rstrip(".")
    if not core:
        return ""
    if lang == "ru":
        core_lower = core.lower()
        if "отвечаю на" in core_lower and "простыми словами" in core_lower:
            return (
                "Если на совсем человеческом: без астрословаря и ребусов — "
                "просто что у тебя работает в жизни, а где обычно спотыкаешься. "
                "Версия «для нормальных людей», не для кафедры."
            )
        if "начну с главного" in core_lower or "разберём" in core_lower:
            return (
                "Если коротко и по делу: это про твои реальные привычки и выборы в жизни, "
                "а не про красивую теорию «где-то в космосе». "
                "Формат: ясно, по-человечески, без астробюрократии."
            )
        return (
            f"Если совсем на пальцах: {core[0].lower()}{core[1:] if len(core) > 1 else ''}. "
            "Без звёзд, домов и словаря — просто про тебя и твою жизнь."
        )
    core_lower = core.lower()
    if "clear words" in core_lower or "no astro dictionary" in core_lower:
        return (
            "In plain human language: no astro maze, no weird terms — "
            "just what actually plays out in your real life."
        )
    if "main point first" in core_lower:
        return (
            "Short version: this is about your real patterns and choices, "
            "not abstract cosmic poetry."
        )
    lower = core[0].lower() + core[1:] if core else core
    return (
        f"In the simplest words: {lower}. "
        "No houses, no dictionary — just you and your life."
    )


def _plain_life_example(locale: str, intent: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        examples = {
            "money": (
                "Пример: ты «экономишь» на себе, но спокойно тратишь на то, что поднимает настроение — "
                "и потом удивляешься, куда ушла зарплата. Карта не про вину, а про паттерн."
            ),
            "career": (
                "Пример: на одной работе ты оживаешь, на другой — как после понедельника без кофе. "
                "Должность важна, но не решает всё."
            ),
            "health": (
                "Пример: «ещё один сезон без сна — потом отсыплюсь». Организм так не договаривался. "
                "Карта часто подсвечивает именно такие «ну ладно, потерплю»."
            ),
            "how_relationship": (
                "Пример: ссора из-за тарелки в раковине — а на самом деле про «ты меня слышишь?». "
                "Быт — это часто переводчик больших тем."
            ),
            "who_partner": (
                "Пример: в голове — «хочу спокойного и надёжного», а рука тянется к яркому и сложному. "
                "Карта любит честность, не список желаний из Pinterest."
            ),
            "challenge": (
                "Пример: ты обещаешь себе «с понедельника по-другому» — и снова ловишь старую реакцию. "
                "Не потому что ты плохой, а потому что привычка сильнее обещания."
            ),
            "when": (
                "Пример: «когда созрею» часто наступает не в календарь, а когда терпеть уже невыносно. "
                "Карта про внутренний «хватит», а не про дату в приложении."
            ),
            "why": (
                "Пример: «почему опять я?» — потому что знакомый сценарий включается быстрее, "
                "чем новый ответ. Карта показывает кнопку, не приговор."
            ),
            "purpose": (
                "Пример: ты бросаешь тему, возвращаешься через год — и снова. "
                "Это не «не можешь определиться», это магнит, который не отпускает."
            ),
            "strength": (
                "Пример: друзья просят совета именно в этом — а ты думаешь «да ладно, мелочь». "
                "Сильная сторона часто кажется обыденной, пока не начнёшь её использовать."
            ),
            "general": (
                "Пример: читаешь текст и ловишь «блин, это же про меня вчера». "
                "Вот в такие моменты карта перестаёт быть абстракцией."
            ),
        }
        return examples.get(intent, examples["general"])
    examples = {
        "money": (
            "Example: you «save» on yourself but spend easily on mood boosts — then wonder where the paycheck went."
        ),
        "career": (
            "Example: one job makes you come alive, another feels like Monday without coffee."
        ),
        "health": (
            "Example: «one more season without sleep, I'll catch up later». The body didn't agree to that deal."
        ),
        "how_relationship": (
            "Example: a fight about a plate in the sink is often really «do you hear me?»."
        ),
        "who_partner": (
            "Example: on paper you want calm and steady, but you reach for bright and complicated."
        ),
        "challenge": (
            "Example: «from Monday I'll be different» — and the old reaction shows up again. Habit beats promise."
        ),
        "when": (
            "Example: «when I'm ready» often means when you can't tolerate the old way anymore."
        ),
        "why": (
            "Example: «why me again?» — because the familiar script boots faster than a new response."
        ),
        "purpose": (
            "Example: you drop a theme, return a year later — and again. That's a magnet, not indecision."
        ),
        "strength": (
            "Example: friends ask you for this exact thing — you think «it's nothing special»."
        ),
        "general": (
            "Example: you read this and go «wait, that was me yesterday». That's when the chart stops being abstract."
        ),
    }
    return examples.get(intent, examples["general"])


def _build_summary(locale: str, sentences: list[str], markers: tuple[str, ...]) -> str:
    lang = _lang(locale)
    if len(sentences) >= 2:
        return sentences[-1] if len(sentences[-1]) < 220 else sentences[0]
    if markers:
        first = _marker_to_prose(locale, markers[0])
        if first:
            return first
    if lang == "ru":
        return "Картина индивидуальная — смотри, откликается ли тебе описание."
    return "The picture is individual — see if it resonates."


def compose_plain_qa_answer(
    locale: str,
    core_html: str,
    markers: tuple[str, ...] = (),
    practice: str = "",
    question: str = "",
) -> str:
    """Flowing plain answer: hook → story → ELI5 → chart lines → life → punchline → tip."""
    from app.natal_qa_synthesis import _classify_question

    lang = _lang(locale)
    intent = _classify_question(question, lang) if question.strip() else "general"
    core = sanitize_plain_qa_text(strip_telegram_html(core_html), locale)
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(core) if s.strip()]

    blocks: list[str] = []

    if sentences:
        blocks.append(b("Главное" if lang == "ru" else "Main point"))
        blocks.append(h(sentences[0]))

        blocks.append(b("Простыми словами 👇" if lang == "ru" else "In simple words 👇"))
        blocks.append(h(_plain_eli5_bridge(locale, sentences[0])))

        if len(sentences) > 1:
            blocks.append(b("Подробнее" if lang == "ru" else "More detail"))
            rest = " ".join(sentences[1:])
            intro = _plain_detail_intro(locale)
            if lang == "ru":
                if not any(rest.lower().startswith(p) for p in ("скажу", "короче", "если", "разверну")):
                    lead = rest[0].lower() + rest[1:] if rest else rest
                    rest = f"{intro} {lead}"
            elif not rest.lower().startswith(("to be clear", "i'll unpack")):
                lead = rest[0].lower() + rest[1:] if rest else rest
                rest = f"{intro} {lead}"
            blocks.append(sentence_paragraphs(rest, sentences_per_para=3))

    if question.strip():
        echo = life_manifestation_echo(locale, question, style="plain")
        if echo and echo.lower()[:50] not in core.lower():
            blocks.append(b("Как это в жизни 🌿" if lang == "ru" else "How it shows up in life 🌿"))
            blocks.append(h(echo))

    example = _plain_life_example(locale, intent)
    if example:
        blocks.append(b("Пример (не из учебника) 😄" if lang == "ru" else "Real-life example 😄"))
        blocks.append(h(example))

    why_lines: list[str] = []
    seen: set[str] = set()
    core_lower = core.lower()
    for marker in markers[:3]:
        line = _marker_to_prose(locale, marker)
        if not line or line.lower() in seen:
            continue
        if line.lower()[:40] in core_lower:
            continue
        seen.add(line.lower())
        why_lines.append(line)

    if why_lines:
        header = "Откуда это в карте 🌿" if lang == "ru" else "Where this comes from in the chart 🌿"
        blocks.append(b(header))
        blocks.append(h("\n".join(f"• {line}" for line in why_lines)))

    blocks.append(b("Короче 🌙" if lang == "ru" else "Short version 🌙"))
    blocks.append(h(_build_summary(locale, sentences, markers)))

    blocks.append(
        h(
            "Карта — подсказка, не приговор и не «всё решено на небесах». "
            "Итог всё равно за тобой — и это, честно, хорошая новость: ты не NPC в чужом сценарии."
            if lang == "ru"
            else "The chart is a hint, not a verdict or a script written in the sky. "
            "You're still in charge — honestly, good news: you're not an NPC."
        )
    )

    practice_clean = sanitize_plain_qa_text(strip_telegram_html(practice), locale)
    if practice_clean:
        prefix = "💡 Попробуй на этой неделе: " if lang == "ru" else "💡 Try this week: "
        blocks.append(h(prefix + practice_clean))

    return p(*blocks)


def plain_topic_hook(locale: str, question: str, *, hint: str = "") -> str:
    topic = " ".join(question.strip().split()).rstrip("?.!")
    if len(topic) > 80:
        topic = topic[:79].rstrip() + "…"
    lang = _lang(locale)
    q = question.lower()
    if lang == "ru":
        if any(w in q for w in ("здоров", "тело", "энерг", "рутин", "режим", "сон")):
            base = "Начну с главного — про твоё тело и запас сил (без лекций про «просто встань и иди»)"
        elif any(w in q for w in ("деньг", "доход", "финанс", "карьер", "ценност", "инвест", "работ")):
            base = "Начну с главного — про деньги и дело (не «богатство на подходе», а как у тебя реально устроено)"
        elif any(w in q for w in ("люб", "роман", "брак", "партн", "отношен", "союз")):
            base = "Начну с главного — про любовь и близость (не роман из сериала, а твой живой сценарий)"
        elif any(w in q for w in ("карм", "прошл", "урок", "воплощ")):
            base = "Начну с главного — про уроки, которые жизнь повторяет, пока ты не скажешь «ага, понял»"
        else:
            base = f"Разберём «{topic}» по-человечески — без ребусов, сухой теории и заумных слов"
        return f"{base}: {hint}" if hint else f"{base}."
    if any(w in q for w in ("love", "romance", "marriage", "partner", "relationship")):
        base = "Main point first — your line in love and closeness"
    elif any(w in q for w in ("money", "income", "finance", "career", "work")):
        base = "Main point first — your line with money and work"
    else:
        base = f"On «{topic}» — clear words, no astro dictionary"
    return f"{base}: {hint}" if hint else f"{base}."


def plain_practice(locale: str, intent: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        tips = {
            "how_relationship": (
                "На неделю: заметь, как ты ведёшь себя в паре — без самокритики, просто наблюдай. "
                "Как будто смотришь сериал, где главный герой — ты (но без драмы в комментах)."
            ),
            "who_partner": (
                "Спроси себя: «меня тянет к похожим или к противоположным?» — ответ часто уже есть, "
                "просто мы его любим игнорировать."
            ),
            "challenge": (
                "Назови вслух одну привычку, которая мешает. Не чтобы себя ругать — "
                "чтобы увидеть паттерн, а не очередной «я опять всё испортил»."
            ),
            "money": (
                "Запиши три траты за неделю: «нужно» или «настроение». "
                "Так виднее, куда уходит — и где ты покупаешь радость вместо отдыха."
            ),
            "career": (
                "Один маленький шаг на месяц в сторону дела — не героизм, а движение. "
                "Не «открыть бизнес за выходные», а что-то, что реально сделаешь."
            ),
            "health": (
                "Сон и режим важнее «закалки характера». Начни с одного вечера без экрана — "
                "телефон переживёт, ты тоже."
            ),
            "general": (
                "Понаблюдай неделю — если узнаёшь себя, значит попали; если нет — не парься, "
                "карта не приговор и не экзамен на пятёрку."
            ),
        }
        return tips.get(intent, tips["general"])
    tips = {
        "how_relationship": "For one week, notice how you act in a pair — no self-judgment, just watch.",
        "who_partner": "Ask: «am I drawn to similar or opposite types?» — you often already know.",
        "challenge": "Name one blocking habit out loud — not to scold yourself, to see the pattern.",
        "money": "Log three spends: «need» or «mood» — you'll see where it goes.",
        "career": "One small step toward your work this month — not heroics, just motion.",
        "health": "Sleep beats willpower stunts. Start with one screen-free evening.",
        "general": "Watch for a week — if it fits, good; if not, don't stress, the chart isn't a verdict.",
    }
    return tips.get(intent, tips["general"])


def humanize_natal_plain(text: str, locale: str) -> str:
    if not text.strip():
        return text
    table = _HUMANIZE_RU if _lang(locale) == "ru" else _HUMANIZE_EN
    result = text
    for pattern, replacement in table:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    result = re.sub(r"\s+\.", ".", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def sanitize_plain_qa_text(text: str, locale: str) -> str:
    """Strip leftover jargon and tighten plain Q&A prose."""
    if not text.strip():
        return text
    lang = _lang(locale)
    result = humanize_natal_plain(text, locale)
    extra: tuple[tuple[str, str], ...] = (
        (r"\b\d+\s*[-‑]?\s*(?:й|го)\s+дом\b", "эта сфера"),
        (r"\(\s*\)", ""),
        (r"\s{2,}", " "),
        (r" · · ", " · "),
    )
    if lang == "ru":
        extra = (
            (r"управител\w*", "ключ"),
            (r"стеллиум\w*", "скученность"),
            (r"ретроград\w*", "внутренний разворот"),
            (r"накшатр\w*", ""),
            (r"джйотиш\w*", ""),
            (r"ведическ\w*", ""),
            *extra,
        )
    for pattern, replacement in extra:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result.strip(" ·,")
