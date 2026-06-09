from __future__ import annotations

from datetime import date, timedelta

from app.astro_engine import build_moon_day_data, sign_label

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

PHASE_GUIDANCE = {
    "ru": {
        "new_moon": {
            "do": "задумать намерения и начать новое",
            "avoid": "спешки и перегруза расписания",
        },
        "waxing_crescent": {
            "do": "делать первые шаги и закреплять план",
            "avoid": "сомнений и откладывания старта",
        },
        "first_quarter": {
            "do": "проявлять решительность и уточнять детали",
            "avoid": "конфликтов из-за нетерпения",
        },
        "waxing_gibbous": {
            "do": "доводить начатое и корректировать курс",
            "avoid": "перфекционизма и лишней критики",
        },
        "full_moon": {
            "do": "подводить итоги и завершать важное",
            "avoid": "эмоциональных крайностей и резких решений",
        },
        "waning_gibbous": {
            "do": "делиться опытом и благодарить за результат",
            "avoid": "давления на себя и других",
        },
        "last_quarter": {
            "do": "упрощать, отпускать лишнее и пересматривать планы",
            "avoid": "упрямства и попыток удержать всё как есть",
        },
        "waning_crescent": {
            "do": "отдыхать, восстанавливаться и готовиться к новому циклу",
            "avoid": "новых крупных запусков и перегруза",
        },
    },
    "en": {
        "new_moon": {
            "do": "set intentions and start something new",
            "avoid": "rush and overloaded schedules",
        },
        "waxing_crescent": {
            "do": "take first steps and anchor your plan",
            "avoid": "doubting and delaying the start",
        },
        "first_quarter": {
            "do": "act decisively and clarify details",
            "avoid": "conflicts driven by impatience",
        },
        "waxing_gibbous": {
            "do": "refine what you started and adjust course",
            "avoid": "perfectionism and harsh self-criticism",
        },
        "full_moon": {
            "do": "review outcomes and finish what matters",
            "avoid": "emotional extremes and sharp decisions",
        },
        "waning_gibbous": {
            "do": "share results and express gratitude",
            "avoid": "pressure on yourself and others",
        },
        "last_quarter": {
            "do": "simplify, release excess, and revise plans",
            "avoid": "stubbornly holding onto what no longer fits",
        },
        "waning_crescent": {
            "do": "rest, recover, and prepare for a new cycle",
            "avoid": "major launches and overload",
        },
    },
}


def _locale(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _phase_name(locale: str, phase_key: str) -> str:
    return PHASE_NAMES[_locale(locale)][phase_key]


def _short_phase(locale: str, phase_key: str) -> str:
    return SHORT_PHASE[_locale(locale)][phase_key]


def _guidance(locale: str, phase_key: str) -> tuple[str, str]:
    guidance = PHASE_GUIDANCE[_locale(locale)][phase_key]
    return guidance["do"], guidance["avoid"]


def _moon_snapshot(locale: str, for_date: date) -> dict[str, str | int | float] | None:
    data = build_moon_day_data(for_date)
    if data is None:
        return None
    rec_do, rec_avoid = _guidance(locale, data.phase_key)
    return {
        "date": for_date,
        "age": data.age_days,
        "phase_key": data.phase_key,
        "phase_name": _phase_name(locale, data.phase_key),
        "short_phase": _short_phase(locale, data.phase_key),
        "illumination": data.illumination,
        "lunar_day": data.lunar_day,
        "moon_sign": sign_label(locale, data.moon_sign),
        "next_phase_key": data.next_phase_key,
        "next_phase_days": data.next_phase_days,
        "do": rec_do,
        "avoid": rec_avoid,
    }


def _fallback_text(locale: str) -> str:
    if _locale(locale) == "ru":
        return "Не удалось рассчитать лунные данные. Попробуй позже."
    return "Could not compute lunar data. Please try again later."


def generate_moon_calendar_text(locale: str, for_date: date | None = None) -> str:
    current_locale = _locale(locale)
    if for_date is None:
        for_date = date.today()

    snap = _moon_snapshot(locale, for_date)
    if snap is None:
        return _fallback_text(locale)

    age = float(snap["age"])
    phase_name = str(snap["phase_name"])
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    moon_sign = str(snap["moon_sign"])
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    next_phase_name = _phase_name(locale, str(snap["next_phase_key"]))
    days_left = int(snap["next_phase_days"])
    next_date = for_date + timedelta(days=days_left)

    if current_locale == "ru":
        return (
            f"🌙 Лунный календарь на {for_date.strftime('%d.%m.%Y')}\n\n"
            f"• Фаза Луны: {phase_name}\n"
            f"• Луна в знаке: {moon_sign}\n"
            f"• Освещённость диска: {illumination}%\n"
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
        f"• Moon sign: {moon_sign}\n"
        f"• Illumination: {illumination}%\n"
        f"• Lunar day: {lunar_day}\n"
        f"• Moon age: {age:.1f} days\n"
        f"• Next major phase: {next_phase_name} "
        f"(in about {days_left} day(s), {next_date.isoformat()})\n"
        f"• Best focus: {rec_do}\n"
        f"• Better avoid: {rec_avoid}"
    )


def generate_moon_table_text(locale: str, days: int, start_date: date | None = None) -> str:
    current_locale = _locale(locale)
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
        snap = _moon_snapshot(locale, current_date)
        if snap is None:
            continue

        if offset % 7 == 0:
            if offset > 0:
                lines.append("")
            if current_locale == "ru":
                lines.append(f"━━ Неделя {week_index} ━━")
                lines.append("Дата | День | Знак | Фаза | %")
            else:
                lines.append(f"━━ Week {week_index} ━━")
                lines.append("Date | Day | Sign | Phase | %")
            week_index += 1

        date_str = current_date.strftime("%d.%m")
        lines.append(
            f"{date_str} | {int(snap['lunar_day']):>2} | {snap['moon_sign'][:8]:<8} | "
            f"{snap['short_phase']} | {int(snap['illumination']):>3}%"
        )
        if current_locale == "ru":
            lines.append(f"  ✔ {snap['do']}")
            lines.append(f"  ✖ {snap['avoid']}")
        else:
            lines.append(f"  ✔ {snap['do']}")
            lines.append(f"  ✖ {snap['avoid']}")

    if len(lines) <= 2:
        return _fallback_text(locale)
    return "\n".join(lines)


def generate_moon_compact_table_text(locale: str, days: int, start_date: date | None = None) -> str:
    current_locale = _locale(locale)
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
        snap = _moon_snapshot(locale, current_date)
        if snap is None:
            continue
        date_str = current_date.strftime("%d.%m")
        lines.append(
            f"{date_str} | {int(snap['lunar_day']):>2} | {snap['short_phase']} | {int(snap['illumination']):>3}%"
        )

    if len(lines) <= 3:
        return _fallback_text(locale)
    return "\n".join(lines)


MAJOR_LUNAR_PHASES = ("new_moon", "full_moon")
LUNAR_PREVIEW_DAYS = 7


def major_lunar_phase_on(for_date: date) -> str | None:
    data = build_moon_day_data(for_date)
    if data is None:
        return None
    if data.phase_key in MAJOR_LUNAR_PHASES:
        return data.phase_key
    return None


def lunar_event_title(phase_key: str, locale: str) -> str:
    return _phase_name(locale, phase_key)


def format_lunar_day_notification(phase_key: str, locale: str, for_date: date) -> str:
    current_locale = _locale(locale)
    title = lunar_event_title(phase_key, current_locale)
    snap = _moon_snapshot(locale, for_date)
    if snap is None:
        return _fallback_text(locale)
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    moon_sign = str(snap["moon_sign"])

    if current_locale == "ru":
        return (
            f"🌑 Сегодня {title.lower()} ({for_date.strftime('%d.%m.%Y')})\n\n"
            f"• Луна в знаке: {moon_sign}\n"
            f"• Что делать: {rec_do}\n"
            f"• Чего избегать: {rec_avoid}"
        )
    return (
        f"🌑 Today is {title} ({for_date.isoformat()})\n\n"
        f"• Moon sign: {moon_sign}\n"
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
    current_locale = _locale(locale)
    title = lunar_event_title(phase_key, current_locale)
    snap = _moon_snapshot(locale, event_date)
    if snap is None:
        return _fallback_text(locale)
    rec_do = str(snap["do"])
    moon_sign = str(snap["moon_sign"])

    if current_locale == "ru":
        return (
            f"🌙 Через {days_left} дн. — {title.lower()} "
            f"({event_date.strftime('%d.%m.%Y')})\n\n"
            f"• Луна будет в знаке: {moon_sign}\n"
            f"Premium-напоминание: начни готовиться — {rec_do}."
        )
    return (
        f"🌙 In {days_left} days — {title} ({event_date.isoformat()})\n\n"
        f"• Moon sign: {moon_sign}\n"
        f"Premium reminder: start preparing — {rec_do}."
    )
