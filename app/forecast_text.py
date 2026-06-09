from __future__ import annotations

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
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
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
    },
    "en": {
        "SUN": ("Sun", "Sun", "core identity"),
        "MOON": ("Moon", "Moon", "emotional habits"),
        "MERCURY": ("Mercury", "Mercury", "thinking and speech style"),
        "VENUS": ("Venus", "Venus", "values and closeness"),
        "MARS": ("Mars", "Mars", "will and drive"),
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


def _aspect_link(locale: str, aspect: str, orb: float, *, natal: str) -> str:
    lang = _lang(locale)
    tight = orb <= 2.0
    orb_part = _orb_note(locale, orb)
    natal_dat, natal_inst, _role = _natal_forms(locale, natal)
    if lang == "ru":
        exact = "точный " if tight else ""
        if aspect == "conjunction":
            return f"в соединении с натальной {natal_inst}{orb_part}"
        mapping = {
            "sextile": f"образует {exact}секстиль к натальному {natal_dat}{orb_part}",
            "trine": f"образует {exact}трин к натальному {natal_dat}{orb_part}",
            "square": f"образует {exact}квадрат к натальному {natal_dat}{orb_part}",
            "opposition": f"образует {exact}оппозицию к натальному {natal_dat}{orb_part}",
        }
        return mapping[aspect]
    exact = "exact " if tight else ""
    label = ASPECT_LABELS[lang][aspect]
    if aspect == "conjunction":
        return f"is conjunct natal {natal_inst}{orb_part}"
    mapping = {
        "sextile": f"forms an {exact}{label} to natal {natal_dat}{orb_part}",
        "trine": f"forms an {exact}{label} to natal {natal_dat}{orb_part}",
        "square": f"forms an {exact}{label} to natal {natal_dat}{orb_part}",
        "opposition": f"forms an {exact}{label} to natal {natal_dat}{orb_part}",
    }
    return mapping[aspect]


def _love_suffix(locale: str, domain: str, transit: str, relationship_status: str | None) -> str:
    if domain != "love" or not relationship_status:
        return ""
    lang = _lang(locale)
    if relationship_status == "single" and transit in {"VENUS", "MOON"}:
        return " Это особенно заметно в новых знакомствах." if lang == "ru" else " Especially visible in new connections."
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
) -> str:
    lang = _lang(locale)
    activation = TRANSIT_DOMAIN_VERB[lang].get(
        (transit, domain),
        TRANSIT_DOMAIN_VERB[lang].get((transit, "energy"), _planet_label(locale, transit)),
    )
    natal_dat, _natal_inst, natal_role = _natal_forms(locale, natal)
    link = _aspect_link(locale, aspect, orb, natal=natal)
    suffix = _love_suffix(locale, domain, transit, relationship_status)

    if lang == "ru":
        body = f"{activation} и {link} ({natal_role})"
        if include_opener:
            return f"{DOMAIN_OPENERS[lang][domain]}: {body}.{suffix}"
        return f"Также {body}.{suffix}"

    body = f"{activation} and {link} ({natal_role})"
    if include_opener:
        return f"{DOMAIN_OPENERS[lang][domain]}: {body}.{suffix}"
    return f"Also {body}.{suffix}"


def format_neutral_domain(
    locale: str,
    domain: str,
    moon_sign: str,
    natal_sun_sign: str,
) -> str:
    lang = _lang(locale)
    moon = _sign_label(locale, moon_sign)
    element = SIGN_ELEMENTS.get(moon_sign, "air")
    clause = MOON_ELEMENT_DOMAIN[lang][element][domain]
    relation = _element_relation(moon_sign, natal_sun_sign)
    relation_line = SUN_MOON_RELATION[lang][relation]
    if lang == "ru":
        return (
            f"{DOMAIN_OPENERS[lang][domain]}: точных транзитов к наталу здесь нет. "
            f"Луна в {moon} — {clause}. {relation_line}"
        )
    return (
        f"{DOMAIN_OPENERS[lang][domain]}: no exact natal transits here. "
        f"Moon in {moon} — {clause}. {relation_line}"
    )


def format_domain_section(
    locale: str,
    domain: str,
    hits: list[Hit],
    *,
    moon_sign: str,
    natal_sun_sign: str,
    relationship_status: str | None = None,
) -> str:
    if not hits:
        return format_neutral_domain(locale, domain, moon_sign, natal_sun_sign)
    parts = []
    for index, (orb, transit, natal, aspect) in enumerate(hits[:2]):
        parts.append(
            format_domain_hit(
                locale,
                domain,
                transit,
                natal,
                aspect,
                orb,
                relationship_status=relationship_status,
                include_opener=index == 0,
            )
        )
    return " ".join(parts)


def format_summary_aspect(locale: str, transit: str, natal: str, aspect: str, orb: float) -> str:
    lang = _lang(locale)
    natal_dat, natal_inst, natal_role = _natal_forms(locale, natal)
    link = _aspect_link(locale, aspect, orb, natal=natal)
    if lang == "ru":
        prefix = TRANSIT_PREFIX[lang].get(transit, f"Транзитный {_planet_label(locale, transit)}")
        return f"{prefix} {link} ({natal_role})."
    prefix = TRANSIT_PREFIX[lang].get(transit, f"Transit {_planet_label(locale, transit)}")
    return f"{prefix} {link} ({natal_role})."


def format_avoid(locale: str, hits: list[Hit]) -> str:
    lang = _lang(locale)
    challenging = [hit for hit in hits if hit[3] in {"square", "opposition"}]
    if not challenging:
        if lang == "ru":
            return "Острых аспектов в прогнозе нет — придерживайся обычной осмотрительности."
        return "No sharp aspects in the forecast — keep your usual caution."

    orb, transit, natal, aspect = challenging[0]
    natal_dat, natal_inst, natal_role = _natal_forms(locale, natal)
    if lang == "ru":
        if aspect == "square":
            return (
                f"Квадрат {_planet_label(locale, transit)} к {natal_dat} ({natal_role}): "
                f"не форсируй тему и не принимай резких решений на эмоциях."
            )
        return (
            f"Оппозиция {_planet_label(locale, transit)} к {natal_dat} ({natal_role}): "
            f"ищи компромисс, а не крайности."
        )
    if aspect == "square":
        return (
            f"Square of {_planet_label(locale, transit)} to {natal_dat} ({natal_role}): "
            f"don't force the issue or decide in heat."
        )
    return (
        f"Opposition of {_planet_label(locale, transit)} to {natal_dat} ({natal_role}): "
        f"seek compromise, not extremes."
    )


def format_advice(locale: str, hits: list[Hit], moon_sign: str) -> str:
    lang = _lang(locale)
    if not hits:
        moon = _sign_label(locale, moon_sign)
        if lang == "ru":
            return f"Точных аспектов мало — ориентируйся на ритм Луны в {moon} и не разгоняй день искусственно."
        return f"Few exact aspects — follow the Moon in {moon} and don't force the pace."

    orb, transit, natal, aspect = hits[0]
    natal_dat, natal_inst, natal_role = _natal_forms(locale, natal)
    if lang == "ru":
        if aspect in {"trine", "sextile"}:
            return (
                f"Опирайся на {ASPECT_LABELS[lang][aspect]} {_planet_label(locale, transit)} "
                f"к {natal_dat}: {natal_role} получает поддержку — используй это осознанно."
            )
        if aspect == "conjunction":
            return (
                f"Соединение {_planet_label(locale, transit)} с {natal_inst} усиливает тему "
                f"«{natal_role}» — выбери один конкретный шаг, а не всё сразу."
            )
        if aspect == "square":
            return (
                f"Квадрат {_planet_label(locale, transit)} к {natal_dat} давит на "
                f"«{natal_role}» — сначала снизь напряжение, потом действуй."
            )
        return (
            f"Оппозиция {_planet_label(locale, transit)} к {natal_dat} тянет "
            f"«{natal_role}» в разные стороны — ищи середину."
        )

    if aspect in {"trine", "sextile"}:
        return (
            f"Lean on {_planet_label(locale, transit)} {ASPECT_LABELS[lang][aspect]} "
            f"to {natal_dat}: {natal_role} is supported — use it deliberately."
        )
    if aspect == "conjunction":
        return (
            f"{_planet_label(locale, transit)} conjunct {natal_inst} intensifies "
            f"{natal_role} — pick one concrete step, not everything at once."
        )
    if aspect == "square":
        return (
            f"{_planet_label(locale, transit)} square {natal_dat} presses on "
            f"{natal_role} — reduce tension first, then act."
        )
    return (
        f"{_planet_label(locale, transit)} opposite {natal_dat} pulls "
        f"{natal_role} in two directions — find the middle."
    )


def format_affirmation(locale: str, hits: list[Hit]) -> str:
    lang = _lang(locale)
    if not hits:
        if lang == "ru":
            return "Я сохраняю свой ритм, даже когда небо не задаёт ярких акцентов."
        return "I keep my rhythm even when the sky sets no strong accents."

    orb, transit, natal, aspect = hits[0]
    natal_dat, natal_inst, natal_role = _natal_forms(locale, natal)
    if lang == "ru":
        mapping = {
            "trine": f"Я принимаю поддержку {_planet_label(locale, transit)} к {natal_dat} и укрепляю {natal_role}.",
            "sextile": f"Я замечаю возможность, которую открывает {_planet_label(locale, transit)} к {natal_dat}.",
            "conjunction": f"Я осознанно усиливаю {natal_role}, когда {_planet_label(locale, transit)} соединяется с {natal_inst}.",
            "square": f"Я не форсирую {natal_role}, пока {_planet_label(locale, transit)} создаёт напряжение с {natal_inst}.",
            "opposition": f"Я ищу баланс между потребностями {natal_role} и влиянием {_planet_label(locale, transit)}.",
        }
        return mapping[aspect]
    mapping = {
        "trine": f"I accept {_planet_label(locale, transit)} support to {natal_dat} and strengthen {natal_role}.",
        "sextile": f"I notice the opening {_planet_label(locale, transit)} to {natal_dat} creates.",
        "conjunction": f"I consciously strengthen {natal_role} as {_planet_label(locale, transit)} meets {natal_inst}.",
        "square": f"I do not force {natal_role} while {_planet_label(locale, transit)} squares {natal_inst}.",
        "opposition": f"I balance {natal_role} with the pull of {_planet_label(locale, transit)}.",
    }
    return mapping[aspect]
