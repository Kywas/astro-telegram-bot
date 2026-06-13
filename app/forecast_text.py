from __future__ import annotations

from datetime import date

from app.astro_glossary import format_moon_in_sign_short, moon_in_sign_hint

SIGN_ELEMENTS = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
        "ASC": "Асцендент",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
        "ASC": "Ascendant",
    },
}

SIGN_LABELS = {
    "ru": {
        "Aries": "Овен",
        "Taurus": "Телец",
        "Gemini": "Близнецы",
        "Cancer": "Рак",
        "Leo": "Лев",
        "Virgo": "Дева",
        "Libra": "Весы",
        "Scorpio": "Скорпион",
        "Sagittarius": "Стрелец",
        "Capricorn": "Козерог",
        "Aquarius": "Водолей",
        "Pisces": "Рыбы",
    },
    "en": {
        "Aries": "Aries",
        "Taurus": "Taurus",
        "Gemini": "Gemini",
        "Cancer": "Cancer",
        "Leo": "Leo",
        "Virgo": "Virgo",
        "Libra": "Libra",
        "Scorpio": "Scorpio",
        "Sagittarius": "Sagittarius",
        "Capricorn": "Capricorn",
        "Aquarius": "Aquarius",
        "Pisces": "Pisces",
    },
}

ASPECT_LABELS = {
    "ru": {
        "conjunction": "соединение",
        "sextile": "секстиль",
        "square": "квадрат",
        "trine": "трин",
        "opposition": "оппозиция",
    },
    "en": {
        "conjunction": "conjunction",
        "sextile": "sextile",
        "square": "square",
        "trine": "trine",
        "opposition": "opposition",
    },
}

Hit = tuple[float, str, str, str]


def _use_terms(style: str) -> bool:
    return style != "plain"


NATAL_ROLE_SHORT = {
    "ru": {
        "SUN": "личные цели",
        "MOON": "эмоции",
        "MERCURY": "мысли и речь",
        "VENUS": "близость и ценности",
        "MARS": "волю и действия",
        "JUPITER": "рост и возможности",
        "SATURN": "границы и дисциплину",
        "ASC": "образ и первое впечатление",
    },
    "en": {
        "SUN": "personal goals",
        "MOON": "emotions",
        "MERCURY": "thoughts and words",
        "VENUS": "closeness and values",
        "MARS": "will and action",
        "JUPITER": "growth and opportunity",
        "SATURN": "boundaries and discipline",
        "ASC": "image and first impression",
    },
}

ASPECT_VERB_SHORT = {
    "ru": {
        "conjunction": "усиливает",
        "sextile": "поддерживает",
        "trine": "облегчает",
        "square": "давит на",
        "opposition": "раскачивает",
    },
    "en": {
        "conjunction": "intensifies",
        "sextile": "supports",
        "trine": "eases",
        "square": "presses on",
        "opposition": "pulls on",
    },
}

DOMAIN_FOCUS = {
    "ru": {
        "energy": {
            "SUN": "личную силу и самопроявление",
            "MOON": "эмоциональный фон и тонус",
            "MERCURY": "ясность мыслей",
            "VENUS": "настроение и приятные импульсы",
            "MARS": "драйв и напор",
            "JUPITER": "масштаб и уверенность дня",
            "SATURN": "дисциплину и сдержанность",
        },
        "work": {
            "SUN": "карьерные приоритеты и статус",
            "MOON": "рабочий настрой",
            "MERCURY": "задачи, сроки и договорённости",
            "VENUS": "ценность результата",
            "MARS": "темп и конкуренцию",
            "JUPITER": "рост и новые возможности",
            "SATURN": "ответственность и структуру",
        },
        "finance": {
            "SUN": "финансовую уверенность",
            "MOON": "эмоциональные траты",
            "MERCURY": "расчёты и сделки",
            "VENUS": "удовольствие и покупки",
            "MARS": "импульсивные решения",
            "JUPITER": "оптимизм в деньгах",
            "SATURN": "бюджет и ограничения",
        },
        "love": {
            "SUN": "важность и видимость в паре",
            "MOON": "потребность в тепле",
            "MERCURY": "слова и ожидания",
            "VENUS": "близость и притяжение",
            "MARS": "страсть и возможные трения",
            "JUPITER": "щедрость и открытость",
            "SATURN": "границы и серьёзность",
        },
        "social": {
            "SUN": "видимость в контактах",
            "MOON": "личный тон общения",
            "MERCURY": "переписку и диалог",
            "VENUS": "приятные контакты",
            "MARS": "остроту в словах",
            "JUPITER": "новые связи",
            "SATURN": "формальность и дистанцию",
        },
        "health": {
            "SUN": "жизненный ресурс",
            "MOON": "сон, питание и настроение",
            "MERCURY": "нервную систему",
            "VENUS": "телесный комфорт",
            "MARS": "активность и нагрузку",
            "JUPITER": "склонность к перегрузу",
            "SATURN": "режим и границы нагрузки",
        },
    },
    "en": {
        "energy": {
            "SUN": "personal strength and self-expression",
            "MOON": "emotional tone and vitality",
            "MERCURY": "mental clarity",
            "VENUS": "mood and pleasant impulses",
            "MARS": "drive and momentum",
            "JUPITER": "confidence and scale of the day",
            "SATURN": "discipline and restraint",
        },
        "work": {
            "SUN": "career priorities and status",
            "MOON": "work mood",
            "MERCURY": "tasks, deadlines, and agreements",
            "VENUS": "value of the outcome",
            "MARS": "pace and competition",
            "JUPITER": "growth and new opportunities",
            "SATURN": "responsibility and structure",
        },
        "finance": {
            "SUN": "financial confidence",
            "MOON": "emotional spending",
            "MERCURY": "calculations and deals",
            "VENUS": "pleasure and purchases",
            "MARS": "impulsive decisions",
            "JUPITER": "optimism about money",
            "SATURN": "budget and limits",
        },
        "love": {
            "SUN": "importance and visibility in a relationship",
            "MOON": "need for warmth",
            "MERCURY": "words and expectations",
            "VENUS": "closeness and attraction",
            "MARS": "passion and possible friction",
            "JUPITER": "generosity and openness",
            "SATURN": "boundaries and seriousness",
        },
        "social": {
            "SUN": "visibility in contacts",
            "MOON": "personal tone in communication",
            "MERCURY": "messages and dialogue",
            "VENUS": "pleasant contacts",
            "MARS": "sharpness in speech",
            "JUPITER": "new connections",
            "SATURN": "formality and distance",
        },
        "health": {
            "SUN": "life force",
            "MOON": "sleep, food, and mood",
            "MERCURY": "nervous system",
            "VENUS": "physical comfort",
            "MARS": "activity and exertion",
            "JUPITER": "tendency to overdo it",
            "SATURN": "routine and load limits",
        },
    },
}

DOMAIN_OPENERS = {
    "ru": {
        "energy": "Энергия",
        "work": "Работа",
        "finance": "Финансы",
        "love": "Отношения",
        "social": "Общение",
        "health": "Самочувствие",
    },
    "en": {
        "energy": "Energy",
        "work": "Work",
        "finance": "Finances",
        "love": "Relationships",
        "social": "Communication",
        "health": "Well-being",
    },
}

TRANSIT_DOMAIN_VERB = {
    "ru": {
        ("SUN", "energy"): "Солнце включает тему личной силы и самопроявления",
        ("SUN", "work"): "Солнце подсвечивает карьерные приоритеты и статус",
        ("SUN", "finance"): "Солнце фокусирует внимание на финансовой самооценке",
        ("SUN", "love"): "Солнце выводит на поверхность потребность быть увиденным в паре",
        ("SUN", "social"): "Солнце усиливает видимость в контактах",
        ("SUN", "health"): "Солнце требует честной оценки жизненного ресурса",
        ("MOON", "energy"): "Луна смещает эмоциональный фон и телесный отклик",
        ("MOON", "work"): "Луна делает рабочий ритм более чувствительным к настроению",
        ("MOON", "finance"): "Луна усиливает эмоциональную окраску трат и решений",
        ("MOON", "love"): "Луна обостряет потребность в тепле и принятии",
        ("MOON", "social"): "Луна делает переписку и встречи более личными",
        ("MOON", "health"): "Луна напоминает о связи сна, питания и настроения",
        ("MERCURY", "energy"): "Меркурий ускоряет мысли и переключает внимание",
        ("MERCURY", "work"): "Меркурий активирует договорённости, документы и логику задач",
        ("MERCURY", "finance"): "Меркурий включает расчёты, переговоры и мелкие сделки",
        ("MERCURY", "love"): "Меркурий ставит в центр слова, сообщения и ясность ожиданий",
        ("MERCURY", "social"): "Меркурий усиливает переписку, звонки и обмен информацией",
        ("MERCURY", "health"): "Меркурий может перегружать нервную систему — следи за темпом",
        ("VENUS", "energy"): "Венера смягчает день и тянет к приятному",
        ("VENUS", "work"): "Венера связывает работу с эстетикой и ценностью результата",
        ("VENUS", "finance"): "Венера включает траты, удовольствие и финансовый комфорт",
        ("VENUS", "love"): "Венера усиливает притяжение, нежность и тему близости",
        ("VENUS", "social"): "Венера облегчает приятные контакты и комплименты",
        ("VENUS", "health"): "Венера напоминает о телесном комфорте и заботе о себе",
        ("MARS", "energy"): "Марс добавляет напор, скорость и импульс",
        ("MARS", "work"): "Марс толкает к действию, дедлайнам и конкуренции",
        ("MARS", "finance"): "Марс провоцирует быстрые траты и рискованные решения",
        ("MARS", "love"): "Марс усиливает страсть, прямоту и возможные трения",
        ("MARS", "social"): "Марс делает речь резче — легко спорить",
        ("MARS", "health"): "Марс требует движения, но перегружает при избытке",
        ("JUPITER", "energy"): "Юпитер расширяет масштаб и уверенность",
        ("JUPITER", "work"): "Юпитер открывает возможности роста и обучения",
        ("JUPITER", "finance"): "Юпитер провоцирует оптимизм в деньгах — проверяй цифры",
        ("JUPITER", "love"): "Юпитер добавляет щедрости и желания делиться",
        ("JUPITER", "social"): "Юпитер расширяет круг общения и новые связи",
        ("JUPITER", "health"): "Юпитер склоняет к избытку — не переборщи с нагрузкой",
        ("SATURN", "energy"): "Сатурн замедляет и требует дисциплины",
        ("SATURN", "work"): "Сатурн проверяет ответственность и структуру задач",
        ("SATURN", "finance"): "Сатурн включает ограничения, бюджет и долгосрочные расчёты",
        ("SATURN", "love"): "Сатурн проясняет границы и серьёзность намерений",
        ("SATURN", "social"): "Сатурн делает общение более сдержанным и формальным",
        ("SATURN", "health"): "Сатурн напоминает о режиме и последствиях перегруза",
    },
    "en": {
        ("SUN", "energy"): "The Sun activates personal strength and self-expression",
        ("SUN", "work"): "The Sun highlights career priorities and status",
        ("SUN", "finance"): "The Sun focuses financial self-worth",
        ("SUN", "love"): "The Sun brings visibility needs into relationships",
        ("SUN", "social"): "The Sun increases visibility in contacts",
        ("SUN", "health"): "The Sun asks for an honest read of your vitality",
        ("MOON", "energy"): "The Moon shifts emotional tone and bodily response",
        ("MOON", "work"): "The Moon makes work rhythm mood-sensitive",
        ("MOON", "finance"): "The Moon colors spending and money choices emotionally",
        ("MOON", "love"): "The Moon heightens the need for warmth and acceptance",
        ("MOON", "social"): "The Moon makes chats and meetings more personal",
        ("MOON", "health"): "The Moon links sleep, food, and mood",
        ("MERCURY", "energy"): "Mercury speeds thoughts and attention shifts",
        ("MERCURY", "work"): "Mercury activates agreements, paperwork, and task logic",
        ("MERCURY", "finance"): "Mercury turns on calculations and small deals",
        ("MERCURY", "love"): "Mercury centers words, messages, and clear expectations",
        ("MERCURY", "social"): "Mercury boosts messages, calls, and information flow",
        ("MERCURY", "health"): "Mercury can overload nerves — watch your pace",
        ("VENUS", "energy"): "Venus softens the day and pulls toward comfort",
        ("VENUS", "work"): "Venus links work with aesthetics and value",
        ("VENUS", "finance"): "Venus activates spending, pleasure, and financial ease",
        ("VENUS", "love"): "Venus intensifies attraction, tenderness, and closeness",
        ("VENUS", "social"): "Venus eases pleasant contact and compliments",
        ("VENUS", "health"): "Venus reminds you about bodily comfort and self-care",
        ("MARS", "energy"): "Mars adds drive, speed, and impulse",
        ("MARS", "work"): "Mars pushes deadlines, action, and competition",
        ("MARS", "finance"): "Mars provokes quick spending and risky calls",
        ("MARS", "love"): "Mars intensifies passion, directness, and friction",
        ("MARS", "social"): "Mars sharpens speech — arguments come easier",
        ("MARS", "health"): "Mars demands movement but overloads if excessive",
        ("JUPITER", "energy"): "Jupiter expands confidence and scale",
        ("JUPITER", "work"): "Jupiter opens growth and learning opportunities",
        ("JUPITER", "finance"): "Jupiter brings money optimism — check the numbers",
        ("JUPITER", "love"): "Jupiter adds generosity and sharing",
        ("JUPITER", "social"): "Jupiter widens your social circle",
        ("JUPITER", "health"): "Jupiter tends toward excess — don't overdo load",
        ("SATURN", "energy"): "Saturn slows the pace and asks for discipline",
        ("SATURN", "work"): "Saturn tests responsibility and task structure",
        ("SATURN", "finance"): "Saturn brings limits, budgets, and long-range math",
        ("SATURN", "love"): "Saturn clarifies boundaries and serious intent",
        ("SATURN", "social"): "Saturn makes contact more reserved and formal",
        ("SATURN", "health"): "Saturn reminds you about routine and overload cost",
    },
}

NATAL_POINT = {
    "ru": {
        "SUN": ("Солнцу", "Солнцем", "ядро личности"),
        "MOON": ("Луне", "Луной", "эмоциональные привычки"),
        "MERCURY": ("Меркурию", "Меркурием", "стиль мышления и речи"),
        "VENUS": ("Венере", "Венерой", "ценности и близость"),
        "MARS": ("Марсу", "Марсом", "волю и способ действовать"),
        "JUPITER": ("Юпитеру", "Юпитером", "рост и возможности"),
        "SATURN": ("Сатурну", "Сатурном", "границы и ответственность"),
        "ASC": ("Асценденту", "Асцендентом", "образ и первое впечатление"),
    },
    "en": {
        "SUN": ("Sun", "Sun", "core identity"),
        "MOON": ("Moon", "Moon", "emotional habits"),
        "MERCURY": ("Mercury", "Mercury", "thinking and speech style"),
        "VENUS": ("Venus", "Venus", "values and closeness"),
        "MARS": ("Mars", "Mars", "will and drive"),
        "JUPITER": ("Jupiter", "Jupiter", "growth and opportunity"),
        "SATURN": ("Saturn", "Saturn", "boundaries and discipline"),
        "ASC": ("Ascendant", "Ascendant", "image and first impression"),
    },
}

MOON_ELEMENT_DOMAIN = {
    "ru": {
        "fire": {
            "energy": "день просит коротких рывков и быстрых решений",
            "work": "легче брать инициативу и открывать новое",
            "finance": "растёт импульс трат — проверяй мотивацию",
            "love": "эмоции выражаются прямо и горячо",
            "social": "контакты оживляются, но возможны споры",
            "health": "нужен активный сброс энергии без перегруза",
        },
        "earth": {
            "energy": "лучше держать ровный, практичный темп",
            "work": "хорошо для рутины, сроков и конкретных результатов",
            "finance": "уместны расчёт и проверка цифр",
            "love": "важнее надёжность, чем яркие жесты",
            "social": "полезны деловые и спокойные разговоры",
            "health": "тело откликается на режим и простую еду",
        },
        "air": {
            "energy": "умственная активность выше физической",
            "work": "идут переговоры, идеи и переключения",
            "finance": "решения принимаются через сравнение и обсуждение",
            "love": "слова и переписка важнее жестов",
            "social": "лучший день для встреч и обмена мнениями",
            "health": "нервная система чувствительна к информационному шуму",
        },
        "water": {
            "energy": "силы зависят от настроения и близости",
            "work": "интуиция помогает, но легко уйти в прокрастинацию",
            "finance": "эмоции могут тянуть к утешительным покупкам",
            "love": "глубже чувствуется потребность в поддержке",
            "social": "лучше выбирать доверительный тон",
            "health": "важны сон, вода и эмоциональная разгрузка",
        },
    },
    "en": {
        "fire": {
            "energy": "the day favors short bursts and quick calls",
            "work": "initiative and fresh starts come easier",
            "finance": "spending impulse rises — check your motive",
            "love": "feelings run direct and warm",
            "social": "contacts liven up, but debates are possible",
            "health": "you need active release without overload",
        },
        "earth": {
            "energy": "a steady, practical pace works best",
            "work": "good for routine, deadlines, and tangible results",
            "finance": "calculation and number checks fit well",
            "love": "reliability matters more than flashy gestures",
            "social": "calm, useful conversations help most",
            "health": "your body responds to routine and simple food",
        },
        "air": {
            "energy": "mental activity runs higher than physical drive",
            "work": "negotiation, ideas, and switching tasks flow",
            "finance": "choices come through comparison and talk",
            "love": "words and messages matter more than gestures",
            "social": "a strong day for meetings and exchange",
            "health": "nerves react to information overload",
        },
        "water": {
            "energy": "energy depends on mood and closeness",
            "work": "intuition helps, but procrastination is easy",
            "finance": "emotions may pull toward comfort spending",
            "love": "the need for support feels deeper",
            "social": "a trusting tone works better",
            "health": "sleep, hydration, and emotional release matter",
        },
    },
}

SUN_MOON_RELATION = {
    "ru": {
        "harmony": "Луна и ваш солнечный знак в одном стихийном ключе — день звучит цельно.",
        "support": "Луна поддерживает солнечный знак через смежную стихию — легче действовать последовательно.",
        "tension": "Луна и солнечный знак в разных стихиях — держи баланс между желанием и реальностью.",
    },
    "en": {
        "harmony": "Moon and your Sun sign share an element — the day feels coherent.",
        "support": "Moon supports your Sun through a friendly element — consistency comes easier.",
        "tension": "Moon and Sun sit in different elements — balance want and reality.",
    },
}


TRANSIT_PREFIX = {
    "ru": {
        "SUN": "Транзитное Солнце",
        "MOON": "Транзитная Луна",
        "MERCURY": "Транзитный Меркурий",
        "VENUS": "Транзитная Венера",
        "MARS": "Транзитный Марс",
        "JUPITER": "Транзитный Юпитер",
        "SATURN": "Транзитный Сатурн",
    },
    "en": {
        "SUN": "Transit Sun",
        "MOON": "Transit Moon",
        "MERCURY": "Transit Mercury",
        "VENUS": "Transit Venus",
        "MARS": "Transit Mars",
        "JUPITER": "Transit Jupiter",
        "SATURN": "Transit Saturn",
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, key: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(key, key)


def _sign_label(locale: str, sign: str) -> str:
    return SIGN_LABELS[_lang(locale)].get(sign, sign)


def _element_relation(first_sign: str, second_sign: str) -> str:
    first = SIGN_ELEMENTS.get(first_sign, "fire")
    second = SIGN_ELEMENTS.get(second_sign, "fire")
    if first == second:
        return "harmony"
    pairs = {frozenset({"fire", "air"}), frozenset({"earth", "water"})}
    if frozenset({first, second}) in pairs:
        return "support"
    return "tension"


def _orb_note(locale: str, orb: float) -> str:
    if orb > 2.5:
        return ""
    if _lang(locale) == "ru":
        return f" (орб {orb:.1f}°)"
    return f" (orb {orb:.1f}°)"


def _natal_forms(locale: str, natal: str) -> tuple[str, str, str]:
    lang = _lang(locale)
    default = _planet_label(locale, natal)
    entry = NATAL_POINT[lang].get(natal, (default, default, default))
    return entry[0], entry[1], entry[2]


def _aspect_label(locale: str, aspect: str) -> str:
    return ASPECT_LABELS[_lang(locale)].get(aspect, aspect)


def _natal_role_short(locale: str, natal: str) -> str:
    lang = _lang(locale)
    return NATAL_ROLE_SHORT[lang].get(natal, _planet_label(locale, natal).lower())


def _domain_focus(locale: str, domain: str, natal: str) -> str:
    lang = _lang(locale)
    return DOMAIN_FOCUS[lang].get(domain, {}).get(natal, _natal_role_short(locale, natal))


def _transit_domain_intro(locale: str, transit: str, domain: str) -> str:
    lang = _lang(locale)
    text = TRANSIT_DOMAIN_VERB[lang].get(
        (transit, domain),
        TRANSIT_DOMAIN_VERB[lang].get((transit, "energy"), _planet_label(locale, transit)),
    )
    return f"{text}."


def _domain_hit_line(
    locale: str,
    domain: str,
    transit: str,
    natal: str,
    aspect: str,
    orb: float,
    *,
    bullet: str = "",
    focus_planet: str | None = None,
) -> str:
    lang = _lang(locale)
    transit_name = _planet_label(locale, transit)
    natal_name = _planet_label(locale, natal)
    aspect_label = _aspect_label(locale, aspect)
    orb_part = f" ({orb:.1f}°)" if orb <= 2.5 else ""
    verb = ASPECT_VERB_SHORT[lang][aspect]
    focus = _domain_focus(locale, domain, focus_planet or natal)
    if lang == "ru":
        core = f"{transit_name}, {aspect_label} к {natal_name}{orb_part} — {verb} {focus}"
    else:
        core = f"{transit_name} {aspect_label} {natal_name}{orb_part} — {verb} {focus}"
    if not bullet:
        return core
    return f"{bullet} {core}"


def _compact_hit_line(
    locale: str,
    transit: str,
    natal: str,
    aspect: str,
    orb: float,
    *,
    bullet: str = "",
) -> str:
    lang = _lang(locale)
    transit_name = _planet_label(locale, transit)
    natal_name = _planet_label(locale, natal)
    aspect_label = _aspect_label(locale, aspect)
    orb_part = f" ({orb:.1f}°)" if orb <= 2.5 else ""
    verb = ASPECT_VERB_SHORT[lang][aspect]
    role = _natal_role_short(locale, natal)
    if lang == "ru":
        core = f"{transit_name}, {aspect_label} к {natal_name}{orb_part} — {verb} {role}"
    else:
        core = f"{transit_name} {aspect_label} {natal_name}{orb_part} — {verb} {role}"
    if not bullet:
        return core
    return f"{bullet} {core}"


def _love_suffix(locale: str, domain: str, transit: str, relationship_status: str | None) -> str:
    if domain != "love" or not relationship_status:
        return ""
    lang = _lang(locale)
    if relationship_status == "single" and transit in {"VENUS", "MOON"}:
        return " Особенно заметно в новых знакомствах." if lang == "ru" else " Especially visible in new connections."
    if relationship_status == "relationship" and transit in {"VENUS", "MOON", "MARS"}:
        return " Обсуди это с партнёром напрямую." if lang == "ru" else " Discuss it openly with your partner."
    return ""


def format_domain_hit(
    locale: str,
    domain: str,
    transit: str,
    natal: str,
    aspect: str,
    orb: float,
    *,
    relationship_status: str | None = None,
    include_opener: bool = True,
    focus_planet: str | None = None,
) -> str:
    del include_opener
    line = _domain_hit_line(
        locale,
        domain,
        transit,
        natal,
        aspect,
        orb,
        focus_planet=focus_planet,
    )
    return line + _love_suffix(locale, domain, transit, relationship_status)


def _collapse_prose(text: str) -> str:
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def format_score_word(score: int, locale: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        if score >= 8:
            return "высокая"
        if score >= 6:
            return "живая"
        if score >= 4:
            return "ровная"
        return "спокойная"
    if score >= 8:
        return "high"
    if score >= 6:
        return "active"
    if score >= 4:
        return "steady"
    return "quiet"


def format_plain_accent(
    locale: str,
    _transit: str,
    natal: str,
    aspect: str,
    _orb: float,
    *,
    period: str = "day",
) -> str:
    lang = _lang(locale)
    role = _natal_role_short(locale, natal)
    if lang == "ru":
        scope = {"day": "день", "week": "неделя", "month": "месяц"}.get(period, "день")
        mapping = {
            "conjunction": f"Главный акцент {scope} — {role}: усилит эту тему.",
            "sextile": f"Мягкая поддержка на {scope} в теме «{role}».",
            "trine": f"{scope.capitalize()} облегчает {role} — можно опираться на это.",
            "square": f"На {role} давление — не форсируй и снижай темп.",
            "opposition": f"{role.capitalize()} тянут в разные стороны — ищи середину.",
        }
        return mapping.get(aspect, f"Акцент {scope} — {role}.")
    scope = {"day": "today", "week": "this week", "month": "this month"}.get(period, "today")
    mapping = {
        "conjunction": f"Main focus {scope} — {role}: amplifies this theme.",
        "sextile": f"Gentle support {scope} around {role}.",
        "trine": f"{scope.capitalize()} eases {role} — you can lean on that.",
        "square": f"Pressure on {role} — don't force it; slow down.",
        "opposition": f"{role.capitalize()} pull in opposite directions — find the middle.",
    }
    return mapping.get(aspect, f"{scope.capitalize()} accent — {role}.")


def format_forecast_opening(
    locale: str,
    period: str,
    moon_sign: str,
    accent_line: str | None = None,
    *,
    period_start: date | None = None,
    period_end: date | None = None,
) -> str:
    lang = _lang(locale)
    moon = format_moon_in_sign_short(locale, moon_sign)
    hint = moon_in_sign_hint(locale, moon_sign)
    if period == "week" and period_start and period_end:
        if lang == "ru":
            period_line = (
                f"На этой неделе ({period_start.strftime('%d.%m')}–{period_end.strftime('%d.%m')}) "
                f"старт с {moon.lower()}."
            )
        else:
            period_line = (
                f"This week ({period_start.strftime('%d.%m')}–{period_end.strftime('%d.%m')}) "
                f"opens with {moon.lower()}."
            )
    elif period == "month" and period_start and period_end:
        if lang == "ru":
            period_line = (
                f"В этом месяце ({period_start.strftime('%d.%m')}–{period_end.strftime('%d.%m')}) "
                f"тон задаёт {moon.lower()}."
            )
        else:
            period_line = (
                f"This month ({period_start.strftime('%d.%m')}–{period_end.strftime('%d.%m')}) "
                f"— tone from {moon.lower()}."
            )
    else:
        period_word = {
            "ru": {"day": "Сегодня", "week": "На этой неделе", "month": "В этом месяце"},
            "en": {"day": "Today", "week": "This week", "month": "This month"},
        }[lang][period]
        period_line = f"{period_word} {moon.lower()}."

    parts = [period_line]
    if hint:
        hint_clean = hint.strip()
        if hint_clean and not hint_clean.endswith("."):
            hint_clean += "."
        parts.append(hint_clean[0].upper() + hint_clean[1:])
    if accent_line:
        parts.append(accent_line)
    elif lang == "ru":
        if period == "week":
            parts.append("Ярких транзитов мало — выстраивай неделю без рывков.")
        elif period == "month":
            parts.append("Ярких транзитов мало — держи ровный месячный ритм.")
        else:
            parts.append("Ярких транзитов нет — держи свой обычный ритм.")
    else:
        if period == "week":
            parts.append("Few strong transits — pace the week without forcing.")
        elif period == "month":
            parts.append("Few strong transits — keep a steady monthly rhythm.")
        else:
            parts.append("No strong transits — keep your usual rhythm.")
    return " ".join(parts)


def format_neutral_domain(
    locale: str,
    domain: str,
    moon_sign: str,
    natal_sun_sign: str,
    *,
    period: str = "day",
) -> str:
    lang = _lang(locale)
    element = SIGN_ELEMENTS.get(moon_sign, "air")
    clause = MOON_ELEMENT_DOMAIN[lang][element][domain]
    relation = _element_relation(moon_sign, natal_sun_sign)
    relation_line = SUN_MOON_RELATION[lang][relation]
    moon = _sign_label(locale, moon_sign)
    if lang == "ru":
        if period == "week":
            return f"На неделе в {moon} тон такой: {clause}. {relation_line}"
        if period == "month":
            return f"В месяце при {moon} тон такой: {clause}. {relation_line}"
        return f"Луна в {moon} задаёт тон: {clause}. {relation_line}"
    if period == "week":
        return f"This week in {moon} the tone is: {clause}. {relation_line}"
    if period == "month":
        return f"This month with {moon} the tone is: {clause}. {relation_line}"
    return f"Moon in {moon} sets the tone: {clause}. {relation_line}"


def format_domain_section(
    locale: str,
    domain: str,
    hits: list[Hit],
    *,
    moon_sign: str,
    natal_sun_sign: str,
    relationship_status: str | None = None,
    style: str = "terms",
    period: str = "day",
) -> str:
    if not hits:
        return format_neutral_domain(
            locale,
            domain,
            moon_sign,
            natal_sun_sign,
            period=period,
        )

    orb, transit, natal, aspect = hits[0]
    if _use_terms(style):
        line = _domain_hit_line(
            locale,
            domain,
            transit,
            natal,
            aspect,
            orb,
        )
        return line + _love_suffix(locale, domain, transit, relationship_status)

    lang = _lang(locale)
    intro = _transit_domain_intro(locale, transit, domain).rstrip(".")
    verb = ASPECT_VERB_SHORT[lang][aspect]
    focus = _domain_focus(locale, domain, natal)
    if lang == "ru":
        prose = f"{intro} — {verb} {focus}."
    else:
        prose = f"{intro} — {verb} {focus}."
    return prose + _love_suffix(locale, domain, transit, relationship_status)


def format_summary_aspect(
    locale: str,
    transit: str,
    natal: str,
    aspect: str,
    orb: float,
    *,
    style: str = "terms",
    period: str = "day",
) -> str:
    if _use_terms(style):
        return _compact_hit_line(locale, transit, natal, aspect, orb)
    return format_plain_accent(locale, transit, natal, aspect, orb, period=period)


def format_avoid(locale: str, hits: list[Hit], *, period: str = "day") -> str:
    lang = _lang(locale)
    challenging = [hit for hit in hits if hit[3] in {"square", "opposition"}]
    if not challenging:
        if lang == "ru":
            if period == "week":
                return "Острых аспектов на неделе мало — обычная осмотрительность."
            if period == "month":
                return "Острых аспектов в месяце мало — обычная осмотрительность."
            return "Острых аспектов в прогнозе нет — придерживайся обычной осмотрительности."
        if period == "week":
            return "Few sharp aspects this week — keep your usual caution."
        if period == "month":
            return "Few sharp aspects this month — keep your usual caution."
        return "No sharp aspects in the forecast — keep your usual caution."

    orb, transit, natal, aspect = challenging[0]
    role = _natal_role_short(locale, natal)
    if lang == "ru":
        if aspect == "square":
            if period == "week":
                return f"На неделе не форсируй — {role} под давлением."
            if period == "month":
                return f"В месяце не форсируй — {role} под давлением."
            return f"Не форсируй и не спеши — {role} под давлением."
        if period == "week":
            return f"На неделе не уходи в крайности — {role} требуют баланса."
        if period == "month":
            return f"В месяце не уходи в крайности — {role} требуют баланса."
        return f"Не уходи в крайности — {role} требуют баланса."
    if aspect == "square":
        if period == "week":
            return f"This week don't force it — {role} are under pressure."
        if period == "month":
            return f"This month don't force it — {role} are under pressure."
        return f"Don't force it or rush — {role} are under pressure."
    if period == "week":
        return f"This week avoid extremes — {role} need balance."
    if period == "month":
        return f"This month avoid extremes — {role} need balance."
    return f"Avoid extremes — {role} need balance."


def format_advice(locale: str, hits: list[Hit], moon_sign: str, *, period: str = "day") -> str:
    lang = _lang(locale)
    if not hits:
        moon = format_moon_in_sign_short(locale, moon_sign)
        if lang == "ru":
            if period == "week":
                return f"Точных аспектов мало — выстраивай неделю по ритму ({moon.lower()})."
            if period == "month":
                return f"Точных аспектов мало — планируй месяц по ритму ({moon.lower()})."
            return f"Точных аспектов мало — ориентируйся на ритм ({moon.lower()}) и не разгоняй день искусственно."
        if period == "week":
            return f"Few exact aspects — pace the week with {moon.lower()}."
        if period == "month":
            return f"Few exact aspects — plan the month with {moon.lower()}."
        return f"Few exact aspects — follow the rhythm ({moon.lower()}) and don't force the pace."

    orb, transit, natal, aspect = hits[0]
    role = _natal_role_short(locale, natal)
    if lang == "ru":
        if aspect in {"trine", "sextile"}:
            if period == "week":
                return f"На неделе опирайся на поддержку — особенно в теме «{role}»."
            if period == "month":
                return f"В месяце опирайся на поддержку — особенно в теме «{role}»."
            return f"Опирайся на поддержку дня — особенно в теме «{role}»."
        if aspect == "conjunction":
            if period == "week":
                return f"На неделе выбери один шаг в теме «{role}», не распыляйся."
            if period == "month":
                return f"В месяце выбери один главный фокус в теме «{role}»."
            return f"Выбери один конкретный шаг в теме «{role}», не распыляйся."
        if aspect == "square":
            if period == "week":
                return f"На неделе сначала снизь напряжение — это про {role}."
            if period == "month":
                return f"В месяце не форсируй {role} — снижай темп."
            return f"Сначала снизь напряжение, потом действуй — это про {role}."
        if period == "week":
            return f"На неделе ищи середину — {role} тянут в разные стороны."
        if period == "month":
            return f"В месяце ищи баланс — {role} требуют терпения."
        return f"Ищи середину — {role} тянут в разные стороны."

    if aspect in {"trine", "sextile"}:
        if period == "week":
            return f"This week lean on support — especially around {role}."
        if period == "month":
            return f"This month lean on support — especially around {role}."
        return f"Use today's support — especially around {role}."
    if aspect == "conjunction":
        if period == "week":
            return f"This week pick one step around {role}; don't scatter focus."
        if period == "month":
            return f"This month choose one main focus around {role}."
        return f"Pick one concrete step around {role}; don't scatter your focus."
    if aspect == "square":
        if period == "week":
            return f"This week ease tension first — especially around {role}."
        if period == "month":
            return f"This month don't force {role}; slow the pace."
        return f"Ease tension first, then act — especially around {role}."
    if period == "week":
        return f"This week find the middle ground — {role} are pulled two ways."
    if period == "month":
        return f"This month find balance — {role} need patience."
    return f"Find the middle ground — {role} are pulled in two directions."


def format_affirmation(locale: str, hits: list[Hit], *, period: str = "day") -> str:
    lang = _lang(locale)
    if not hits:
        if lang == "ru":
            if period == "week":
                return "Я выстраиваю неделю в своём ритме, без лишней спешки."
            if period == "month":
                return "Я двигаюсь через месяц спокойно и последовательно."
            return "Я сохраняю свой ритм, даже когда небо не задаёт ярких акцентов."
        if period == "week":
            return "I pace my week in my own rhythm, without rush."
        if period == "month":
            return "I move through the month calmly and steadily."
        return "I keep my rhythm even when the sky sets no strong accents."

    orb, transit, natal, aspect = hits[0]
    role = _natal_role_short(locale, natal)
    if lang == "ru":
        day_word = "дня" if period == "day" else ("недели" if period == "week" else "месяца")
        mapping = {
            "trine": f"Я спокойно опираюсь на поддержку {day_word} — {role}.",
            "sextile": f"Я замечаю возможность {day_word} и использую её — {role}.",
            "conjunction": f"Я усиливаю {role} осознанно и без спешки.",
            "square": f"Я не форсирую {role} и сохраняю ясность.",
            "opposition": f"Я нахожу баланс — {role}.",
        }
        return mapping[aspect]
    scope = "today" if period == "day" else ("this week" if period == "week" else "this month")
    mapping = {
        "trine": f"I calmly accept {scope}'s support in {role}.",
        "sextile": f"I notice an opening {scope} and use it in {role}.",
        "conjunction": f"I strengthen {role} with intention and without rush.",
        "square": f"I don't force {role} and keep my clarity.",
        "opposition": f"I find balance in {role}.",
    }
    return mapping[aspect]
