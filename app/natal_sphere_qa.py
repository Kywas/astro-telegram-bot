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
from app.family_qa_detail import build_family_structured
from app.natal_qa_synthesis import format_qa_body
from app.natal_qa_voice import plain_role
from app.natal_sphere_qa_detail import build_natal_sphere_structured
from app.text_format import b, h, p, qa_response

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
        "Как у меня устроена романтика — не «для сторис», а по-настоящему?",
        "Кого я притягиваю — и кто реально подходит, а не «из списка желаний»?",
        "Что карта говорит про брак и долгий союз?",
        "Как у меня с домом, семьёй и ощущением «свои»?",
        "Где в паре и семье обычно зацепляемся — и почему?",
    ),
    "en": (
        "How do I build romantic relationships?",
        "Who do I attract and who suits me?",
        "What does the chart say about marriage and union?",
        "How do family and home themes play out?",
        "Where do frictions show up in couple and family life?",
    ),
}

FINANCE_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Как у меня устроены деньги и ценности — не «просто счёт в банке»?",
        "Куда вести карьеру — и «зачем я встаю утром» (не только должность)?",
        "Как у меня с инвестициями и риском — без «быстрых денег»?",
        "Откуда приходит доход и рост — не «удача с неба»?",
        "Где финансовые риски и типичные ошибки — и как не наступать?",
    ),
    "en": (
        "How do I relate to money and values?",
        "Where should I take my career and how do I grow?",
        "How do investments and risk work for me?",
        "Where does income and financial growth come from?",
        "Where are financial risks and typical mistakes?",
    ),
}

KARMA_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Какая «кармическая» тема у меня крутится по кругу?",
        "Что карта помнит про прошлые жизни — если верить в такое?",
        "Чему меня учит Сатурн — и почему так долго?",
        "Что из прошлого тянет Раху, а что отпускает Кету?",
        "Как прожить свои уроки осознаннее — без мистического тумана?",
    ),
    "en": (
        "What karmic theme runs through my chart?",
        "What does the chart say about past incarnations?",
        "What lessons does Saturn carry?",
        "What do Rahu and Ketu pull from the past?",
        "How can I live this karma more consciously?",
    ),
}

TRAITS_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Кто я по сути — с чего начинается моя «версия себя»?",
        "Какой у меня темперамент — и где заряжаюсь, а где выгораю?",
        "Как устроены мои эмоции — не «слабость», а внутренний GPS?",
        "Как я действую и общаюсь — когда громко, а когда молчу?",
        "Какие качества даны от рождения — и что с ними делать?",
    ),
    "en": (
        "Who am I at core — where does my chart begin?",
        "What is my temperament and energy?",
        "How are my emotions and inner world built?",
        "How do I act and communicate?",
        "What qualities was I born with?",
    ),
}

LINEAGE_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Что карта говорит про маму — и как у нас с ней «внутри»?",
        "Что про отца — и какие правила я от него унаследовал?",
        "Какие темы рода и предков у меня «идут по наследству»?",
        "Как семейные корни дают опору — или забирают её?",
        "Где с родителями и родом обычно зацепляемся — и почему?",
    ),
    "en": (
        "What does the chart say about my mother and our bond?",
        "What does the chart say about my father and his influence?",
        "What lineage and ancestor themes run through the chart?",
        "How do family roots shape my sense of support?",
        "Where do difficulties with parents and lineage show up?",
    ),
}

HEALTH_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Как у меня устроены тело и энергия — где «бензин», а где «утечка»?",
        "На что смотреть в здоровье — без паники и Google-диагноза?",
        "Как у меня со силами и восстановлением — не «я же сильный»?",
        "Где у меня типичные слабые места — и как не геройствовать?",
        "Как заботиться о теле по карте — без лекций «просто соберись»?",
    ),
    "en": (
        "How is my body and life energy built?",
        "What should I watch for in health?",
        "How do strength and recovery work for me?",
        "Where are typical weak spots in the body?",
        "How should I care for my body according to the chart?",
    ),
}

PURPOSE_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "В чём моё предназначение — не «табличка на двери», а живой путь?",
        "Какие таланты у меня от рождения — и что с ними делать?",
        "Как найти своё дело — когда «что я делаю» совпадает с «зачем»?",
        "Что помогает реализации, а что тихо мешает?",
        "Куда направить энергию — чтобы раскрыться, а не выгореть?",
    ),
    "en": (
        "What is my purpose and main life path?",
        "What talents was I born with?",
        "How do I realize myself and find my calling?",
        "What helps and what blocks my realization?",
        "Where should I direct energy for fullest unfolding?",
    ),
}

DHARMA_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Какой у меня духовный путь — без обязательного монастыря?",
        "Как у меня со связью с верой и смыслом — не «всё будет хорошо»?",
        "Что карта говорит про медитацию и уединение — без понтов?",
        "Какие уроки несут Юпитер и Кету — рост vs отпускание?",
        "Как жить по дхарме каждый день — не только в позе лотоса?",
    ),
    "en": (
        "What is my spiritual path and dharma?",
        "How does my connection to faith and meaning work?",
        "What does the chart say about meditation and solitude?",
        "What spiritual lessons do Jupiter and Ketu carry?",
        "How do I live in alignment with dharma every day?",
    ),
}

TRAVEL_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Есть ли у меня тема переезда — или жизни «не там, где родился»?",
        "Как у меня с дальними путешествиями — отдых или перезагрузка?",
        "Куда меня тянет — какие страны и направления «магнитят»?",
        "Что помогает переезду, а что тихо тормозит?",
        "Как чувствовать себя «дома» далеко от родины — без розовых очков?",
    ),
    "en": (
        "Does my chart show relocation or life abroad?",
        "How do long-distance journeys work for me?",
        "Where am I pulled — directions and places?",
        "What helps and what blocks relocation?",
        "How do I feel at home far from my homeland?",
    ),
}

UPAYA_QUESTIONS: dict[str, tuple[str, str, str, str, str]] = {
    "ru": (
        "Какие упайи подходят моей карте — без «купи камень и забудь»?",
        "Как смягчить напряжённые планеты — не «стать другим человеком»?",
        "Как усилить сильные стороны — опираться, а не чинить?",
        "Какие дни и практики поддержат баланс — без драмы?",
        "Мантры, благотворительность и камни — что реально актуально?",
    ),
    "en": (
        "What upayas fit my chart overall?",
        "How do I soften tense planets?",
        "How do I strengthen the chart's strong sides?",
        "Which days and practices support balance?",
        "Mantras, charity, and gems — what applies to me?",
    ),
}


def _wrap_structured(
    locale: str,
    question: str,
    chart: JyotishChart,
    evidence: str,
    block: str,
    question_index: int,
    *,
    style: str,
    **kwargs,
) -> str:
    structured = build_natal_sphere_structured(
        block,
        chart,
        locale,
        question_index,
        question,
        style=style,
        **kwargs,
    )
    return format_qa_body(
        locale,
        structured.brief,
        "" if not _use_terms(style) else evidence,
        style=style,
        markers=structured.markers,
        practice=structured.practice,
        question=question,
    )


UPAYA_BY_PLANET: dict[str, dict[str, str]] = {
    "ru": {
        "SUN": "воскресенье — уважение к отцу и старшим, солнечный свет, «Om Suryaya Namaha»",
        "MOON": "понедельник — забота о эмоциях, вода, белые тона, «Om Chandraya Namaha»",
        "MARS": "вторник — спорт без агрессии, красные тона умеренно, «Om Mangalaya Namaha»",
        "MERCURY": "среда — обучение, ясная речь, зелёные тона, «Om Budhaya Namaha»",
        "JUPITER": "четверг — наставники, знание, щедрость, «Om Gurave Namaha»",
        "VENUS": "пятница — искусство, гармония в отношениях, «Om Shukraya Namaha»",
        "SATURN": "суббота — дисциплина, служение, масло/кунжут нуждающимся, «Om Shanaye Namaha»",
        "RAHU": "суббота/среда — простота, без резких обходов, дана нуждающимся",
        "KETU": "вторник/четверг — духовная практика, отпускание лишнего, «Om Ketave Namaha»",
    },
    "en": {
        "SUN": "Sunday — respect for father/elders, sunlight, «Om Suryaya Namaha»",
        "MOON": "Monday — emotional care, water, white tones, «Om Chandraya Namaha»",
        "MARS": "Tuesday — sport without aggression, moderate red tones, «Om Mangalaya Namaha»",
        "MERCURY": "Wednesday — learning, clear speech, green tones, «Om Budhaya Namaha»",
        "JUPITER": "Thursday — teachers, wisdom, generosity, «Om Gurave Namaha»",
        "VENUS": "Friday — art, harmony in relationships, «Om Shukraya Namaha»",
        "SATURN": "Saturday — discipline, service, oil/sesame charity, «Om Shanaye Namaha»",
        "RAHU": "Saturday/Wednesday — simplicity, no sharp shortcuts, charity",
        "KETU": "Tuesday/Thursday — spiritual practice, letting go, «Om Ketave Namaha»",
    },
}

GEM_HINT: dict[str, dict[str, str]] = {
    "ru": {
        "SUN": "рубин",
        "MOON": "жемчуг",
        "MARS": "красный коралл",
        "MERCURY": "изумруд",
        "JUPITER": "жёлтый сапфир",
        "VENUS": "алмаз/белый сапфир",
        "SATURN": "синий сапфир",
        "RAHU": "гессонит",
        "KETU": "кошачий глаз",
    },
    "en": {
        "SUN": "ruby",
        "MOON": "pearl",
        "MARS": "red coral",
        "MERCURY": "emerald",
        "JUPITER": "yellow sapphire",
        "VENUS": "diamond/white sapphire",
        "SATURN": "blue sapphire",
        "RAHU": "hessonite",
        "KETU": "cat's eye",
    },
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


BUTTON_TEXT_MAX = 64


def truncate_button_text(text: str, *, max_len: int = BUTTON_TEXT_MAX) -> str:
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def format_numbered_questions(questions: tuple[str, ...] | list[str]) -> str:
    return p(*(f"{idx + 1}️⃣ {h(question)}" for idx, question in enumerate(questions)))


def popular_button_label(locale: str, question_id: str) -> str:
    block = popular_block(locale, question_id)
    return truncate_button_text(f"{block.emoji} {block.title}")


def format_popular_block(block: PopularBlock) -> str:
    return p(
        f"{block.number}️⃣ {block.emoji} {b(block.title)}",
        h(block.question),
    )


def question_button_label(index: int, question: str) -> str:
    prefix = f"{index + 1}. "
    budget = BUTTON_TEXT_MAX - len(prefix)
    return f"{prefix}{truncate_button_text(question, max_len=budget)}"


def family_questions(locale: str) -> tuple[str, str, str, str, str]:
    return FAMILY_QUESTIONS[_lang(locale)]


def family_question_text(locale: str, index: int) -> str:
    questions = family_questions(locale)
    return questions[max(0, min(4, index))]


def finance_questions(locale: str) -> tuple[str, str, str, str, str]:
    return FINANCE_QUESTIONS[_lang(locale)]


def finance_question_text(locale: str, index: int) -> str:
    questions = finance_questions(locale)
    return questions[max(0, min(4, index))]


def karma_questions(locale: str) -> tuple[str, str, str, str, str]:
    return KARMA_QUESTIONS[_lang(locale)]


def karma_question_text(locale: str, index: int) -> str:
    questions = karma_questions(locale)
    return questions[max(0, min(4, index))]


def traits_questions(locale: str) -> tuple[str, str, str, str, str]:
    return TRAITS_QUESTIONS[_lang(locale)]


def traits_question_text(locale: str, index: int) -> str:
    questions = traits_questions(locale)
    return questions[max(0, min(4, index))]


def lineage_questions(locale: str) -> tuple[str, str, str, str, str]:
    return LINEAGE_QUESTIONS[_lang(locale)]


def lineage_question_text(locale: str, index: int) -> str:
    questions = lineage_questions(locale)
    return questions[max(0, min(4, index))]


def health_questions(locale: str) -> tuple[str, str, str, str, str]:
    return HEALTH_QUESTIONS[_lang(locale)]


def health_question_text(locale: str, index: int) -> str:
    questions = health_questions(locale)
    return questions[max(0, min(4, index))]


def purpose_questions(locale: str) -> tuple[str, str, str, str, str]:
    return PURPOSE_QUESTIONS[_lang(locale)]


def purpose_question_text(locale: str, index: int) -> str:
    questions = purpose_questions(locale)
    return questions[max(0, min(4, index))]


def dharma_questions(locale: str) -> tuple[str, str, str, str, str]:
    return DHARMA_QUESTIONS[_lang(locale)]


def dharma_question_text(locale: str, index: int) -> str:
    questions = dharma_questions(locale)
    return questions[max(0, min(4, index))]


def travel_questions(locale: str) -> tuple[str, str, str, str, str]:
    return TRAVEL_QUESTIONS[_lang(locale)]


def travel_question_text(locale: str, index: int) -> str:
    questions = travel_questions(locale)
    return questions[max(0, min(4, index))]


def upaya_questions(locale: str) -> tuple[str, str, str, str, str]:
    return UPAYA_QUESTIONS[_lang(locale)]


def upaya_question_text(locale: str, index: int) -> str:
    questions = upaya_questions(locale)
    return questions[max(0, min(4, index))]


def _upaya_hint(locale: str, planet_key: str) -> str:
    lang = _lang(locale)
    name = _pl(locale, planet_key)
    hint = UPAYA_BY_PLANET[lang].get(planet_key, "")
    return f"{name}: {hint}" if hint else name


def _debilitated_planets(chart: JyotishChart) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
    return [chart.planets[key] for key in order if chart.planets[key].dignity == "debilitated"]


def _strong_planets(chart: JyotishChart) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
    return [
        chart.planets[key]
        for key in order
        if chart.planets[key].dignity in {"exalted", "own"}
    ]


def _tense_planets(chart: JyotishChart) -> list[PlanetPlacement]:
    seen: set[str] = set()
    tense: list[PlanetPlacement] = []
    for pl in (
        *_debilitated_planets(chart),
        chart.planets["SATURN"],
        chart.planets["RAHU"],
        chart.planets["MARS"],
    ):
        if pl.key not in seen:
            seen.add(pl.key)
            tense.append(pl)
    return tense[:4]


def family_block_teaser(locale: str) -> str:
    if _lang(locale) == "ru":
        return (
            "\n\n💍 Отношение / Брак / Семья\n"
            "Любовь, союз и дом — без «несовместимы по звёздам», по-человечески."
        )
    return (
        "\n\n💍 Relationship / Marriage / Family\n"
        "Partnership, union, and home — couple, «your people», and warmth, plain and simple."
    )


def family_picker_intro(locale: str) -> str:
    questions = family_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "💍 Отношение / Брак / Семья\n\n"
            "Про любовь, союз и дом — без «вы несовместимы по звёздам». "
            "Тыкни в вопрос: отвечу по твоей карте, простым языком, местами с улыбкой.\n"
        )
    else:
        header = (
            "💍 Relationship / Marriage / Family\n\n"
            "Partnership, marriage, and family — couple, home, and «your people». "
            "No astro dictionary: pick a question, get a plain answer, sometimes with a smile.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def finance_picker_intro(locale: str) -> str:
    questions = finance_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "💼 Финансы / Инвестиции / Карьера\n\n"
            "Деньги, работа и рост — без «богатство на подходе» и без магии вселенной. "
            "Тыкни в вопрос: разберём по карте, просто и по-человечески.\n"
        )
    else:
        header = (
            "💼 Finance / Investments / Career\n\n"
            "Money, growth, and profession in your chart — "
            "house 2 (resources), house 10 (career), houses 5 and 11 (risk and income), "
            "Venus, Jupiter, Sun, and Saturn.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def karma_picker_intro(locale: str) -> str:
    questions = karma_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "🪷 Прошлые воплощения / Карма\n\n"
            "Уроки, которые жизнь повторяет, пока не скажешь «ага, понял». "
            "Тыкни в вопрос — объясню по карте простым языком, без «ты наказан звёздами».\n"
        )
    else:
        header = (
            "🪷 Past Incarnations / Karma\n\n"
            "Karmic themes in your chart — "
            "house 12 (past experience and release), house 8 (deep lessons), "
            "house 9 (dharma), Saturn, Rahu, and Ketu.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def traits_picker_intro(locale: str) -> str:
    questions = traits_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "✨ Твои изначальные характеристики\n\n"
            "Базовое «я», темп, эмоции и стиль — то, с чем ты пришёл в жизнь, "
            "а не «идеальный человек из Instagram». Тыкни в вопрос — разберём по карте, просто и по-человечески.\n"
        )
    else:
        header = (
            "✨ Your Innate Characteristics\n\n"
            "Inborn temperament and core self in the chart — "
            "Lagna and house 1, Sun, Moon, Mars, and Mercury.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def lineage_picker_intro(locale: str) -> str:
    questions = lineage_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "🌳 Род / Мать / Отец\n\n"
            "Мама, папа, предки и «свои» — не семейный сериал, а живые темы, "
            "которые карта показывает без осуждения. Тыкни в вопрос — разберём по-человечески.\n"
        )
    else:
        header = (
            "🌳 Lineage / Mother / Father\n\n"
            "Lineage, parents, and family roots in the chart — "
            "house 4 (mother, home), house 9 (father, lineage), Moon, Sun, and Jupiter.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def health_picker_intro(locale: str) -> str:
    questions = health_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "💪 Здоровье / Тело\n\n"
            "Энергия, режим и восстановление — без «просто соберись» и без Google вместо врача. "
            "Тыкни в вопрос: разберём по карте, по-человечески, иногда с улыбкой.\n"
        )
    else:
        header = (
            "💪 Health / Body\n\n"
            "Body, energy, and recovery in the chart — "
            "house 1 (body), house 6 (health and routine), house 8 (deep processes), "
            "Sun, Moon, Mars, and Saturn.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def purpose_picker_intro(locale: str) -> str:
    questions = purpose_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "🎯 Предназначение / Таланты / Реализация\n\n"
            "Смысл, дар и своё дело — не «найди призвание за 5 минут по YouTube». "
            "Тыкни в вопрос: разберём по карте, просто и по-человечески.\n"
        )
    else:
        header = (
            "🎯 Purpose / Talents / Realization\n\n"
            "Meaning, gift, and path of realization in the chart — "
            "house 9 (dharma), house 5 (talent), house 10 (work), "
            "Sun, Jupiter, and Lagna.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def dharma_picker_intro(locale: str) -> str:
    questions = dharma_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "🕉️ Духовность / Путь / Дхарма\n\n"
            "Смысл, вера и «зачем я здесь» — без мистического тумана и без «просветись за 3 дня». "
            "Тыкни в вопрос: разберём по карте, просто и по-человечески.\n"
        )
    else:
        header = (
            "🕉️ Spirituality / Path / Dharma\n\n"
            "Spiritual path and dharma in the chart — "
            "house 9 (faith, meaning, guidance), house 12 (moksha, solitude), "
            "Jupiter, Ketu, and Sun.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def travel_picker_intro(locale: str) -> str:
    questions = travel_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "✈️ Эмиграция / Путешествия\n\n"
            "Переезд, дорога и «жизнь за границей» — без «сбеги от себя, станешь другим». "
            "Тыкни в вопрос: разберём по карте, просто и по-человечески.\n"
        )
    else:
        header = (
            "✈️ Emigration / Travel\n\n"
            "Relocation and travel in the chart — "
            "house 9 (long journeys), house 12 (life abroad), "
            "house 3 (the road), Rahu, Jupiter, and Moon.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def upaya_picker_intro(locale: str) -> str:
    questions = upaya_questions(locale)
    if _lang(locale) == "ru":
        header = (
            "🪬 Гармонизация / Упайи\n\n"
            "Баланс по карте — режим, мантры, добрые дела и честность с собой. "
            "Не «магический шопинг», а практики, которые реально работают. Тыкни в вопрос.\n"
        )
    else:
        header = (
            "🪬 Harmonization / Upayas\n\n"
            "Balance methods from your chart — planetary days, mantras, charity, "
            "and conscious work with weak and tense indicators.\n"
        )
    if _lang(locale) == "ru":
        title = "❓ Вопросы по натальной карте"
    else:
        title = "❓ Natal chart questions"
    return p(b(title), header.strip(), format_numbered_questions(questions))


def popular_blocks_text(locale: str) -> str:
    blocks = popular_blocks(locale)
    if _lang(locale) == "ru":
        intro = p(
            b("🔥 Популярные вопросы"),
            h("Тыкни в вопрос — разберу по твоей карте, без сухой теории."),
        )
    else:
        intro = p(
            b("🔥 Popular questions"),
            h("Pick a question — the answer comes from your chart."),
        )
    body = p(*(format_popular_block(block) for block in blocks))
    return p(intro, body)


def qa_picker_intro(locale: str) -> str:
    if _lang(locale) == "ru":
        return p(
            b("❓ Вопросы по натальной карте"),
            h("Выбери раздел — и посмотрим, как это у тебя работает в жизни."),
            h(
                "🔥 Популярные вопросы — коротко по самым частым темам.\n"
                "💍 Отношение / Брак / Семья — любовь, союз и дом без «несовместимы по звёздам».\n"
                "💼 Финансы / Инвестиции / Карьера — деньги и работа без «богатство на подходе».\n"
                "🪷 Прошлые воплощения / Карма — уроки и повторы без «наказаны звёздами».\n"
                "✨ Твои изначальные характеристики — базовое «я» без «идеального человека из Instagram».\n"
            ),
            h(
                "🌳 Род / Мать / Отец — мама, папа и корни без семейного сериала.\n"
                "💪 Здоровье / Тело — энергия и режим без «просто соберись».\n"
                "🎯 Предназначение / Таланты / Реализация — смысл и дело без «призвание за 5 минут».\n"
                "🕉️ Духовность / Путь / Дхарма — смысл без «просветись за 3 дня».\n"
                "✈️ Эмиграция / Путешествия — переезд и дорога без «сбеги от себя».\n"
            ),
            h(
                "🪬 Гармонизация / Упайи — баланс без «купи камень и забудь»."
            ),
        )
    return p(
        b("❓ Natal chart questions"),
        h("Pick a section — the answer comes from your chart."),
        h(
            "🔥 Popular questions — main chart themes.\n"
            "💍 Relationship / Marriage / Family — partnership, union, and home.\n"
            "💼 Finance / Investments / Career — money, growth, and profession.\n"
            "🪷 Past Incarnations / Karma — lessons, past experience, and awareness.\n"
            "✨ Your Innate Characteristics — temperament, self, and inborn qualities."
        ),
        h(
            "🌳 Lineage / Mother / Father — parents, ancestors, and family roots.\n"
            "💪 Health / Body — energy, routine, and self-care.\n"
            "🎯 Purpose / Talents / Realization — meaning, gift, and your calling.\n"
            "🕉️ Spirituality / Path / Dharma — faith, meaning, and spiritual practice.\n"
            "✈️ Emigration / Travel — relocation, the road, and life abroad."
        ),
        h(
            "🪬 Harmonization / Upayas — balance practices, mantras, and charity."
        ),
    )


def popular_list_intro(locale: str) -> str:
    if _lang(locale) == "ru":
        return p(b("❓ Вопросы по натальной карте"), popular_blocks_text(locale))
    return p(b("❓ Natal chart questions"), popular_blocks_text(locale))


def popular_picker_intro(locale: str) -> str:
    return qa_picker_intro(locale)


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
                f"тема идёт через {plain_role(locale, lord.key)} ({lord_sign})."
            )
        if _use_terms(style):
            focus_bits = {
                "strength": f"{lord_name} в {lord_sign} даёт опору: здесь проявляется сила этой темы.",
                "challenge": f"Следи за перекосом через {lord_name} в {lord_sign} — там же и типичное напряжение.",
                "default": f"Ключ — {lord_name} в {lord_sign}: через него эта сфера «оживает» в карте.",
            }
        else:
            role = plain_role(locale, lord.key)
            focus_bits = {
                "strength": f"{role.capitalize()} ({lord_sign}) — тут твоя опора в этой теме.",
                "challenge": f"Следи, где {role} ({lord_sign}) перегибает — там обычно и ссора с собой.",
                "default": f"Ключ — {role} ({lord_sign}): через это сфера «оживает».",
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

    body = _wrap_structured(
        locale, question, chart, body, "house", question_index,
        style=style, house=house, focus=focus,
    )

    sphere = _sphere_label(locale, house, style=style)
    if lang == "ru":
        header = f"Сфера: {sphere}"
    else:
        header = f"Sphere: {sphere}"
    return qa_response(header, question, body)


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
                else "Романтика и притяжение — про пару, нежность и эмоции. "
            )
        else:
            intro = (
                "Romance and attraction — house 7, Venus, and Moon. "
                if _use_terms(style)
                else "Romance and attraction — partnership, feelings, and warmth. "
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
                    f"Притяжение и тип партнёра — кого ты выбираешь и кто выбирает тебя "
                    f"(линия «{h7_sign}»). "
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
                else "Брак и долгий союз — как у тебя устроена близость на длинной дистанции, не «дата штампа». "
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
                else "Семья и дом — где сердце выдыхает или сжимается; Луна показывает, как ты это чувствуешь. "
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
                else "Трения в паре и семье — резкость, границы и повторяющиеся ссоры, не «вы несовместимы». "
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

    structured = build_family_structured(
        chart, locale, question_index, question, style=style
    )
    body = format_qa_body(
        locale,
        structured.brief,
        body,
        style=style,
        markers=structured.markers,
        practice=structured.practice,
        question=question,
    )

    if lang == "ru":
        header = "💍 Отношение / Брак / Семья"
    else:
        header = "💍 Relationship / Marriage / Family"
    return qa_response(header, question, body)


def build_finance_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = finance_question_text(locale, question_index)
    venus = chart.planets["VENUS"]
    jupiter = chart.planets["JUPITER"]
    sun = chart.planets["SUN"]
    saturn = chart.planets["SATURN"]
    mars = chart.planets["MARS"]
    rahu = chart.planets["RAHU"]
    h2_planets = _planets_in_house(chart, 2)
    h5_planets = _planets_in_house(chart, 5)
    h8_planets = _planets_in_house(chart, 8)
    h10_planets = _planets_in_house(chart, 10)
    h11_planets = _planets_in_house(chart, 11)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h2_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 2), style=style)]
        if lang == "ru":
            intro = (
                "Деньги и ценности — 2-й дом, Венера и Юпитер. "
                if _use_terms(style)
                else "Деньги и ценности — сфера ресурсов, Венера и Юпитер. "
            )
        else:
            intro = (
                "Money and values — house 2, Venus, and Jupiter. "
                if _use_terms(style)
                else "Money and values — resources, Venus, and Jupiter. "
            )
        body = (
            f"{intro}{_render_planet(locale, venus, style=style)} "
            f"{_render_planet(locale, jupiter, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 1:
        bits = [_render_planet(locale, pl, style=style) for pl in h10_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 10), style=style)]
        if lang == "ru":
            intro = (
                "Карьера и реализация — 10-й дом, Солнце и Сатурн. "
                if _use_terms(style)
                else "Карьера и реализация — сфера статуса, Солнце и Сатурн. "
            )
            tail = (
                " 10-й дом насыщен — профессиональная линия для тебя судьбоносна."
                if chart.house_planet_count.get(10, 0) >= 2
                else ""
            )
        else:
            intro = (
                "Career and realization — house 10, Sun, and Saturn. "
                if _use_terms(style)
                else "Career and realization — status, Sun, and Saturn. "
            )
            tail = (
                " A packed 10th house makes profession a life-defining line."
                if chart.house_planet_count.get(10, 0) >= 2
                else ""
            )
        body = (
            f"{intro}{_render_planet(locale, sun, style=style)} "
            f"{_render_planet(locale, saturn, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    elif question_index == 2:
        bits: list[str] = []
        seen_pl: set[str] = set()
        for pl in (*h5_planets, *h8_planets, mars, rahu):
            if pl.key not in seen_pl and (pl.house in {5, 8} or pl.key in {"MARS", "RAHU"}):
                seen_pl.add(pl.key)
                bits.append(_render_planet(locale, pl, style=style))
        if not bits:
            bits = [
                _render_planet(locale, _lord_placement(chart, 5), style=style),
                _render_planet(locale, _lord_placement(chart, 8), style=style),
            ]
        if lang == "ru":
            intro = (
                "Инвестиции и риск — 5-й дом (спекуляция), 8-й дом (чужие ресурсы), "
                "Марс и Раху как показатели смелости и нестандартных ставок. "
                if _use_terms(style)
                else "Инвестиции и риск — темы ставок и чужих ресурсов, смелость и нестандартные решения. "
            )
        else:
            intro = (
                "Investments and risk — house 5 (speculation), house 8 (others' resources), "
                "Mars and Rahu as bold and unconventional bets. "
                if _use_terms(style)
                else "Investments and risk — betting themes, courage, and unconventional moves. "
            )
        body = f"{intro}{' '.join(bits[:3])}".strip()

    elif question_index == 3:
        bits = [_render_planet(locale, pl, style=style) for pl in h11_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 11), style=style)]
        lord2 = _lord_placement(chart, 2)
        if lang == "ru":
            intro = (
                "Доход и рост — 2-й и 11-й дома, их управители, Юпитер как расширение. "
                if _use_terms(style)
                else "Доход и рост — ресурсы, цели и выгода, Юпитер как расширение. "
            )
        else:
            intro = (
                "Income and growth — houses 2 and 11, their lords, Jupiter as expansion. "
                if _use_terms(style)
                else "Income and growth — resources, goals, and gain, Jupiter as expansion. "
            )
        body = (
            f"{intro}{_render_planet(locale, jupiter, style=style)} "
            f"{_render_planet(locale, lord2, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    else:
        h12_planets = _planets_in_house(chart, 12)
        bits: list[str] = []
        seen: set[str] = set()
        for pl in (saturn, rahu, mars, *h8_planets, *h12_planets):
            if pl.key in {"SATURN", "RAHU", "MARS"} and pl.key not in seen:
                seen.add(pl.key)
                bits.append(_render_planet(locale, pl, style=style))
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 2), style=style)]
        if lang == "ru":
            intro = (
                "Финансовые риски часто идут через Сатурн, Раху, 8-й и 12-й дома — "
                "долги, потери, импульсивные траты и переоценка риска. "
                if _use_terms(style)
                else "Финансовые риски часто связаны с ограничениями, импульсом и темами потерь и долгов. "
            )
            tail = " Следи за поспешными решениями и обещаниями «быстрого дохода»."
        else:
            intro = (
                "Financial risks often run through Saturn, Rahu, houses 8 and 12 — "
                "debts, losses, impulsive spending, and misjudged risk. "
                if _use_terms(style)
                else "Financial risks often tie to limits, impulse, and themes of loss and debt. "
            )
            tail = " Watch hasty decisions and promises of «easy money»."
        body = f"{intro}{' '.join(bits[:3])}{tail}".strip()

    body = _wrap_structured(locale, question, chart, body, "finance", question_index, style=style)

    if lang == "ru":
        header = "💼 Финансы / Инвестиции / Карьера"
    else:
        header = "💼 Finance / Investments / Career"
    return qa_response(header, question, body)


def build_karma_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = karma_question_text(locale, question_index)
    saturn = chart.planets["SATURN"]
    rahu = chart.planets["RAHU"]
    ketu = chart.planets["KETU"]
    jupiter = chart.planets["JUPITER"]
    moon = chart.planets["MOON"]
    h8_planets = _planets_in_house(chart, 8)
    h9_planets = _planets_in_house(chart, 9)
    h12_planets = _planets_in_house(chart, 12)

    if question_index == 0:
        bits: list[str] = []
        for house in (8, 12):
            house_bits = [_render_planet(locale, pl, style=style) for pl in _planets_in_house(chart, house)[:1]]
            bits.extend(house_bits)
        if not bits:
            bits = [
                _render_planet(locale, _lord_placement(chart, 12), style=style),
                _render_planet(locale, _lord_placement(chart, 8), style=style),
            ]
        if lang == "ru":
            intro = (
                "Главная кармическая линия часто звучит через 8-й и 12-й дома — "
                "глубинные уроки, отпускание и то, что тянется из прошлого. "
                if _use_terms(style)
                else "Главная кармическая линия — глубинные уроки, отпускание и то, что тянется из прошлого. "
            )
        else:
            intro = (
                "The main karmic line often runs through houses 8 and 12 — "
                "deep lessons, release, and what carries over from the past. "
                if _use_terms(style)
                else "The main karmic line — deep lessons, release, and what carries from the past. "
            )
        body = f"{intro}{' '.join(bits[:2])} {_render_planet(locale, saturn, style=style)}".strip()

    elif question_index == 1:
        bits = [_render_planet(locale, pl, style=style) for pl in h12_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 12), style=style)]
        if lang == "ru":
            intro = (
                "Прошлые воплощения и отпечаток прошлого — Кету, 12-й дом и Луна как память души. "
                if _use_terms(style)
                else "Прошлый опыт и отпечаток души — Кету, тема уединения и Луна как внутренняя память. "
            )
        else:
            intro = (
                "Past incarnations and the past's imprint — Ketu, house 12, and the Moon as soul memory. "
                if _use_terms(style)
                else "Past experience and soul imprint — Ketu, solitude themes, and the Moon as inner memory. "
            )
        body = (
            f"{intro}{_render_planet(locale, ketu, style=style)} "
            f"{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 2:
        lord_sat = _lord_placement(chart, saturn.house)
        if lang == "ru":
            intro = (
                "Сатурн — учитель кармы: задержки, дисциплина и уроки, которые нельзя обойти. "
                if _use_terms(style)
                else "Сатурн — учитель терпения и ответственности: уроки, которые нельзя обойти. "
            )
            tail = " Не спеши — Сатурн награждает за честный труд и зрелость, а не за обход."
        else:
            intro = (
                "Saturn is the karmic teacher — delays, discipline, and lessons you cannot skip. "
                if _use_terms(style)
                else "Saturn teaches patience and responsibility — lessons you cannot skip. "
            )
            tail = " Do not rush — Saturn rewards honest work and maturity, not shortcuts."
        body = (
            f"{intro}{_render_planet(locale, saturn, style=style)} "
            f"{_render_planet(locale, lord_sat, style=style)}{tail}"
        ).strip()

    elif question_index == 3:
        bits = [
            _render_planet(locale, rahu, style=style),
            _render_planet(locale, ketu, style=style),
        ]
        if h8_planets:
            bits.append(_render_planet(locale, h8_planets[0], style=style))
        if lang == "ru":
            intro = (
                "Раху и Кету — кармическая ось: незакрытые желания и навыки из прошлого, "
                "которые тянут в эту жизнь. "
                if _use_terms(style)
                else "Раху и Кету — ось прошлого и будущего: тяга к новому и отпускание старого. "
            )
        else:
            intro = (
                "Rahu and Ketu are the karmic axis — unfinished desires and past skills "
                "pulling into this life. "
                if _use_terms(style)
                else "Rahu and Ketu — the axis of past and future: craving the new and releasing the old. "
            )
        body = f"{intro}{' '.join(bits)}".strip()

    else:
        bits = [_render_planet(locale, pl, style=style) for pl in h9_planets[:1]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 9), style=style)]
        if lang == "ru":
            intro = (
                "Осознанная карма — через 9-й дом, Юпитер и дхарму: смысл, веру и правильный путь. "
                if _use_terms(style)
                else "Осознанная карма — через смысл, веру и выбор пути, который опирается на ценности. "
            )
            tail = (
                " Замечай повторяющиеся сценарии — это не наказание, а приглашение вырасти."
            )
        else:
            intro = (
                "Conscious karma — through house 9, Jupiter, and dharma: meaning, faith, and right path. "
                if _use_terms(style)
                else "Conscious karma — through meaning, faith, and choices aligned with values. "
            )
            tail = " Notice repeating patterns — not punishment, but an invitation to grow."
        body = (
            f"{intro}{_render_planet(locale, jupiter, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    body = _wrap_structured(locale, question, chart, body, "karma", question_index, style=style)

    if lang == "ru":
        header = "🪷 Прошлые воплощения / Карма"
    else:
        header = "🪷 Past Incarnations / Karma"
    return qa_response(header, question, body)


def build_traits_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    from app.jyotish_text import LAGNA_ESSENCE, _derive_summary, _list_to_prose

    lang = _lang(locale)
    question = traits_question_text(locale, question_index)
    sun = chart.planets["SUN"]
    moon = chart.planets["MOON"]
    mars = chart.planets["MARS"]
    mercury = chart.planets["MERCURY"]
    h1_planets = _planets_in_house(chart, 1)
    h3_planets = _planets_in_house(chart, 3)
    lagna = sign_label(locale, chart.lagna_sign)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h1_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 1), style=style)]
        if lang == "ru":
            if _use_terms(style):
                lead = f"Лагна в {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            else:
                lead = f"Вход в жизнь через {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            intro = (
                "Суть карты начинается с Лагны и 1-го дома — базовый образ «я». "
                if _use_terms(style)
                else "Суть карты — твой базовый образ «я» и то, как ты входишь в жизнь. "
            )
        else:
            if _use_terms(style):
                lead = f"Lagna in {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            else:
                lead = f"Rising through {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            intro = (
                "The chart begins with Lagna and house 1 — your baseline sense of self. "
                if _use_terms(style)
                else "The chart's core — your baseline self and how you enter life. "
            )
        body = f"{intro}{lead} {' '.join(bits)}".strip()

    elif question_index == 1:
        if lang == "ru":
            intro = (
                "Темперамент и энергия — Солнце как стержень и Марс как драйв и напор. "
                if _use_terms(style)
                else "Темперамент и энергия — внутренний стержень и напор действия. "
            )
        else:
            intro = (
                "Temperament and energy — the Sun as core and Mars as drive and push. "
                if _use_terms(style)
                else "Temperament and energy — inner core and the push to act. "
            )
        body = (
            f"{intro}{_render_planet(locale, sun, style=style)} "
            f"{_render_planet(locale, mars, style=style)}"
        ).strip()

    elif question_index == 2:
        h4_planets = _planets_in_house(chart, 4)
        bits = [_render_planet(locale, pl, style=style) for pl in h4_planets[:1]]
        if lang == "ru":
            intro = (
                "Эмоции и внутренний мир — Луна как ум и 4-й дом как чувство дома внутри. "
                if _use_terms(style)
                else "Эмоции и внутренний мир — Луна как настроение и потребность в опоре. "
            )
        else:
            intro = (
                "Emotions and inner life — the Moon as mind and house 4 as inner belonging. "
                if _use_terms(style)
                else "Emotions and inner life — the Moon as mood and need for support. "
            )
        body = (
            f"{intro}{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 3:
        bits = [_render_planet(locale, pl, style=style) for pl in h3_planets[:1]]
        if lang == "ru":
            intro = (
                "Действие и речь — 3-й дом, Марс и Меркурий: как рискуешь, говоришь и заявляешь о себе. "
                if _use_terms(style)
                else "Действие и речь — как рискуешь, говоришь и заявляешь о себе. "
            )
        else:
            intro = (
                "Action and speech — house 3, Mars, and Mercury: how you risk, speak, and show up. "
                if _use_terms(style)
                else "Action and speech — how you risk, speak, and show up. "
            )
        body = (
            f"{intro}{_render_planet(locale, mars, style=style)} "
            f"{_render_planet(locale, mercury, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    else:
        strengths, weaknesses, _, _ = _derive_summary(chart, lang)
        bits = [_render_planet(locale, pl, style=style) for pl in h1_planets[:1]]
        if not bits:
            bits = [_render_planet(locale, sun, style=style)]
        if lang == "ru":
            intro = (
                "Врождённые качества — 1-й дом, Солнце и сильные стороны карты. "
                if _use_terms(style)
                else "Врождённые качества — базовый образ и природные сильные стороны. "
            )
            body = (
                f"{intro}{' '.join(bits)} "
                f"Сильные стороны — {_list_to_prose(strengths, lang)}. "
                f"Сложнее проявляются {_list_to_prose(weaknesses, lang)}."
            ).strip()
        else:
            intro = (
                "Inborn qualities — house 1, Sun, and the chart's strong sides. "
                if _use_terms(style)
                else "Inborn qualities — baseline self and natural strengths. "
            )
            body = (
                f"{intro}{' '.join(bits)} "
                f"Strengths — {_list_to_prose(strengths, lang)}. "
                f"Harder to express: {_list_to_prose(weaknesses, lang)}."
            ).strip()

    body = _wrap_structured(locale, question, chart, body, "traits", question_index, style=style)

    if lang == "ru":
        header = "✨ Твои изначальные характеристики"
    else:
        header = "✨ Your Innate Characteristics"
    return qa_response(header, question, body)


def build_lineage_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = lineage_question_text(locale, question_index)
    moon = chart.planets["MOON"]
    sun = chart.planets["SUN"]
    jupiter = chart.planets["JUPITER"]
    saturn = chart.planets["SATURN"]
    rahu = chart.planets["RAHU"]
    h4_planets = _planets_in_house(chart, 4)
    h9_planets = _planets_in_house(chart, 9)
    lord4 = _lord_placement(chart, 4)
    lord9 = _lord_placement(chart, 9)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h4_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord4, style=style)]
        if lang == "ru":
            intro = (
                "Мать и эмоциональная связь — 4-й дом, Луна как показатель матери и внутреннего дома. "
                if _use_terms(style)
                else "Мать и эмоциональная связь — тема дома и Луна как чувство материнской опоры. "
            )
        else:
            intro = (
                "Mother and emotional bond — house 4, the Moon as mother and inner home. "
                if _use_terms(style)
                else "Mother and emotional bond — home themes and the Moon as maternal support. "
            )
        body = (
            f"{intro}{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 1:
        bits = [_render_planet(locale, pl, style=style) for pl in h9_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord9, style=style)]
        if lang == "ru":
            intro = (
                "Отец и его влияние — 9-й дом, Солнце как показатель отца и внутреннего авторитета. "
                if _use_terms(style)
                else "Отец и его влияние — тема наставничества и Солнце как образ отца и опоры. "
            )
        else:
            intro = (
                "Father and his influence — house 9, the Sun as father and inner authority. "
                if _use_terms(style)
                else "Father and his influence — guidance themes and the Sun as father figure. "
            )
        body = (
            f"{intro}{_render_planet(locale, sun, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 2:
        bits = [
            _render_planet(locale, lord4, style=style),
            _render_planet(locale, lord9, style=style),
        ]
        if h4_planets:
            bits.append(_render_planet(locale, h4_planets[0], style=style))
        if lang == "ru":
            intro = (
                "Род и предки — 4-й дом (семейные корни) и 9-й дом (род, традиция, дхарма рода). "
                if _use_terms(style)
                else "Род и предки — семейные корни и тема традиции, передаваемой через род. "
            )
        else:
            intro = (
                "Lineage and ancestors — house 4 (family roots) and house 9 (lineage, tradition). "
                if _use_terms(style)
                else "Lineage and ancestors — family roots and tradition passed through the line. "
            )
        body = f"{intro}{' '.join(bits[:3])} {_render_planet(locale, jupiter, style=style)}".strip()

    elif question_index == 3:
        bits = [_render_planet(locale, pl, style=style) for pl in h4_planets[:1]]
        if lang == "ru":
            intro = (
                "Семейная опора — 4-й дом, Луна и Юпитер как чувство защищённости и «своих». "
                if _use_terms(style)
                else "Семейная опора — дом, Луна и Юпитер как чувство защищённости и «своих». "
            )
            tail = " Это база, на которую можно опираться, даже если связь с родом была непростой."
        else:
            intro = (
                "Family support — house 4, Moon, and Jupiter as safety and belonging. "
                if _use_terms(style)
                else "Family support — home, Moon, and Jupiter as safety and belonging. "
            )
            tail = " This is a base you can lean on, even if the bond with family was not easy."
        body = (
            f"{intro}{_render_planet(locale, moon, style=style)} "
            f"{_render_planet(locale, jupiter, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    else:
        bits: list[str] = []
        seen: set[str] = set()
        for pl in (saturn, rahu, moon, sun):
            if pl.key not in seen:
                seen.add(pl.key)
                bits.append(_render_planet(locale, pl, style=style))
        if lang == "ru":
            intro = (
                "Сложности с родителями и родом часто идут через напряжённые положения в 4-м и 9-м домах, "
                "Сатурн, Раху, Луну и Солнце. "
                if _use_terms(style)
                else "Сложности с родителями и родом часто связаны с дистанцией, ожиданиями и старыми сценариями. "
            )
            tail = " Это не приговор — замечай повторяющиеся паттерны, чтобы исцелять, а не повторять."
        else:
            intro = (
                "Parent and lineage friction often runs through tense 4th/9th-house themes, "
                "Saturn, Rahu, Moon, and Sun. "
                if _use_terms(style)
                else "Parent and lineage friction often ties to distance, expectations, and old scripts. "
            )
            tail = " Not a verdict — notice repeating patterns to heal rather than repeat."
        body = f"{intro}{' '.join(bits[:4])}{tail}".strip()

    body = _wrap_structured(locale, question, chart, body, "lineage", question_index, style=style)

    if lang == "ru":
        header = "🌳 Род / Мать / Отец"
    else:
        header = "🌳 Lineage / Mother / Father"
    return qa_response(header, question, body)


def build_health_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = health_question_text(locale, question_index)
    sun = chart.planets["SUN"]
    moon = chart.planets["MOON"]
    mars = chart.planets["MARS"]
    saturn = chart.planets["SATURN"]
    h1_planets = _planets_in_house(chart, 1)
    h6_planets = _planets_in_house(chart, 6)
    h8_planets = _planets_in_house(chart, 8)
    lord1 = _lord_placement(chart, 1)
    lord6 = _lord_placement(chart, 6)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h1_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord1, style=style)]
        if lang == "ru":
            intro = (
                "Тело и жизненная энергия — 1-й дом, Солнце как витальность и Марс как напор. "
                if _use_terms(style)
                else "Тело и жизненная энергия — базовая конституция, внутренний огонь и напор. "
            )
        else:
            intro = (
                "Body and life energy — house 1, the Sun as vitality and Mars as drive. "
                if _use_terms(style)
                else "Body and life energy — baseline constitution, inner fire, and drive. "
            )
        body = (
            f"{intro}{_render_planet(locale, sun, style=style)} "
            f"{_render_planet(locale, mars, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 1:
        bits = [_render_planet(locale, pl, style=style) for pl in h6_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord6, style=style)]
        if lang == "ru":
            intro = (
                "На что смотреть в здоровье — 6-й дом, его управитель и ежедневный режим. "
                if _use_terms(style)
                else "На что смотреть в здоровье — привычки, нагрузка и то, что легко игнорировать. "
            )
        else:
            intro = (
                "What to watch in health — house 6, its lord, and daily routine. "
                if _use_terms(style)
                else "What to watch in health — habits, load, and what is easy to ignore. "
            )
        body = f"{intro}{' '.join(bits)} {_render_planet(locale, saturn, style=style)}".strip()

    elif question_index == 2:
        h4_planets = _planets_in_house(chart, 4)
        bits = [_render_planet(locale, pl, style=style) for pl in h4_planets[:1]]
        if lang == "ru":
            intro = (
                "Силы и восстановление — Луна, 4-й дом и качество отдыха. "
                if _use_terms(style)
                else "Силы и восстановление — Луна, отдых и чувство внутренней опоры. "
            )
            tail = " Без восстановления даже сильная карта быстро выгорает."
        else:
            intro = (
                "Strength and recovery — the Moon, house 4, and quality of rest. "
                if _use_terms(style)
                else "Strength and recovery — the Moon, rest, and inner support. "
            )
            tail = " Without recovery, even a strong chart burns out fast."
        body = (
            f"{intro}{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    elif question_index == 3:
        bits: list[str] = []
        seen: set[str] = set()
        for pl in (*h6_planets, *h8_planets, saturn, mars):
            if pl.key not in seen:
                seen.add(pl.key)
                bits.append(_render_planet(locale, pl, style=style))
        if not bits:
            bits = [_render_planet(locale, lord6, style=style)]
        if lang == "ru":
            intro = (
                "Слабые места часто идут через 6-й и 8-й дома, Сатурн и Марс — "
                "хроническое напряжение, воспаление, переутомление. "
                if _use_terms(style)
                else "Слабые места часто связаны с перегрузом, хроническим напряжением и игнорированием сигналов тела. "
            )
        else:
            intro = (
                "Weak spots often run through houses 6 and 8, Saturn, and Mars — "
                "chronic tension, inflammation, overwork. "
                if _use_terms(style)
                else "Weak spots often tie to overload, chronic tension, and ignored body signals. "
            )
        body = f"{intro}{' '.join(bits[:3])}".strip()

    else:
        if lang == "ru":
            intro = (
                "Забота о теле — стабильный режим, 6-й дом и баланс Марса (нагрузка) с Луной (отдых). "
                if _use_terms(style)
                else "Забота о теле — режим, умеренная нагрузка и достаточный отдых. "
            )
            tail = (
                " Это астрологический взгляд — при симптомах обращайся к врачу, а не только к карте."
            )
        else:
            intro = (
                "Body care — steady routine, house 6, and balancing Mars (load) with Moon (rest). "
                if _use_terms(style)
                else "Body care — routine, moderate load, and enough rest. "
            )
            tail = " This is an astrological view — see a doctor for symptoms, not the chart alone."
        body = (
            f"{intro}{_render_planet(locale, lord6, style=style)} "
            f"{_render_planet(locale, mars, style=style)} "
            f"{_render_planet(locale, moon, style=style)}{tail}"
        ).strip()

    body = _wrap_structured(locale, question, chart, body, "health", question_index, style=style)

    if lang == "ru":
        header = "💪 Здоровье / Тело"
    else:
        header = "💪 Health / Body"
    return qa_response(header, question, body)


def build_purpose_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    from app.jyotish_text import LAGNA_ESSENCE, _derive_summary, _list_to_prose

    lang = _lang(locale)
    question = purpose_question_text(locale, question_index)
    sun = chart.planets["SUN"]
    jupiter = chart.planets["JUPITER"]
    saturn = chart.planets["SATURN"]
    mercury = chart.planets["MERCURY"]
    venus = chart.planets["VENUS"]
    h5_planets = _planets_in_house(chart, 5)
    h9_planets = _planets_in_house(chart, 9)
    h10_planets = _planets_in_house(chart, 10)
    lord9 = _lord_placement(chart, 9)
    lord10 = _lord_placement(chart, 10)
    strengths, weaknesses, risks, opportunities = _derive_summary(chart, lang)
    lagna = sign_label(locale, chart.lagna_sign)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h9_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord9, style=style)]
        if lang == "ru":
            if _use_terms(style):
                lead = f"Лагна в {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            else:
                lead = f"Вход в жизнь через {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            intro = (
                "Предназначение — 9-й дом (дхарма), Солнце и Юпитер как смысл и направление. "
                if _use_terms(style)
                else "Предназначение — смысл, вера в свой путь и направление жизни. "
            )
        else:
            if _use_terms(style):
                lead = f"Lagna in {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            else:
                lead = f"Rising through {lagna} — {LAGNA_ESSENCE[lang][chart.lagna_sign]}."
            intro = (
                "Purpose — house 9 (dharma), Sun, and Jupiter as meaning and direction. "
                if _use_terms(style)
                else "Purpose — meaning, faith in your path, and life direction. "
            )
        body = (
            f"{intro}{lead} "
            f"{_render_planet(locale, sun, style=style)} "
            f"{_render_planet(locale, jupiter, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 1:
        bits = [_render_planet(locale, pl, style=style) for pl in h5_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, _lord_placement(chart, 5), style=style)]
        if lang == "ru":
            intro = (
                "Таланты — 5-й дом, Меркурий и Венера как ум, творчество и природный дар. "
                if _use_terms(style)
                else "Таланты — творчество, ум и то, что даётся легко и с радостью. "
            )
            tail = f" Сильные стороны — {_list_to_prose(strengths, lang)}."
        else:
            intro = (
                "Talents — house 5, Mercury, and Venus as mind, creativity, and natural gift. "
                if _use_terms(style)
                else "Talents — creativity, mind, and what comes easily with joy. "
            )
            tail = f" Strengths — {_list_to_prose(strengths, lang)}."
        body = (
            f"{intro}{_render_planet(locale, mercury, style=style)} "
            f"{_render_planet(locale, venus, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    elif question_index == 2:
        bits = [_render_planet(locale, pl, style=style) for pl in h10_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord10, style=style)]
        if lang == "ru":
            intro = (
                "Реализация и своё дело — 10-й дом, Солнце и Сатурн как путь статуса и зрелости. "
                if _use_terms(style)
                else "Реализация и своё дело — путь статуса, ответственности и зрелого труда. "
            )
            tail = (
                " 10-й дом насыщен — профессиональная линия для тебя судьбоносна."
                if chart.house_planet_count.get(10, 0) >= 2
                else ""
            )
        else:
            intro = (
                "Realization and calling — house 10, Sun, and Saturn as status and maturity. "
                if _use_terms(style)
                else "Realization and calling — status, responsibility, and mature work. "
            )
            tail = (
                " A packed 10th house makes profession a life-defining line."
                if chart.house_planet_count.get(10, 0) >= 2
                else ""
            )
        body = (
            f"{intro}{_render_planet(locale, sun, style=style)} "
            f"{_render_planet(locale, saturn, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    elif question_index == 3:
        if lang == "ru":
            intro = (
                "Реализации помогают сильные стороны и Юпитер; мешают слабые зоны, Сатурн и риск «{risks}». "
                if _use_terms(style)
                else "Реализации помогают сильные стороны; мешают слабые зоны и повторяющийся риск «{risks}». "
            ).format(risks=risks)
            body = (
                f"{intro}"
                f"Помогает: {_list_to_prose(strengths, lang)}. "
                f"Мешает: {_list_to_prose(weaknesses, lang)}. "
                f"{_render_planet(locale, jupiter, style=style)} "
                f"{_render_planet(locale, saturn, style=style)}"
            ).strip()
        else:
            intro = (
                "Realization is helped by strengths and Jupiter; blocked by weak spots, Saturn, and «{risks}». "
                if _use_terms(style)
                else "Strengths help realization; weak spots and repeating «{risks}» get in the way. "
            ).format(risks=risks)
            body = (
                f"{intro}"
                f"Helps: {_list_to_prose(strengths, lang)}. "
                f"Blocks: {_list_to_prose(weaknesses, lang)}. "
                f"{_render_planet(locale, jupiter, style=style)} "
                f"{_render_planet(locale, saturn, style=style)}"
            ).strip()

    else:
        if chart.stellium_house and chart.stellium_sign:
            st_sign = sign_label(locale, chart.stellium_sign)
            theme = _house_theme(locale, chart.stellium_house)
            if lang == "ru":
                if _use_terms(style):
                    focus = (
                        f"Стеллиум в {st_sign} в {chart.stellium_house}-м доме («{theme}») — "
                        "сюда стоит вести главную энергию."
                    )
                else:
                    focus = (
                        f"Несколько планет в {st_sign} в сфере «{theme}» — "
                        "сюда стоит вести главную энергию."
                    )
            elif _use_terms(style):
                focus = (
                    f"Stellium in {st_sign} in house {chart.stellium_house} ({theme}) — "
                    "pour main energy here."
                )
            else:
                focus = (
                    f"Several planets in {st_sign} in {theme} — "
                    "pour main energy here."
                )
        elif chart.strong_houses:
            h = chart.strong_houses[0]
            theme = _house_theme(locale, h)
            if lang == "ru":
                focus = (
                    f"Ярче всего звучит {h}-й дом («{theme}») — туда и веди основной фокус."
                    if _use_terms(style)
                    else f"Ярче всего звучит «{theme}» — туда и веди основной фокус."
                )
            else:
                focus = (
                    f"House {h} ({theme}) stands out — lead with that focus."
                    if _use_terms(style)
                    else f"{theme.capitalize()} stands out — lead with that focus."
                )
        else:
            focus = opportunities
        if lang == "ru":
            intro = (
                "Максимальное раскрытие — через сильные дома, Юпитер и главную возможность карты. "
                if _use_terms(style)
                else "Максимальное раскрытие — через сильные стороны и главную возможность карты. "
            )
            tail = f" Главная возможность — {opportunities}."
        else:
            intro = (
                "Fullest unfolding — through strong houses, Jupiter, and the chart's main opportunity. "
                if _use_terms(style)
                else "Fullest unfolding — through strengths and the chart's main opportunity. "
            )
            tail = f" Main opportunity — {opportunities}."
        body = (
            f"{intro}{focus}{tail} {_render_planet(locale, jupiter, style=style)}"
        ).strip()

    body = _wrap_structured(locale, question, chart, body, "purpose", question_index, style=style)

    if lang == "ru":
        header = "🎯 Предназначение / Таланты / Реализация"
    else:
        header = "🎯 Purpose / Talents / Realization"
    return qa_response(header, question, body)


def build_dharma_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = dharma_question_text(locale, question_index)
    sun = chart.planets["SUN"]
    jupiter = chart.planets["JUPITER"]
    ketu = chart.planets["KETU"]
    moon = chart.planets["MOON"]
    h9_planets = _planets_in_house(chart, 9)
    h12_planets = _planets_in_house(chart, 12)
    lord9 = _lord_placement(chart, 9)
    lord12 = _lord_placement(chart, 12)
    lord10 = _lord_placement(chart, 10)

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in h9_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord9, style=style)]
        if lang == "ru":
            intro = (
                "Духовный путь и дхарма — 9-й дом, Юпитер как наставник и Солнце как внутренний свет. "
                if _use_terms(style)
                else "Духовный путь и дхарма — вера в смысл, мудрость и внутренний свет. "
            )
        else:
            intro = (
                "Spiritual path and dharma — house 9, Jupiter as guide, and Sun as inner light. "
                if _use_terms(style)
                else "Spiritual path and dharma — faith in meaning, wisdom, and inner light. "
            )
        body = (
            f"{intro}{_render_planet(locale, jupiter, style=style)} "
            f"{_render_planet(locale, sun, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 1:
        if lang == "ru":
            intro = (
                "Вера и смысл — 9-й дом, его управитель и Юпитер как показатель мировоззрения. "
                if _use_terms(style)
                else "Вера и смысл — мировоззрение, наставники и то, во что опираешься внутри. "
            )
        else:
            intro = (
                "Faith and meaning — house 9, its lord, and Jupiter as worldview. "
                if _use_terms(style)
                else "Faith and meaning — worldview, guides, and inner anchors. "
            )
        body = (
            f"{intro}{_render_planet(locale, jupiter, style=style)} "
            f"{_render_planet(locale, lord9, style=style)} "
            f"{_render_planet(locale, sun, style=style)}"
        ).strip()

    elif question_index == 2:
        bits = [_render_planet(locale, pl, style=style) for pl in h12_planets[:2]]
        if not bits:
            bits = [_render_planet(locale, lord12, style=style)]
        if lang == "ru":
            intro = (
                "Медитация и уединение — 12-й дом (мокша), Кету и Луна как тишина и отпускание. "
                if _use_terms(style)
                else "Медитация и уединение — тишина, отпускание и уход внутрь себя. "
            )
            tail = " Регулярная практика тишины для тебя не роскошь, а питание души."
        else:
            intro = (
                "Meditation and solitude — house 12 (moksha), Ketu, and Moon as silence and release. "
                if _use_terms(style)
                else "Meditation and solitude — silence, release, and turning inward. "
            )
            tail = " Regular silence is not luxury for you — it feeds the soul."
        body = (
            f"{intro}{_render_planet(locale, ketu, style=style)} "
            f"{_render_planet(locale, moon, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    elif question_index == 3:
        if lang == "ru":
            intro = (
                "Духовные уроки — Юпитер как мудрость и рост, Кету как отпускание и освобождение от лишнего. "
                if _use_terms(style)
                else "Духовные уроки — мудрость и рост через Юпитер, отпускание и простоту через Кету. "
            )
        else:
            intro = (
                "Spiritual lessons — Jupiter as wisdom and growth, Ketu as release and letting go. "
                if _use_terms(style)
                else "Spiritual lessons — wisdom through Jupiter, release and simplicity through Ketu. "
            )
        body = (
            f"{intro}{_render_planet(locale, jupiter, style=style)} "
            f"{_render_planet(locale, ketu, style=style)} "
            f"{_render_planet(locale, lord9, style=style)}"
        ).strip()

    else:
        if lang == "ru":
            intro = (
                "Дхарма в повседневности — связка 9-го дома (смысл) и 10-го (дело): жить правильно через поступки. "
                if _use_terms(style)
                else "Дхарма в повседневности — жить в согласии со смыслом через конкретные поступки и дело. "
            )
            tail = " Дхарма — не только идея, а честность в том, что делаешь каждый день."
        else:
            intro = (
                "Daily dharma — linking house 9 (meaning) and house 10 (action): live rightly through deeds. "
                if _use_terms(style)
                else "Daily dharma — align with meaning through concrete actions and work. "
            )
            tail = " Dharma is not only an idea — honesty in what you do each day."
        body = (
            f"{intro}{_render_planet(locale, lord9, style=style)} "
            f"{_render_planet(locale, lord10, style=style)} "
            f"{_render_planet(locale, jupiter, style=style)}{tail}"
        ).strip()

    body = _wrap_structured(locale, question, chart, body, "dharma", question_index, style=style)

    if lang == "ru":
        header = "🕉️ Духовность / Путь / Дхарма"
    else:
        header = "🕉️ Spirituality / Path / Dharma"
    return qa_response(header, question, body)


def build_travel_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    question = travel_question_text(locale, question_index)
    rahu = chart.planets["RAHU"]
    jupiter = chart.planets["JUPITER"]
    moon = chart.planets["MOON"]
    saturn = chart.planets["SATURN"]
    mercury = chart.planets["MERCURY"]
    h3_planets = _planets_in_house(chart, 3)
    h9_planets = _planets_in_house(chart, 9)
    h12_planets = _planets_in_house(chart, 12)
    h4_planets = _planets_in_house(chart, 4)
    lord9 = _lord_placement(chart, 9)
    lord12 = _lord_placement(chart, 12)
    h9_sign = sign_label(locale, chart.house_signs[9])
    h12_sign = sign_label(locale, chart.house_signs[12])

    if question_index == 0:
        bits = [_render_planet(locale, pl, style=style) for pl in (*h12_planets, *h9_planets)[:2]]
        if not bits:
            bits = [
                _render_planet(locale, lord12, style=style),
                _render_planet(locale, lord9, style=style),
            ]
        if lang == "ru":
            intro = (
                "Переезд и жизнь за границей — 12-й дом, 9-й дом и Раху как тяга к чужим землям. "
                if _use_terms(style)
                else "Переезд и жизнь за границей — тема дистанции от привычного и тяги к новым местам. "
            )
            tail = (
                " 12-й или 9-й дом насыщен — тема эмиграции для тебя особенно живая."
                if chart.house_planet_count.get(12, 0) + chart.house_planet_count.get(9, 0) >= 2
                else ""
            )
        else:
            intro = (
                "Relocation and life abroad — houses 12 and 9, Rahu as pull to foreign ground. "
                if _use_terms(style)
                else "Relocation and life abroad — distance from the familiar and pull to new places. "
            )
            tail = (
                " A loaded 12th or 9th house makes emigration themes especially alive."
                if chart.house_planet_count.get(12, 0) + chart.house_planet_count.get(9, 0) >= 2
                else ""
            )
        body = f"{intro}{_render_planet(locale, rahu, style=style)} {' '.join(bits)}{tail}".strip()

    elif question_index == 1:
        bits = [_render_planet(locale, pl, style=style) for pl in h3_planets[:1]]
        if lang == "ru":
            intro = (
                "Дальние путешествия — 9-й дом, Юпитер и 3-й дом как дорога и смелость двигаться. "
                if _use_terms(style)
                else "Дальние путешествия — расширение горизонта, дорога и смелость двигаться. "
            )
        else:
            intro = (
                "Long journeys — house 9, Jupiter, and house 3 as road and courage to move. "
                if _use_terms(style)
                else "Long journeys — expanding horizons, the road, and courage to move. "
            )
        body = (
            f"{intro}{_render_planet(locale, jupiter, style=style)} "
            f"{_render_planet(locale, lord9, style=style)} "
            f"{' '.join(bits)}"
        ).strip()

    elif question_index == 2:
        rahu_sign = sign_label(locale, rahu.sign)
        if lang == "ru":
            if _use_terms(style):
                intro = (
                    f"Направления и места — знак 9-го дома ({h9_sign}), 12-го ({h12_sign}), "
                    f"Раху в {rahu_sign} и куда падают их управители. "
                )
            else:
                intro = (
                    f"Направления и места — темы «{_house_theme(locale, 9)}» ({h9_sign}) "
                    f"и дистанции ({h12_sign}), Раху в {rahu_sign}. "
                )
        elif _use_terms(style):
            intro = (
                f"Directions and places — 9th-house sign ({h9_sign}), 12th ({h12_sign}), "
                f"Rahu in {rahu_sign}, and where their lords land. "
            )
        else:
            intro = (
                f"Directions and places — {_house_theme(locale, 9)} ({h9_sign}), "
                f"distance ({h12_sign}), Rahu in {rahu_sign}. "
            )
        body = (
            f"{intro}{_render_planet(locale, rahu, style=style)} "
            f"{_render_planet(locale, lord9, style=style)} "
            f"{_render_planet(locale, lord12, style=style)}"
        ).strip()

    elif question_index == 3:
        if lang == "ru":
            intro = (
                "Переезду помогают Раху, Юпитер и сильный 9-й дом; "
                "мешают привязка к 4-му дому, Луна и Сатурн как страх перемен. "
                if _use_terms(style)
                else "Переезду помогают смелость и открытость; мешают привязка к дому и страх перемен. "
            )
        else:
            intro = (
                "Relocation is helped by Rahu, Jupiter, and a strong 9th house; "
                "blocked by 4th-house ties, Moon, and Saturn as fear of change. "
                if _use_terms(style)
                else "Courage and openness help relocation; home ties and fear of change block it. "
            )
        body = (
            f"{intro}{_render_planet(locale, rahu, style=style)} "
            f"{_render_planet(locale, jupiter, style=style)} "
            f"{_render_planet(locale, moon, style=style)} "
            f"{_render_planet(locale, saturn, style=style)}"
        ).strip()

    else:
        bits = [_render_planet(locale, pl, style=style) for pl in h4_planets[:1]]
        if lang == "ru":
            intro = (
                "«Дом» вдали от родины — баланс 4-го дома (корни) и 12-го (новая земля), Луна и Меркурий. "
                if _use_terms(style)
                else "«Дом» вдали от родины — баланс корней и нового места, Луна и адаптация. "
            )
            tail = " Создавай опору там, где живёшь — не только в памяти о прошлом."
        else:
            intro = (
                "Home far from homeland — balance of house 4 (roots) and 12 (new ground), Moon and Mercury. "
                if _use_terms(style)
                else "Home far from homeland — balance of roots and new place, Moon and adaptation. "
            )
            tail = " Build support where you live — not only in memory of the past."
        body = (
            f"{intro}{_render_planet(locale, moon, style=style)} "
            f"{_render_planet(locale, mercury, style=style)} "
            f"{_render_planet(locale, lord12, style=style)} "
            f"{' '.join(bits)}{tail}"
        ).strip()

    body = _wrap_structured(locale, question, chart, body, "travel", question_index, style=style)

    if lang == "ru":
        header = "✈️ Эмиграция / Путешествия"
    else:
        header = "✈️ Emigration / Travel"
    return qa_response(header, question, body)


def build_upaya_answer(
    chart: JyotishChart,
    locale: str,
    question_index: int,
    *,
    style: str = "terms",
) -> str:
    from app.jyotish_text import _derive_summary, _list_to_prose

    lang = _lang(locale)
    question = upaya_question_text(locale, question_index)
    strengths, weaknesses, risks, opportunities = _derive_summary(chart, lang)
    jupiter = chart.planets["JUPITER"]
    tense = _tense_planets(chart)
    strong = _strong_planets(chart)
    debilitated = _debilitated_planets(chart)

    if question_index == 0:
        hints = [_upaya_hint(locale, pl.key) for pl in tense[:2]]
        if lang == "ru":
            intro = (
                "Общие упайи — сознательная работа со слабыми зонами, "
                "благотворительность и день покровителя планеты. "
                if _use_terms(style)
                else "Общие упайи — бережное отношение к слабым темам, "
                "щедрость и регулярные практики баланса. "
            )
            tail = (
                f" Главный риск карты — «{risks}»; смягчай через дисциплину и практики {_pl(locale, 'JUPITER').lower()}."
            )
        else:
            intro = (
                "General upayas — conscious work with weak spots, "
                "charity, and the planet's day of patronage. "
                if _use_terms(style)
                else "General upayas — gentle work with weak themes, generosity, and regular balance practices. "
            )
            tail = f" Main chart risk — «{risks}»; soften through discipline and Jupiter practices."
        body = f"{intro}{'; '.join(hints)}.{tail} {_render_planet(locale, jupiter, style=style)}".strip()

    elif question_index == 1:
        if debilitated:
            targets = debilitated[:3]
        else:
            targets = tense[:3]
        hints = [_upaya_hint(locale, pl.key) for pl in targets]
        if lang == "ru":
            intro = (
                "Смягчение напряжённых планет — их день недели, мантра и благотворительность по теме планеты. "
                if _use_terms(style)
                else "Смягчение напряжённых тем — день недели, простая мантра и доброе дело по теме планеты. "
            )
        else:
            intro = (
                "Softening tense planets — weekday, mantra, and charity aligned with the planet. "
                if _use_terms(style)
                else "Softening tense themes — weekday, simple mantra, and kind action aligned with the planet. "
            )
        body = f"{intro}{'; '.join(hints)}.".strip()

    elif question_index == 2:
        if strong:
            targets = strong[:3]
        else:
            targets = [chart.planets["SUN"], jupiter]
        hints = [_upaya_hint(locale, pl.key) for pl in targets]
        if lang == "ru":
            intro = (
                "Усиление сильных сторон — почитание планет в силе, их день и качества, которые уже опираются на карту. "
                if _use_terms(style)
                else "Усиление сильных сторон — опирайся на то, что уже даётся легче, и развивай это сознательно. "
            )
            tail = f" Сильные стороны — {_list_to_prose(strengths, lang)}."
        else:
            intro = (
                "Strengthening strong sides — honor strong planets, their day, and qualities the chart already supports. "
                if _use_terms(style)
                else "Strengthen strong sides — lean on what comes easier and grow it consciously. "
            )
            tail = f" Strengths — {_list_to_prose(strengths, lang)}."
        body = f"{intro}{'; '.join(hints)}.{tail}".strip()

    elif question_index == 3:
        days_planets = tense[:3] if tense else [jupiter, chart.planets["MOON"]]
        hints = [_upaya_hint(locale, pl.key) for pl in days_planets]
        if lang == "ru":
            intro = (
                "Дни и практики — выдели день покровителя планеты для медитации, дана или служения. "
                if _use_terms(style)
                else "Дни и практики — выдели один день в неделю под медитацию, доброе дело или заботу о себе. "
            )
            tail = " Регулярность важнее драматичных ритуалов."
        else:
            intro = (
                "Days and practices — set the planet's weekday for meditation, charity, or service. "
                if _use_terms(style)
                else "Days and practices — set one weekday for meditation, a kind act, or self-care. "
            )
            tail = " Regularity matters more than dramatic rituals."
        body = f"{intro}{'; '.join(hints)}.{tail}".strip()

    else:
        focus = debilitated[0] if debilitated else tense[0]
        gem = GEM_HINT[lang].get(focus.key, "")
        gem_name = _pl(locale, focus.key)
        if lang == "ru":
            intro = (
                f"Мантра и дана — {_upaya_hint(locale, focus.key)}. "
                f"Камень традиции — {gem} для {gem_name.lower()}, "
                if _use_terms(style)
                else f"Мантра и доброе дело — {_upaya_hint(locale, focus.key)}. "
                f"В традиции камень — {gem} для темы {gem_name.lower()}, "
            )
            tail = (
                " но камни носят только после консультации с опытным джйотиши — "
                "неправильный камень может усилить напряжение."
            )
        else:
            intro = (
                f"Mantra and charity — {_upaya_hint(locale, focus.key)}. "
                f"Traditional gem — {gem} for {gem_name}, "
                if _use_terms(style)
                else f"Mantra and charity — {_upaya_hint(locale, focus.key)}. "
                f"Traditional gem for this theme — {gem}, "
            )
            tail = (
                " but wear gems only after consulting an experienced jyotishi — "
                "the wrong stone can increase tension."
            )
        body = f"{intro}{tail} {_render_planet(locale, focus, style=style)}".strip()

    body = _wrap_structured(locale, question, chart, body, "upaya", question_index, style=style)

    if lang == "ru":
        header = "🪬 Гармонизация / Упайи"
    else:
        header = "🪬 Harmonization / Upayas"
    return qa_response(header, question, body)


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
                if _use_terms(style):
                    body += " Солнце в силе даёт уверенный стержень и ощущение своего курса."
                else:
                    body += " Внутренний стержень и ощущение своего курса у тебя сильные."
        else:
            body = f"Strengths — {_list_to_prose(strengths, lang)}."
            if chart.planets["SUN"].dignity == "exalted":
                if _use_terms(style):
                    body += " Exalted Sun adds a confident core and sense of direction."
                else:
                    body += " You have a confident inner core and a clear sense of direction."

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
    body = _wrap_structured(
        locale,
        question,
        chart,
        body,
        "popular",
        0,
        style=style,
        question_id=question_id,
    )
    return qa_response(header, question, body)


def questions_intro(locale: str, house: int, *, style: str) -> str:
    sphere = _sphere_label(locale, house, style=style)
    questions = sphere_questions(locale, house)
    if _lang(locale) == "ru":
        return p(b(f"Сфера: {sphere}"), format_numbered_questions(questions))
    return p(b(f"Sphere: {sphere}"), format_numbered_questions(questions))
