from __future__ import annotations

from datetime import date

from app.astro_engine import EveningSnapshot, build_evening_snapshot
from app.astro_glossary import format_moon_in_sign_short, moon_in_sign_hint
from app.forecast_text import format_summary_aspect
from app.i18n import goal_display
from app.moon_calendar import PHASE_GUIDANCE, PHASE_NAMES
from app.text_format import b, format_screen_body, p

GOAL_EVENING = {
    "ru": {
        "love": (
            "Темы близости можно отложить — «давай поговорим серьёзно» "
            "лучше не сегодня, если сил уже нет."
        ),
        "career": (
            "Рабочие чаты можно заглушить — завтра всё равно никуда не денется, "
            "а мозгу нужен офлайн."
        ),
        "money": (
            "Финансовые «надо бы» подождут до утра — вечером цифры только злят, "
            "если устал."
        ),
        "balance": (
            "Не обязательно вечером «дожимать баланс» — ты уже отметился, "
            "этого достаточно."
        ),
    },
    "en": {
        "love": (
            "Closeness topics can wait — «let's talk seriously» is better not tonight "
            "if you're out of steam."
        ),
        "career": (
            "Work chats can go on mute — nothing urgent will vanish, your brain needs offline."
        ),
        "money": (
            "Money to-dos can wait until morning — numbers only annoy when you're tired."
        ),
        "balance": (
            "No need to «force balance» tonight — you checked in, that's enough."
        ),
    },
}

GOAL_RELATIONSHIP_EVENING = {
    "ru": {
        ("love", "relationship"): " Партнёр никуда не денется — «устал, обниму завтра» тоже норм.",
        ("love", "single"): " Свидания и переписки подождут — вечер для восстановления, не для свайпов.",
    },
    "en": {
        ("love", "relationship"): " Your partner isn't going anywhere — «tired, hug tomorrow» counts.",
        ("love", "single"): " Dating can wait — evening is for recharge, not swiping.",
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


def _mood_feel_label(locale: str, score: int) -> str:
    lang = _lang(locale)
    if lang == "ru":
        if score >= 8:
            return "хорошо"
        if score >= 6:
            return "нормально"
        if score >= 4:
            return "так себе"
        return "тяжело"
    if score >= 8:
        return "good"
    if score >= 6:
        return "okay"
    if score >= 4:
        return "so-so"
    return "rough"


def _day_strength_label(locale: str, score: int) -> str:
    """Plain label for chart day-energy (not the user's mood rating)."""
    lang = _lang(locale)
    if lang == "ru":
        if score >= 8:
            return "бодрый"
        if score >= 6:
            return "средний"
        if score >= 4:
            return "спокойный"
        return "на экономном режиме"
    if score >= 8:
        return "high"
    if score >= 6:
        return "moderate"
    if score >= 4:
        return "calm"
    return "low battery"


def _format_evening_header(
    locale: str,
    score: int,
    energy_score: int,
    *,
    name_bit: str = "",
) -> str:
    lang = _lang(locale)
    mood_word = _mood_feel_label(locale, score)
    strength_word = _day_strength_label(locale, energy_score)
    if lang == "ru":
        return (
            f"🌙 Принято{name_bit}! Ты отметил настроение: {mood_word} ({score}/10) · "
            f"день по силам на карте: {strength_word} ({energy_score}/10)"
        )
    return (
        f"🌙 Got it{name_bit}! You rated your mood: {mood_word} ({score}/10) · "
        f"chart day strength: {strength_word} ({energy_score}/10)"
    )


def _personal_sky_opener(
    locale: str,
    snapshot: EveningSnapshot,
    profile,
    *,
    include_energy: bool = True,
) -> str:
    """One short line tying today's sky to this user's chart."""
    lang = _lang(locale)
    phase = PHASE_NAMES[lang][snapshot.moon_phase_key].lower()
    moon_line = format_moon_in_sign_short(locale, snapshot.moon_sign)

    if lang == "ru":
        base = f"Сегодня {phase}, {moon_line}"
        if not include_energy:
            return f"{base}."
        strength = _day_strength_label(locale, snapshot.energy_score)
        return f"{base} — по карте день шёл на {strength} уровень сил."
    base = f"Today: {phase}, {moon_line}"
    if not include_energy:
        return f"{base}."
    strength = _day_strength_label(locale, snapshot.energy_score)
    return f"{base} — on your chart, a {strength} day strength-wise."


def _mood_energy_gap_note(locale: str, score: int, snapshot: EveningSnapshot) -> str | None:
    """When self-reported mood diverges from chart energy for this user."""
    lang = _lang(locale)
    gap = score - snapshot.energy_score
    if gap >= 3:
        if lang == "ru":
            return (
                "Твоё настроение выше, чем силы дня по карте — "
                "держишь лицо, хотя день забрал больше энергии."
            )
        return (
            "Your mood is higher than the chart's day strength — "
            "you're holding up even though the day cost more."
        )
    if gap <= -3:
        if lang == "ru":
            return (
                "Твоё настроение ниже, чем силы дня по карте — "
                "видимо, просело не из‑за «неба», а по своим причинам."
            )
        return (
            "Your mood is lower than the chart's day strength — "
            "likely dipped for your own reasons, not just the sky."
        )
    if score >= 8 and snapshot.energy_score <= score - 2:
        if lang == "ru":
            return (
                "Классика: настроение хорошее, а силы по карте уже на спаде — "
                "батарейка села раньше, чем настроение."
            )
        return (
            "Classic: mood still good, chart strength already fading — "
            "battery died before the vibe."
        )
    return None


def _build_mood_reflection(
    locale: str,
    score: int,
    snapshot: EveningSnapshot,
    profile=None,
) -> str:
    lang = _lang(locale)
    tone = _sky_tone(snapshot)
    aspect_line = _top_aspect_line(locale, snapshot)
    gap_note = _mood_energy_gap_note(locale, score, snapshot)
    opener = _personal_sky_opener(locale, snapshot, profile, include_energy=gap_note is None)
    moon_hint = moon_in_sign_hint(locale, snapshot.moon_sign)

    def _join(*parts: str) -> str:
        return " ".join(part for part in parts if part)

    if score <= 4:
        if snapshot.energy_score >= 7:
            body = (
                "По карте день был бодрый, а ты чувствуешь себя иначе — "
                "похоже, забрал больше сил, чем кажется. Это нормально."
                if lang == "ru"
                else "Your chart had a brighter day than you feel — it likely cost more. That's normal."
            )
            return _join(opener, body)
        if tone == "heavy":
            if aspect_line:
                lead = (
                    f"К твоей карте сегодня шёл напряжённый фон: {aspect_line}."
                    if lang == "ru"
                    else f"Tense backdrop to your chart today: {aspect_line}."
                )
            else:
                lead = (
                    "По транзитам день мог давить — это фон, не приговор тебе лично."
                    if lang == "ru"
                    else "Transits may have pressed today — background noise, not a verdict on you."
                )
            tail = (
                "Сейчас не разбирать — просто выдохни."
                if lang == "ru"
                else "No unpacking now — just exhale."
            )
            return _join(opener, lead, tail)

        if tone == "light":
            body = (
                "Небо подкидывало поддержку, а настроение всё равно просело — "
                "видимо, отдал слишком много. Можно остановиться без вины."
                if lang == "ru"
                else "The sky offered support, but mood still dipped — you may have given a lot. Stop without guilt."
            )
            return _join(opener, body)

        body = (
            "Низкое настроение — сигнал «хватит на сегодня», не приговор. "
            "Телефон можно отложить."
            if lang == "ru"
            else "Low mood is a «stop for today» signal, not a verdict. Phone can wait."
        )
        return _join(opener, body)

    if score >= 8:
        if gap_note:
            tail = (
                "Вспомни один маленький момент, который хочется повторить — "
                "не для отчёта, просто чтобы мозг не стёр за ночь."
                if lang == "ru"
                else "Recall one small moment you'd repeat — not for a report, so your brain won't erase it."
            )
            return _join(opener, gap_note, tail)
        if tone == "heavy":
            body = (
                "Ты выдержал непростой день по карте — и настроение всё равно хорошее. "
                "Это победа, даже если кажется «просто пережил»."
                if lang == "ru"
                else "You held a heavy chart day — mood still good. A win, even if it feels like «just survived»."
            )
            return _join(opener, body)
        if aspect_line and tone == "light":
            body = (
                f"Настроение и небо совпали — приятно. Главный транзит к тебе: {aspect_line}. "
                f"Можно не анализировать до утра."
                if lang == "ru"
                else f"Mood and sky aligned — nice. Main transit to you: {aspect_line}. Skip analysis until morning."
            )
            return _join(opener, body)
        if moon_hint:
            body = (
                f"{moon_hint.capitalize()} — хороший финал. "
                f"Один маленький момент на память, и на сегодня достаточно."
                if lang == "ru"
                else f"{moon_hint.capitalize()} — nice finish. One small moment to remember, then enough for today."
            )
            return _join(opener, body)
        body = (
            "Хороший день — приятный финал. Вспомни один маленький момент, "
            "который хочется повторить: не для отчёта, просто чтобы мозг не стёр его за ночь."
            if lang == "ru"
            else "A good day — nice finish. Recall one small moment you'd repeat: not for a report, so your brain won't erase it overnight."
        )
        return _join(opener, body)

    if gap_note:
        tail = (
            "Можно не докручивать итоги."
            if lang == "ru"
            else "No need to over-process."
        )
        return _join(opener, gap_note, tail)

    if aspect_line:
        body = (
            f"День ровный. К твоей карте: {aspect_line} — "
            f"вечером это не домашнее задание."
            if lang == "ru"
            else f"Steady day. To your chart: {aspect_line} — not homework tonight."
        )
        return _join(opener, body)
    body = (
        "День прошёл ровно — для вечера достаточно. Короткий итог в голове, и можно отпускать."
        if lang == "ru"
        else "A steady day — enough for evening. A short mental note, then let go."
    )
    return _join(opener, body)


def _build_evening_tip(
    locale: str,
    score: int,
    snapshot: EveningSnapshot,
    profile=None,
) -> str:
    lang = _lang(locale)
    guidance = PHASE_GUIDANCE[lang].get(
        snapshot.moon_phase_key,
        PHASE_GUIDANCE[lang]["waxing_gibbous"],
    )
    goal = profile.goal if profile else None
    goal_label = goal_display(locale, goal) if goal else None
    phase_name = PHASE_NAMES[lang][snapshot.moon_phase_key].lower()

    if score <= 4:
        avoid_bit = snapshot.avoid_line if snapshot.avoid_line else guidance["avoid"]
        if lang == "ru":
            tip = (
                f"🌙 {phase_name.capitalize()} + твой вечер: {avoid_bit} — "
                f"новые решения подождут до утра."
            )
        else:
            tip = (
                f"🌙 {phase_name.capitalize()} + your evening: {avoid_bit} — "
                f"new decisions can wait until morning."
            )
    elif score >= 8:
        if lang == "ru":
            tip = (
                f"💡 Лунная фаза ({phase_name}) подсказывает на завтра: {guidance['do']} — "
                f"но только если захочется, не по приказу."
            )
        else:
            tip = (
                f"💡 Moon phase ({phase_name}) hints for tomorrow: {guidance['do']} — "
                f"only if you feel like it."
            )
    else:
        if lang == "ru":
            tip = (
                f"🌙 Ты уже отметился — этого достаточно. "
                f"Завтра, если будет настроение ({phase_name}): {guidance['do']}."
            )
        else:
            tip = (
                f"🌙 You checked in — that's enough. "
                f"Tomorrow, if you're up for it ({phase_name}): {guidance['do']}."
            )

    if goal and goal in GOAL_EVENING[lang]:
        tip += f" {GOAL_EVENING[lang][goal]}"
        if profile and profile.relationship_status:
            rel_extra = GOAL_RELATIONSHIP_EVENING[lang].get((goal, profile.relationship_status))
            if rel_extra:
                tip += rel_extra
    elif goal_label:
        if lang == "ru":
            tip += f" Фокус «{goal_label.lower()}» вечером можно отложить — смена закончилась."
        else:
            tip += f" «{goal_label}» focus can wait tonight — shift's over."

    if snapshot.solar_only:
        if lang == "ru":
            tip += " Когда будет минута — добавь дату, время и город рождения: вечерний разбор станет точнее."
        else:
            tip += " When you have a minute — add birth date, time, and city for a sharper evening read."

    return tip


def format_streak_message(locale: str, streak: int) -> str:
    lang = _lang(locale)
    if streak == 1:
        return (
            "Серия началась — ты уже в ритме 🌱 (да, просто отметить настроение тоже считается)"
            if lang == "ru"
            else "Streak started — you're in rhythm 🌱 (yes, tapping mood counts)"
        )
    if streak == 3:
        return (
            "3 дня подряд — привычка держится ✨ Мозг начинает верить, что это не разовая акция."
            if lang == "ru"
            else "3 days in a row — the habit is holding ✨ Your brain is starting to believe it."
        )
    if streak == 7:
        return (
            "🔥 7 дней подряд — ты реально строишь полезный ритм. Не героизм, просто регулярность."
            if lang == "ru"
            else "🔥 7 days in a row — you're building a useful rhythm. Not heroics, just showing up."
        )
    if lang == "ru":
        return f"🔥 Серия: {streak} дн. подряд — продолжай в своём темпе."
    return f"🔥 Streak: {streak} days in a row — keep your own pace."


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
        mood_word = _mood_feel_label(locale, score)
        if lang == "ru":
            return format_screen_body(
                f"🌙 Принято! Ты отметил настроение: {mood_word} ({score}/10)\n\n"
                f"{format_streak_message(locale, streak)}"
            )
        return format_screen_body(
            f"🌙 Got it! You rated your mood: {mood_word} ({score}/10)\n\n"
            f"{format_streak_message(locale, streak)}"
        )

    reflection = _build_mood_reflection(locale, score, snapshot, profile=profile)
    tip = _build_evening_tip(locale, score, snapshot, profile=profile)
    streak_line = format_streak_message(locale, streak)

    name_bit = ""
    if profile and profile.first_name and len(profile.first_name.strip()) <= 20:
        name_bit = f", {profile.first_name.strip()}"

    if lang == "ru":
        header = _format_evening_header(locale, score, snapshot.energy_score, name_bit=name_bit)
        footer = "На сегодня хватит. Спокойного вечера — телефон можно отложить 🌙"
    else:
        header = _format_evening_header(locale, score, snapshot.energy_score, name_bit=name_bit)
        footer = "That's enough for today. Good evening — phone can wait 🌙"

    return p(
        b(header),
        format_screen_body(reflection),
        format_screen_body(tip),
        format_screen_body(streak_line),
        format_screen_body(footer),
    )
