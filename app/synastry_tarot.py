"""Esoteric compatibility: six-card Tarot spread «Couple compatibility»."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

POSITION_KEYS = ("past", "present", "future", "strengths", "weaknesses", "advice")

POSITION_LABELS = {
    "ru": {
        "past": "Прошлое — что привело вас друг к другу",
        "present": "Настоящее — текущая динамика",
        "future": "Будущее — потенциал развития",
        "strengths": "Сильные стороны — точки опоры",
        "weaknesses": "Слабые стороны — зоны риска",
        "advice": "Совет — как улучшить отношения",
    },
    "en": {
        "past": "Past — what brought you together",
        "present": "Present — current dynamics",
        "future": "Future — growth potential",
        "strengths": "Strengths — points of support",
        "weaknesses": "Weaknesses — risk zones",
        "advice": "Advice — how to improve the bond",
    },
}

POSITION_LABELS_PLAIN = {
    "ru": {
        "past": "Прошлое",
        "present": "Сейчас",
        "future": "Будущее",
        "strengths": "Сильные стороны",
        "weaknesses": "Слабые стороны",
        "advice": "Совет",
    },
    "en": {
        "past": "Past",
        "present": "Now",
        "future": "Future",
        "strengths": "Strengths",
        "weaknesses": "Weak spots",
        "advice": "Advice",
    },
}

POSITION_LABELS_PLAIN_BY_MODE = {
    "ru": {
        "love": POSITION_LABELS_PLAIN["ru"],
        "friendship": {
            "past": "Откуда вы как друзья",
            "present": "Сейчас в дружбе",
            "future": "Куда может пойти",
            "strengths": "Сильные стороны",
            "weaknesses": "Слабые места",
            "advice": "Совет",
        },
        "work": {
            "past": "Откуда вы как команда",
            "present": "Сейчас на проекте",
            "future": "Куда может пойти",
            "strengths": "Сильные стороны",
            "weaknesses": "Слабые места",
            "advice": "Совет",
        },
    },
    "en": {
        "love": POSITION_LABELS_PLAIN["en"],
        "friendship": {
            "past": "Where you started as friends",
            "present": "Friendship now",
            "future": "Where it might go",
            "strengths": "Strengths",
            "weaknesses": "Weak spots",
            "advice": "Advice",
        },
        "work": {
            "past": "Where you started as a team",
            "present": "Project now",
            "future": "Where it might go",
            "strengths": "Strengths",
            "weaknesses": "Weak spots",
            "advice": "Advice",
        },
    },
}

# Major Arcana: (name_ru, name_en, readings ru×6, readings en×6)
_MAJOR: list[tuple[str, str, tuple[str, ...], tuple[str, ...]]] = [
    (
        "Шут",
        "The Fool",
        (
            "случайная встреча и смелость открыться без гарантий",
            "лёгкость, эксперименты и отсутствие жёстких правил",
            "новый виток — союз может выйти на другой уровень свободы",
            "спонтанность и вера в пару",
            "необдуманные шаги и страх обязательств",
            "не терять игру, но договариваться о границах",
        ),
        (
            "a chance meeting and courage to open up without guarantees",
            "lightness, experiments, and few fixed rules",
            "a new turn — the bond may reach a freer level",
            "spontaneity and faith in the pair",
            "rash steps and fear of commitment",
            "keep play alive, but agree on boundaries",
        ),
    ),
    (
        "Маг",
        "The Magician",
        (
            "взаимное притяжение сильных личностей и инициатива",
            "активное влияние друг на друга и совместные проекты",
            "реализация общих замыслов при ясном намерении",
            "умение договариваться и воплощать идеи",
            "манипуляции и борьба «кто главный»",
            "направлять энергию в общее дело, а не в спор",
        ),
        (
            "mutual pull of strong personalities and initiative",
            "active influence on each other and shared projects",
            "shared plans realized with clear intent",
            "skill in agreeing and turning ideas into action",
            "manipulation and fights over who leads",
            "channel energy into shared goals, not rivalry",
        ),
    ),
    (
        "Жрица",
        "The High Priestess",
        (
            "тихое узнавание «своего» без лишних слов",
            "интуиция, недосказанность и глубокие чувства",
            "раскрытие тайн и более честная близость",
            "тонкое понимание без давления",
            "молчание, догадки и закрытость",
            "говорить о важном мягко, но прямо",
        ),
        (
            "quiet recognition without many words",
            "intuition, things left unsaid, and deep feeling",
            "secrets unveiled and more honest closeness",
            "subtle understanding without pressure",
            "silence, guessing, and emotional closure",
            "speak about what matters — gently but clearly",
        ),
    ),
    (
        "Императрица",
        "The Empress",
        (
            "тепло, забота и чувство «дома» с первых встреч",
            "нежность, уют и желание растить связь",
            "расцвет чувств, быт и совместный комфорт",
            "забота, принятие и плодородность союза",
            "избыточный контроль или уход в быт без страсти",
            "беречь нежность и не забывать о романтике",
        ),
        (
            "warmth, care, and a sense of home from early on",
            "tenderness, comfort, and desire to nurture the bond",
            "feelings in bloom, daily life, and shared comfort",
            "care, acceptance, and a fertile partnership",
            "smothering control or routine without passion",
            "protect tenderness and keep romance alive",
        ),
    ),
    (
        "Император",
        "The Emperor",
        (
            "надёжность, структура и ощущение опоры",
            "чёткие роли, правила и ответственность",
            "стабильный союз с ясными договорённостями",
            "защита, порядок и верность обещаниям",
            "жёсткость, контроль и мало гибкости",
            "сохранять структуру, но оставлять место чувствам",
        ),
        (
            "reliability, structure, and a sense of support",
            "clear roles, rules, and responsibility",
            "a stable union with explicit agreements",
            "protection, order, and keeping promises",
            "rigidity, control, and little flexibility",
            "keep structure, but leave room for feeling",
        ),
    ),
    (
        "Иерофант",
        "The Hierophant",
        (
            "общие ценности, традиции или «правильная» встреча",
            "ориентация на статус, семью или принятые нормы",
            "укрепление через обязательства и общий путь",
            "верность принципам и взаимное уважение",
            "давление «как должно быть» и мало свободы",
            "сверять ценности, не навязывая сценарий",
        ),
        (
            "shared values, traditions, or a «proper» meeting",
            "focus on status, family, or accepted norms",
            "strengthening through commitment and a shared path",
            "loyalty to principles and mutual respect",
            "pressure of «how it should be» and little freedom",
            "align values without imposing a script",
        ),
    ),
    (
        "Влюблённые",
        "The Lovers",
        (
            "сильный выбор друг друга и магнетизм",
            "осознанная близость и важные решения в паре",
            "углубление любви или новый этап выбора",
            "искренность, притяжение и единство",
            "колебания между двумя путями или страх выбора",
            "выбирать друг друга каждый день, а не один раз",
        ),
        (
            "a strong mutual choice and magnetism",
            "conscious closeness and big decisions as a pair",
            "love deepening or a new stage of choice",
            "sincerity, attraction, and unity",
            "wavering between paths or fear of choosing",
            "choose each other daily, not just once",
        ),
    ),
    (
        "Колесница",
        "The Chariot",
        (
            "стремительное сближение и общая цель",
            "активное движение, амбиции и напор",
            "совместные победы при согласованном курсе",
            "воля, драйв и умение идти вперёд",
            "конфликт направлений и борьба за руль",
            "согласовать курс, прежде чем ускоряться",
        ),
        (
            "a fast coming-together and a shared aim",
            "active motion, ambition, and drive",
            "shared wins with an aligned direction",
            "will, momentum, and moving forward together",
            "clashing directions and fighting for the wheel",
            "agree on direction before speeding up",
        ),
    ),
    (
        "Сила",
        "Strength",
        (
            "терпение и мягкая стойкость друг перед другом",
            "сдержанная страсть и принятие слабостей",
            "укрепление через доверие и смелость быть собой",
            "мужество, нежность и внутренняя опора",
            "упрямство, подавление чувств или борьба характеров",
            "сила — в мягкости, а не в подавлении",
        ),
        (
            "patience and gentle steadiness toward each other",
            "restrained passion and accepting weaknesses",
            "strengthening through trust and being yourselves",
            "courage, tenderness, and inner support",
            "stubbornness, suppressed feeling, or clashing wills",
            "strength lies in gentleness, not suppression",
        ),
    ),
    (
        "Отшельник",
        "The Hermit",
        (
            "зрелость, одиночество перед встречей или поиск смысла",
            "больше личного пространства и тишины",
            "осознанная дистанция или пауза для роста",
            "мудрость, честность и глубокая верность",
            "холод, отдаление и страх близости",
            "уважать паузы, но не терять контакт",
        ),
        (
            "maturity, solitude before meeting, or a search for meaning",
            "more personal space and quiet",
            "conscious distance or a pause for growth",
            "wisdom, honesty, and deep loyalty",
            "coldness, distance, and fear of closeness",
            "honor pauses, but don't lose contact",
        ),
    ),
    (
        "Колесо Фортуны",
        "Wheel of Fortune",
        (
            "случайность, судьба или поворотный момент",
            "перемены, циклы «вверх–вниз» в паре",
            "новый виток судьбы — шанс или испытание",
            "гибкость и умение принимать перемены",
            "нестабильность и зависимость от обстоятельств",
            "держаться друг за друга, когда крутится колесо",
        ),
        (
            "chance, fate, or a turning point",
            "change and up-and-down cycles in the pair",
            "a new fate cycle — opportunity or test",
            "flexibility and accepting change",
            "instability and dependence on circumstances",
            "hold on to each other when the wheel turns",
        ),
    ),
    (
        "Справедливость",
        "Justice",
        (
            "кarma, честный обмен или «по заслугам»",
            "баланс «даю — получаю» и ясные договорённости",
            "восстановление равновесия и справедливости",
            "честность, равноправие и ясные правила",
            "обиды, счёт и ощущение несправедливости",
            "говорить о балансе, не копя счёт",
        ),
        (
            "karma, fair exchange, or «getting what's due»",
            "balance of give-and-take and clear agreements",
            "restoring balance and fairness",
            "honesty, equality, and clear rules",
            "grievances, score-keeping, and unfairness",
            "talk about balance instead of keeping score",
        ),
    ),
    (
        "Повешенный",
        "The Hanged Man",
        (
            "нестандартная встреча или жертва ради связи",
            "пауза, переосмысление и другой взгляд",
            "трансформация через отпускание старого",
            "терпение и готовность видеть иначе",
            "застой, зависание и ощущение тупика",
            "иногда остановиться — значит двигаться дальше",
        ),
        (
            "an unusual meeting or sacrifice for the bond",
            "pause, rethinking, and a new perspective",
            "transformation by letting go of the old",
            "patience and willingness to see differently",
            "stagnation, limbo, and feeling stuck",
            "sometimes stopping is how you move forward",
        ),
    ),
    (
        "Смерть",
        "Death",
        (
            "конец старого этапа и мощное перерождение",
            "глубокие перемены и отпускание прошлого",
            "качественный переход в новую форму союза",
            "честность перемен и смелость обновиться",
            "страх потери и сопротивление изменениям",
            "не цепляться за то, что уже завершилось",
        ),
        (
            "end of an old stage and powerful rebirth",
            "deep change and releasing the past",
            "a qualitative shift into a new form of union",
            "honesty about change and courage to renew",
            "fear of loss and resisting change",
            "don't cling to what has already ended",
        ),
    ),
    (
        "Умеренность",
        "Temperance",
        (
            "постепенное сближение и «правильный темп»",
            "смешение разных качеств в гармонии",
            "исцеление и зрелый долгий союз",
            "терпение, компромисс и баланс",
            "крайности и качели «всё или ничего»",
            "искать золотую середину каждый день",
        ),
        (
            "gradual coming together at the right pace",
            "blending different qualities in harmony",
            "healing and a mature long-term union",
            "patience, compromise, and balance",
            "extremes and all-or-nothing swings",
            "seek the middle ground every day",
        ),
    ),
    (
        "Дьявол",
        "The Devil",
        (
            "сильная страсть, зависимость или «невозможно отпустить»",
            "ревность, собственничество или скрытые привязки",
            "осознание цепей — выход или углубление",
            "магнетизм и мощная химия",
            "зависимость, контроль и манипуляции",
            "называть тень вслух и не кормить её",
        ),
        (
            "intense passion, attachment, or «can't let go»",
            "jealousy, possessiveness, or hidden bonds",
            "seeing the chains — break free or go deeper",
            "magnetism and strong chemistry",
            "dependency, control, and manipulation",
            "name the shadow aloud and stop feeding it",
        ),
    ),
    (
        "Башня",
        "The Tower",
        (
            "резкий поворот, кризис или встряска судьбы",
            "вскрытие правды и нестабильность",
            "перестройка после разрушения иллюзий",
            "честность после кризиса",
            "внезапные конфликты и разрушительные сценарии",
            "строить заново на правде, а не на иллюзиях",
        ),
        (
            "a sharp turn, crisis, or jolt of fate",
            "truth revealed and instability",
            "rebuilding after illusions fall",
            "honesty after crisis",
            "sudden conflicts and destructive patterns",
            "rebuild on truth, not on illusions",
        ),
    ),
    (
        "Звезда",
        "The Star",
        (
            "надежда, исцеление после трудного периода",
            "мягкая вера в пару и восстановление",
            "светлое будущее и вдохновение",
            "надежда, доверие и духовная близость",
            "разочарование и страх мечтать",
            "питать надежду конкретными маленькими шагами",
        ),
        (
            "hope and healing after a hard period",
            "gentle faith in the pair and recovery",
            "a bright future and inspiration",
            "hope, trust, and spiritual closeness",
            "disappointment and fear of dreaming",
            "feed hope with small concrete steps",
        ),
    ),
    (
        "Луна",
        "The Moon",
        (
            "тайна, иллюзии или сильная фантазия о друг друге",
            "тревога, недоверие и эмоциональные качели",
            "прояснение или прохождение через страхи",
            "глубокая эмпатия и тонкая связь",
            "обманы, проекции и неясность",
            "проверять догадки разговором, а не фантазией",
        ),
        (
            "mystery, illusions, or strong fantasy about each other",
            "anxiety, mistrust, and emotional swings",
            "clarity emerging or moving through fears",
            "deep empathy and a subtle bond",
            "deception, projections, and uncertainty",
            "test guesses in talk, not in fantasy",
        ),
    ),
    (
        "Солнце",
        "The Sun",
        (
            "радость, открытость и ощущение «это оно»",
            "тепло, успех и ясность в паре",
            "счастливый период и общий свет",
            "радость, искренность и жизненная сила",
            "завышенные ожидания и страх потерять идеал",
            "радоваться друг другу без перфекционизма",
        ),
        (
            "joy, openness, and a sense of «this is it»",
            "warmth, success, and clarity as a pair",
            "a happy phase and shared light",
            "joy, sincerity, and vitality",
            "inflated expectations and fear of losing the ideal",
            "celebrate each other without perfectionism",
        ),
    ),
    (
        "Суд",
        "Judgement",
        (
            "кармический зов и чувство «мы встретились не зря»",
            "пробуждение, прощение и второй шанс",
            "важный выбор и обновление союза",
            "прощение, призвание и глубокая связь",
            "зацикленность на прошлых ошибках",
            "отпустить старое и ответить на зов связи",
        ),
        (
            "a karmic call and «we met for a reason»",
            "awakening, forgiveness, and a second chance",
            "a major choice and renewal of the union",
            "forgiveness, calling, and a deep bond",
            "fixation on past mistakes",
            "release the old and answer the call of the bond",
        ),
    ),
    (
        "Мир",
        "The World",
        (
            "завершение поиска и ощущение целостности",
            "гармония, успех и чувство «мы — команда»",
            "полнота союза и общая цель",
            "целостность, успех и зрелость пары",
            "страх закрепить результат или застой в комфорте",
            "ценить достигнутое и двигаться дальше вместе",
        ),
        (
            "end of searching and a sense of wholeness",
            "harmony, success, and «we are a team»",
            "fullness of union and a shared goal",
            "wholeness, success, and pair maturity",
            "fear of locking in the result or comfort stagnation",
            "value what you've built and keep moving together",
        ),
    ),
]

HARMONIOUS_CARDS = frozenset({2, 3, 6, 8, 14, 17, 19, 21})
CHALLENGING_CARDS = frozenset({12, 15, 16, 18})
ADVICE_BONUS_CARDS = frozenset({6, 8, 14, 17, 19, 21})


@dataclass(frozen=True)
class TarotSpreadCard:
    position: str
    card_id: int
    name: str
    reading: str


@dataclass(frozen=True)
class TarotCompatSpread:
    cards: tuple[TarotSpreadCard, ...]
    score_delta: int


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _birth_digit_sum(birth_date: date) -> int:
    raw = f"{birth_date.day:02d}{birth_date.month:02d}{birth_date.year}"
    return sum(int(char) for char in raw)


def _spread_seed(user_birth_date: date, partner_birth_date: date) -> int:
    user_sum = _birth_digit_sum(user_birth_date)
    partner_sum = _birth_digit_sum(partner_birth_date)
    return (user_sum * 1009 + partner_sum * 917 + user_birth_date.toordinal()) % 100_003


def _draw_card_ids(seed: int, count: int = 6) -> list[int]:
    state = seed
    available = list(range(len(_MAJOR)))
    picked: list[int] = []
    for _ in range(count):
        state = (state * 1_103_515_245 + 12_345) & 0x7FFFFFFF
        index = state % len(available)
        picked.append(available.pop(index))
    return picked


def _card_name(card_id: int, lang: str) -> str:
    name_ru, name_en, _, _ = _MAJOR[card_id]
    return name_ru if lang == "ru" else name_en


def _card_reading(card_id: int, position: str, lang: str) -> str:
    _, _, readings_ru, readings_en = _MAJOR[card_id]
    readings = readings_ru if lang == "ru" else readings_en
    position_index = POSITION_KEYS.index(position)
    return readings[position_index]


def _score_delta(strengths_id: int, weaknesses_id: int, advice_id: int) -> int:
    delta = 0
    if strengths_id in HARMONIOUS_CARDS:
        delta += 2
    elif strengths_id not in CHALLENGING_CARDS:
        delta += 1
    if weaknesses_id in CHALLENGING_CARDS:
        delta -= 1
    if advice_id in ADVICE_BONUS_CARDS:
        delta += 1
    return delta


def analyze_couple_tarot_spread(
    user_birth_date: date,
    partner_birth_date: date,
    *,
    locale: str = "ru",
) -> TarotCompatSpread:
    lang = _lang(locale)
    card_ids = _draw_card_ids(_spread_seed(user_birth_date, partner_birth_date))
    cards: list[TarotSpreadCard] = []
    for position, card_id in zip(POSITION_KEYS, card_ids, strict=True):
        cards.append(
            TarotSpreadCard(
                position=position,
                card_id=card_id,
                name=_card_name(card_id, lang),
                reading=_card_reading(card_id, position, lang),
            )
        )
    strengths_id = card_ids[POSITION_KEYS.index("strengths")]
    weaknesses_id = card_ids[POSITION_KEYS.index("weaknesses")]
    advice_id = card_ids[POSITION_KEYS.index("advice")]
    return TarotCompatSpread(
        cards=tuple(cards),
        score_delta=_score_delta(strengths_id, weaknesses_id, advice_id),
    )


def tarot_score_delta(analysis: TarotCompatSpread) -> int:
    return analysis.score_delta


def format_synastry_tarot_section(
    locale: str,
    analysis: TarotCompatSpread,
    *,
    style: str = "terms",
    mode: str = "love",
) -> str:
    from app.compat_mode_plain import mode_key as _mode_key
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    mode_key = _mode_key(mode)
    lines: list[str] = []
    terms = use_synastry_terms(style)

    if lang == "ru":
        if terms:
            lines.append("🃏 Таро-расклад «Совместимость пары»")
        else:
            plain_titles = {
                "love": "🃏 Карты вашей пары",
                "friendship": "🃏 Карты вашей дружбы",
                "work": "🃏 Карты вашей команды",
            }
            lines.append(plain_titles[mode_key])
        if terms:
            lines.append(
                "Шесть позиций по датам рождения: прошлое, настоящее, будущее, "
                "сильные и слабые стороны, совет."
            )
        else:
            plain_intros = {
                "love": "Шесть карт о вашей связи: от прошлого до совета.",
                "friendship": (
                    "Шесть карт о дружбе: от «как познакомились» до «не пропадай на полгода»."
                ),
                "work": (
                    "Шесть карт о команде: от «как попали в проект» до «кто пишет итоговый слайд»."
                ),
            }
            lines.append(plain_intros[mode_key])
    else:
        if terms:
            lines.append("🃏 Tarot spread «Couple compatibility»")
        else:
            plain_titles = {
                "love": "🃏 Your pair's cards",
                "friendship": "🃏 Your friendship's cards",
                "work": "🃏 Your team's cards",
            }
            lines.append(plain_titles[mode_key])
        if terms:
            lines.append(
                "Six positions from birth dates: past, present, future, "
                "strengths, weaknesses, advice."
            )
        else:
            plain_intros = {
                "love": "Six cards about your bond: from past to advice.",
                "friendship": (
                    "Six cards about friendship: from «how you met» to «don't ghost for six months»."
                ),
                "work": (
                    "Six cards about the team: from «how you landed on the project» "
                    "to «who writes the final slide»."
                ),
            }
            lines.append(plain_intros[mode_key])

    labels = POSITION_LABELS[lang] if terms else POSITION_LABELS_PLAIN_BY_MODE[lang][mode_key]
    lines.append("")
    for card in analysis.cards:
        label = labels[card.position]
        if terms:
            lines.append(f"• {label}: {card.name} — {card.reading}.")
        else:
            lines.append(f"• {label}: {card.name}. {card.reading.capitalize()}.")

    return "\n".join(lines)
