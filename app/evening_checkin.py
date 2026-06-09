EVENING_SUMMARY = {
    "ru": {
        "low": [
            "Сегодня было непросто — это нормально. Побудь с собой без давления.",
            "День забрал силы. Завтра можно начать с маленького, спокойного шага.",
            "Ты уже сделал(а) достаточно. Сейчас важнее отдых и мягкость к себе.",
        ],
        "mid": [
            "День прошёл ровно. Завтра будет проще, если сегодня не перегружать себя.",
            "Нейтральный день — хороший момент подвести итог и отпустить лишнее.",
            "Ты держишь баланс. Сохрани этот темп и завтра продолжай в своём ритме.",
        ],
        "high": [
            "Отличный день! Зафиксируй, что сработало — это пригодится завтра.",
            "Энергия на подъёме. Используй этот импульс для одного важного дела.",
            "Ты в хорошем потоке. Поблагодари себя за то, как прошёл(а) этот день.",
        ],
    },
    "en": {
        "low": [
            "Today was tough, and that is okay. Give yourself space without pressure.",
            "The day took energy. Tomorrow can start with one small, calm step.",
            "You did enough. Rest and self-kindness matter most right now.",
        ],
        "mid": [
            "A steady day. Tomorrow gets easier if you avoid overloading tonight.",
            "A neutral day is a good moment to summarize and release what is extra.",
            "You are keeping balance. Hold this pace and continue in your rhythm tomorrow.",
        ],
        "high": [
            "Great day! Note what worked — it will help tomorrow.",
            "Energy is up. Use this momentum for one meaningful action.",
            "You are in a good flow. Appreciate yourself for how you handled today.",
        ],
    },
}

STREAK_MESSAGES = {
    "ru": {
        1: "Серия началась — отличное начало 🌱",
        3: "3 дня подряд — ритм уже формируется ✨",
        7: "🔥 7 дней подряд! Ты строишь полезную привычку.",
        "default": "Серия: {streak} дн. подряд 🌙",
    },
    "en": {
        1: "Streak started — great beginning 🌱",
        3: "3 days in a row — rhythm is forming ✨",
        7: "🔥 7 days in a row! You are building a useful habit.",
        "default": "Streak: {streak} days in a row 🌙",
    },
}


def mood_bucket(score: int) -> str:
    if score <= 3:
        return "low"
    if score <= 6:
        return "mid"
    return "high"


def pick_evening_summary(locale: str, score: int) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    bucket = mood_bucket(score)
    lines = EVENING_SUMMARY[current_locale][bucket]
    return lines[score % len(lines)]


def format_streak_message(locale: str, streak: int) -> str:
    current_locale = "ru" if locale == "ru" else "en"
    messages = STREAK_MESSAGES[current_locale]
    if streak in messages:
        return messages[streak]
    return messages["default"].format(streak=streak)


def build_evening_checkin_prompt(locale: str) -> str:
    if locale == "ru":
        return (
            "🌆 Вечерний чек-ин\n\n"
            "Как прошёл день? Оцени настроение от 1 до 10 — "
            "это поможет точнее настроить прогнозы."
        )
    return (
        "🌆 Evening check-in\n\n"
        "How was your day? Rate your mood from 1 to 10 — "
        "it helps personalize your forecasts."
    )


def build_evening_response(locale: str, score: int, streak: int) -> str:
    summary = pick_evening_summary(locale, score)
    streak_line = format_streak_message(locale, streak)
    if locale == "ru":
        return f"🌙 Спасибо! Настроение: {score}/10\n\n{summary}\n\n{streak_line}"
    return f"🌙 Thanks! Mood: {score}/10\n\n{summary}\n\n{streak_line}"
