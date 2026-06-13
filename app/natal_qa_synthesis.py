"""Direct-answer synthesis for natal chart Q&A."""
from __future__ import annotations

from dataclasses import dataclass

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import LAGNA_ESSENCE, _house_theme, _lang, _pl, _sign_line, _use_terms
from app.text_format import b, h, labeled_block, p

_DIGNITY_RANK = {"exalted": 4, "own": 3, "neutral": 2, "debilitated": 1}

_PLAIN_LIFE_AREA = {
    "ru": {
        1: "личный образ и то, как ты проявляешь себя",
        2: "деньги, ценности и чувство внутренней опоры",
        3: "общение, смелость и повседневные решения",
        4: "дом, семья и внутреннее спокойствие",
        5: "радость, творчество и самовыражение",
        6: "работа, режим и забота о теле",
        7: "партнёрство, брак и близость с другим человеком",
        8: "кризисы, перемены и глубинные переживания",
        9: "смысл жизни, вера и расширение горизонта",
        10: "карьера, статус и профессиональная реализация",
        11: "цели, друзья и поддержка вокруг",
        12: "отдых, уединение и внутреннее отпускание",
    },
    "en": {
        1: "personal image and how you show up",
        2: "money, values, and inner stability",
        3: "communication, courage, and daily choices",
        4: "home, family, and inner peace",
        5: "joy, creativity, and self-expression",
        6: "work, routine, and caring for your body",
        7: "partnership, marriage, and closeness with another person",
        8: "crises, change, and deep inner processes",
        9: "life meaning, faith, and broad horizons",
        10: "career, status, and professional realization",
        11: "goals, friends, and support around you",
        12: "rest, solitude, and letting go",
    },
}

_PLAIN_PLANET_ROLE = {
    "ru": {
        "SUN": "стержень личности и ощущение «кто я»",
        "MOON": "эмоции, привычки и потребность в безопасности",
        "MERCURY": "мышление, слова и способ договариваться",
        "VENUS": "любовь, симпатия и то, что тебя притягивает",
        "MARS": "воля, напор и способ отстаивать себя",
        "JUPITER": "рост, надежда и ощущение смысла",
        "SATURN": "границы, терпение и ответственность",
        "RAHU": "амбиции и тяга к необычному опыту",
        "KETU": "глубина, отпускание и внутренний поиск",
    },
    "en": {
        "SUN": "your core self and sense of identity",
        "MOON": "emotions, habits, and need for safety",
        "MERCURY": "thinking, words, and how you negotiate",
        "VENUS": "love, attraction, and what draws you in",
        "MARS": "will, drive, and how you stand up for yourself",
        "JUPITER": "growth, hope, and sense of meaning",
        "SATURN": "boundaries, patience, and responsibility",
        "RAHU": "ambition and pull toward unusual experience",
        "KETU": "depth, release, and inner search",
    },
}


_PLAIN_LIFE_AREA_PREP = {
    "ru": {
        1: "личного образа и самопроявления",
        2: "денег и личных ценностей",
        3: "общения и повседневных решений",
        4: "дома и семейного фона",
        5: "радости, творчества и романтики",
        6: "работы, режима и здоровья",
        7: "партнёрства и близости",
        8: "кризисов и глубинных перемен",
        9: "смысла, веры и мировоззрения",
        10: "карьеры и социальной реализации",
        11: "целей, друзей и поддержки",
        12: "отдыха, уединения и внутреннего отпускания",
    },
    "en": {
        1: "personal image and self-expression",
        2: "money and personal values",
        3: "communication and daily choices",
        4: "home and family background",
        5: "joy, creativity, and romance",
        6: "work, routine, and health",
        7: "partnership and closeness",
        8: "crises and deep change",
        9: "meaning, faith, and worldview",
        10: "career and social realization",
        11: "goals, friends, and support",
        12: "rest, solitude, and release",
    },
}


@dataclass(frozen=True)
class QaSynthFocus:
    houses: tuple[int, ...] = ()
    planet_keys: tuple[str, ...] = ()
    focus: str = "default"


def _planets_in_house(chart: JyotishChart, house: int) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")
    return [chart.planets[key] for key in order if chart.planets[key].house == house]


def _lord_placement(chart: JyotishChart, house: int) -> PlanetPlacement:
    return chart.planets[chart.house_lords[house]]


def _collect_placements(
    chart: JyotishChart,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
) -> list[PlanetPlacement]:
    seen: set[str] = set()
    out: list[PlanetPlacement] = []
    for house in houses:
        for pl in _planets_in_house(chart, house):
            if pl.key not in seen:
                seen.add(pl.key)
                out.append(pl)
        lord = _lord_placement(chart, house)
        if lord.key not in seen:
            seen.add(lord.key)
            out.append(lord)
    for key in planet_keys:
        if key not in seen:
            seen.add(key)
            out.append(chart.planets[key])
    return out


def _pick_focus_planet(
    chart: JyotishChart,
    placements: list[PlanetPlacement],
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    focus: str = "default",
    intent: str = "general",
) -> PlanetPlacement:
    if not placements:
        if houses:
            return _lord_placement(chart, houses[0])
        return chart.planets["SUN"]

    if focus == "default" and houses:
        in_target = [pl for pl in placements if pl.house in houses]
        if in_target:
            if intent == "money" and any(pl.key in {"VENUS", "JUPITER"} for pl in in_target):
                for key in ("VENUS", "JUPITER"):
                    for pl in in_target:
                        if pl.key == key:
                            return pl
            if intent == "career" and any(pl.key in {"SUN", "SATURN"} for pl in in_target):
                for key in ("SUN", "SATURN"):
                    for pl in in_target:
                        if pl.key == key:
                            return pl
            return in_target[0]

    if focus == "default" and planet_keys:
        by_key = {pl.key: pl for pl in placements}
        for key in planet_keys:
            if key in by_key:
                return by_key[key]

    if focus == "strength":
        return max(placements, key=lambda p: _DIGNITY_RANK.get(p.dignity, 2))
    if focus == "challenge":
        weak = [p for p in placements if p.dignity == "debilitated"]
        if weak:
            return weak[0]
        return min(placements, key=lambda p: _DIGNITY_RANK.get(p.dignity, 2))
    return placements[0]


def _plain_life_area(locale: str, house: int) -> str:
    lang = _lang(locale)
    return _PLAIN_LIFE_AREA[lang].get(house, _house_theme(locale, house))


def _plain_life_area_prep(locale: str, house: int) -> str:
    lang = _lang(locale)
    return _PLAIN_LIFE_AREA_PREP[lang].get(house, _plain_life_area(locale, house))


def _plain_planet_role(locale: str, planet_key: str) -> str:
    lang = _lang(locale)
    return _PLAIN_PLANET_ROLE[lang].get(planet_key, _pl(locale, planet_key).lower())


def _humanize_core(locale: str, pl: PlanetPlacement) -> str:
    """Turn a sign-line fragment into a readable clause."""
    lang = _lang(locale)
    core = _sign_line(locale, pl.key, pl.sign).rstrip(".")
    sign = sign_label(locale, pl.sign)

    if lang == "ru":
        if ":" in core:
            left, right = core.split(":", 1)
            left = left.strip()
            right = right.strip()
            if left and right:
                return f"{left} — {right[0].lower()}{right[1:]}"
        replacements = {
            "окрашивает самовыражение и стиль действия": (
                f"ты действуешь и проявляешь себя с оттенком {sign.lower()}"
            ),
            "раскрывает свой характер": (
                f"твоё поведение здесь окрашено качествами {sign.lower()}"
            ),
            "окрашивает чувства и внутренний ритм": (
                "настроение и привычные реакции сильно влияют на твоё состояние"
            ),
            "задаёт ценности и притяжение": (
                "важно, чтобы рядом было приятно, красиво и по-настоящему интересно"
            ),
            "даёт волю и способ действовать": (
                "ты не ждёшь долго — скорее делаешь и потом разбираешься"
            ),
            "формирует мышление и речь": (
                "ты думаешь и говоришь так, как тебе свойственно — без лишней воды"
            ),
            "расширяет горизонт и смысл": (
                "тебе важно видеть перспективу и ощущать, что жизнь не сужается"
            ),
            "учит дисциплине и терпению": (
                "результаты приходят через время, усилие и умение держать рамки"
            ),
        }
        if core in replacements:
            return replacements[core]
        return core

    if "expresses through" in core:
        return f"you express this with a {sign.lower()} tone"
    return core


def _classify_question(question: str, lang: str) -> str:
    q = question.lower()
    if lang == "ru":
        if any(w in q for w in ("деньг", "доход", "финанс", "инвест", "ценност")):
            return "money"
        if any(w in q for w in ("карьер", "реализ", "професс", "работ")):
            return "career"
        if any(w in q for w in ("здоров", "тело", "энерг")):
            return "health"
        if any(w in q for w in ("романт", "близост", "партн", "брак", "союз", "семь")) or (
            "отнош" in q and "деньг" not in q and "ценност" not in q
        ):
            if q.startswith("как") or "стро" in q or "склады" in q:
                return "how_relationship"
            if "кого" in q or "кто" in q:
                return "who_partner"
        if q.startswith("как"):
            return "how"
        if q.startswith("где") or "откуда" in q or q.startswith("куда"):
            return "where"
        if q.startswith("что") or q.startswith("кто") or q.startswith("какие"):
            return "what"
        if "есть ли" in q:
            return "yes_no"
        if "предназнач" in q or q.startswith("в чём"):
            return "purpose"
        if any(w in q for w in ("риск", "мешает", "трен", "сложн", "слаб")):
            return "challenge"
        if any(w in q for w in ("талант", "сильн", "опор")):
            return "strength"
        return "general"

    if any(w in q for w in ("money", "income", "finance", "invest", "value")):
        return "money"
    if any(w in q for w in ("career", "job", "profession", "work")):
        return "career"
    if any(w in q for w in ("health", "body", "energy")):
        return "health"
    if any(w in q for w in ("relationship", "romance", "marriage", "partner", "love")):
        if q.startswith("how"):
            return "how_relationship"
        if q.startswith("who"):
            return "who_partner"
    if q.startswith("how"):
        return "how"
    if q.startswith("where"):
        return "where"
    if q.startswith("what") or q.startswith("who") or q.startswith("which"):
        return "what"
    if "is there" in q:
        return "yes_no"
    if "purpose" in q or "calling" in q:
        return "purpose"
    if any(w in q for w in ("risk", "friction", "weak", "block")):
        return "challenge"
    if any(w in q for w in ("strength", "talent", "anchor")):
        return "strength"
    return "general"


def _emph(text: str) -> str:
    return b(text)


def _plain_primary_sentence(locale: str, pl: PlanetPlacement, intent: str) -> str:
    lang = _lang(locale)
    trait = _humanize_core(locale, pl)
    area = _plain_life_area_prep(locale, pl.house)
    trait_b = _emph(trait)

    if lang == "ru":
        if pl.key == "VENUS" and intent == "money":
            return (
                f"К деньгам и ценностям у тебя такой подход: {trait_b}. "
                f"Ты тратишь и копишь не «просто так», а когда чувствуешь смысл и качество. "
                f"Это проявляется в сфере {h(area)}."
            )
        if pl.key == "JUPITER" and intent == "money":
            return (
                f"С деньгами у тебя связана тема роста: {trait_b}. "
                f"Важно не только сохранять, но и видеть, куда можно расшириться. "
                f"На практике это часто проявляется через {h(area)}."
            )
        if pl.key == "VENUS":
            return (
                f"В любви и симпатии у тебя работает такой принцип: {trait_b}. "
                f"Это сильнее всего проявляется в сфере {h(area)}."
            )
        if pl.key == "MOON":
            return (
                f"На эмоциональном уровне для тебя важно, что {trait_b}. "
                f"Это особенно заметно там, где звучит тема {h(area)}."
            )
        if pl.key == "SUN":
            return (
                f"В основе ответа — твоё ощущение себя и своего курса: {trait_b}. "
                f"Это проявляется в сфере {h(area)}."
            )
        if pl.key == "MARS":
            return (
                f"В действии ты обычно опираешься на такой стиль: {trait_b}. "
                f"Это чувствуется в теме {h(area)}."
            )
        if pl.key == "MERCURY":
            return (
                f"В мышлении и словах у тебя складывается такая линия: {trait_b}. "
                f"На практике это часто связано с {h(area)}."
            )
        if pl.key == "JUPITER":
            return (
                f"Для тебя важны рост и ощущение перспективы: {trait_b}. "
                f"Это особенно связано с {h(area)}."
            )
        if pl.key == "SATURN":
            return (
                f"Здесь включаются терпение, границы и ответственность: {trait_b}. "
                f"Это проявляется в сфере {h(area)}."
            )
        role = _plain_planet_role(locale, pl.key)
        return (
            f"Главный акцент связан с темой «{h(role)}»: {trait_b}. "
            f"Это проявляется в сфере {h(area)}."
        )

    trait_b = _emph(trait)
    if pl.key == "VENUS":
        return (
            f"In love and attraction, your pattern is this: {trait_b}. "
            f"It shows most clearly around {h(area)}."
        )
    if pl.key == "MOON":
        return (
            f"Emotionally, it matters to you that {trait_b}. "
            f"This is especially visible in {h(area)}."
        )
    role = _plain_planet_role(locale, pl.key)
    return (
        f"The main accent is {h(role)}: {trait_b}. "
        f"This plays out in {h(area)}."
    )


def _plain_secondary_sentence(
    locale: str,
    primary: PlanetPlacement,
    secondary: PlanetPlacement,
) -> str:
    lang = _lang(locale)
    trait = _humanize_core(locale, secondary)
    trait_b = _emph(trait)
    if secondary.house == primary.house:
        if lang == "ru":
            return f"К этому добавляется ещё один оттенок: {trait_b}."
        return f"Another layer adds this: {trait_b}."

    area = _plain_life_area_prep(locale, secondary.house)
    if lang == "ru":
        if secondary.key == "MOON":
            return (
                f"Параллельно важны эмоции и привычные реакции: {trait_b}. "
                f"Это усиливает тему {h(area)}."
            )
        if secondary.key == "SATURN":
            return (
                f"При этом включаются границы и реализм: {trait_b}. "
                f"Это добавляет серьёзности в тему {h(area)}."
            )
        return (
            f"Рядом с этим работает ещё одна линия: {trait_b}. "
            f"Она добавляет глубины в тему {h(area)}."
        )
    return (
        f"Alongside this, another line runs: {trait_b}. "
        f"It adds depth in {h(area)}."
    )


def _plain_dignity_sentence(locale: str, pl: PlanetPlacement, focus: str) -> str:
    lang = _lang(locale)
    if pl.dignity == "exalted":
        if focus == "challenge":
            if lang == "ru":
                return "Даже в напряжённых темах у тебя есть внутренняя опора — её стоит замечать."
            return "Even in tense themes, you have inner support worth noticing."
        if lang == "ru":
            return "Эта линия у тебя сильная: на неё можно опираться, когда хочется понять себя."
        return "This line is strong in your chart — lean on it when you want to understand yourself."
    if pl.dignity == "debilitated":
        if lang == "ru":
            return (
                "Здесь тема не «сломана», но требует бережности: "
                "лучше не давить на себя и давать процессу время."
            )
        return (
            "This theme is not broken, but it asks for care — "
            "avoid pushing yourself and give the process time."
        )
    if focus == "challenge":
        if lang == "ru":
            return "Это не приговор, а подсказка: где стоит быть внимательнее к своим реакциям."
        return "This is not a verdict, but a hint about where to watch your reactions."
    if focus == "strength":
        if lang == "ru":
            return "Это одна из опор, на которую можно опираться в повседневной жизни."
        return "This is one of the anchors you can rely on in daily life."
    return ""


def _plain_opening(locale: str, intent: str, question: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        mapping = {
            "how_relationship": "В отношениях у тебя складывается такой рисунок.",
            "who_partner": "К тебе чаще тянет людей с таким сочетанием качеств.",
            "how": "Если ответить на твой вопрос, картина выглядит так.",
            "where": "Чаще всего это проявляется в таких жизненных сферах.",
            "what": "Если собрать ответ по карте, получается такая картина.",
            "yes_no": "Да, эта тема в твоей карте действительно звучит.",
            "purpose": "Твой путь и смысл здесь связаны с такими качествами.",
            "challenge": "Напряжение чаще всего приходит отсюда — не как наказание, а как зона роста.",
            "strength": "Твои сильные стороны здесь проявляются так.",
            "health": "С телом и энергией у тебя связана такая история.",
            "money": "С деньгами и ценностями у тебя складывается такая линия.",
            "career": "С карьерой и реализацией у тебя связано следующее.",
            "general": "Если собрать ответ по твоей карте, получается такая картина.",
        }
        return mapping.get(intent, mapping["general"])
    mapping = {
        "how_relationship": "In relationships, your chart paints this picture.",
        "who_partner": "You tend to attract people with this mix of qualities.",
        "how": "Answered from your chart, the picture looks like this.",
        "where": "This most often shows up in these life areas.",
        "what": "From your chart, here is what stands out.",
        "yes_no": "Yes — this theme is genuinely present in your chart.",
        "purpose": "Your path and meaning connect to these qualities.",
        "challenge": "Tension usually comes from here — not as punishment, but as a growth zone.",
        "strength": "Your strengths show up like this.",
        "health": "With body and energy, your chart tells this story.",
        "money": "With money and values, this is your line.",
        "career": "With career and realization, this is what connects.",
        "general": "Put together from your chart, the picture looks like this.",
    }
    return mapping.get(intent, mapping["general"])


def _build_plain_narrative(
    locale: str,
    question: str,
    primary: PlanetPlacement,
    secondary: PlanetPlacement | None,
    *,
    focus: str,
) -> str:
    lang = _lang(locale)
    intent = _classify_question(question, lang)
    opening = _plain_opening(locale, intent, question)

    parts = [b(opening), _plain_primary_sentence(locale, primary, intent)]
    if secondary and secondary.key != primary.key:
        parts.append(_plain_secondary_sentence(locale, primary, secondary))

    dignity = _plain_dignity_sentence(locale, primary, focus)
    if dignity:
        parts.append(dignity)

    if lang == "ru":
        closers = {
            "how_relationship": (
                "Это не готовый сценарий отношений, а описание твоего естественного стиля — "
                "его можно осознанно поддерживать, а не ломать через себя."
            ),
            "money": (
                "Это не приговор про богатство или бедность, а подсказка о том, "
                "как ты относишься к ресурсам и что для тебя по-настоящему ценно."
            ),
            "career": (
                "Это не список профессий, а описание того, через какие качества "
                "тебе легче всего реализоваться."
            ),
            "challenge": (
                "Замечать эти места полезнее, чем бороться с собой — "
                "обычно напряжение смягчается, когда ты понимаешь свой паттерн."
            ),
        }
        if intent in closers:
            parts.append(closers[intent])
        elif intent in {"how", "what", "who_partner"}:
            parts.append(
                "Это не жёсткая схема, а способ лучше понять себя и свои привычные реакции."
            )
    elif intent in {"how_relationship", "how", "what", "who_partner"}:
        parts.append(
            "This is not a rigid script, but a way to understand your natural style more clearly."
        )

    return p(*parts)


def _plain_phrase_from_placement(
    locale: str,
    question: str,
    pl: PlanetPlacement,
    *,
    secondary: PlanetPlacement | None = None,
    focus: str = "default",
) -> str:
    return _build_plain_narrative(
        locale,
        question,
        pl,
        secondary,
        focus=focus,
    )


def _lagna_answer(locale: str, chart: JyotishChart, question: str, *, style: str) -> str | None:
    lang = _lang(locale)
    q = question.lower()
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
    if not any(w in q for w in ("перв", "видят", "образ", "суть", "кто я", "начина", "first", "see me", "core", "who am", "begin")):
        return None

    if not _use_terms(style):
        if lang == "ru":
            return p(
                b("При первой встрече люди считывают тебя так"),
                h(
                    f"Как человека с таким образом: {essence}. "
                    "Это не маска на один вечер — так ты естественно входишь в контакт "
                    "и держишься в новых ситуациях."
                ),
            )
        return p(
            b("At first meeting, people read you like this"),
            h(
                f"As someone with this presence: {essence}. "
                "It is not a one-night mask — this is how you naturally enter contact "
                "and hold yourself in new situations."
            ),
        )

    lagna = sign_label(locale, chart.lagna_sign)
    if lang == "ru":
        return f"При первой встрече тебя читают через Лагну в {lagna}: {essence}."
    return f"At first contact people read your Lagna in {lagna}: {essence}."


def _terms_phrase_from_placement(
    locale: str,
    question: str,
    pl: PlanetPlacement,
) -> str:
    lang = _lang(locale)
    pname = _pl(locale, pl.key)
    sign = sign_label(locale, pl.sign)
    theme = _house_theme(locale, pl.house)
    core = _sign_line(locale, pl.key, pl.sign).rstrip(".")
    q = question.lower()

    dignity_tail = ""
    if pl.dignity == "exalted":
        dignity_tail = (
            " Это одна из сильных опор карты."
            if lang == "ru"
            else " This is one of the chart's strong anchors."
        )
    elif pl.dignity == "debilitated":
        dignity_tail = (
            " Здесь важна осознанность — тема не слабая, но требует внимания."
            if lang == "ru"
            else " Conscious attention helps — the theme is workable, not blocked."
        )

    if lang == "ru":
        if q.startswith("как ") or "как я" in q or "как склады" in q or "как отнош" in q:
            return (
                f"Скорее всего — {core}: {pname} в {sign} связывает это с темой «{theme}»."
                f"{dignity_tail}"
            )
        if q.startswith("где") or " где " in q or "откуда" in q or q.startswith("куда"):
            return (
                f"Это чаще проявляется через «{theme}»: {pname} в {sign} — {core}."
                f"{dignity_tail}"
            )
        if q.startswith("что") or q.startswith("кто") or "кого" in q:
            return (
                f"Карта показывает: {core}; ключ — {pname} в {sign} в сфере «{theme}»."
                f"{dignity_tail}"
            )
        return (
            f"По карте: {core}; главный маркер — {pname} в {sign} («{theme}»)."
            f"{dignity_tail}"
        )

    if q.startswith("how") or "how do" in q:
        return (
            f"Most likely — {core}: {pname} in {sign} ties this to {theme}."
            f"{dignity_tail}"
        )
    return (
        f"From the chart: {core}; main marker — {pname} in {sign} ({theme})."
        f"{dignity_tail}"
    )


def _phrase_from_placement(
    locale: str,
    question: str,
    pl: PlanetPlacement,
    *,
    style: str,
    secondary: PlanetPlacement | None = None,
    focus: str = "default",
) -> str:
    if not _use_terms(style):
        return _plain_phrase_from_placement(
            locale,
            question,
            pl,
            secondary=secondary,
            focus=focus,
        )
    return _terms_phrase_from_placement(locale, question, pl)


def synthesize_direct_answer(
    chart: JyotishChart,
    locale: str,
    question: str,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    focus: str = "default",
    style: str = "terms",
    lagna_first: bool = False,
) -> str:
    if lagna_first:
        lagna_line = _lagna_answer(locale, chart, question, style=style)
        if lagna_line:
            return lagna_line

    placements = _collect_placements(chart, houses=houses, planet_keys=planet_keys)
    intent = _classify_question(question, _lang(locale))
    primary = _pick_focus_planet(
        chart,
        placements,
        houses=houses,
        planet_keys=planet_keys,
        focus=focus,
        intent=intent,
    )
    secondary = None
    for pl in placements:
        if pl.key != primary.key:
            secondary = pl
            break
    if secondary is None and houses:
        lord = _lord_placement(chart, houses[0])
        if lord.key != primary.key:
            secondary = lord

    return _phrase_from_placement(
        locale,
        question,
        primary,
        style=style,
        secondary=secondary,
        focus=focus,
    )


def format_qa_body(
    locale: str,
    direct_answer: str,
    evidence: str,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    answer = direct_answer.strip()
    if not _use_terms(style):
        return answer

    evidence = evidence.strip()
    if lang == "ru":
        blocks = [labeled_block("💬 Ответ", answer)]
        if evidence:
            blocks.append(labeled_block("📊 Подробнее по карте", evidence))
        return p(*blocks)
    blocks = [labeled_block("💬 Answer", answer)]
    if evidence:
        blocks.append(labeled_block("📊 Chart details", evidence))
    return p(*blocks)


def finish_qa_body(
    locale: str,
    question: str,
    chart: JyotishChart,
    evidence: str,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    focus: str = "default",
    style: str = "terms",
    lagna_first: bool = False,
    direct_answer: str | None = None,
) -> str:
    answer = direct_answer or synthesize_direct_answer(
        chart,
        locale,
        question,
        houses=houses,
        planet_keys=planet_keys,
        focus=focus,
        style=style,
        lagna_first=lagna_first,
    )
    if not _use_terms(style):
        return format_qa_body(locale, answer, "", style=style)
    return format_qa_body(locale, answer, evidence, style=style)
