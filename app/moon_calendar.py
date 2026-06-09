from datetime import date, datetime, time, timedelta, timezone
from math import cos, pi

SYNODIC_MONTH_DAYS = 29.53058867
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)

PHASE_NAMES = {
    "ru": {
        "new_moon": "Новолуние",
        "waxing_crescent": "Растущий серп",
        "first_quarter": "Первая четверть",
        "waxing_gibbous": "Растущая Луна",
        "full_moon": "Полнолуние",
        "waning_gibbous": "Убывающая Луна",
        "last_quarter": "Последняя четверть",
        "waning_crescent": "Убывающий серп",
    },
    "en": {
        "new_moon": "New Moon",
        "waxing_crescent": "Waxing Crescent",
        "first_quarter": "First Quarter",
        "waxing_gibbous": "Waxing Gibbous",
        "full_moon": "Full Moon",
        "waning_gibbous": "Waning Gibbous",
        "last_quarter": "Last Quarter",
        "waning_crescent": "Waning Crescent",
    },
}

SHORT_PHASE = {
    "ru": {
        "new_moon": "нов.",
        "waxing_crescent": "раст.серп",
        "first_quarter": "1/4",
        "waxing_gibbous": "раст.",
        "full_moon": "полн.",
        "waning_gibbous": "убыв.",
        "last_quarter": "3/4",
        "waning_crescent": "убыв.серп",
    },
    "en": {
        "new_moon": "new",
        "waxing_crescent": "wax.cres",
        "first_quarter": "1/4",
        "waxing_gibbous": "wax.gib",
        "full_moon": "full",
        "waning_gibbous": "wan.gib",
        "last_quarter": "3/4",
        "waning_crescent": "wan.cres",
    },
}

DO_RECOMMENDATIONS = {
    "ru": [
        "планировать и начинать",
        "доделывать и упорядочивать",
        "общаться и договариваться",
        "учиться и анализировать",
        "замедлиться и восстановиться",
    ],
    "en": [
        "plan and start",
        "finish and organize",
        "communicate and agree",
        "study and analyze",
        "slow down and recover",
    ],
}

AVOID_RECOMMENDATIONS = {
    "ru": [
        "спешки и резких решений",
        "хаоса и перегруза",
        "конфликтов и критики",
        "поверхностных выводов",
        "эмоциональных трат",
    ],
    "en": [
        "rush and sharp decisions",
        "chaos and overload",
        "conflicts and criticism",
        "superficial conclusions",
        "emotional spending",
    ],
}


def _moon_age_days(for_date: date) -> float:
    moment = datetime.combine(for_date, time(12, 0), tzinfo=timezone.utc)
    days_since_known = (moment - KNOWN_NEW_MOON).total_seconds() / 86400.0
    return days_since_known % SYNODIC_MONTH_DAYS


def _phase_key_by_age(age_days: float) -> str:
    phase = age_days / SYNODIC_MONTH_DAYS
    if phase < 0.0625 or phase >= 0.9375:
        return "new_moon"
    if phase < 0.1875:
        return "waxing_crescent"
    if phase < 0.3125:
        return "first_quarter"
    if phase < 0.4375:
        return "waxing_gibbous"
    if phase < 0.5625:
        return "full_moon"
    if phase < 0.6875:
        return "waning_gibbous"
    if phase < 0.8125:
        return "last_quarter"
    return "waning_crescent"


def _illumination_percent(age_days: float) -> int:
    phase = age_days / SYNODIC_MONTH_DAYS
    illum = (1 - cos(2 * pi * phase)) / 2
    return round(illum * 100)


def _next_major_phase(age_days: float, locale: str) -> tuple[str, int]:
    current_fraction = age_days / SYNODIC_MONTH_DAYS
    targets = [
        ("new_moon", 0.0),
        ("first_quarter", 0.25),
        ("full_moon", 0.5),
        ("last_quarter", 0.75),
    ]
    candidates: list[tuple[str, float]] = []
    for phase_key, target in targets:
        delta_fraction = (target - current_fraction) % 1.0
        delta_days = delta_fraction * SYNODIC_MONTH_DAYS
        if delta_days < 0.2:
            delta_days += SYNODIC_MONTH_DAYS
        candidates.append((phase_key, delta_days))

    phase_key, days_left = min(candidates, key=lambda item: item[1])
    phase_name = PHASE_NAMES[locale][phase_key]
    return phase_name, round(days_left)


def _recommendation_pair(locale: str, lunar_day: int) -> tuple[str, str]:
    idx = (lunar_day - 1) % len(DO_RECOMMENDATIONS[locale])
    return DO_RECOMMENDATIONS[locale][idx], AVOID_RECOMMENDATIONS[locale][idx]


def _moon_snapshot(locale: str, for_date: date) -> dict[str, str | int | float]:
    age = _moon_age_days(for_date)
    phase_key = _phase_key_by_age(age)
    phase_name = PHASE_NAMES[locale][phase_key]
    short_phase = SHORT_PHASE[locale][phase_key]
    illumination = _illumination_percent(age)
    lunar_day = int(age) + 1
    rec_do, rec_avoid = _recommendation_pair(locale, lunar_day)
    return {
        "date": for_date,
        "age": age,
        "phase_name": phase_name,
        "short_phase": short_phase,
        "illumination": illumination,
        "lunar_day": lunar_day,
        "do": rec_do,
        "avoid": rec_avoid,
    }


def generate_moon_calendar_text(locale: str, for_date: date | None = None) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    if for_date is None:
        for_date = date.today()

    snap = _moon_snapshot(current_locale, for_date)
    age = float(snap["age"])
    phase_name = str(snap["phase_name"])
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    next_phase_name, days_left = _next_major_phase(age, current_locale)
    next_date = for_date + timedelta(days=days_left)

    if current_locale == "ru":
        return (
            f"🌙 Лунный календарь на {for_date.strftime('%d.%m.%Y')}\n\n"
            f"• Фаза Луны: {phase_name}\n"
            f"• Освещенность диска: {illumination}%\n"
            f"• Лунный день: {lunar_day}\n"
            f"• Возраст Луны: {age:.1f} суток\n"
            f"• Следующая ключевая фаза: {next_phase_name} "
            f"(примерно через {days_left} дн., {next_date.strftime('%d.%m.%Y')})\n"
            f"• Что делать: {rec_do}\n"
            f"• Чего избегать: {rec_avoid}"
        )

    return (
        f"🌙 Moon calendar for {for_date.isoformat()}\n\n"
        f"• Moon phase: {phase_name}\n"
        f"• Illumination: {illumination}%\n"
        f"• Lunar day: {lunar_day}\n"
        f"• Moon age: {age:.1f} days\n"
        f"• Next major phase: {next_phase_name} "
        f"(in about {days_left} day(s), {next_date.isoformat()})\n"
        f"• Best focus: {rec_do}\n"
        f"• Better avoid: {rec_avoid}"
    )


def generate_moon_table_text(locale: str, days: int, start_date: date | None = None) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    if start_date is None:
        start_date = date.today()
    total_days = max(1, min(30, days))

    if current_locale == "ru":
        lines = [f"🌙 Лунный календарь на {total_days} дней", ""]
    else:
        lines = [f"🌙 Moon calendar for {total_days} days", ""]

    week_index = 1
    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        snap = _moon_snapshot(current_locale, current_date)

        if offset % 7 == 0:
            if offset > 0:
                lines.append("")
            if current_locale == "ru":
                lines.append(f"━━ Неделя {week_index} ━━")
                lines.append("Дата | День | Фаза | %")
            else:
                lines.append(f"━━ Week {week_index} ━━")
                lines.append("Date | Day | Phase | %")
            week_index += 1

        date_str = current_date.strftime("%d.%m")
        lines.append(
            f"{date_str} | {int(snap['lunar_day']):>2} | {snap['short_phase']} | {int(snap['illumination']):>3}%"
        )
        if current_locale == "ru":
            lines.append(f"  ✔ {snap['do']}")
            lines.append(f"  ✖ {snap['avoid']}")
        else:
            lines.append(f"  ✔ {snap['do']}")
            lines.append(f"  ✖ {snap['avoid']}")

    return "\n".join(lines)


def generate_moon_compact_table_text(locale: str, days: int, start_date: date | None = None) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    if start_date is None:
        start_date = date.today()
    total_days = max(1, min(30, days))

    if current_locale == "ru":
        lines = [
            f"🌙 Компактный лунный календарь на {total_days} дней",
            "",
            "Дата | День | Фаза | %",
        ]
    else:
        lines = [
            f"🌙 Compact moon calendar for {total_days} days",
            "",
            "Date | Day | Phase | %",
        ]

    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        snap = _moon_snapshot(current_locale, current_date)
        date_str = current_date.strftime("%d.%m")
        lines.append(
            f"{date_str} | {int(snap['lunar_day']):>2} | {snap['short_phase']} | {int(snap['illumination']):>3}%"
        )

    return "\n".join(lines)


MAJOR_LUNAR_PHASES = ("new_moon", "full_moon")
LUNAR_PREVIEW_DAYS = 7


def major_lunar_phase_on(for_date: date) -> str | None:
    age = _moon_age_days(for_date)
    phase_key = _phase_key_by_age(age)
    if phase_key in MAJOR_LUNAR_PHASES:
        return phase_key
    return None


def lunar_event_title(phase_key: str, locale: str) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    return PHASE_NAMES[current_locale][phase_key]


def format_lunar_day_notification(phase_key: str, locale: str, for_date: date) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    title = lunar_event_title(phase_key, current_locale)
    snap = _moon_snapshot(current_locale, for_date)
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])

    if current_locale == "ru":
        return (
            f"🌑 Сегодня {title.lower()} ({for_date.strftime('%d.%m.%Y')})\n\n"
            f"• Что делать: {rec_do}\n"
            f"• Чего избегать: {rec_avoid}"
        )
    return (
        f"🌑 Today is {title} ({for_date.isoformat()})\n\n"
        f"• Do: {rec_do}\n"
        f"• Avoid: {rec_avoid}"
    )


def format_lunar_preview_notification(
    phase_key: str,
    locale: str,
    event_date: date,
    *,
    days_left: int,
) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    title = lunar_event_title(phase_key, current_locale)
    snap = _moon_snapshot(current_locale, event_date)
    rec_do = str(snap["do"])

    if current_locale == "ru":
        return (
            f"🌙 Через {days_left} дн. — {title.lower()} "
            f"({event_date.strftime('%d.%m.%Y')})\n\n"
            f"Premium-напоминание: начни готовиться — {rec_do}."
        )
    return (
        f"🌙 In {days_left} days — {title} ({event_date.isoformat()})\n\n"
        f"Premium reminder: start preparing — {rec_do}."
    )
