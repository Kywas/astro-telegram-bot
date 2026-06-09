from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from app.geo import resolve_birth_location
from app.timezones import normalize_timezone

logger = logging.getLogger(__name__)

ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

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

PLANETS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
}

TRANSIT_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
NATAL_POINTS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")
DOMAINS = ("energy", "work", "finance", "love", "social", "health")

ASPECTS = (
    ("conjunction", 0, 8),
    ("sextile", 60, 6),
    ("square", 90, 7),
    ("trine", 120, 8),
    ("opposition", 180, 8),
)

PLANET_DOMAINS: dict[str, list[str]] = {
    "SUN": ["energy"],
    "MOON": ["health", "love"],
    "MERCURY": ["work", "social"],
    "VENUS": ["love", "finance"],
    "MARS": ["energy", "work"],
    "JUPITER": ["finance", "work"],
    "SATURN": ["work", "health"],
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
    "en": {sign: sign for sign in ZODIAC_SIGNS},
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

AVOID_BY_PLANET = {
    "ru": {
        "SUN": "давления на себя и спешки в главных решениях",
        "MOON": "эмоциональных перегрузок и недосыпа",
        "MERCURY": "поспешных договорённостей и путаницы в переписке",
        "VENUS": "эмоциональных трат и обидчивости в близости",
        "MARS": "конфликтов и импульсивных поступков",
        "JUPITER": "избыточного риска и переоценки возможностей",
        "SATURN": "жёсткого самокритицизма и перегруза обязанностями",
    },
    "en": {
        "SUN": "self-pressure and rushed major decisions",
        "MOON": "emotional overload and sleep deprivation",
        "MERCURY": "hasty agreements and messy communication",
        "VENUS": "emotional spending and touchiness in closeness",
        "MARS": "conflicts and impulsive actions",
        "JUPITER": "excessive risk and overestimating opportunities",
        "SATURN": "harsh self-criticism and duty overload",
    },
}

ADVICE_BY_PLANET = {
    "ru": {
        "SUN": "Сфокусируйся на одном приоритете — солнечный транзит поддерживает ясность цели.",
        "MOON": "Слушай своё состояние: ритм дня важнее внешнего давления.",
        "MERCURY": "Сначала проясни детали и договорённости, затем принимай решения.",
        "VENUS": "Инвестируй внимание в то, что приносит гармонию и ценность.",
        "MARS": "Направь напор в конкретное дело, избегая лишних столкновений.",
        "JUPITER": "Расширяй горизонты, но проверяй реалистичность планов.",
        "SATURN": "Структурируй задачи и двигайся последовательно — дисциплина сейчас полезна.",
    },
    "en": {
        "SUN": "Focus on one priority — the solar transit supports clear intent.",
        "MOON": "Listen to your state: your daily rhythm matters more than outside pressure.",
        "MERCURY": "Clarify details and agreements before making decisions.",
        "VENUS": "Invest attention in what brings harmony and real value.",
        "MARS": "Channel drive into one concrete task and avoid unnecessary clashes.",
        "JUPITER": "Expand your horizon, but check whether plans stay realistic.",
        "SATURN": "Structure tasks and move step by step — discipline helps now.",
    },
}

AFFIRMATION_BY_ASPECT = {
    "ru": {
        "trine": "Я принимаю поддержку дня и действую спокойно, в своём ритме.",
        "sextile": "Я замечаю возможности и использую их в нужный момент.",
        "conjunction": "Я осознанно усиливаю главную тему дня и держу фокус.",
        "square": "Я сохраняю равновесие и не форсирую события.",
        "opposition": "Я нахожу баланс между своими потребностями и обстоятельствами.",
    },
    "en": {
        "trine": "I accept the day's support and act calmly at my own pace.",
        "sextile": "I notice opportunities and use them at the right moment.",
        "conjunction": "I consciously strengthen today's main theme and stay focused.",
        "square": "I keep balance and do not force outcomes.",
        "opposition": "I balance my needs with what the situation requires.",
    },
}


@dataclass
class SectionForecast:
    text: str
    score: int


@dataclass
class AstroForecast:
    summary_lines: list[str]
    energy: SectionForecast
    work: SectionForecast
    finance: SectionForecast
    love: SectionForecast
    social: SectionForecast
    health: SectionForecast
    lucky_time: str
    avoid: str
    affirmation: str
    advice: str
    moon_sign: str = ""


@dataclass
class AstroHoroscopeContext:
    """Backward-compatible subset used by legacy callers."""

    summary_lines: list[str]
    score_adjustments: dict[str, int] = field(default_factory=dict)
    moon_sign: str = ""


def _longitude_to_sign(longitude: float) -> str:
    normalized = longitude % 360
    index = int(normalized // 30) % 12
    return ZODIAC_SIGNS[index]


def _sign_index(sign: str) -> int:
    try:
        return ZODIAC_SIGNS.index(sign)
    except ValueError:
        return 0


def _element_relation(first_sign: str, second_sign: str) -> str:
    first = SIGN_ELEMENTS.get(first_sign, "fire")
    second = SIGN_ELEMENTS.get(second_sign, "fire")
    if first == second:
        return "harmony"
    pairs = {frozenset({"fire", "air"}), frozenset({"earth", "water"})}
    if frozenset({first, second}) in pairs:
        return "support"
    return "tension"


def _angle_diff(first: float, second: float) -> float:
    diff = abs(first - second) % 360
    return diff if diff <= 180 else 360 - diff


def _find_aspect(first: float, second: float) -> tuple[str, float] | None:
    diff = _angle_diff(first, second)
    best: tuple[str, float] | None = None
    for name, exact, orb in ASPECTS:
        delta = abs(diff - exact)
        if delta <= orb and (best is None or delta < best[1]):
            best = (name, delta)
    return best


def _planet_longitude(julian_day: float, planet_id: int) -> float:
    result, _retflag = swe.calc_ut(julian_day, planet_id)
    return float(result[0])


def _local_moment_jd(
    for_date: date,
    timezone_name: str,
    *,
    hour: int = 12,
    minute: int = 0,
) -> float:
    tz = ZoneInfo(timezone_name)
    moment = datetime.combine(for_date, time(hour, minute), tzinfo=tz).astimezone(timezone.utc)
    ut_hours = moment.hour + moment.minute / 60 + moment.second / 3600
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def _natal_julian_day(
    birth_date: date,
    birth_time: time | None,
    timezone_name: str,
) -> float:
    if birth_time is None:
        return _local_moment_jd(birth_date, timezone_name, hour=12, minute=0)
    tz = ZoneInfo(timezone_name)
    moment = datetime.combine(birth_date, birth_time, tzinfo=tz).astimezone(timezone.utc)
    ut_hours = moment.hour + moment.minute / 60 + moment.second / 3600
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def _collect_longitudes(julian_day: float, keys: tuple[str, ...]) -> dict[str, float]:
    return {key: _planet_longitude(julian_day, PLANETS[key]) for key in keys}


def _planet_label(locale: str, key: str) -> str:
    lang = "ru" if locale == "ru" else "en"
    return PLANET_LABELS[lang].get(key, key)


def _sign_label(locale: str, sign: str) -> str:
    lang = "ru" if locale == "ru" else "en"
    return SIGN_LABELS[lang].get(sign, sign)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def planet_label(locale: str, key: str) -> str:
    return _planet_label(locale, key)


def sign_label(locale: str, sign: str) -> str:
    return _sign_label(locale, sign)


def longitude_to_sign(longitude: float) -> str:
    return _longitude_to_sign(longitude)


def _solar_natal_longitudes(sign: str) -> dict[str, float]:
    sun_lon = _sign_index(sign) * 30 + 15
    return {"SUN": sun_lon}


def _period_dates(period: str, for_date: date) -> list[date]:
    if period == "week":
        week_start = for_date - timedelta(days=for_date.weekday())
        return [week_start + timedelta(days=i) for i in range(7)]
    if period == "month":
        month_start = for_date.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        days = (next_month - month_start).days
        return [month_start + timedelta(days=i) for i in range(days)]
    return [for_date]


def _score_delta(aspect: str, transit: str) -> int:
    if aspect in {"trine", "sextile"}:
        return 1
    if aspect == "conjunction":
        return 1 if transit in {"VENUS", "JUPITER", "SUN"} else -1
    return -1


def _hit_domains(transit: str, natal: str) -> set[str]:
    domains: set[str] = set()
    domains.update(PLANET_DOMAINS.get(transit, []))
    domains.update(PLANET_DOMAINS.get(natal, []))
    return domains


def _collect_hits(
    natal_longitudes: dict[str, float],
    transit_longitudes: dict[str, float],
    *,
    birth_time: time | None,
    include_moon_transits: bool = False,
) -> list[tuple[float, str, str, str]]:
    hits: list[tuple[float, str, str, str]] = []
    for transit_key in TRANSIT_PLANETS:
        if transit_key == "MOON" and not include_moon_transits:
            continue
        for natal_key in natal_longitudes:
            if natal_key == "MOON" and birth_time is None:
                continue
            aspect_info = _find_aspect(
                transit_longitudes[transit_key],
                natal_longitudes[natal_key],
            )
            if aspect_info is None:
                continue
            aspect_name, orb_delta = aspect_info
            hits.append((orb_delta, transit_key, natal_key, aspect_name))
    hits.sort(key=lambda item: item[0])
    return hits


def _domain_hits(
    hits: list[tuple[float, str, str, str]],
    domain: str,
) -> list[tuple[float, str, str, str]]:
    return [hit for hit in hits if domain in _hit_domains(hit[1], hit[2])]


def _domain_score(domain_hits: list[tuple[float, str, str, str]]) -> int:
    score = 5
    for _orb, transit_key, _natal_key, aspect_name in domain_hits:
        score += _score_delta(aspect_name, transit_key)
    return max(1, min(10, score))


def _domain_hit_line(
    locale: str,
    domain: str,
    transit: str,
    natal: str,
    aspect: str,
    *,
    relationship_status: str | None = None,
    include_opener: bool = True,
) -> str:
    lang = _lang(locale)
    t = _planet_label(locale, transit)
    n = _planet_label(locale, natal)
    openers = {
        "ru": {
            "energy": "В сфере энергии",
            "work": "В работе",
            "finance": "В финансах",
            "love": "В отношениях",
            "social": "В общении",
            "health": "Для самочувствия",
        },
        "en": {
            "energy": "For energy",
            "work": "At work",
            "finance": "In finances",
            "love": "In relationships",
            "social": "In communication",
            "health": "For well-being",
        },
    }
    verbs = {
        "ru": {
            "trine": f"гармоничный аспект {t} к натальному {n} поддерживает и облегчает день",
            "sextile": f"секстиль {t}—{n} открывает полезные возможности",
            "conjunction": f"соединение {t} с {n} усиливает тему — действуй осознанно",
            "square": f"квадрат {t}—{n} создаёт напряжение — не форсируй",
            "opposition": f"оппозиция {t}—{n} требует баланса между противоположными потребностями",
        },
        "en": {
            "trine": f"harmonious aspect of {t} to natal {n} supports and eases the day",
            "sextile": f"sextile {t}–{n} opens useful opportunities",
            "conjunction": f"conjunction of {t} with {n} intensifies the theme — act consciously",
            "square": f"square {t}–{n} creates tension — avoid forcing outcomes",
            "opposition": f"opposition {t}–{n} asks for balance between opposing needs",
        },
    }
    suffix = ""
    if domain == "love":
        if relationship_status == "single" and transit in {"VENUS", "MOON"}:
            suffix = (
                " Благоприятный фон для новых знакомств."
                if lang == "ru"
                else " Supportive backdrop for new connections."
            )
        elif relationship_status == "relationship" and transit in {"VENUS", "MOON", "MARS"}:
            suffix = (
                " Удели внимание партнёру и совместным договорённостям."
                if lang == "ru"
                else " Give attention to your partner and shared agreements."
            )
    body = verbs[lang][aspect]
    if not include_opener:
        also = "Также " if lang == "ru" else "Also "
        return f"{also}{body}.{suffix}"
    return f"{openers[lang][domain]}: {body}.{suffix}"


def _neutral_domain_line(
    locale: str,
    domain: str,
    moon_sign: str,
    natal_sun_sign: str,
) -> str:
    lang = _lang(locale)
    relation = _element_relation(moon_sign, natal_sun_sign)
    moon = _sign_label(locale, moon_sign)
    templates = {
        "ru": {
            ("energy", "harmony"): f"Луна в {moon} поддерживает твой солнечный знак — ровный приток сил.",
            ("energy", "support"): f"Луна в {moon} благоприятна для активности без резких перепадов.",
            ("energy", "tension"): f"Луна в {moon} требует бережного отношения к ресурсу — не перегружай день.",
            ("work", "harmony"): f"Луна в {moon} помогает сосредоточиться на задачах без лишней суеты.",
            ("work", "support"): f"Луна в {moon} поддерживает рабочий ритм — двигай приоритеты спокойно.",
            ("work", "tension"): f"Луна в {moon} советует не спешить с решениями в делах.",
            ("finance", "harmony"): f"Луна в {moon} благоприятна для спокойного финансового планирования.",
            ("finance", "support"): f"Луна в {moon} поддерживает аккуратные денежные решения.",
            ("finance", "tension"): f"Луна в {moon} — лучше избегать импульсивных трат.",
            ("love", "harmony"): f"Луна в {moon} создаёт тёплый эмоциональный фон для близости.",
            ("love", "support"): f"Луна в {moon} помогает открытому и спокойному общению.",
            ("love", "tension"): f"Луна в {moon} усиливает чувствительность — говори мягче.",
            ("social", "harmony"): f"Луна в {moon} облегчает контакты и короткие встречи.",
            ("social", "support"): f"Луна в {moon} поддерживает полезные разговоры.",
            ("social", "tension"): f"Луна в {moon} — избегай резких формулировок в переписке.",
            ("health", "harmony"): f"Луна в {moon} поддерживает восстановление и стабильный режим.",
            ("health", "support"): f"Луна в {moon} благоприятна для умеренной активности и отдыха.",
            ("health", "tension"): f"Луна в {moon} — береги сон и не перегружай тело.",
        },
        "en": {
            ("energy", "harmony"): f"Moon in {moon} supports your sun sign — steady vitality.",
            ("energy", "support"): f"Moon in {moon} favors activity without sharp swings.",
            ("energy", "tension"): f"Moon in {moon} asks you to protect your energy — avoid overload.",
            ("work", "harmony"): f"Moon in {moon} helps you focus on tasks without extra noise.",
            ("work", "support"): f"Moon in {moon} supports a calm work rhythm.",
            ("work", "tension"): f"Moon in {moon} advises against rushing business decisions.",
            ("finance", "harmony"): f"Moon in {moon} favors calm financial planning.",
            ("finance", "support"): f"Moon in {moon} supports careful money choices.",
            ("finance", "tension"): f"Moon in {moon} — avoid impulsive spending.",
            ("love", "harmony"): f"Moon in {moon} brings a warm emotional tone for closeness.",
            ("love", "support"): f"Moon in {moon} helps open and calm communication.",
            ("love", "tension"): f"Moon in {moon} increases sensitivity — speak gently.",
            ("social", "harmony"): f"Moon in {moon} eases contacts and short meetings.",
            ("social", "support"): f"Moon in {moon} supports useful conversations.",
            ("social", "tension"): f"Moon in {moon} — avoid sharp wording in chats.",
            ("health", "harmony"): f"Moon in {moon} supports recovery and a steady routine.",
            ("health", "support"): f"Moon in {moon} favors moderate activity and rest.",
            ("health", "tension"): f"Moon in {moon} — protect sleep and avoid overloading your body.",
        },
    }
    return templates[lang][(domain, relation)]


def _domain_text(
    locale: str,
    domain: str,
    hits: list[tuple[float, str, str, str]],
    *,
    moon_sign: str,
    natal_sun_sign: str,
    relationship_status: str | None = None,
) -> str:
    domain_hits = _domain_hits(hits, domain)
    if not domain_hits:
        return _neutral_domain_line(locale, domain, moon_sign, natal_sun_sign)
    parts = []
    for index, (_orb, transit, natal, aspect) in enumerate(domain_hits[:2]):
        parts.append(
            _domain_hit_line(
                locale,
                domain,
                transit,
                natal,
                aspect,
                relationship_status=relationship_status,
                include_opener=index == 0,
            )
        )
    return " ".join(parts)


def _format_hour_ranges(hours: list[int], locale: str) -> str:
    if not hours:
        lang = _lang(locale)
        return (
            "нет ярко выраженных окон — ориентируйся на спокойный ритм"
            if lang == "ru"
            else "no strong windows — follow a calm daily rhythm"
        )

    ranges: list[tuple[int, int]] = []
    start = prev = hours[0]
    for hour in hours[1:]:
        if hour == prev + 1:
            prev = hour
            continue
        ranges.append((start, prev))
        start = prev = hour
    ranges.append((start, prev))

    parts = []
    for start_hour, end_hour in ranges[:2]:
        end_display = end_hour + 1
        parts.append(f"{start_hour:02d}:00-{end_display:02d}:00")

    lang = _lang(locale)
    if len(parts) == 1:
        return parts[0]
    connector = " и " if lang == "ru" else " and "
    return connector.join(parts)


def _lucky_hours_for_day(
    for_date: date,
    timezone_name: str,
    natal_longitudes: dict[str, float],
    *,
    birth_time: time | None,
) -> list[int]:
    lucky: list[int] = []
    natal_targets = [key for key in ("SUN", "VENUS", "JUPITER") if key in natal_longitudes]
    if not natal_targets:
        natal_targets = ["SUN"]

    for hour in range(7, 22):
        jd = _local_moment_jd(for_date, timezone_name, hour=hour, minute=0)
        moon_lon = _planet_longitude(jd, PLANETS["MOON"])
        for natal_key in natal_targets:
            if natal_key == "MOON" and birth_time is None:
                continue
            aspect_info = _find_aspect(moon_lon, natal_longitudes[natal_key])
            if aspect_info and aspect_info[0] in {"trine", "sextile", "conjunction"}:
                lucky.append(hour)
                break
    return lucky


def _lucky_time_text(
    period: str,
    period_dates: list[date],
    timezone_name: str,
    natal_longitudes: dict[str, float],
    locale: str,
    *,
    birth_time: time | None,
) -> str:
    if period == "day":
        hours = _lucky_hours_for_day(
            period_dates[0],
            timezone_name,
            natal_longitudes,
            birth_time=birth_time,
        )
        return _format_hour_ranges(hours, locale)

    best_date = period_dates[0]
    best_hours: list[int] = []
    for day in period_dates:
        hours = _lucky_hours_for_day(day, timezone_name, natal_longitudes, birth_time=birth_time)
        if len(hours) > len(best_hours):
            best_date = day
            best_hours = hours

    hours_text = _format_hour_ranges(best_hours, locale)
    lang = _lang(locale)
    if lang == "ru":
        weekday_names = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        day_label = weekday_names[best_date.weekday()]
        if period == "month":
            day_label = f"{best_date.day} число"
        return f"{day_label}, {hours_text}"
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_label = weekday_names[best_date.weekday()]
    if period == "month":
        day_label = f"the {best_date.day}th"
    return f"{day_label}, {hours_text}"


def _avoid_text(
    hits: list[tuple[float, str, str, str]],
    locale: str,
) -> str:
    lang = _lang(locale)
    challenging = [hit for hit in hits if hit[3] in {"square", "opposition"}]
    if not challenging:
        if lang == "ru":
            return "острых астрологических противоречий нет — держи обычную осмотрительность."
        return "no sharp astrological friction — keep your usual caution."

    _orb, transit, _natal, aspect = challenging[0]
    planet_avoid = AVOID_BY_PLANET[lang][transit]
    aspect_label = ASPECT_LABELS[lang][aspect]
    if lang == "ru":
        return f"{aspect_label} транзитного {_planet_label(locale, transit)}: {planet_avoid}."
    return f"{aspect_label} from transit {_planet_label(locale, transit)}: {planet_avoid}."


def _affirmation_text(
    hits: list[tuple[float, str, str, str]],
    locale: str,
) -> str:
    lang = _lang(locale)
    positive = [hit for hit in hits if hit[3] in {"trine", "sextile", "conjunction"}]
    if positive:
        return AFFIRMATION_BY_ASPECT[lang][positive[0][3]]
    if hits:
        return AFFIRMATION_BY_ASPECT[lang][hits[0][3]]
    if lang == "ru":
        return "Я сохраняю спокойствие и двигаюсь в своём ритме."
    return "I stay calm and move at my own pace."


def _advice_text(
    hits: list[tuple[float, str, str, str]],
    locale: str,
) -> str:
    lang = _lang(locale)
    if hits:
        _orb, transit, _natal, _aspect = hits[0]
        return ADVICE_BY_PLANET[lang][transit]
    if lang == "ru":
        return "Ориентируйся на стабильный ритм — день без ярких транзитов."
    return "Follow a steady rhythm — a day without major transits."


def _aspect_phrase(locale: str, transit: str, natal: str, aspect: str) -> str:
    lang = _lang(locale)
    aspect_name = ASPECT_LABELS[lang][aspect]
    if lang == "ru":
        tone = {
            "trine": "поддерживает и облегчает",
            "sextile": "открывает возможности",
            "conjunction": "усиливает тему",
            "square": "создаёт напряжение",
            "opposition": "требует баланса",
        }[aspect]
        return (
            f"Транзитный {_planet_label(locale, transit)} — {aspect_name} "
            f"к натальному {_planet_label(locale, natal)}: {tone}."
        )
    tone = {
        "trine": "supports and eases the flow",
        "sextile": "opens opportunities",
        "conjunction": "intensifies the theme",
        "square": "creates tension",
        "opposition": "asks for balance",
    }[aspect]
    return (
        f"Transit {_planet_label(locale, transit)} {aspect_name} "
        f"natal {_planet_label(locale, natal)}: {tone}."
    )


def _build_summary_lines(
    locale: str,
    hits: list[tuple[float, str, str, str]],
    moon_sign: str,
    *,
    birth_time: time | None,
    solar_only: bool,
    period: str,
) -> list[str]:
    lang = _lang(locale)
    period_note = ""
    if period == "week":
        period_note = " (неделя)" if lang == "ru" else " (week)"
    elif period == "month":
        period_note = " (месяц)" if lang == "ru" else " (month)"

    summary = [
        (
            f"🪐 Астрологический прогноз (Swiss Ephemeris){period_note}"
            if lang == "ru"
            else f"🪐 Astrological forecast (Swiss Ephemeris){period_note}"
        ),
        (
            f"• Луна в {_sign_label(locale, moon_sign)}"
            if lang == "ru"
            else f"• Moon in {_sign_label(locale, moon_sign)}"
        ),
    ]
    if solar_only:
        summary.append(
            "• Расчёт по солнечному знаку — укажите дату рождения для натальной карты."
            if lang == "ru"
            else "• Solar-sign chart only — add your birth date for a natal chart."
        )
    elif birth_time is None:
        summary.append(
            "• Натал: время рождения не указано — Луна и дома не учитываются."
            if lang == "ru"
            else "• Natal: birth time missing — Moon and houses are not included."
        )
    if not hits:
        summary.append(
            "• Ярких транзитных аспектов к наталу нет — день более ровный."
            if lang == "ru"
            else "• No major transits to your natal chart — a steadier day."
        )
    else:
        for _orb, transit_key, natal_key, aspect_name in hits[:3]:
            summary.append(f"• {_aspect_phrase(locale, transit_key, natal_key, aspect_name)}")
    return summary


def _aggregate_hits(
    natal_longitudes: dict[str, float],
    period_dates: list[date],
    timezone_name: str,
    *,
    birth_time: time | None,
) -> tuple[list[tuple[float, str, str, str]], str, dict[str, float]]:
    all_hits: list[tuple[float, str, str, str]] = []
    last_transit: dict[str, float] = {}
    moon_sign = "Aries"

    for day in period_dates:
        transit_jd = _local_moment_jd(day, timezone_name, hour=12, minute=0)
        transit_longitudes = _collect_longitudes(transit_jd, TRANSIT_PLANETS)
        last_transit = transit_longitudes
        moon_sign = _longitude_to_sign(transit_longitudes["MOON"])
        day_hits = _collect_hits(
            natal_longitudes,
            transit_longitudes,
            birth_time=birth_time,
        )
        all_hits.extend(day_hits)

    unique: dict[tuple[str, str, str], tuple[float, str, str, str]] = {}
    for hit in all_hits:
        key = (hit[1], hit[2], hit[3])
        if key not in unique or hit[0] < unique[key][0]:
            unique[key] = hit
    merged = sorted(unique.values(), key=lambda item: item[0])
    return merged, moon_sign, last_transit


def build_astro_forecast(
    *,
    birth_date: date | None,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    for_date: date,
    locale: str,
    period: str = "day",
    sign: str | None = None,
    relationship_status: str | None = None,
    user_id: int | None = None,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> AstroForecast | None:
    try:
        tz = normalize_timezone(birth_timezone or timezone_name)
        _lat, _lon, resolved_tz = resolve_birth_location(
            city,
            tz,
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        period_key = period if period in {"day", "week", "month"} else "day"
        period_dates = _period_dates(period_key, for_date)

        solar_only = birth_date is None
        if solar_only:
            if not sign:
                return None
            natal_longitudes = _solar_natal_longitudes(sign)
        else:
            natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
            natal_longitudes = _collect_longitudes(natal_jd, NATAL_POINTS)

        hits, moon_sign, _transit_longitudes = _aggregate_hits(
            natal_longitudes,
            period_dates,
            tz,
            birth_time=birth_time,
        )
        natal_sun_sign = _longitude_to_sign(natal_longitudes["SUN"])

        summary_lines = _build_summary_lines(
            locale,
            hits,
            moon_sign,
            birth_time=birth_time,
            solar_only=solar_only,
            period=period_key,
        )

        sections = {}
        for domain in DOMAINS:
            domain_hits = _domain_hits(hits, domain)
            if len(period_dates) > 1:
                daily_scores = []
                for day in period_dates:
                    day_jd = _local_moment_jd(day, tz, hour=12, minute=0)
                    day_transit = _collect_longitudes(day_jd, TRANSIT_PLANETS)
                    day_hits = _collect_hits(natal_longitudes, day_transit, birth_time=birth_time)
                    daily_scores.append(_domain_score(_domain_hits(day_hits, domain)))
                score = max(1, min(10, round(sum(daily_scores) / len(daily_scores))))
            else:
                score = _domain_score(domain_hits)
            text = _domain_text(
                locale,
                domain,
                hits,
                moon_sign=moon_sign,
                natal_sun_sign=natal_sun_sign,
                relationship_status=relationship_status,
            )
            sections[domain] = SectionForecast(text=text, score=score)

        lucky_time = _lucky_time_text(
            period_key,
            period_dates,
            tz,
            natal_longitudes,
            locale,
            birth_time=birth_time,
        )

        return AstroForecast(
            summary_lines=summary_lines,
            energy=sections["energy"],
            work=sections["work"],
            finance=sections["finance"],
            love=sections["love"],
            social=sections["social"],
            health=sections["health"],
            lucky_time=lucky_time,
            avoid=_avoid_text(hits, locale),
            affirmation=_affirmation_text(hits, locale),
            advice=_advice_text(hits, locale),
            moon_sign=moon_sign,
        )
    except Exception:
        logger.warning(
            (
                "astro forecast failed user_id=%s birth_date=%s birth_time=%s "
                "city=%r timezone=%s for_date=%s period=%s locale=%s sign=%s"
            ),
            user_id,
            birth_date,
            birth_time,
            city,
            timezone_name,
            for_date,
            period,
            locale,
            sign,
            exc_info=True,
        )
        return None


def build_astro_horoscope_context(
    *,
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    for_date: date,
    locale: str,
    user_id: int | None = None,
) -> AstroHoroscopeContext | None:
    forecast = build_astro_forecast(
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        timezone_name=timezone_name,
        for_date=for_date,
        locale=locale,
        period="day",
        user_id=user_id,
    )
    if forecast is None:
        return None

    adjustments: dict[str, int] = {}
    for domain, section in (
        ("energy", forecast.energy),
        ("work", forecast.work),
        ("finance", forecast.finance),
        ("love", forecast.love),
        ("social", forecast.social),
        ("health", forecast.health),
    ):
        adjustments[domain] = section.score - 5

    return AstroHoroscopeContext(
        summary_lines=forecast.summary_lines,
        score_adjustments=adjustments,
        moon_sign=forecast.moon_sign,
    )


NATAL_CHART_BODIES = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")


@dataclass
class NatalAspectHit:
    planet_a: str
    planet_b: str
    aspect: str
    orb: float


@dataclass
class NatalChartData:
    longitudes: dict[str, float]
    ascendant: float | None
    aspects: list[NatalAspectHit]
    has_birth_time: bool
    moon_included: bool
    asc_included: bool
    coordinates_available: bool
    resolved_timezone: str
    sun_sign: str


def _collect_natal_aspects(
    longitudes: dict[str, float],
    ascendant: float | None,
) -> list[NatalAspectHit]:
    points: dict[str, float] = dict(longitudes)
    if ascendant is not None:
        points["ASC"] = ascendant
    keys = list(points.keys())
    hits: list[NatalAspectHit] = []
    for index, first_key in enumerate(keys):
        for second_key in keys[index + 1 :]:
            aspect_info = _find_aspect(points[first_key], points[second_key])
            if aspect_info is None:
                continue
            aspect_name, orb_delta = aspect_info
            hits.append(NatalAspectHit(first_key, second_key, aspect_name, orb_delta))
    hits.sort(key=lambda item: item.orb)
    return hits


def build_natal_chart_data(
    *,
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> NatalChartData | None:
    try:
        resolved_lat, resolved_lon, resolved_tz = resolve_birth_location(
            city,
            normalize_timezone(birth_timezone or timezone_name),
            lat=lat,
            lon=lon,
            birth_timezone=birth_timezone,
        )
        natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
        has_birth_time = birth_time is not None
        keys: tuple[str, ...]
        if has_birth_time:
            keys = NATAL_CHART_BODIES
        else:
            keys = tuple(key for key in NATAL_CHART_BODIES if key != "MOON")
        longitudes = _collect_longitudes(natal_jd, keys)

        ascendant: float | None = None
        asc_included = False
        coordinates_available = resolved_lat is not None and resolved_lon is not None
        if has_birth_time and coordinates_available:
            _cusps, ascmc = swe.houses(natal_jd, resolved_lat, resolved_lon, b"P")
            ascendant = float(ascmc[0])
            asc_included = True

        aspects = _collect_natal_aspects(longitudes, ascendant)
        sun_sign = _longitude_to_sign(longitudes["SUN"])
        return NatalChartData(
            longitudes=longitudes,
            ascendant=ascendant,
            aspects=aspects,
            has_birth_time=has_birth_time,
            moon_included="MOON" in longitudes,
            asc_included=asc_included,
            coordinates_available=coordinates_available,
            resolved_timezone=resolved_tz,
            sun_sign=sun_sign,
        )
    except Exception:
        logger.warning(
            "natal chart failed birth_date=%s birth_time=%s city=%r timezone=%s",
            birth_date,
            birth_time,
            city,
            timezone_name,
            exc_info=True,
        )
        return None


SYNASTRY_POINTS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")

MODE_PLANET_WEIGHT: dict[str, dict[str, float]] = {
    "love": {"SUN": 1.0, "MOON": 2.0, "MERCURY": 0.8, "VENUS": 2.5, "MARS": 1.5},
    "friendship": {"SUN": 1.5, "MOON": 1.2, "MERCURY": 2.0, "VENUS": 1.0, "MARS": 0.8},
    "work": {"SUN": 1.2, "MOON": 0.6, "MERCURY": 2.2, "VENUS": 0.8, "MARS": 1.5},
}

MODE_LABELS = {
    "ru": {"love": "любовь", "friendship": "дружба", "work": "работа"},
    "en": {"love": "love", "friendship": "friendship", "work": "work"},
}


@dataclass
class SynastryAnalysis:
    score: int
    details: str
    partner_sign: str


def _natal_chart(
    birth_date: date,
    birth_time: time | None,
    city: str | None,
    timezone_name: str,
    *,
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> tuple[dict[str, float], str]:
    tz = normalize_timezone(birth_timezone or timezone_name)
    _lat, _lon, resolved_tz = resolve_birth_location(
        city,
        tz,
        lat=lat,
        lon=lon,
        birth_timezone=birth_timezone,
    )
    natal_jd = _natal_julian_day(birth_date, birth_time, resolved_tz)
    keys = SYNASTRY_POINTS if birth_time is not None else tuple(k for k in SYNASTRY_POINTS if k != "MOON")
    longitudes = _collect_longitudes(natal_jd, keys)
    sun_sign = _longitude_to_sign(longitudes["SUN"])
    return longitudes, sun_sign


def _collect_synastry_hits(
    user_chart: dict[str, float],
    partner_chart: dict[str, float],
) -> list[tuple[float, float, str, str, str]]:
    hits: list[tuple[float, float, str, str, str]] = []
    for user_planet, user_lon in user_chart.items():
        for partner_planet, partner_lon in partner_chart.items():
            aspect_info = _find_aspect(user_lon, partner_lon)
            if aspect_info is None:
                continue
            aspect_name, orb_delta = aspect_info
            hits.append((orb_delta, orb_delta, user_planet, partner_planet, aspect_name))
    hits.sort(key=lambda item: item[0])
    return hits


def _synastry_pair_weight(planet_a: str, planet_b: str, mode: str) -> float:
    weights = MODE_PLANET_WEIGHT.get(mode, MODE_PLANET_WEIGHT["love"])
    return (weights.get(planet_a, 1.0) + weights.get(planet_b, 1.0)) / 2


def _synastry_aspect_delta(aspect: str, planet_a: str, planet_b: str) -> int:
    if aspect in {"trine", "sextile"}:
        return 4 if aspect == "trine" else 3
    if aspect == "conjunction":
        benefics = {"VENUS", "JUPITER", "SUN", "MOON"}
        if planet_a in benefics or planet_b in benefics:
            return 3
        if planet_a in {"SATURN", "MARS"} and planet_b in {"SATURN", "MARS"}:
            return -3
        return 1
    if aspect == "opposition":
        return -2
    return -4


def _synastry_score(hits: list[tuple[float, float, str, str, str]], mode: str) -> int:
    if not hits:
        return 55
    total = 50.0
    for _orb, _orb2, planet_a, planet_b, aspect in hits:
        delta = _synastry_aspect_delta(aspect, planet_a, planet_b)
        weight = _synastry_pair_weight(planet_a, planet_b, mode)
        total += delta * weight
    return max(35, min(98, round(total)))


def _synastry_tone(locale: str, aspect: str, mode: str) -> str:
    lang = _lang(locale)
    tones = {
        "ru": {
            "love": {
                "trine": "сильное притяжение и эмоциональная поддержка",
                "sextile": "лёгкий контакт и взаимный интерес",
                "conjunction": "мощное слияние энергий — тема отношений усиливается",
                "square": "страсть и напряжение — важен диалог",
                "opposition": "магнетизм через контраст — нужен баланс",
            },
            "friendship": {
                "trine": "лёгкое взаимопонимание и общий язык",
                "sextile": "комфортное общение и совместные идеи",
                "conjunction": "сильная связь интересов и тем",
                "square": "разные темпы — учитесь договариваться",
                "opposition": "дополняете друг друга через различия",
            },
            "work": {
                "trine": "продуктивное взаимодействие и синхронность в задачах",
                "sextile": "удачное сотрудничество и обмен идеями",
                "conjunction": "фокус на общей цели усиливается",
                "square": "разные подходы — нужны чёткие роли",
                "opposition": "конструктивное напряжение требует структуры",
            },
        },
        "en": {
            "love": {
                "trine": "strong attraction and emotional support",
                "sextile": "easy contact and mutual interest",
                "conjunction": "powerful merging of energies in the relationship theme",
                "square": "passion and tension — dialogue matters",
                "opposition": "magnetism through contrast — balance is needed",
            },
            "friendship": {
                "trine": "easy understanding and shared language",
                "sextile": "comfortable communication and shared ideas",
                "conjunction": "strong link of interests and themes",
                "square": "different rhythms — negotiate expectations",
                "opposition": "you complement each other through differences",
            },
            "work": {
                "trine": "productive interaction and task synchrony",
                "sextile": "successful cooperation and idea exchange",
                "conjunction": "focus on a shared goal intensifies",
                "square": "different approaches — define clear roles",
                "opposition": "constructive tension needs structure",
            },
        },
    }
    mode_key = mode if mode in tones[lang] else "love"
    return tones[lang][mode_key][aspect]


def _synastry_aspect_line(
    locale: str,
    user_planet: str,
    partner_planet: str,
    aspect: str,
    mode: str,
) -> str:
    lang = _lang(locale)
    aspect_name = ASPECT_LABELS[lang][aspect]
    user_label = _planet_label(locale, user_planet)
    partner_label = _planet_label(locale, partner_planet)
    tone = _synastry_tone(locale, aspect, mode)
    if lang == "ru":
        return (
            f"• Ваше {user_label} — {aspect_name} к {partner_label} партнёра: {tone}."
        )
    return f"• Your {user_label} {aspect_name} partner's {partner_label}: {tone}."


def build_synastry_analysis(
    *,
    user_birth_date: date,
    user_birth_time: time | None,
    user_city: str | None,
    user_timezone: str,
    partner_birth_date: date,
    partner_birth_time: time | None = None,
    partner_city: str | None = None,
    partner_timezone: str | None = None,
    relation_mode: str,
    locale: str,
    user_id: int | None = None,
    user_lat: float | None = None,
    user_lon: float | None = None,
    user_birth_timezone: str | None = None,
    partner_lat: float | None = None,
    partner_lon: float | None = None,
    partner_birth_timezone: str | None = None,
) -> SynastryAnalysis | None:
    try:
        mode = relation_mode if relation_mode in MODE_PLANET_WEIGHT else "love"
        lang = _lang(locale)
        partner_tz = partner_birth_timezone or partner_timezone or user_birth_timezone or user_timezone

        user_chart, _user_sign = _natal_chart(
            user_birth_date,
            user_birth_time,
            user_city,
            user_birth_timezone or user_timezone,
            lat=user_lat,
            lon=user_lon,
            birth_timezone=user_birth_timezone,
        )
        partner_chart, partner_sign = _natal_chart(
            partner_birth_date,
            partner_birth_time,
            partner_city,
            partner_tz,
            lat=partner_lat,
            lon=partner_lon,
            birth_timezone=partner_birth_timezone,
        )
        hits = _collect_synastry_hits(user_chart, partner_chart)
        score = _synastry_score(hits, mode)

        lines = [
            f"💞 {'Синастрия (Swiss Ephemeris)' if lang == 'ru' else 'Synastry (Swiss Ephemeris)'} · "
            f"{MODE_LABELS[lang][mode]}",
        ]
        if user_birth_time is None:
            lines.append(
                "• Ваше время рождения не указано — ваша Луна не учитывается."
                if lang == "ru"
                else "• Your birth time is missing — your Moon is not included."
            )
        if partner_birth_time is None:
            lines.append(
                "• У партнёра нет времени рождения — Луна партнёра не учитывается."
                if lang == "ru"
                else "• Partner birth time is missing — partner Moon is not included."
            )
        if not hits:
            lines.append(
                "• Ярких межкартовых аспектов не найдено — связь более нейтральная."
                if lang == "ru"
                else "• No major cross-chart aspects found — the connection is more neutral."
            )
        else:
            ranked = sorted(
                hits,
                key=lambda item: abs(_synastry_aspect_delta(item[4], item[2], item[3]))
                * _synastry_pair_weight(item[2], item[3], mode),
                reverse=True,
            )
            for _orb, _orb2, user_planet, partner_planet, aspect in ranked[:4]:
                lines.append(
                    _synastry_aspect_line(locale, user_planet, partner_planet, aspect, mode)
                )

        return SynastryAnalysis(
            score=score,
            details="\n".join(lines),
            partner_sign=partner_sign,
        )
    except Exception:
        logger.warning(
            (
                "synastry analysis failed user_id=%s user_birth=%s partner_birth=%s "
                "mode=%s locale=%s"
            ),
            user_id,
            user_birth_date,
            partner_birth_date,
            relation_mode,
            locale,
            exc_info=True,
        )
        return None
