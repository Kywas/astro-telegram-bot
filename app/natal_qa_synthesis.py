"""Direct-answer synthesis for natal chart Q&A."""
from __future__ import annotations

from dataclasses import dataclass

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import LAGNA_ESSENCE, _house_theme, _lang, _pl, _sign_line, _use_terms
from app.natal_qa_voice import compose_plain_qa_answer, humanize_natal_plain, life_manifestation_echo, plain_practice, plain_topic_hook, strip_telegram_html
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
        if any(w in q for w in ("риск", "мешает", "меша", "блок", "препят", "трен", "сложн", "слаб")):
            return "challenge"
        if any(w in q for w in ("когда", "срок", "пора", "скоро", "время")):
            return "when"
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
        if q.startswith("почему") or "зачем" in q:
            return "why"
        if q.startswith("как"):
            return "how"
        if q.startswith("что") or q.startswith("кто") or q.startswith("какие"):
            return "what"
        if "есть ли" in q:
            return "yes_no"
        if "предназнач" in q or q.startswith("в чём"):
            return "purpose"
        if any(w in q for w in ("талант", "сильн", "опор")):
            return "strength"
        return "general"

    if any(w in q for w in ("risk", "block", "obstacle", "friction", "weak", "holds me back")):
        return "challenge"
    if any(w in q for w in ("when", "timing", "soon", "deadline")):
        return "when"
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
    if q.startswith("why"):
        return "why"
    if q.startswith("how"):
        return "how"
    if q.startswith("what") or q.startswith("who") or q.startswith("which"):
        return "what"
    if "is there" in q:
        return "yes_no"
    if "purpose" in q or "calling" in q:
        return "purpose"
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
        if intent == "challenge":
            return f"Главный затык — {trait_b}; особенно там, где {h(area)}."
        if intent == "why":
            return f"Короче: {trait_b} — и это слышно в {h(area)}."
        if intent == "when":
            return (
                f"Не «вторник в 15:00», а когда тема {h(area)} станет ощущаться ярче. "
                f"Маркер — {trait_b}."
            )
        if intent in {"how", "how_relationship"}:
            return f"Твой способ — {trait_b}. Это видно в {h(area)}."
        if intent == "what" or intent == "who_partner":
            return f"Суть — {trait_b}; ключ в {h(area)}."
        if pl.key == "VENUS" and intent == "money":
            return (
                f"С деньгами ты не «просто тратишь» — {trait_b}. "
                f"Когда чувствуешь смысл и качество, кошелёк открывается в {h(area)}."
            )
        if pl.key == "JUPITER" and intent == "money":
            return (
                f"Деньги у тебя связаны с ростом: {trait_b}. "
                f"Не только копить — ещё и видеть, куда расшириться ({h(area)})."
            )
        if pl.key == "VENUS":
            return (
                f"В любви работает так: {trait_b}. "
                f"Сильнее всего — в {h(area)}."
            )
        if pl.key == "MOON":
            return (
                f"На эмоциях важно, что {trait_b}. "
                f"Заметнее всего — {h(area)}."
            )
        if pl.key == "SUN":
            return f"В основе — {trait_b}. Проявляется в {h(area)}."
        if pl.key == "MARS":
            return f"В действии — {trait_b}. Чувствуется в {h(area)}."
        if pl.key == "MERCURY":
            return f"В голове и словах — {trait_b}. На практике — {h(area)}."
        if pl.key == "JUPITER":
            return f"Тянет к росту: {trait_b}. Связано с {h(area)}."
        if pl.key == "SATURN":
            return f"Тут терпение и рамки: {trait_b}. Сфера — {h(area)}."
        return f"Главное — {trait_b}. Это про {h(area)}."

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
    *,
    intent: str = "general",
) -> str:
    lang = _lang(locale)
    trait = _humanize_core(locale, secondary)
    trait_b = _emph(trait)
    if secondary.house == primary.house:
        if intent in {"how", "how_relationship"}:
            if lang == "ru":
                return f"Второй штрих — {trait_b} в той же сфере."
            return f"Second layer — {trait_b} in the same area."
        if lang == "ru":
            if intent == "challenge":
                return f"Второй узел — {trait_b} в той же сфере."
            return f"К этому добавляется ещё один оттенок: {trait_b}."
        if intent == "challenge":
            return f"Second friction point — {trait_b} in the same area."
        return f"Another layer adds this: {trait_b}."

    area = _plain_life_area_prep(locale, secondary.house)
    if lang == "ru":
        if intent == "challenge":
            return f"Ещё один затык — {trait_b}; усиливает {h(area)}."
        if secondary.key == "MOON":
            return f"Плюс эмоции: {trait_b} — это про {h(area)}."
        if secondary.key == "SATURN":
            return f"И границы: {trait_b} — добавляет серьёзности в {h(area)}."
        return f"Рядом работает ещё: {trait_b} — глубина в {h(area)}."
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


@dataclass(frozen=True)
class StructuredQaAnswer:
    brief: str
    markers: tuple[str, ...]
    practice: str


def _short_question(question: str, *, limit: int = 120) -> str:
    q = " ".join(question.strip().split())
    if len(q) <= limit:
        return q.rstrip("?.!")
    return q[: limit - 1].rstrip() + "…"


def _question_already_asks(intent: str, question: str) -> bool:
    q = question.lower().strip()
    if intent == "challenge":
        return any(w in q for w in ("мешает", "меша", "блок", "препят", "мешают", "holds me back"))
    if intent == "why":
        return q.startswith("почему") or "зачем" in q or q.startswith("why")
    if intent == "when":
        return any(w in q for w in ("когда", "срок", "пора", "скоро")) or q.startswith("when")
    if intent == "what":
        return q.startswith("что") or q.startswith("какие") or q.startswith("what")
    if intent == "how" or intent == "how_relationship":
        return q.startswith("как") or q.startswith("how")
    if intent == "who_partner":
        return "кого" in q or q.startswith("кто") or q.startswith("who")
    return False


def _question_frame(locale: str, question: str, intent: str, *, style: str = "terms") -> str:
    """Anchor the answer to the user's exact wording."""
    lang = _lang(locale)
    if not _use_terms(style):
        hooks = {
            "ru": {
                "challenge": "Где застревает — без мистики, по делу.",
                "why": "Почему так — коротко.",
                "when": "Когда — не дата в календаре, а «когда созреешь».",
                "what": "Суть вопроса — вот так.",
                "how": "Как у тебя это работает — простыми словами.",
                "how_relationship": "Про отношения — без астрологического словаря.",
                "who_partner": "Кого тянет — типаж, не загадка.",
                "money": "Про деньги — как ты реально тратишь и копишь.",
                "career": "Про работу — куда тянет и где тормозит.",
                "health": "Про тело и энергию — без занудства.",
                "general": plain_topic_hook(locale, question),
            },
            "en": {
                "challenge": "Where it sticks — no mysticism, just the point.",
                "why": "Why — short version.",
                "when": "When — not a calendar date, but readiness.",
                "what": "The gist — like this.",
                "how": "How it works for you — plain words.",
                "how_relationship": "On relationships — no astro dictionary.",
                "who_partner": "Who you're drawn to — a type, not a riddle.",
                "money": "On money — how you actually spend and save.",
                "career": "On work — pull and friction.",
                "health": "On body and energy — no lecture.",
                "general": plain_topic_hook(locale, question),
            },
        }
        return hooks[lang].get(intent, hooks[lang]["general"])

    topic = _short_question(question)
    if _question_already_asks(intent, question):
        if lang == "ru":
            echo = {
                "challenge": f"По вопросу «{topic}» — вот что даёт карта.",
                "why": f"Про «{topic}» — причины в этих линиях.",
                "when": f"Про срок («{topic}») — не дата, а условия готовности.",
                "what": f"На «{topic}» — главное такое.",
                "how": f"На «{topic}» — твой способ действовать такой.",
                "how_relationship": f"На «{topic}» — вот как у тебя складывается близость.",
                "who_partner": f"На «{topic}» — такой тип притяжения.",
            }
            return echo.get(intent, f"На «{topic}»:")
        echo = {
            "challenge": f"On «{topic}» — here's what the chart shows.",
            "why": f"On «{topic}» — the reasons sit in these lines.",
            "when": f"On timing («{topic}») — conditions, not a fixed date.",
            "what": f"On «{topic}» — the main point is this.",
            "how": f"On «{topic}» — your way of acting looks like this.",
            "how_relationship": f"On «{topic}» — this is how closeness forms for you.",
            "who_partner": f"On «{topic}» — this is the pull pattern.",
        }
        return echo.get(intent, f"On «{topic}»:")
    if lang == "ru":
        frames = {
            "how_relationship": f"На вопрос «{topic}» в отношениях карта показывает следующее.",
            "who_partner": f"Кого ты притягиваешь — если смотреть на «{topic}», картина такая.",
            "how": f"На «{topic}» ответ складывается так.",
            "where": f"Где это проявляется — если брать твой вопрос «{topic}»:",
            "when": f"По срокам и моменту («{topic}») карта не даёт точную дату, но показывает условия.",
            "why": f"Почему так («{topic}») — главные маркеры вот здесь.",
            "what": f"Что именно («{topic}») — по карте выходит так.",
            "yes_no": f"На «{topic}» — да, тема в карте есть, но важны нюансы ниже.",
            "purpose": f"Про предназначение («{topic}») карта указывает на такие качества.",
            "challenge": f"Что мешает («{topic}») — упирается в эти места карты.",
            "strength": f"Где сила («{topic}») — опирайся на это.",
            "health": f"Про здоровье и энергию («{topic}») — такая связка.",
            "money": f"Про деньги («{topic}») — линия в карте такая.",
            "career": f"Про работу и реализацию («{topic}») — вот что видно.",
            "general": f"На твой вопрос «{topic}» карта отвечает так.",
        }
        return frames.get(intent, frames["general"])
    frames = {
        "how_relationship": f"On «{topic}» in relationships, your chart shows this.",
        "who_partner": f"Who you attract — for «{topic}», the pattern looks like this.",
        "how": f"On «{topic}», the answer comes together like this.",
        "where": f"Where it shows up — for «{topic}»:",
        "when": f"On timing («{topic}») the chart gives conditions, not an exact date.",
        "why": f"Why («{topic}») — the main markers are here.",
        "what": f"What exactly («{topic}») — from the chart:",
        "yes_no": f"On «{topic}» — yes, the theme is there, with nuances below.",
        "purpose": f"On purpose («{topic}») — these qualities stand out.",
        "challenge": f"What blocks you («{topic}») — it points here.",
        "strength": f"Where you're strong («{topic}») — lean on this.",
        "health": f"On health and energy («{topic}»):",
        "money": f"On money («{topic}»):",
        "career": f"On work and realization («{topic}»):",
        "general": f"On your question «{topic}», the chart answers like this.",
    }
    return frames.get(intent, frames["general"])


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
    opening = _question_frame(locale, question, intent, style="plain")

    chunks = [opening, strip_telegram_html(_plain_primary_sentence(locale, primary, intent))]
    if secondary and secondary.key != primary.key:
        chunks.append(strip_telegram_html(_plain_secondary_sentence(locale, primary, secondary, intent=intent)))

    if primary.dignity == "debilitated":
        dignity = _plain_dignity_sentence(locale, primary, focus)
        if dignity:
            chunks.append(dignity)
    elif intent == "when":
        if lang == "ru":
            chunks.append(
                "Точную дату не назову — смотри, когда внутри «да, готов» "
                "и тема перестаёт быть фоном. Календарь тут как напоминалка, не начальник."
            )
        else:
            chunks.append(
                "The chart does not give an exact date — watch inner readiness "
                "and periods when this theme feels louder."
            )
    elif lang == "ru" and focus != "challenge":
        chunks.append(
            "Если коротко и по-человечески: это не про «судьба решила», "
            "а про то, как ты обычно реагируешь — и что можно подкрутить без революции."
        )

    return h(" ".join(part for part in chunks if part))


def _dignity_tag(locale: str, pl: PlanetPlacement) -> str:
    lang = _lang(locale)
    if pl.dignity == "exalted":
        return "усилено" if lang == "ru" else "strong"
    if pl.dignity == "debilitated":
        return "нужна бережность" if lang == "ru" else "needs care"
    if pl.dignity == "own":
        return "устойчиво" if lang == "ru" else "steady"
    return ""


def _build_chart_markers(
    chart: JyotishChart,
    locale: str,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    style: str = "terms",
    limit: int = 3,
) -> tuple[str, ...]:
    placements = _collect_placements(chart, houses=houses, planet_keys=planet_keys)
    if not placements:
        return ()
    markers: list[str] = []
    seen: set[str] = set()
    for pl in placements:
        if pl.key in seen:
            continue
        seen.add(pl.key)
        tag = _dignity_tag(locale, pl)
        if not _use_terms(style):
            from app.natal_qa_voice import plain_placement_line

            line = plain_placement_line(locale, pl)
        else:
            pname = _pl(locale, pl.key)
            sign = sign_label(locale, pl.sign)
            theme = _house_theme(locale, pl.house)
            line = f"{pname} в {sign} · дом «{theme}»"
            if tag:
                line = f"{line} · {tag}"
        markers.append(line)
        if len(markers) >= limit:
            break
    return tuple(markers)


def _practical_takeaway(
    locale: str,
    intent: str,
    *,
    focus: str,
    primary: PlanetPlacement,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    if not _use_terms(style):
        return plain_practice(locale, intent)
    area = _plain_life_area_prep(locale, primary.house)
    if lang == "ru":
        mapping = {
            "how_relationship": f"На неделю: заметь, как ты ведё себя в теме «{area}» — это и есть твой стиль в паре.",
            "how": "Попробуй одну неделю наблюдать, как это проявляется в жизни — без оценки, просто замечай.",
            "when": "Смотри на периоды, когда тема карты ощущается ярче — тогда решения даются легче.",
            "why": "Если узнаёшь себя в описании — это и есть ответ «почему»; дальше можно менять реакцию, не ломая себя.",
            "challenge": (
                "На неделю: назови вслух одну привычку, которая мешает, — "
                "не чтобы себя осуждать, а чтобы увидеть паттерн."
            ),
            "strength": "Сознательно опирайся на эту линию хотя бы раз в неделю — так она работает сильнее.",
            "money": "Запиши, что для тебя «достаточно» — карта про ценности, не про цифры в вакууме.",
            "career": "Выбери одно действие на месяц в сторону реализации — маленький, но конкретный шаг.",
            "health": "Режим сна и нагрузки здесь важнее «волевых подвигов» — начни с малого.",
            "yes_no": "Если откликается — тема живая; если нет — доверяй ощущению больше текста.",
            "general": f"На неделю понаблюдай тему «{area}» — так ответ станет не абстракцией, а опытом.",
        }
        return mapping.get(intent, mapping["general"])
    mapping = {
        "how_relationship": f"For one week, notice how you act around «{area}» — that's your pair style.",
        "how": "Try one week of noticing how this shows up — no judgment, just observation.",
        "when": "Watch when this theme feels louder in life — decisions land easier then.",
        "why": "If you recognize yourself here, that's your «why»; you can shift reactions without breaking yourself.",
        "challenge": (
            "For one week, name one habit that blocks you — "
            "not to judge yourself, but to see the pattern."
        ),
        "strength": "Lean on this line consciously once a week — it grows stronger with use.",
        "money": "Write down what «enough» means for you — the chart is about values, not empty numbers.",
        "career": "Pick one concrete step this month toward realization — small but real.",
        "health": "Sleep and load matter more than heroic pushes — start small.",
        "yes_no": "If it resonates, the theme is alive; if not, trust your feeling over the text.",
        "general": f"Observe «{area}» for a week — then the answer becomes experience, not abstraction.",
    }
    return mapping.get(intent, mapping["general"])


def synthesize_structured_answer(
    chart: JyotishChart,
    locale: str,
    question: str,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    focus: str = "default",
    style: str = "terms",
    lagna_first: bool = False,
) -> StructuredQaAnswer:
    if lagna_first:
        lagna_line = _lagna_answer(locale, chart, question, style=style)
        if lagna_line:
            return StructuredQaAnswer(lagna_line, (), "")

    intent = _classify_question(question, _lang(locale))
    placements = _collect_placements(chart, houses=houses, planet_keys=planet_keys)
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

    brief = _phrase_from_placement(
        locale,
        question,
        primary,
        style=style,
        secondary=secondary,
        focus=focus,
    )
    markers = _build_chart_markers(
        chart,
        locale,
        houses=houses,
        planet_keys=planet_keys,
        style=style,
    )
    practice = _practical_takeaway(locale, intent, focus=focus, primary=primary, style=style)
    return StructuredQaAnswer(brief, markers, practice)


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
        if any(w in q for w in ("мешает", "блок", "препят", "меша")):
            return (
                f"Главный узел — {core}; маркер {pname} в {sign} в сфере «{theme}»."
                f"{dignity_tail}"
            )
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
    markers: tuple[str, ...] = (),
    practice: str = "",
    question: str = "",
) -> str:
    lang = _lang(locale)
    answer = direct_answer.strip()
    marker_lines = list(markers)
    if not marker_lines and evidence.strip():
        marker_lines = [
            line.lstrip("•·- ").strip()
            for line in evidence.split("\n")
            if line.strip()
        ][:4]

    if not _use_terms(style):
        return compose_plain_qa_answer(
            locale,
            answer,
            tuple(marker_lines),
            practice,
            question,
        )

    answer_block = labeled_block("💬 Ответ" if lang == "ru" else "💬 Answer", answer)
    blocks = [answer_block]
    if question.strip():
        echo = life_manifestation_echo(locale, question, style=style)
        if echo:
            blocks.append(
                labeled_block(
                    "📖 Как это проявляется" if lang == "ru" else "📖 How it shows up",
                    echo,
                )
            )
    if marker_lines:
        chart_block = "\n".join(f"• {line}" for line in marker_lines[:4])
        blocks.append(
            labeled_block("📊 По карте" if lang == "ru" else "📊 Chart markers", chart_block)
        )
    elif evidence.strip():
        blocks.append(
            labeled_block("📊 Подробнее по карте" if lang == "ru" else "📊 Chart details", evidence)
        )
    if practice.strip():
        label = "💡 На практике" if lang == "ru" else "💡 In practice"
        blocks.append(labeled_block(label, practice))
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
    if direct_answer is None:
        structured = synthesize_structured_answer(
            chart,
            locale,
            question,
            houses=houses,
            planet_keys=planet_keys,
            focus=focus,
            style=style,
            lagna_first=lagna_first,
        )
        return format_qa_body(
            locale,
            structured.brief,
            evidence,
            style=style,
            markers=structured.markers,
            practice=structured.practice,
            question=question,
        )

    markers = _build_chart_markers(
        chart,
        locale,
        houses=houses,
        planet_keys=planet_keys,
        style=style,
    )
    intent = _classify_question(question, _lang(locale))
    placements = _collect_placements(chart, houses=houses, planet_keys=planet_keys)
    primary = _pick_focus_planet(
        chart,
        placements,
        houses=houses,
        planet_keys=planet_keys,
        focus=focus,
        intent=intent,
    )
    practice = _practical_takeaway(locale, intent, focus=focus, primary=primary, style=style)
    return format_qa_body(
        locale,
        direct_answer,
        evidence,
        style=style,
        markers=markers,
        practice=practice,
        question=question,
    )
