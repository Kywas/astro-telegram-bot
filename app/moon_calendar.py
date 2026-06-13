from __future__ import annotations

from datetime import date, timedelta

from app.astro_engine import build_moon_day_data, sign_label
from app.astro_glossary import format_moon_in_sign_short

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

MOON_FOCUS_KEYS = ("practices", "health", "creativity")

FOCUS_SECTION = {
    "ru": {
        "practices": "🧘 Планирование практик",
        "health": "💚 Забота о здоровье",
        "creativity": "✨ Творчество и саморазвитие",
    },
    "en": {
        "practices": "🧘 Practice planning",
        "health": "💚 Health care",
        "creativity": "✨ Creativity and growth",
    },
}

MODE_PHASE_GUIDANCE = {
    "ru": {
        "practices": {
            "new_moon": {
                "do": "короткая медитация на намерение, лёгкий ритуал начала",
                "avoid": "длинных сложных ритуалов без подготовки",
            },
            "waxing_crescent": {
                "do": "ежедневная практика 10–15 минут, закрепление привычки",
                "avoid": "откладывания «до лучших условий»",
            },
            "first_quarter": {
                "do": "активная практика, мантры, дисциплина",
                "avoid": "формального чтения без внимания",
            },
            "waxing_gibbous": {
                "do": "углубление практики, работа с качеством",
                "avoid": "перегруза новыми техниками",
            },
            "full_moon": {
                "do": "медитация благодарности, завершение цикла практики",
                "avoid": "экстремальных практик и ночных ритуалов",
            },
            "waning_gibbous": {
                "do": "делиться опытом, мягкая практика",
                "avoid": "давления на результат",
            },
            "last_quarter": {
                "do": "упрощение практики, отпускание лишнего",
                "avoid": "наращивания объёма без смысла",
            },
            "waning_crescent": {
                "do": "тихая медитация, отдых, подготовка к новому циклу",
                "avoid": "старта новых длинных курсов",
            },
        },
        "health": {
            "new_moon": {
                "do": "лёгкая еда, намерение по режиму и сну",
                "avoid": "жёстких диет и резкого детокса",
            },
            "waxing_crescent": {
                "do": "постепенное укрепление режима, достаточно воды",
                "avoid": "резких ограничений и скачков нагрузки",
            },
            "first_quarter": {
                "do": "умеренная активность, белок, овощи, режим сна",
                "avoid": "пропуска сна ради тренировок",
            },
            "waxing_gibbous": {
                "do": "корректировка питания и восстановления",
                "avoid": "перегруза стимуляторами и сахаром",
            },
            "full_moon": {
                "do": "умеренность, простая еда, отдых",
                "avoid": "переедания, алкоголя и недосыпа",
            },
            "waning_gibbous": {
                "do": "лёгкий разгрузочный день, прогулки",
                "avoid": "жёсткого голодания и экстремальных диет",
            },
            "last_quarter": {
                "do": "упрощение рациона, мягкое очищение",
                "avoid": "новых жёстких диет и стрессовых нагрузок",
            },
            "waning_crescent": {
                "do": "отдых, сон, простая еда",
                "avoid": "детокс-экстремов и перегруза организма",
            },
        },
        "creativity": {
            "new_moon": {
                "do": "записать 3 идеи, черновик намерения",
                "avoid": "запуска большого проекта «с нуля» без плана",
            },
            "waxing_crescent": {
                "do": "первые шаги, наброски, пробные форматы",
                "avoid": "самокритики и страха «неидеального» старта",
            },
            "first_quarter": {
                "do": "активная работа, правки, один главный фокус",
                "avoid": "распыления на много задач сразу",
            },
            "waxing_gibbous": {
                "do": "доработка, финальные штрихи, тестирование",
                "avoid": "бесконечного переделывания",
            },
            "full_moon": {
                "do": "показать работу, подвести итог, отметить результат",
                "avoid": "резких публичных решений на эмоциях",
            },
            "waning_gibbous": {
                "do": "делиться feedback, благодарить, собирать отклики",
                "avoid": "давления на аудиторию и сравнения",
            },
            "last_quarter": {
                "do": "редактирование, архив лишнего, пересмотр планов",
                "avoid": "удаления всего подряд из импульсивности",
            },
            "waning_crescent": {
                "do": "дневник инсайтов, мягкий brainstorming",
                "avoid": "старта крупных проектов без восстановления",
            },
        },
    },
    "en": {
        "practices": {
            "new_moon": {
                "do": "a short intention meditation and a light opening ritual",
                "avoid": "long complex rituals without preparation",
            },
            "waxing_crescent": {
                "do": "a daily 10–15 minute practice and habit anchoring",
                "avoid": "postponing until conditions are perfect",
            },
            "first_quarter": {
                "do": "active practice, mantras, and steady discipline",
                "avoid": "going through the motions without attention",
            },
            "waxing_gibbous": {
                "do": "deepening practice and refining quality",
                "avoid": "overloading with new techniques",
            },
            "full_moon": {
                "do": "gratitude meditation and closing a practice cycle",
                "avoid": "extreme practices and late-night rituals",
            },
            "waning_gibbous": {
                "do": "sharing experience and gentle practice",
                "avoid": "pressure for measurable results",
            },
            "last_quarter": {
                "do": "simplifying practice and releasing excess",
                "avoid": "adding volume without purpose",
            },
            "waning_crescent": {
                "do": "quiet meditation, rest, and preparing a new cycle",
                "avoid": "starting long new courses",
            },
        },
        "health": {
            "new_moon": {
                "do": "light meals and an intention for sleep and routine",
                "avoid": "strict diets and harsh detox",
            },
            "waxing_crescent": {
                "do": "gradually strengthening routine and hydration",
                "avoid": "sharp restrictions and sudden load spikes",
            },
            "first_quarter": {
                "do": "moderate activity, protein, vegetables, and sleep rhythm",
                "avoid": "skipping sleep for workouts",
            },
            "waxing_gibbous": {
                "do": "adjusting nutrition and recovery",
                "avoid": "stimulant and sugar overload",
            },
            "full_moon": {
                "do": "moderation, simple food, and rest",
                "avoid": "overeating, alcohol, and sleep debt",
            },
            "waning_gibbous": {
                "do": "a light unloading day and walks",
                "avoid": "hard fasting and extreme diets",
            },
            "last_quarter": {
                "do": "simplifying meals and gentle cleansing",
                "avoid": "new strict diets and stressful loads",
            },
            "waning_crescent": {
                "do": "rest, sleep, and simple food",
                "avoid": "extreme detox and bodily overload",
            },
        },
        "creativity": {
            "new_moon": {
                "do": "write down 3 ideas and a draft intention",
                "avoid": "launching a big project from zero without a plan",
            },
            "waxing_crescent": {
                "do": "first steps, sketches, and trial formats",
                "avoid": "self-criticism and fear of an imperfect start",
            },
            "first_quarter": {
                "do": "active work, edits, and one main focus",
                "avoid": "spreading across too many tasks",
            },
            "waxing_gibbous": {
                "do": "refinement, final touches, and testing",
                "avoid": "endless reworking",
            },
            "full_moon": {
                "do": "show your work, review outcomes, celebrate progress",
                "avoid": "sharp public decisions driven by emotion",
            },
            "waning_gibbous": {
                "do": "share feedback, thank others, gather responses",
                "avoid": "pressure on audience and comparison",
            },
            "last_quarter": {
                "do": "editing, archiving excess, revising plans",
                "avoid": "deleting everything impulsively",
            },
            "waning_crescent": {
                "do": "insight journaling and gentle brainstorming",
                "avoid": "starting major projects before recovery",
            },
        },
    },
}


def normalize_moon_focus(focus: str | None) -> str:
    if focus in MOON_FOCUS_KEYS:
        return focus
    return "practices"


def _use_terms(style: str) -> bool:
    return style != "plain"


def _lunar_day_label(locale: str, lunar_day: int, *, style: str = "terms") -> str:
    if _locale(locale) == "ru":
        if _use_terms(style):
            return f"{lunar_day}-й лунный день"
        return f"{lunar_day}-й день цикла"
    if _use_terms(style):
        return f"lunar day {lunar_day}"
    return f"cycle day {lunar_day}"


def _moon_age_label(locale: str, age: float, *, style: str = "terms") -> str:
    if _locale(locale) == "ru":
        if _use_terms(style):
            return f"• Возраст Луны: {age:.1f} суток"
        return f"• Дней с новолуния: {age:.1f}"
    if _use_terms(style):
        return f"• Moon age: {age:.1f} days"
    return f"• Days since new moon: {age:.1f}"


def _next_phase_label(locale: str, phase_name: str, days_left: int, next_date: date, *, style: str = "terms") -> str:
    if _locale(locale) == "ru":
        if _use_terms(style):
            return (
                f"• Следующая ключевая фаза: {phase_name} "
                f"(примерно через {days_left} дн., {next_date.strftime('%d.%m.%Y')})"
            )
        return (
            f"• Ближайшая фаза: {phase_name} "
            f"(через ~{days_left} дн., {next_date.strftime('%d.%m.%Y')})"
        )
    if _use_terms(style):
        return (
            f"• Next major phase: {phase_name} "
            f"(in about {days_left} day(s), {next_date.isoformat()})"
        )
    return (
        f"• Next phase: {phase_name} "
        f"(in ~{days_left} day(s), {next_date.isoformat()})"
    )


def _locale(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _phase_name(locale: str, phase_key: str) -> str:
    return PHASE_NAMES[_locale(locale)][phase_key]


def _short_phase(locale: str, phase_key: str) -> str:
    return SHORT_PHASE[_locale(locale)][phase_key]


def _guidance(locale: str, phase_key: str, focus: str = "practices") -> tuple[str, str]:
    lang = _locale(locale)
    normalized = normalize_moon_focus(focus)
    mode = MODE_PHASE_GUIDANCE[lang].get(normalized, {})
    if phase_key in mode:
        guidance = mode[phase_key]
        return guidance["do"], guidance["avoid"]
    guidance = PHASE_GUIDANCE[lang][phase_key]
    return guidance["do"], guidance["avoid"]


def _planning_lines(
    locale: str,
    phase_key: str,
    *,
    focus: str = "practices",
    show_all_focuses: bool = False,
) -> list[str]:
    lang = _locale(locale)
    focuses = MOON_FOCUS_KEYS if show_all_focuses else (normalize_moon_focus(focus),)
    lines: list[str] = []
    for key in focuses:
        rec_do, rec_avoid = _guidance(locale, phase_key, key)
        if lang == "ru":
            lines.append(f"• {FOCUS_SECTION[lang][key]}")
            lines.append(f"  ✓ {rec_do}")
            lines.append(f"  ✗ {rec_avoid}")
        else:
            lines.append(f"• {FOCUS_SECTION[lang][key]}")
            lines.append(f"  ✓ {rec_do}")
            lines.append(f"  ✗ {rec_avoid}")
        if show_all_focuses and key != focuses[-1]:
            lines.append("")
    return lines


def _moon_snapshot(
    locale: str,
    for_date: date,
    *,
    focus: str = "practices",
) -> dict[str, str | int | float] | None:
    data = build_moon_day_data(for_date)
    if data is None:
        return None
    rec_do, rec_avoid = _guidance(locale, data.phase_key, focus)
    return {
        "date": for_date,
        "age": data.age_days,
        "phase_key": data.phase_key,
        "phase_name": _phase_name(locale, data.phase_key),
        "short_phase": _short_phase(locale, data.phase_key),
        "illumination": data.illumination,
        "lunar_day": data.lunar_day,
        "moon_sign": sign_label(locale, data.moon_sign),
        "moon_sign_key": data.moon_sign,
        "next_phase_key": data.next_phase_key,
        "next_phase_days": data.next_phase_days,
        "do": rec_do,
        "avoid": rec_avoid,
    }


def _fallback_text(locale: str) -> str:
    if _locale(locale) == "ru":
        return "Не удалось рассчитать лунные данные. Попробуй позже."
    return "Could not compute lunar data. Please try again later."


def generate_moon_calendar_text(
    locale: str,
    for_date: date | None = None,
    *,
    focus: str = "practices",
    show_all_focuses: bool = False,
    style: str = "terms",
) -> str:
    current_locale = _locale(locale)
    if for_date is None:
        for_date = date.today()

    snap = _moon_snapshot(locale, for_date, focus=focus)
    if snap is None:
        return _fallback_text(locale)

    age = float(snap["age"])
    phase_name = str(snap["phase_name"])
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    moon_line = format_moon_in_sign_short(locale, str(snap["moon_sign_key"]))
    next_phase_name = _phase_name(locale, str(snap["next_phase_key"]))
    days_left = int(snap["next_phase_days"])
    next_date = for_date + timedelta(days=days_left)
    planning = _planning_lines(
        locale,
        str(snap["phase_key"]),
        focus=focus,
        show_all_focuses=show_all_focuses,
    )
    lunar_day_line = _lunar_day_label(locale, lunar_day, style=style)
    age_line = _moon_age_label(locale, age, style=style)
    next_phase_line = _next_phase_label(
        locale,
        next_phase_name,
        days_left,
        next_date,
        style=style,
    )
    if current_locale == "ru":
        phase_label = "• Фаза Луны" if _use_terms(style) else "• Фаза"
        illum_label = "• Освещённость диска" if _use_terms(style) else "• Освещённость"
        header = (
            f"🌙 Лунный календарь на {for_date.strftime('%d.%m.%Y')}\n\n"
            f"{phase_label}: {phase_name}\n"
            f"• {moon_line}\n"
            f"{illum_label}: {illumination}%\n"
            f"• {lunar_day_line}\n"
            f"{age_line}\n"
            f"{next_phase_line}"
        )
        return header + "\n\n" + "\n".join(planning)

    phase_label = "• Moon phase" if _use_terms(style) else "• Phase"
    illum_label = "• Illumination" if _use_terms(style) else "• Lit"
    header = (
        f"🌙 Moon calendar for {for_date.isoformat()}\n\n"
        f"{phase_label}: {phase_name}\n"
        f"• {moon_line}\n"
        f"{illum_label}: {illumination}%\n"
        f"• {lunar_day_line}\n"
        f"{age_line}\n"
        f"{next_phase_line}"
    )
    return header + "\n\n" + "\n".join(planning)


def generate_moon_table_text(
    locale: str,
    days: int,
    start_date: date | None = None,
    *,
    focus: str = "practices",
) -> str:
    current_locale = _locale(locale)
    if start_date is None:
        start_date = date.today()
    total_days = max(1, min(30, days))

    if current_locale == "ru":
        section = FOCUS_SECTION[current_locale][normalize_moon_focus(focus)]
        lines = [f"🌙 Лунный календарь на {total_days} дней", section, ""]
    else:
        section = FOCUS_SECTION[current_locale][normalize_moon_focus(focus)]
        lines = [f"🌙 Moon calendar for {total_days} days", section, ""]

    week_index = 1
    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        snap = _moon_snapshot(locale, current_date, focus=focus)
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


MAJOR_LUNAR_PHASES = ("new_moon", "first_quarter", "full_moon", "last_quarter")
LUNAR_PREVIEW_DAYS = 7
LUNAR_PREVIEW_FREE_DAYS = 1


def major_lunar_phase_on(for_date: date) -> str | None:
    data = build_moon_day_data(for_date)
    if data is None:
        return None
    if data.phase_key in MAJOR_LUNAR_PHASES:
        return data.phase_key
    return None


def _next_major_phase_line(locale: str, snap: dict[str, str | int | float]) -> str | None:
    current_locale = _locale(locale)
    next_key = str(snap["next_phase_key"])
    if next_key not in MAJOR_LUNAR_PHASES:
        return None
    days_left = int(snap["next_phase_days"])
    if days_left > 3:
        return None
    title = _phase_name(locale, next_key).lower()
    if current_locale == "ru":
        if days_left == 0:
            return f"Сегодня — {title}."
        if days_left == 1:
            return f"Завтра — {title}."
        return f"Через {days_left} дн. — {title}."
    if days_left == 0:
        return f"Today — {title}."
    if days_left == 1:
        return f"Tomorrow — {title}."
    return f"In {days_left} days — {title}."


def format_lunar_daily_reminder(
    locale: str,
    for_date: date,
    *,
    focus: str = "practices",
    style: str = "terms",
) -> str:
    current_locale = _locale(locale)
    snap = _moon_snapshot(locale, for_date, focus=focus)
    if snap is None:
        return _fallback_text(locale)

    phase_name = str(snap["phase_name"])
    moon_line = format_moon_in_sign_short(locale, str(snap["moon_sign_key"]))
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    next_line = _next_major_phase_line(locale, snap)
    section = FOCUS_SECTION[current_locale][normalize_moon_focus(focus)]
    day_label = _lunar_day_label(locale, lunar_day, style=style)

    if current_locale == "ru":
        lines = [
            f"🌙 Лунный фокус · {for_date.strftime('%d.%m')}",
            "",
            f"{moon_line} · {phase_name.lower()} · {illumination}% · {day_label}",
            "",
            section,
            f"✅ Уместно: {rec_do}",
            f"⚠️ Избегать: {rec_avoid}",
        ]
        if next_line:
            lines.extend(["", next_line])
        return "\n".join(lines)

    lines = [
        f"🌙 Lunar focus · {for_date.isoformat()}",
        "",
        f"{moon_line} · {phase_name.lower()} · {illumination}% · {day_label}",
        "",
        section,
        f"✅ Do: {rec_do}",
        f"⚠️ Avoid: {rec_avoid}",
    ]
    if next_line:
        lines.extend(["", next_line])
    return "\n".join(lines)


def lunar_event_title(phase_key: str, locale: str) -> str:
    return _phase_name(locale, phase_key)


def format_lunar_day_notification(
    phase_key: str,
    locale: str,
    for_date: date,
    *,
    focus: str = "practices",
    style: str = "terms",
) -> str:
    current_locale = _locale(locale)
    title = lunar_event_title(phase_key, current_locale)
    snap = _moon_snapshot(locale, for_date, focus=focus)
    if snap is None:
        return _fallback_text(locale)
    moon_line = format_moon_in_sign_short(locale, str(snap["moon_sign_key"]))
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    section = FOCUS_SECTION[current_locale][normalize_moon_focus(focus)]
    day_label = _lunar_day_label(locale, lunar_day, style=style)
    if current_locale == "ru":
        return (
            f"🌑 Сегодня {title.lower()} · {for_date.strftime('%d.%m.%Y')}\n\n"
            f"• {moon_line} · {illumination}% · {day_label}\n"
            f"• {section}\n"
            f"• Что делать: {rec_do}\n"
            f"• Чего избегать: {rec_avoid}"
        )
    return (
        f"🌑 Today is {title} · {for_date.isoformat()}\n\n"
        f"• {moon_line} · {illumination}% · {day_label}\n"
        f"• {section}\n"
        f"• Do: {rec_do}\n"
        f"• Avoid: {rec_avoid}"
    )


def format_lunar_preview_notification(
    phase_key: str,
    locale: str,
    event_date: date,
    *,
    days_left: int,
    early: bool = False,
    focus: str = "practices",
    style: str = "terms",
) -> str:
    current_locale = _locale(locale)
    title = lunar_event_title(phase_key, current_locale)
    snap = _moon_snapshot(locale, event_date, focus=focus)
    if snap is None:
        return _fallback_text(locale)
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    moon_line = format_moon_in_sign_short(locale, str(snap["moon_sign_key"]))
    section = FOCUS_SECTION[current_locale][normalize_moon_focus(focus)]

    if current_locale == "ru":
        when = (
            f"Через {days_left} дн."
            if days_left > 1
            else ("Завтра" if days_left == 1 else "Сегодня")
        )
        prefix = "Premium-напоминание" if early else "Напоминание"
        return (
            f"🌙 {when} — {title.lower()} ({event_date.strftime('%d.%m.%Y')})\n\n"
            f"• {moon_line}\n"
            f"• {section}\n"
            f"• {prefix}: {rec_do}\n"
            f"• Чего избегать ближе к фазе: {rec_avoid}"
        )
    when = (
        f"In {days_left} days"
        if days_left > 1
        else ("Tomorrow" if days_left == 1 else "Today")
    )
    prefix = "Premium reminder" if early else "Reminder"
    return (
        f"🌙 {when} — {title} ({event_date.isoformat()})\n\n"
        f"• {moon_line}\n"
        f"• {section}\n"
        f"• {prefix}: {rec_do}\n"
        f"• Avoid closer to the phase: {rec_avoid}"
    )
