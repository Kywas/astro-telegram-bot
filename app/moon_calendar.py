from __future__ import annotations

from datetime import date, datetime, timedelta

from app.astro_engine import build_moon_day_data, jd_to_local_datetime, major_phase_on_local_date, sign_label
from app.astro_glossary import format_moon_in_sign_short, moon_in_sign_hint
from app.moon_calendar_extras import (
    FOCUS_PERSONAL_HEADER,
    FOCUS_PERSONAL_NOTES,
    PHASE_ACCENT,
    PLAIN_FOCUS_PERSONAL_HEADER,
    PLAIN_FOCUS_PERSONAL_NOTES,
    PLAIN_PHASE_ACCENT,
)
from app.moon_calendar_plain_data import (
    PLAIN_FOCUS_SECTION,
    PLAIN_MODE_PHASE_GUIDANCE,
    PLAIN_PHASE_GUIDANCE,
    PLAIN_PHASE_NAMES,
    PLAIN_SHORT_PHASE,
    TERMS_FOCUS_SECTION,
)

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


def resolve_moon_style(profile, *, default: str = "terms") -> str:
    if profile is None:
        return default
    style = getattr(profile, "moon_style", None) or default
    return "plain" if style == "plain" else "terms"


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


def _next_lunar_day_label(
    locale: str,
    for_date: date,
    next_moment: datetime,
    *,
    style: str = "terms",
) -> str:
    if next_moment.date() == for_date:
        when = (
            f"сегодня в {next_moment.strftime('%H:%M')}"
            if _locale(locale) == "ru"
            else f"today at {next_moment.strftime('%H:%M')}"
        )
    elif next_moment.date() == for_date + timedelta(days=1):
        when = (
            f"завтра в {next_moment.strftime('%H:%M')}"
            if _locale(locale) == "ru"
            else f"tomorrow at {next_moment.strftime('%H:%M')}"
        )
    else:
        when = next_moment.strftime("%d.%m %H:%M" if _locale(locale) == "ru" else "%Y-%m-%d %H:%M")
    if _locale(locale) == "ru":
        if _use_terms(style):
            return f"• Следующий лунный день: {when}"
        return f"• Смена дня цикла: {when}"
    if _use_terms(style):
        return f"• Next lunar day: {when}"
    return f"• Next cycle day: {when}"


def _next_phase_label(
    locale: str,
    phase_name: str,
    days_left: int,
    next_date: date,
    *,
    style: str = "terms",
    next_phase_moment: datetime | None = None,
) -> str:
    time_suffix = ""
    if next_phase_moment is not None:
        time_suffix = f", {next_phase_moment.strftime('%H:%M')}"
    if _locale(locale) == "ru":
        if _use_terms(style):
            return (
                f"• Следующая ключевая фаза: {phase_name} "
                f"(через {days_left} дн., {next_date.strftime('%d.%m.%Y')}{time_suffix})"
            )
        return (
            f"• Ближайшая фаза: {phase_name} "
            f"(через ~{days_left} дн., {next_date.strftime('%d.%m.%Y')}{time_suffix})"
        )
    if _use_terms(style):
        return (
            f"• Next major phase: {phase_name} "
            f"(in {days_left} day(s), {next_date.isoformat()}{time_suffix})"
        )
    return (
        f"• Next phase: {phase_name} "
        f"(in ~{days_left} day(s), {next_date.isoformat()}{time_suffix})"
    )


def _locale(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _phase_name(locale: str, phase_key: str, *, style: str = "terms") -> str:
    lang = _locale(locale)
    if _use_terms(style):
        return PHASE_NAMES[lang][phase_key]
    return PLAIN_PHASE_NAMES[lang][phase_key]


def _short_phase(locale: str, phase_key: str, *, style: str = "terms") -> str:
    lang = _locale(locale)
    if _use_terms(style):
        return SHORT_PHASE[lang][phase_key]
    return PLAIN_SHORT_PHASE[lang][phase_key]


def _focus_section(locale: str, focus: str, *, style: str = "terms") -> str:
    lang = _locale(locale)
    normalized = normalize_moon_focus(focus)
    if _use_terms(style):
        return TERMS_FOCUS_SECTION[lang][normalized]
    return PLAIN_FOCUS_SECTION[lang][normalized]


def _format_moon_sign_line(locale: str, sign_key: str, *, style: str = "terms") -> str:
    if _use_terms(style):
        return format_moon_in_sign_short(locale, sign_key)
    sign = sign_label(locale, sign_key)
    hint = moon_in_sign_hint(locale, sign_key)
    if _locale(locale) == "ru":
        if hint:
            return f"Настроение дня — {sign}: {hint}"
        return f"Настроение дня — {sign}"
    if hint:
        return f"Daily mood — {sign}: {hint}"
    return f"Daily mood — {sign}"


def _guidance(
    locale: str,
    phase_key: str,
    focus: str = "practices",
    *,
    style: str = "terms",
) -> tuple[str, str]:
    lang = _locale(locale)
    normalized = normalize_moon_focus(focus)
    if _use_terms(style):
        mode = MODE_PHASE_GUIDANCE[lang].get(normalized, {})
        fallback = PHASE_GUIDANCE[lang]
    else:
        mode = PLAIN_MODE_PHASE_GUIDANCE[lang].get(normalized, {})
        fallback = PLAIN_PHASE_GUIDANCE[lang]
    if phase_key in mode:
        guidance = mode[phase_key]
        return guidance["do"], guidance["avoid"]
    guidance = fallback[phase_key]
    return guidance["do"], guidance["avoid"]


def _phase_accent_lines(
    locale: str,
    phase_key: str,
    *,
    focus: str = "practices",
    style: str = "terms",
) -> list[str]:
    lang = _locale(locale)
    if _use_terms(style):
        accent = PHASE_ACCENT[lang].get(phase_key)
        if accent is None:
            return []
        lines = [f"  {accent['color']} {accent['label']}"]
        if normalize_moon_focus(focus) != "creativity":
            lines.append(f"  💬 «{accent['affirmation']}»")
        return lines
    accent = PLAIN_PHASE_ACCENT[lang].get(phase_key)
    if accent is None:
        return []
    lines = [f"  ✨ {accent['label']}"]
    if normalize_moon_focus(focus) != "creativity":
        lines.append(f"  💬 «{accent['affirmation']}»")
    return lines


def _focus_personal_header(locale: str, focus: str, *, style: str = "terms") -> str:
    lang = _locale(locale)
    normalized = normalize_moon_focus(focus)
    if _use_terms(style):
        return FOCUS_PERSONAL_HEADER[lang][normalized]
    return PLAIN_FOCUS_PERSONAL_HEADER[lang][normalized]


def _focus_personal_lines(
    locale: str,
    phase_key: str,
    focus: str,
    *,
    style: str = "terms",
) -> list[str]:
    lang = _locale(locale)
    normalized = normalize_moon_focus(focus)
    if _use_terms(style):
        bucket = FOCUS_PERSONAL_NOTES[lang].get(normalized, {})
    else:
        bucket = PLAIN_FOCUS_PERSONAL_NOTES[lang].get(normalized, {})
    lines = bucket.get(phase_key, [])
    return list(lines)


def _append_focus_personal_lines(
    lines: list[str],
    locale: str,
    phase_key: str,
    focus: str,
    *,
    style: str = "terms",
) -> None:
    personal_lines = _focus_personal_lines(locale, phase_key, focus, style=style)
    if not personal_lines:
        return
    lines.append(f"  {_focus_personal_header(locale, focus, style=style)}")
    for note in personal_lines:
        lines.append(f"  {note}")


def _planning_lines(
    locale: str,
    phase_key: str,
    *,
    focus: str = "practices",
    show_all_focuses: bool = False,
    style: str = "terms",
) -> list[str]:
    focuses = MOON_FOCUS_KEYS if show_all_focuses else (normalize_moon_focus(focus),)
    lines: list[str] = []
    for key in focuses:
        rec_do, rec_avoid = _guidance(locale, phase_key, key, style=style)
        lines.append(f"• {_focus_section(locale, key, style=style)}")
        lines.append(f"  ✓ {rec_do}")
        lines.append(f"  ✗ {rec_avoid}")
        _append_focus_personal_lines(lines, locale, phase_key, key, style=style)
        if not show_all_focuses:
            lines.extend(_phase_accent_lines(locale, phase_key, focus=key, style=style))
        if show_all_focuses and key != focuses[-1]:
            lines.append("")
    return lines


def _moon_snapshot(
    locale: str,
    for_date: date,
    *,
    focus: str = "practices",
    style: str = "terms",
    timezone_name: str = "UTC",
) -> dict[str, str | int | float] | None:
    data = build_moon_day_data(for_date, timezone_name=timezone_name)
    if data is None:
        return None
    rec_do, rec_avoid = _guidance(locale, data.phase_key, focus, style=style)
    accent = PHASE_ACCENT[_locale(locale)].get(data.phase_key, {})
    plain_accent = PLAIN_PHASE_ACCENT[_locale(locale)].get(data.phase_key, {})
    personal_lines = _focus_personal_lines(locale, data.phase_key, focus, style=style)
    next_phase_moment = jd_to_local_datetime(data.next_phase_jd, data.timezone_name)
    lunar_day_start = jd_to_local_datetime(data.lunar_day_start_jd, data.timezone_name)
    next_lunar_day_start = jd_to_local_datetime(data.next_lunar_day_start_jd, data.timezone_name)
    return {
        "date": for_date,
        "age": data.age_days,
        "phase_key": data.phase_key,
        "phase_name": _phase_name(locale, data.phase_key, style=style),
        "short_phase": _short_phase(locale, data.phase_key, style=style),
        "illumination": data.illumination,
        "lunar_day": data.lunar_day,
        "moon_sign": sign_label(locale, data.moon_sign),
        "moon_sign_key": data.moon_sign,
        "moon_line": _format_moon_sign_line(locale, data.moon_sign, style=style),
        "next_phase_key": data.next_phase_key,
        "next_phase_days": data.next_phase_days,
        "next_phase_date": next_phase_moment.date(),
        "next_phase_moment": next_phase_moment,
        "lunar_day_start_moment": lunar_day_start,
        "next_lunar_day_start_moment": next_lunar_day_start,
        "do": rec_do,
        "avoid": rec_avoid,
        "personal_lines": personal_lines,
        "personal_note": "\n".join(personal_lines),
        "accent_color": accent.get("color", ""),
        "accent_label": accent.get("label", "") if _use_terms(style) else plain_accent.get("label", ""),
        "affirmation": accent.get("affirmation", "") if _use_terms(style) else plain_accent.get("affirmation", ""),
    }


def _snap_extra_lines(snap: dict, *, locale: str, focus: str, style: str = "terms") -> list[str]:
    lines: list[str] = []
    personal_lines = snap.get("personal_lines")
    if isinstance(personal_lines, list) and personal_lines:
        lines.append(_focus_personal_header(locale, focus, style=style))
        lines.extend(str(line) for line in personal_lines if str(line).strip())
    elif str(snap.get("personal_note") or "").strip():
        lines.append(_focus_personal_header(locale, focus, style=style))
        lines.append(str(snap["personal_note"]))
    affirmation = str(snap.get("affirmation") or "").strip()
    if affirmation and normalize_moon_focus(focus) != "creativity":
        lines.append(f"💬 «{affirmation}»")
    accent_color = str(snap.get("accent_color") or "").strip()
    accent_label = str(snap.get("accent_label") or "").strip()
    if accent_label and _use_terms(style) and accent_color:
        lines.insert(0, f"{accent_color} {accent_label}")
    elif accent_label and not _use_terms(style):
        lines.insert(0, f"✨ {accent_label}")
    return lines


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
    timezone_name: str = "UTC",
) -> str:
    current_locale = _locale(locale)
    if for_date is None:
        for_date = date.today()

    snap = _moon_snapshot(
        locale,
        for_date,
        focus=focus,
        style=style,
        timezone_name=timezone_name,
    )
    if snap is None:
        return _fallback_text(locale)

    age = float(snap["age"])
    phase_name = str(snap["phase_name"])
    accent_color = str(snap.get("accent_color") or "")
    phase_line = f"{accent_color} {phase_name}" if accent_color and _use_terms(style) else phase_name
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    moon_line = str(snap["moon_line"])
    next_phase_name = _phase_name(locale, str(snap["next_phase_key"]), style=style)
    days_left = int(snap["next_phase_days"])
    next_date = snap["next_phase_date"]
    if isinstance(next_date, date):
        next_date_value = next_date
    else:
        next_date_value = for_date + timedelta(days=days_left)
    next_phase_moment = snap.get("next_phase_moment")
    next_lunar_day_moment = snap.get("next_lunar_day_start_moment")
    planning = _planning_lines(
        locale,
        str(snap["phase_key"]),
        focus=focus,
        show_all_focuses=show_all_focuses,
        style=style,
    )
    lunar_day_line = _lunar_day_label(locale, lunar_day, style=style)
    age_line = _moon_age_label(locale, age, style=style)
    next_phase_line = _next_phase_label(
        locale,
        next_phase_name,
        days_left,
        next_date_value,
        style=style,
        next_phase_moment=next_phase_moment if isinstance(next_phase_moment, datetime) else None,
    )
    next_lunar_day_line = ""
    if isinstance(next_lunar_day_moment, datetime):
        next_lunar_day_line = _next_lunar_day_label(
            locale,
            for_date,
            next_lunar_day_moment,
            style=style,
        )
    if current_locale == "ru":
        phase_label = "• Фаза Луны" if _use_terms(style) else "• Фаза"
        illum_label = "• Освещённость диска" if _use_terms(style) else "• Освещённость"
        header_lines = [
            f"🌙 Лунный календарь на {for_date.strftime('%d.%m.%Y')}\n",
            f"{phase_label}: {phase_line}\n",
            f"• {moon_line}\n",
            f"{illum_label}: {illumination}%\n",
            f"• {lunar_day_line}\n",
            f"{age_line}\n",
            f"{next_phase_line}",
        ]
        if next_lunar_day_line:
            header_lines.append(f"\n{next_lunar_day_line}")
        header = "".join(header_lines)
        return header + "\n\n" + "\n".join(planning)

    phase_label = "• Moon phase" if _use_terms(style) else "• Phase"
    illum_label = "• Illumination" if _use_terms(style) else "• Lit"
    header_lines = [
        f"🌙 Moon calendar for {for_date.isoformat()}\n\n",
        f"{phase_label}: {phase_line}\n",
        f"• {moon_line}\n",
        f"{illum_label}: {illumination}%\n",
        f"• {lunar_day_line}\n",
        f"{age_line}\n",
        f"{next_phase_line}",
    ]
    if next_lunar_day_line:
        header_lines.append(f"\n{next_lunar_day_line}")
    header = "".join(header_lines)
    return header + "\n\n" + "\n".join(planning)


def generate_moon_table_text(
    locale: str,
    days: int,
    start_date: date | None = None,
    *,
    focus: str = "practices",
    style: str = "terms",
    timezone_name: str = "UTC",
) -> str:
    current_locale = _locale(locale)
    if start_date is None:
        start_date = date.today()
    total_days = max(1, min(30, days))

    section = _focus_section(locale, focus, style=style)
    if current_locale == "ru":
        title = (
            f"🌙 Лунный календарь на {total_days} дней"
            if _use_terms(style)
            else f"🌙 Календарь на {total_days} дней"
        )
        lines = [title, section, ""]
    else:
        title = (
            f"🌙 Moon calendar for {total_days} days"
            if _use_terms(style)
            else f"🌙 Calendar for {total_days} days"
        )
        lines = [title, section, ""]

    week_index = 1
    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        snap = _moon_snapshot(
            locale,
            current_date,
            focus=focus,
            style=style,
            timezone_name=timezone_name,
        )
        if snap is None:
            continue

        if offset % 7 == 0:
            if offset > 0:
                lines.append("")
            if current_locale == "ru":
                lines.append(f"━━ Неделя {week_index} ━━")
                if _use_terms(style):
                    lines.append("Дата | Лун. день | Знак | Фаза | %")
                else:
                    lines.append("Дата | День | Знак | Фаза | %")
            else:
                lines.append(f"━━ Week {week_index} ━━")
                if _use_terms(style):
                    lines.append("Date | Lunar day | Sign | Phase | %")
                else:
                    lines.append("Date | Day | Sign | Phase | %")
            week_index += 1

        date_str = current_date.strftime("%d.%m")
        phase_col = str(snap["short_phase"])
        if _use_terms(style) and snap.get("accent_color"):
            phase_col = f"{snap['accent_color']}{phase_col}"
        lines.append(
            f"{date_str} | {int(snap['lunar_day']):>2} | {snap['moon_sign'][:8]:<8} | "
            f"{phase_col} | {int(snap['illumination']):>3}%"
        )
        if current_locale == "ru":
            lines.append(f"  ✔ {snap['do']}")
            lines.append(f"  ✖ {snap['avoid']}")
        else:
            lines.append(f"  ✔ {snap['do']}")
            lines.append(f"  ✖ {snap['avoid']}")
        personal_lines = _focus_personal_lines(locale, str(snap["phase_key"]), focus, style=style)
        if personal_lines:
            lines.append(f"  {_focus_personal_header(locale, focus, style=style)}")
            for note in personal_lines:
                lines.append(f"  {note}")

    if len(lines) <= 2:
        return _fallback_text(locale)
    return "\n".join(lines)


def generate_moon_compact_table_text(
    locale: str,
    days: int,
    start_date: date | None = None,
    *,
    style: str = "terms",
    timezone_name: str = "UTC",
) -> str:
    current_locale = _locale(locale)
    if start_date is None:
        start_date = date.today()
    total_days = max(1, min(30, days))

    if current_locale == "ru":
        title = (
            f"🌙 Компактный лунный календарь на {total_days} дней"
            if _use_terms(style)
            else f"🌙 Компактный календарь на {total_days} дней"
        )
        day_col = "День" if _use_terms(style) else "День цикла"
        phase_col = "Фаза" if _use_terms(style) else "Фаза"
        lines = [title, "", f"Дата | {day_col} | {phase_col} | %"]
    else:
        title = (
            f"🌙 Compact moon calendar for {total_days} days"
            if _use_terms(style)
            else f"🌙 Compact calendar for {total_days} days"
        )
        day_col = "Day" if _use_terms(style) else "Cycle"
        lines = [title, "", f"Date | {day_col} | Phase | %"]

    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        snap = _moon_snapshot(
            locale,
            current_date,
            style=style,
            timezone_name=timezone_name,
        )
        if snap is None:
            continue
        date_str = current_date.strftime("%d.%m")
        phase_col = str(snap["short_phase"])
        if _use_terms(style) and snap.get("accent_color"):
            phase_col = f"{snap['accent_color']}{phase_col}"
        lines.append(
            f"{date_str} | {int(snap['lunar_day']):>2} | {phase_col} | {int(snap['illumination']):>3}%"
        )

    if len(lines) <= 3:
        return _fallback_text(locale)
    return "\n".join(lines)


MAJOR_LUNAR_PHASES = ("new_moon", "first_quarter", "full_moon", "last_quarter")
LUNAR_PREVIEW_DAYS = 7
LUNAR_PREVIEW_FREE_DAYS = 1


def major_lunar_phase_on(for_date: date, timezone_name: str = "UTC") -> str | None:
    return major_phase_on_local_date(for_date, timezone_name)


def _next_major_phase_line(
    locale: str,
    snap: dict[str, str | int | float],
    *,
    style: str = "terms",
) -> str | None:
    current_locale = _locale(locale)
    next_key = str(snap["next_phase_key"])
    if next_key not in MAJOR_LUNAR_PHASES:
        return None
    days_left = int(snap["next_phase_days"])
    if days_left > 3:
        return None
    title = _phase_name(locale, next_key, style=style).lower()
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
    timezone_name: str = "UTC",
) -> str:
    current_locale = _locale(locale)
    snap = _moon_snapshot(
        locale,
        for_date,
        focus=focus,
        style=style,
        timezone_name=timezone_name,
    )
    if snap is None:
        return _fallback_text(locale)

    phase_name = str(snap["phase_name"])
    moon_line = str(snap["moon_line"])
    illumination = int(snap["illumination"])
    lunar_day = int(snap["lunar_day"])
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    extras = _snap_extra_lines(snap, locale=locale, focus=focus, style=style)
    next_line = _next_major_phase_line(locale, snap, style=style)
    section = _focus_section(locale, focus, style=style)
    day_label = _lunar_day_label(locale, lunar_day, style=style)
    header = (
        f"🌙 Лунный фокус · {for_date.strftime('%d.%m')}"
        if _use_terms(style)
        else f"🌙 Фокус дня · {for_date.strftime('%d.%m')}"
    )

    if current_locale == "ru":
        lines = [
            header,
            "",
            f"{moon_line} · {phase_name.lower()} · {illumination}% · {day_label}",
            "",
            section,
            f"✅ Уместно: {rec_do}",
            f"⚠️ Избегать: {rec_avoid}",
        ]
        lines.extend(extras)
        if next_line:
            lines.extend(["", next_line])
        next_lunar = snap.get("next_lunar_day_start_moment")
        if isinstance(next_lunar, datetime):
            lines.extend(["", _next_lunar_day_label(locale, for_date, next_lunar, style=style)])
        return "\n".join(lines)

    header_en = (
        f"🌙 Lunar focus · {for_date.isoformat()}"
        if _use_terms(style)
        else f"🌙 Daily focus · {for_date.isoformat()}"
    )
    lines = [
        header_en,
        "",
        f"{moon_line} · {phase_name.lower()} · {illumination}% · {day_label}",
        "",
        section,
        f"✅ Do: {rec_do}",
        f"⚠️ Avoid: {rec_avoid}",
    ]
    lines.extend(extras)
    if next_line:
        lines.extend(["", next_line])
    next_lunar = snap.get("next_lunar_day_start_moment")
    if isinstance(next_lunar, datetime):
        lines.extend(["", _next_lunar_day_label(locale, for_date, next_lunar, style=style)])
    return "\n".join(lines)


def lunar_event_title(phase_key: str, locale: str, *, style: str = "terms") -> str:
    return _phase_name(locale, phase_key, style=style)


def format_lunar_day_notification(
    phase_key: str,
    locale: str,
    for_date: date,
    *,
    focus: str = "practices",
    style: str = "terms",
    timezone_name: str = "UTC",
) -> str:
    current_locale = _locale(locale)
    title = lunar_event_title(phase_key, current_locale, style=style)
    snap = _moon_snapshot(
        locale,
        for_date,
        focus=focus,
        style=style,
        timezone_name=timezone_name,
    )
    if snap is None:
        return _fallback_text(locale)
    moon_line = str(snap["moon_line"])
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    illumination = int(snap["illumination"])
    section = _focus_section(locale, focus, style=style)
    day_label = _lunar_day_label(locale, int(snap["lunar_day"]), style=style)
    extras = _snap_extra_lines(snap, locale=locale, focus=focus, style=style)
    extra_block = f"\n{chr(10).join(extras)}" if extras else ""
    if current_locale == "ru":
        return (
            f"🌑 Сегодня {title.lower()} · {for_date.strftime('%d.%m.%Y')}\n\n"
            f"• {moon_line} · {illumination}% · {day_label}\n"
            f"• {section}\n"
            f"• Что делать: {rec_do}\n"
            f"• Чего избегать: {rec_avoid}"
            f"{extra_block}"
        )
    return (
        f"🌑 Today is {title} · {for_date.isoformat()}\n\n"
        f"• {moon_line} · {illumination}% · {day_label}\n"
        f"• {section}\n"
        f"• Do: {rec_do}\n"
        f"• Avoid: {rec_avoid}"
        f"{extra_block}"
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
    timezone_name: str = "UTC",
) -> str:
    current_locale = _locale(locale)
    title = lunar_event_title(phase_key, current_locale, style=style)
    snap = _moon_snapshot(
        locale,
        event_date,
        focus=focus,
        style=style,
        timezone_name=timezone_name,
    )
    if snap is None:
        return _fallback_text(locale)
    rec_do = str(snap["do"])
    rec_avoid = str(snap["avoid"])
    moon_line = str(snap["moon_line"])
    section = _focus_section(locale, focus, style=style)
    extras = _snap_extra_lines(snap, locale=locale, focus=focus, style=style)
    extra_block = f"\n{chr(10).join(extras)}" if extras else ""

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
            f"{extra_block}"
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
        f"{extra_block}"
    )
