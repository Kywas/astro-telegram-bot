from __future__ import annotations

from datetime import date

from app.astro_engine import EveningSnapshot, build_evening_snapshot
from app.astro_glossary import format_moon_in_sign_short
from app.forecast_text import format_summary_aspect
from app.moon_calendar import PHASE_GUIDANCE, PHASE_NAMES
from app.text_format import b, format_screen_body, p

GOAL_FOCUS = {
    "ru": {
        "love": "близость",
        "career": "карьеру",
        "money": "финансы",
        "balance": "баланс",
    },
    "en": {
        "love": "closeness",
        "career": "career",
        "money": "finances",
        "balance": "balance",
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _snapshot_from_profile(profile, locale: str, for_date: date | None) -> EveningSnapshot | None:
    if profile is None or for_date is None or not profile.sign:
        return None
    timezone_name = profile.birth_timezone or profile.timezone or "UTC"
    return build_evening_snapshot(
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        city=profile.city,
        timezone_name=timezone_name,
        for_date=for_date,
        locale=locale,
        sign=profile.sign,
        user_id=profile.user_id,
        lat=profile.birth_lat,
        lon=profile.birth_lon,
        birth_timezone=profile.birth_timezone,
    )


def _sky_tone(snapshot: EveningSnapshot) -> str:
    if snapshot.challenging_count >= 2 and snapshot.supportive_count <= 1:
        return "heavy"
    if snapshot.supportive_count >= 2 and snapshot.challenging_count <= 1:
        return "light"
    return "mixed"


def _top_aspect_line(locale: str, snapshot: EveningSnapshot) -> str | None:
    if snapshot.top_hit is None:
        return None
    orb, transit, natal, aspect = snapshot.top_hit
    return format_summary_aspect(locale, transit, natal, aspect, orb)


def _build_mood_reflection(locale: str, score: int, snapshot: EveningSnapshot) -> str:
    lang = _lang(locale)
    tone = _sky_tone(snapshot)
    aspect_line = _top_aspect_line(locale, snapshot)

    if score <= 4:
        if snapshot.energy_score >= 7:
            return (
                "Небо было бодрее, чем вы себя чувствуете — возможно, день забрал больше сил, чем кажется."
                if lang == "ru"
                else "The sky was brighter than you feel — the day may have cost more energy than it looked."
            )
        if tone == "heavy":
            if aspect_line:
                lead = (
                    f"День мог быть тяжёлым — главный фон: {aspect_line}."
                    if lang == "ru"
                    else f"Today may have felt heavy — main backdrop: {aspect_line}."
                )
            else:
                lead = (
                    "День мог быть тяжёлым — транзиты давили на фон."
                    if lang == "ru"
                    else "Today may have felt heavy — transits pressed on the background."
                )
            tail = (
                "Это про небо, а не про вашу ценность."
                if lang == "ru"
                else "That is about the sky, not your worth."
            )
            return f"{lead} {tail}"

        if tone == "light":
            return (
                "Небо давало поддержку, но вы устали — возможно, отдали слишком много сил."
                if lang == "ru"
                else "The sky offered support, but you are tired — you may have spent a lot of energy."
            )

        return (
            "Низкое настроение — нормальный сигнал замедлиться и отпустить лишнее."
            if lang == "ru"
            else "A low mood is a valid signal to slow down and release what is extra."
        )

    if score >= 8:
        if tone == "heavy":
            return (
                "Вы выдержали непростой день с силой — отметьте, что всё же получилось."
                if lang == "ru"
                else "You held a demanding day with strength — note what still worked."
            )
        if aspect_line and tone == "light":
            return (
                f"Энергия дня и ваше состояние совпали. Главный фон: {aspect_line}."
                if lang == "ru"
                else f"Today's energy matched how you feel. Main backdrop: {aspect_line}."
            )
        return (
            "Хороший день — закрепите один момент, который стоит повторить."
            if lang == "ru"
            else "A good day — anchor one moment worth repeating."
        )

    if snapshot.energy_score >= 7 and score <= 6:
        return (
            "Небо было бодрее, чем ваше состояние — возможно, день потребовал больше, чем казалось."
            if lang == "ru"
            else "The sky was brighter than your mood — the day may have cost more than it looked."
        )
    if snapshot.energy_score <= 4 and score >= 6:
        return (
            "Вы держались лучше, чем позволял фон дня — это внутренний ресурс."
            if lang == "ru"
            else "You held up better than the day's backdrop — that is inner resource."
        )

    if aspect_line:
        return (
            f"День прошёл ровно на фоне: {aspect_line}."
            if lang == "ru"
            else f"The day moved evenly against this backdrop: {aspect_line}."
        )
    return (
        "День прошёл ровно — вечером уместно подвести короткий итог."
        if lang == "ru"
        else "A steady day — a short evening summary is enough."
    )


def _build_evening_tip(
    locale: str,
    score: int,
    snapshot: EveningSnapshot,
    goal: str | None,
) -> str:
    lang = _lang(locale)
    guidance = PHASE_GUIDANCE[lang].get(
        snapshot.moon_phase_key,
        PHASE_GUIDANCE[lang]["waxing_gibbous"],
    )
    goal_focus = GOAL_FOCUS[lang].get(goal or "", "")

    if score <= 4:
        if lang == "ru":
            tip = f"🌙 Вечером: {guidance['avoid'].capitalize()} — отдых важнее новых решений."
        else:
            tip = f"🌙 This evening: {guidance['avoid'].capitalize()} — rest beats new decisions."
    elif score >= 8:
        if lang == "ru":
            tip = f"💡 Зафиксируйте один удачный момент. Завтра уместно: {guidance['do']}."
        else:
            tip = f"💡 Anchor one good moment. Tomorrow suits: {guidance['do']}."
    else:
        if lang == "ru":
            tip = f"🌙 Отпустите лишнее. Завтра: {guidance['do']}."
        else:
            tip = f"🌙 Release what is extra. Tomorrow: {guidance['do']}."

    if goal_focus:
        if lang == "ru":
            tip += f" Фокус «{goal_focus}» лучше не форсировать сегодня вечером."
        else:
            tip += f" Ease off pushing {goal_focus} tonight."

    if snapshot.solar_only:
        if lang == "ru":
            tip += " Укажите дату, время и город рождения — вечерний разбор станет точнее."
        else:
            tip += " Add birth date, time, and city for a sharper evening read."

    return tip


def format_streak_message(locale: str, streak: int) -> str:
    lang = _lang(locale)
    if streak == 1:
        return "Серия началась — хороший ритм 🌱" if lang == "ru" else "Streak started — good rhythm 🌱"
    if streak == 3:
        return (
            "3 дня подряд — привычка уже держится ✨"
            if lang == "ru"
            else "3 days in a row — the habit is holding ✨"
        )
    if streak == 7:
        return (
            "🔥 7 дней подряд — вы строите полезный ритм."
            if lang == "ru"
            else "🔥 7 days in a row — you are building a useful rhythm."
        )
    if lang == "ru":
        return f"🔥 Серия: {streak} дн. подряд."
    return f"🔥 Streak: {streak} days in a row."


def build_evening_checkin_prompt(
    locale: str,
    *,
    profile=None,
    for_date: date | None = None,
) -> str:
    lang = _lang(locale)
    snapshot = _snapshot_from_profile(profile, locale, for_date)
    if snapshot is None:
        if lang == "ru":
            return format_screen_body(
                "🌆 Вечерний чек-ин\n\n"
                "Как прошёл день? Оцени настроение от 1 до 10 — "
                "это поможет точнее настроить прогнозы."
            )
        return format_screen_body(
            "🌆 Evening check-in\n\n"
            "How was your day? Rate your mood from 1 to 10 — "
            "it helps personalize your forecasts."
        )

    moon_line = format_moon_in_sign_short(locale, snapshot.moon_sign)
    phase = PHASE_NAMES[lang][snapshot.moon_phase_key]
    aspect_line = _top_aspect_line(locale, snapshot)
    if lang == "ru":
        lines = [
            "🌆 Вечерний чек-ин",
            "",
            f"Сегодня {phase.lower()}, {moon_line.lower()}.",
        ]
        if aspect_line:
            lines.append(f"Главный транзит дня: {aspect_line}.")
        lines.append("Как прошёл день? Оцени настроение от 1 до 10.")
        return format_screen_body("\n".join(lines))

    lines = [
        "🌆 Evening check-in",
        "",
        f"Today: {phase}, {moon_line}.",
    ]
    if aspect_line:
        lines.append(f"Main transit today: {aspect_line}.")
    lines.append("How was your day? Rate your mood from 1 to 10.")
    return format_screen_body("\n".join(lines))


def build_evening_response(
    locale: str,
    score: int,
    streak: int,
    *,
    profile=None,
    for_date: date | None = None,
) -> str:
    lang = _lang(locale)
    snapshot = _snapshot_from_profile(profile, locale, for_date)

    if snapshot is None:
        if lang == "ru":
            return format_screen_body(
                f"🌙 Спасибо! Настроение: {score}/10\n\n{format_streak_message(locale, streak)}"
            )
        return format_screen_body(
            f"🌙 Thanks! Mood: {score}/10\n\n{format_streak_message(locale, streak)}"
        )

    reflection = _build_mood_reflection(locale, score, snapshot)
    tip = _build_evening_tip(locale, score, snapshot, profile.goal if profile else None)
    streak_line = format_streak_message(locale, streak)

    if lang == "ru":
        header = f"🌙 Спасибо! Настроение: {score}/10 · энергия дня {snapshot.energy_score}/10"
    else:
        header = f"🌙 Thanks! Mood: {score}/10 · day energy {snapshot.energy_score}/10"

    return p(b(header), format_screen_body(reflection), format_screen_body(tip), format_screen_body(streak_line))
