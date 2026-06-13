"""Plain-language glosses for astrological phrases shown to beginners."""
from __future__ import annotations

from app.text_format import format_screen_body, b

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


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _sign_label(locale: str, sign_key: str) -> str:
    return SIGN_LABELS[_lang(locale)].get(sign_key, sign_key)

# How the Moon feels in each zodiac sign (sign key = English name).
MOON_IN_SIGN_HINT = {
    "ru": {
        "Aries": "настроение прямое и энергичное — легче действовать, сложнее ждать",
        "Taurus": "хочется спокойствия, комфорта и предсказуемости",
        "Gemini": "много мыслей и разговоров, внимание быстро переключается",
        "Cancer": "чувствительность выше — важны близость и ощущение защищённости",
        "Leo": "эмоции ярче, хочется признания и тёплого отклика",
        "Virgo": "практичный настрой — внимание к деталям и порядку",
        "Libra": "фокус на гармонии в отношениях, сложнее принимать резкие решения",
        "Scorpio": "чувства глубже и интенсивнее, возможна скрытность",
        "Sagittarius": "оптимизм и тяга к свободе, новым идеям и планам",
        "Capricorn": "сдержанность и деловой тон — меньше суеты, больше ответственности",
        "Aquarius": "отстранённость и интерес к идеям, нестандартным решениям",
        "Pisces": "мечтательность и эмпатия, границы между «своим» и «чужим» размыты",
    },
    "en": {
        "Aries": "mood runs direct and energetic — easier to act, harder to wait",
        "Taurus": "a need for calm, comfort, and predictability",
        "Gemini": "lots of thoughts and talk, attention shifts quickly",
        "Cancer": "higher sensitivity — closeness and safety matter more",
        "Leo": "feelings grow brighter; recognition and warmth feel important",
        "Virgo": "a practical tone — focus on details and order",
        "Libra": "focus on harmony in relationships; sharp calls feel harder",
        "Scorpio": "deeper, more intense feelings; privacy may increase",
        "Sagittarius": "optimism and a pull toward freedom, ideas, and plans",
        "Capricorn": "restraint and a businesslike tone — less fuss, more duty",
        "Aquarius": "some distance and interest in ideas and unusual solutions",
        "Pisces": "dreaminess and empathy; boundaries between self and others blur",
    },
}

SIGN_TONE_HINT = {
    "ru": {
        "Aries": "огненный знак — импульс, инициатива, прямота",
        "Taurus": "земный знак — стабильность, терпение, практичность",
        "Gemini": "воздушный знак — любознательность, общение, гибкость",
        "Cancer": "водный знак — чувствительность, забота, память",
        "Leo": "огненный знак — самовыражение, щедрость, уверенность",
        "Virgo": "земный знак — анализ, полезность, внимание к мелочам",
        "Libra": "воздушный знак — партнёрство, вкус, поиск баланса",
        "Scorpio": "водный знак — глубина, трансформация, интенсивность",
        "Sagittarius": "огненный знак — поиск смысла, свобода, оптимизм",
        "Capricorn": "земный знак — цели, дисциплина, зрелость",
        "Aquarius": "воздушный знак — независимость, идеи, будущее",
        "Pisces": "водный знак — интуиция, сочувствие, воображение",
    },
    "en": {
        "Aries": "fire sign — impulse, initiative, directness",
        "Taurus": "earth sign — stability, patience, practicality",
        "Gemini": "air sign — curiosity, talk, flexibility",
        "Cancer": "water sign — sensitivity, care, memory",
        "Leo": "fire sign — self-expression, generosity, confidence",
        "Virgo": "earth sign — analysis, usefulness, attention to detail",
        "Libra": "air sign — partnership, taste, balance",
        "Scorpio": "water sign — depth, transformation, intensity",
        "Sagittarius": "fire sign — meaning, freedom, optimism",
        "Capricorn": "earth sign — goals, discipline, maturity",
        "Aquarius": "air sign — independence, ideas, the future",
        "Pisces": "water sign — intuition, empathy, imagination",
    },
}

PLANET_ROLE_HINT = {
    "ru": {
        "SUN": "ядро личности и жизненная цель",
        "MOON": "эмоции, привычные реакции и потребности",
        "MERCURY": "мышление, речь и обучение",
        "VENUS": "ценности, притяжение и эстетика",
        "MARS": "воля, напор и способ действовать",
        "JUPITER": "рост, вера и масштаб возможностей",
        "SATURN": "структура, дисциплина и границы",
        "ASC": "первое впечатление и стиль самопроявления",
    },
    "en": {
        "SUN": "core identity and life direction",
        "MOON": "emotions, habits, and needs",
        "MERCURY": "thinking, speech, and learning",
        "VENUS": "values, attraction, and aesthetics",
        "MARS": "will, drive, and how you act",
        "JUPITER": "growth, faith, and sense of possibility",
        "SATURN": "structure, discipline, and boundaries",
        "ASC": "first impression and outward style",
    },
}

ASPECT_PLAIN = {
    "ru": {
        "conjunction": "планеты в одной теме — эффект усиливается",
        "sextile": "мягкая поддержка — возможности открываются легче",
        "trine": "гармоничный поток — тема идёт естественно",
        "square": "напряжение — нужна осознанность и компромисс",
        "opposition": "полюса тянут в разные стороны — ищи баланс",
    },
    "en": {
        "conjunction": "planets merge themes — the effect intensifies",
        "sextile": "gentle support — openings come more easily",
        "trine": "harmonious flow — the theme moves naturally",
        "square": "tension — awareness and compromise help",
        "opposition": "poles pull apart — look for balance",
    },
}

LUNAR_DAY_HINT = {
    "ru": "лунный день — порядковый номер цикла от новолуния; у каждого дня свой эмоциональный оттенок",
    "en": "lunar day — the day number since the new moon; each day has its own emotional tone",
}

MOON_SIGN_LEGEND = {
    "ru": (
        "«Луна в …» — Луна сейчас в этом знаке зодиака (Овен, Телец и т.д.), "
        "а не на планете. От знака зависят настроение и бытовой ритм дня."
    ),
    "en": (
        "“Moon in …” means the Moon is currently in that zodiac sign (Aries, Taurus, etc.), "
        "not on a planet. The sign shapes mood and the day's rhythm."
    ),
}

TRANSIT_LEGEND = {
    "ru": (
        "Транзит — как небо сегодня «касается» вашей натальной карты. "
        "Квадрат и оппозиция — напряжение; трин и секстиль — поддержка."
    ),
    "en": (
        "A transit is how today's sky touches your natal chart. "
        "Squares and oppositions bring tension; trines and sextiles bring support."
    ),
}


def moon_in_sign_hint(locale: str, sign_key: str) -> str:
    lang = _lang(locale)
    return MOON_IN_SIGN_HINT[lang].get(sign_key, "")


def sign_tone_hint(locale: str, sign_key: str) -> str:
    lang = _lang(locale)
    return SIGN_TONE_HINT[lang].get(sign_key, "")


def planet_role_hint(locale: str, planet_key: str) -> str:
    lang = _lang(locale)
    return PLANET_ROLE_HINT[lang].get(planet_key, planet_key)


def aspect_plain(locale: str, aspect_key: str) -> str:
    lang = _lang(locale)
    return ASPECT_PLAIN[lang].get(aspect_key, "")


def format_moon_in_sign_short(locale: str, sign_key: str) -> str:
    sign_name = _sign_label(locale, sign_key)
    if _lang(locale) == "ru":
        return f"Луна в {sign_name}"
    return f"Moon in {sign_name}"


def format_moon_in_sign(locale: str, sign_key: str) -> str:
    """«Луна в Овне» with a beginner-friendly gloss (for help screens)."""
    line = format_moon_in_sign_short(locale, sign_key)
    hint = moon_in_sign_hint(locale, sign_key)
    if hint:
        return f"{line} — {hint}"
    return line


def format_moon_in_sign_bullet(locale: str, sign_key: str) -> str:
    return f"• {format_moon_in_sign_short(locale, sign_key)}"


def format_placement_plain(locale: str, planet_key: str, sign_key: str) -> str:
    """Short gloss for natal «planet in sign» lines."""
    lang = _lang(locale)
    sign_name = _sign_label(locale, sign_key)
    role = planet_role_hint(locale, planet_key)
    tone = sign_tone_hint(locale, sign_key)
    if lang == "ru":
        return f"{role.capitalize()}; в {sign_name} — {tone}."
    return f"{role.capitalize()}; in {sign_name} — {tone}."


def gloss_aspect_line(locale: str, aspect_key: str, base_line: str) -> str:
    plain = aspect_plain(locale, aspect_key)
    if not plain:
        return base_line
    if _lang(locale) == "ru":
        return f"{base_line}\n   ↳ {plain.capitalize()}."
    return f"{base_line}\n   ↳ {plain.capitalize()}."


def moon_glossary_footer(locale: str, *, include_lunar_day: bool = False) -> str:
    lang = _lang(locale)
    lines = [f"💡 {MOON_SIGN_LEGEND[lang]}"]
    if include_lunar_day:
        lines.append(f"💡 {LUNAR_DAY_HINT[lang].capitalize()}.")
    return "\n".join(lines)


def transit_glossary_footer(locale: str) -> str:
    lang = _lang(locale)
    return f"💡 {TRANSIT_LEGEND[lang]}"


def _sign_hints_block(locale: str) -> str:
    lang = _lang(locale)
    lines: list[str] = []
    for sign_key in SIGN_LABELS["en"]:
        hint = moon_in_sign_hint(locale, sign_key)
        if not hint:
            continue
        lines.append(f"• {format_moon_in_sign_short(locale, sign_key)} — {hint}")
    title = "Знаки зодиака и настроение дня" if lang == "ru" else "Zodiac signs and daily mood"
    return f"{title}:\n" + "\n".join(lines)


def _planets_block(locale: str) -> str:
    lang = _lang(locale)
    lines = []
    for key in ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "ASC"):
        role = planet_role_hint(locale, key)
        label = "Асцендент" if key == "ASC" and lang == "ru" else (
            "Ascendant" if key == "ASC" else _planet_name(locale, key)
        )
        lines.append(f"• {label} — {role}")
    title = "Планеты в карте" if lang == "ru" else "Planets in the chart"
    return f"{title}:\n" + "\n".join(lines)


def _planet_name(locale: str, key: str) -> str:
    names = {
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
    return names[_lang(locale)].get(key, key)


def _aspects_block(locale: str) -> str:
    lang = _lang(locale)
    lines = []
    for aspect_key in ("conjunction", "sextile", "trine", "square", "opposition"):
        plain = aspect_plain(locale, aspect_key)
        if not plain:
            continue
        label = {
            "ru": {
                "conjunction": "соединение",
                "sextile": "секстиль",
                "trine": "трин",
                "square": "квадрат",
                "opposition": "оппозиция",
            },
            "en": {
                "conjunction": "conjunction",
                "sextile": "sextile",
                "trine": "trine",
                "square": "square",
                "opposition": "opposition",
            },
        }[lang][aspect_key]
        lines.append(f"• {label} — {plain}")
    title = "Аспекты" if lang == "ru" else "Aspects"
    return f"{title}:\n" + "\n".join(lines)


def build_glossary_help(locale: str, topic: str, *, moon_sign_key: str | None = None) -> str:
    lang = _lang(locale)
    title = "❓ Простыми словами" if lang == "ru" else "❓ In plain language"
    blocks: list[str] = [title, ""]

    if topic == "moon":
        if lang == "ru":
            blocks.append(MOON_SIGN_LEGEND[lang])
            blocks.append(LUNAR_DAY_HINT[lang].capitalize() + ".")
            blocks.append(
                "Фазы Луны (новолуние, полнолуние и т.д.) — сколько света видно на небе "
                "и в какой фазе цикла мы сейчас."
            )
        else:
            blocks.append(MOON_SIGN_LEGEND[lang])
            blocks.append(LUNAR_DAY_HINT[lang].capitalize() + ".")
            blocks.append(
                "Moon phases (new moon, full moon, etc.) show how much light is visible "
                "and where we are in the lunar cycle."
            )
        if moon_sign_key:
            blocks.extend(["", format_moon_in_sign(locale, moon_sign_key)])
        blocks.extend(["", _sign_hints_block(locale)])
        return format_screen_body("\n".join(blocks))

    if topic == "horo":
        if lang == "ru":
            blocks.extend(
                [
                    MOON_SIGN_LEGEND[lang],
                    TRANSIT_LEGEND[lang],
                    (
                        "В прогнозе «Марс квадрат к Луне» значит: сегодняшний Марс давит на вашу "
                        "эмоциональную сферу (Луну в натальной карте). Это не «Луна на Марсе»."
                    ),
                ]
            )
        else:
            blocks.extend(
                [
                    MOON_SIGN_LEGEND[lang],
                    TRANSIT_LEGEND[lang],
                    (
                        "“Mars square Moon” means today's Mars presses on your emotional Moon "
                        "in the natal chart — not “Moon on Mars.”"
                    ),
                ]
            )
        blocks.extend(["", _aspects_block(locale)])
        if moon_sign_key:
            blocks.extend(["", format_moon_in_sign(locale, moon_sign_key)])
        return format_screen_body("\n".join(blocks))

    if topic == "natal":
        if lang == "ru":
            blocks.append(
                "«Лагна» — восходный знак: как ты входишь в жизнь и как тебя видят. "
                "«Дом» — сфера жизни (карьера, отношения…). "
                "«Накшатра» — лунный сектор, уточняющий характер планеты."
            )
            blocks.extend(["", _planets_block(locale), "", _aspects_block(locale)])
        else:
            blocks.append(
                "Lagna is the rising sign; houses are life areas; nakshatras refine planetary expression."
            )
            blocks.extend(["", _planets_block(locale), "", _aspects_block(locale)])
        return format_screen_body("\n".join(blocks))

    if topic == "compat":
        if lang == "ru":
            blocks.extend(
                [
                    (
                        "Шаг 1 — солнечные знаки: стихии (Огонь, Земля, Воздух, Вода), "
                        "противоположные знаки и сочетания Огонь+Воздух / Земля+Вода."
                    ),
                    (
                        "Шаг 2 — ASC и DSC: асцендент (как проявляетесь) и десцендент "
                        "(куспид 7‑го дома — образ идеального партнёра). "
                        "ASC одного = DSC другого — сильное притяжение; совпадение ASC — "
                        "похожие темпераменты; противоположные ASC↔DSC — магнетизм дополняющих типов."
                    ),
                    (
                        "Шаг 3 — синастрия: карты наложены друг на друга. "
                        "Гармоничные углы (0°, 60°, 120°) — поддержка; "
                        "напряжённые (90°, 180°) — рост. "
                        "Ключевые пары: Солнце↔Луна, Венера↔Марс, Меркурий↔Меркурий."
                    ),
                    (
                        "Фиктивные точки — Лилит (средняя Чёрная Луна): искушения и тень; "
                        "аспект к личной планете партнёра — риск манипуляций или зависимости. "
                        "Селена (противоположность Лилит): светлая карма; "
                        "аспект к Солнцу/Луне партнёра — «ангельская» поддержка."
                    ),
                    (
                        "Композитная карта — средняя точка между одинаковыми планетами: "
                        "Солнце/Луна композита — ядро отношений; ASC композита (1‑й дом) — "
                        "стиль пары «в мире»; планеты в угловых домах (1, 4, 7, 10) — "
                        "ключевые темы союза (например, Солнце в 8‑м — трансформация)."
                    ),
                    (
                        "Временные дирекции (вторичные прогрессии): 1 день = 1 год жизни; "
                        "аспекты между прогрессивными планетами партнёров — важные этапы; "
                        "смена знака прогрессивной Луны (~2,5 года) — эмоциональная перезагрузка; "
                        "возвращение к натальной Луне — крупный цикл (~27 лет)."
                    ),
                    (
                        "Нумерология отношений: все цифры даты рождения каждого сводятся "
                        "к одной цифре; сумма двух чисел — число совместимости пары."
                    ),
                    (
                        "Таро «Совместимость пары»: шесть карт — прошлое, настоящее, будущее, "
                        "сильные и слабые стороны, совет. Расклад детерминирован датами рождения."
                    ),
                    (
                        "Шаг 4 — печати: Юпитер→Солнце/Луна (счастье), "
                        "Сатурн→Солнце/Луна (несчастье в квадрате/оппозиции)."
                    ),
                    (
                        "Шаг 5 — синастрия по домам: какие планеты одного попадают в дома другого "
                        "(1 — личность, 2 — финансы, 3 — общение, 4 — семья, 5 — любовь, "
                        "7 — брак, 8 — трансформация, 9 — мировоззрение, 10 — карьера). "
                        "Угловые дома (1, 4, 7, 10) дают наиболее сильное влияние. Placidus."
                    ),
                    (
                        "Шаг 6 — баланс стихий: сколько планет в Огне, Земле, "
                        "Воздухе и Воде у каждого и насколько вы дополняете друг друга."
                    ),
                    (
                        "Шаг 7 — Луна↔Венера: гармония = душевная близость, "
                        "напряжение = разные представления о заботе."
                    ),
                    (
                        "Шаг 8 — узлы Раху/Кету: аспекты к личным планетам = кармическая "
                        "задача; Раху↔Солнце/Луна = «предназначенная» связь."
                    ),
                    (
                        "Шаг 9 — транзиты через синастрию: благоприятные периоды — "
                        "Венера и планета расширения; испытания — Сатурн/Уран/Плутон "
                        "по квадрату/оппозиции; карта на год — пики гармонии и напряжения."
                    ),
                    (
                        "Шаг 10 — итоговая карта: четыре уровня оценки с баллами "
                        "(гармония +1, напряжение −1, нейтрально 0). "
                        "Базовый — солнечные знаки и ASC/DSC; средний — синастрия и дома; "
                        "продвинутый — композит, прогрессии, фиктивные точки; "
                        "эзотерический — нумерология, Таро, энергии стихий."
                    ),
                    (
                        "Шаг 10 — итоговая таблица и интерпретация: высокая (>70% гармонии, "
                        "печать счастья, стихии), умеренная (ключи Луна‑Венера и Солнце‑Луна), "
                        "низкая (напряжение, печать несчастья, дисбаланс стихий)."
                    ),
                    (
                        "Комплексная оценка учитывает все уровни: базовый, средний, "
                        "продвинутый и эзотерический; итог — таблица +1/−1 и общий балл."
                    ),
                    (
                        "Рекомендации: не зацикливаться на «плохих» показателях; доверять интуиции; "
                        "избегать фатализма; обновлять синастрию раз в 5–7 лет; "
                        "использовать эзотерику как подсказку, не догму."
                    ),
                    (
                        "Оговорки: точность времени рождения."
                    ),
                    (
                        "Стиль описания — «с терминами» или «простым языком» "
                        "(кнопка в меню совместимости)."
                    ),
                    TRANSIT_LEGEND[lang],
                ]
            )
        else:
            blocks.extend(
                [
                    (
                        "Step 1 — Sun signs: elements (Fire, Earth, Air, Water), "
                        "opposite signs, and Fire+Air / Earth+Water pairings."
                    ),
                    (
                        "Step 2 — ASC and DSC: Ascendant (how you show up) and Descendant "
                        "(7th-house cusp — ideal partner image). "
                        "One ASC = other's DSC — strong pull; matching ASC — similar temperaments; "
                        "opposite ASC↔DSC — complementary magnetism."
                    ),
                    (
                        "Step 3 — synastry: charts overlaid. "
                        "Harmonious angles (0°, 60°, 120°) support; "
                        "tense ones (90°, 180°) mark growth zones. "
                        "Key pairs: Sun↔Moon, Venus↔Mars, Mercury↔Mercury."
                    ),
                    (
                        "Fictitious points — Lilith (mean Black Moon): temptations and shadow; "
                        "aspect to a partner's personal planet — manipulation or dependency risk. "
                        "Selena (opposite Lilith): light karma; "
                        "aspect to partner's Sun/Moon — “angelic” support."
                    ),
                    (
                        "Composite chart — midpoint between matching planets: "
                        "composite Sun/Moon — core of the bond; composite Ascendant (1st house) — "
                        "how the pair meets the world; planets in angular houses (1, 4, 7, 10) — "
                        "key union themes (e.g. Sun in the 8th — transformation)."
                    ),
                    (
                        "Temporary directions (secondary progressions): 1 day = 1 year of life; "
                        "aspects between partners' progressed planets mark key stages; "
                        "progressed Moon sign change (~2.5 years) — emotional reset; "
                        "return to natal Moon — major cycle (~27 years)."
                    ),
                    (
                        "Relationship numerology: reduce all birth-date digits to one digit per person; "
                        "add both numbers and reduce again — the pair compatibility number."
                    ),
                    (
                        "Tarot «Couple compatibility»: six cards — past, present, future, "
                        "strengths, weaknesses, advice. The spread is fixed by birth dates."
                    ),
                    (
                        "Step 4 — seals: Jupiter→Sun/Moon (happiness), "
                        "Saturn→Sun/Moon (unhappiness in square/opposition)."
                    ),
                    (
                        "Step 5 — house synastry: which planets of one partner fall into the other's houses "
                        "(1 identity, 2 finances, 3 communication, 4 family, 5 love, "
                        "7 marriage, 8 transformation, 9 worldview, 10 career). "
                        "Angular houses (1, 4, 7, 10) have the strongest influence. Placidus."
                    ),
                    (
                        "Step 6 — element balance: planet counts in Fire, Earth, "
                        "Air, and Water for each chart and how you complement."
                    ),
                    (
                        "Step 7 — Moon↔Venus: harmony = emotional closeness, "
                        "tension = different ideas about care."
                    ),
                    (
                        "Step 8 — Rahu/Ketu nodes: aspects to personal planets = karmic task; "
                        "Rahu↔Sun/Moon = “destined” bond."
                    ),
                    (
                        "Step 9 — synastry transits: Jupiter/Venus = favorable windows; "
                        "Saturn/Uranus/Pluto square/opposition = tests; "
                        "one-year map shows harmony and tension peaks."
                    ),
                    (
                        "Step 10 — scorecard: four assessment levels with points "
                        "(harmony +1, tension −1, neutral 0). "
                        "Basic — Sun signs and ASC/DSC; medium — synastry and houses; "
                        "advanced — composite, progressions, fictitious points; "
                        "esoteric — numerology, Tarot, element energies."
                    ),
                    (
                        "Step 10 — summary table and interpretation: high (>70% harmony, "
                        "happiness seal, elements), moderate (Moon‑Venus and Sun‑Moon keys), "
                        "low (tension, unhappiness seal, elemental imbalance)."
                    ),
                    (
                        "The full assessment uses all four levels; the scorecard (+1/−1) "
                        "feeds the headline /100 score."
                    ),
                    (
                        "Recommendations: don't fixate on «bad» scores; trust your intuition; "
                        "avoid fatalism; refresh synastry every 5–7 years; "
                        "use esoteric tools as hints, not dogma."
                    ),
                    (
                        "Notes: birth-time accuracy matters."
                    ),
                    (
                        "Description style — “with terms” or “plain language” "
                        "(button in the compatibility menu)."
                    ),
                    TRANSIT_LEGEND[lang],
                ]
            )
        blocks.extend(["", _aspects_block(locale)])
        return format_screen_body("\n".join(blocks))

    return b(title)
