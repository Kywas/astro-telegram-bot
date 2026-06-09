from datetime import date, timedelta
from random import Random

SECTION_TEMPLATES = {
    "ru": {
        "header": "Расширенный прогноз на сегодня",
        "energy_title": "Общая энергия",
        "work_title": "Работа и деньги",
        "finance_title": "Финансы",
        "love_title": "Отношения",
        "social_title": "Социальная сфера",
        "health_title": "Самочувствие",
        "lucky_time_title": "Удачное время",
        "avoid_title": "Чего лучше избегать",
        "affirmation_title": "Аффирмация дня",
        "advice_title": "Совет дня",
    },
    "en": {
        "header": "Extended daily forecast",
        "energy_title": "General energy",
        "work_title": "Work and money",
        "finance_title": "Finances",
        "love_title": "Relationships",
        "social_title": "Social sphere",
        "health_title": "Well-being",
        "lucky_time_title": "Lucky time",
        "avoid_title": "What to avoid",
        "affirmation_title": "Affirmation",
        "advice_title": "Advice of the day",
    },
}

ENERGY_LINES = {
    "ru": [
        "День подходит для уверенных шагов, если держать фокус на главном.",
        "Энергия нестабильна: лучше чередовать активность и короткий отдых.",
        "Хорошее время, чтобы закрыть старые задачи и освободить голову.",
        "Повышается чувствительность к чужому настроению - не бери все на себя.",
    ],
    "en": [
        "The day favors confident action if you keep your focus on key priorities.",
        "Energy may fluctuate, so balance active periods with short breaks.",
        "A good time to finish old tasks and clear mental space.",
        "You may feel others' moods more strongly today - do not take everything personally.",
    ],
}

WORK_LINES = {
    "ru": [
        "В делах важны детали: перепроверь договоренности и сроки.",
        "Финансовые решения лучше принимать без спешки и импульса.",
        "Командная работа даст лучший результат, чем попытка сделать все в одиночку.",
        "Есть шанс на полезный контакт, который ускорит рабочий процесс.",
    ],
    "en": [
        "Details matter in business today, so double-check agreements and timelines.",
        "Handle money decisions calmly and avoid impulsive moves.",
        "Collaboration will likely bring a better outcome than doing everything alone.",
        "A useful connection may appear and speed up your workflow.",
    ],
}

FINANCE_LINES = {
    "ru": [
        "Подходящий день для аккуратного планирования расходов и приоритетов.",
        "Избегай эмоциональных покупок: полезнее сохранить резерв.",
        "Небольшой пересмотр бюджета даст больше уверенности в ближайшие дни.",
        "Лучше ставить на предсказуемость, чем на рискованные решения.",
    ],
    "en": [
        "A good day for careful spending plans and clearer priorities.",
        "Avoid emotional purchases; keeping a reserve will be wiser.",
        "A small budget review can increase confidence for the coming days.",
        "Choose predictability over risky money decisions.",
    ],
}

LOVE_LINES = {
    "ru": [
        "Открытый разговор поможет снять напряжение и вернуть доверие.",
        "Лучше говорить мягко и по сути, без лишних претензий.",
        "Небольшой знак внимания сегодня может сильно улучшить атмосферу.",
        "Если ты свободен, случайное общение может перерасти в интересный диалог.",
    ],
    "en": [
        "An honest conversation can ease tension and rebuild trust.",
        "Speak gently and clearly, avoiding unnecessary criticism.",
        "A small gesture today can noticeably improve the atmosphere.",
        "If you are single, a casual chat may grow into a meaningful connection.",
    ],
}

SOCIAL_LINES = {
    "ru": [
        "Сегодня полезно поддерживать контакт с теми, кто разделяет твои цели.",
        "Короткая встреча или звонок может принести ценную идею.",
        "Лучше говорить прямо и доброжелательно - это укрепит доверие.",
        "Старый знакомый может неожиданно напомнить о себе с полезным предложением.",
    ],
    "en": [
        "Stay connected with people who share your goals today.",
        "A short call or meeting may bring a valuable idea.",
        "Direct and friendly communication will strengthen trust.",
        "An old contact may return with a useful opportunity.",
    ],
}

HEALTH_LINES = {
    "ru": [
        "Старайся держать стабильный режим сна, это даст больше ресурса.",
        "Легкая физическая активность снимет внутреннее напряжение.",
        "Пей больше воды и снизь информационную перегрузку вечером.",
        "Если чувствуешь усталость, сократи темп и оставь время на восстановление.",
    ],
    "en": [
        "Try to keep a stable sleep routine to preserve your energy.",
        "Light physical activity will help release internal tension.",
        "Drink more water and reduce information overload in the evening.",
        "If you feel tired, slow down and leave space for recovery.",
    ],
}

LUCKY_TIME_LINES = {
    "ru": [
        "08:00-10:00 и 17:00-19:00",
        "09:30-11:30 и 15:00-16:30",
        "11:00-13:00 и 19:00-21:00",
        "07:30-09:00 и 14:00-16:00",
    ],
    "en": [
        "08:00-10:00 and 17:00-19:00",
        "09:30-11:30 and 15:00-16:30",
        "11:00-13:00 and 19:00-21:00",
        "07:30-09:00 and 14:00-16:00",
    ],
}

AVOID_LINES = {
    "ru": [
        "Поспешных выводов и резких ответов в переписке.",
        "Перегруза задачами без четкого приоритета.",
        "Финансовых решений под влиянием эмоций.",
        "Попытки контролировать то, что сейчас вне твоей зоны влияния.",
    ],
    "en": [
        "Hasty conclusions and sharp replies in chats.",
        "Task overload without a clear priority order.",
        "Money decisions made under emotional pressure.",
        "Trying to control things outside your current influence.",
    ],
}

AFFIRMATION_LINES = {
    "ru": [
        "Я действую спокойно и уверенно, шаг за шагом усиливая свой результат.",
        "Я выбираю ясность, дисциплину и уважение к своим границам.",
        "Я замечаю возможности и использую их в нужный момент.",
        "Я создаю устойчивый прогресс через небольшие, но точные действия.",
    ],
    "en": [
        "I act calmly and confidently, improving my results step by step.",
        "I choose clarity, discipline, and respect for my boundaries.",
        "I notice opportunities and use them at the right moment.",
        "I create steady progress through small but precise actions.",
    ],
}

ADVICE_LINES = {
    "ru": [
        "Выбери один главный приоритет и доведи его до конца.",
        "Не сравнивай свой темп с другими - держись своего маршрута.",
        "Сначала факты, потом эмоции: это поможет принять верное решение.",
        "Сделай маленький шаг сегодня - он запустит большие изменения завтра.",
    ],
    "en": [
        "Pick one top priority and bring it to completion.",
        "Do not compare your pace to others - stay on your own path.",
        "Facts first, emotions second - this will help you make a better decision.",
        "Take one small step today, and it can trigger bigger changes tomorrow.",
    ],
}


PERIOD_LABELS = {
    "ru": {
        "day": "сегодня",
        "week": "эту неделю",
        "month": "этот месяц",
    },
    "en": {
        "day": "today",
        "week": "this week",
        "month": "this month",
    },
}


def _period_seed_key(period: str, for_date: date) -> str:
    if period == "week":
        week_start = for_date - timedelta(days=for_date.weekday())
        return week_start.isoformat()
    if period == "month":
        month_start = for_date.replace(day=1)
        return month_start.isoformat()
    return for_date.isoformat()


def _score(rnd: Random, low: int = 5, high: int = 10) -> int:
    return rnd.randint(low, high)


def _day_random(sign: str, locale: str, for_date: date) -> Random:
    current_locale = "ru" if locale == "ru" else "en"
    seed = f"{sign}-{for_date.isoformat()}-{current_locale}-day"
    return Random(seed)


def generate_home_teaser(
    sign: str,
    locale: str,
    *,
    sign_label: str,
    sign_emoji: str = "",
    for_date: date | None = None,
) -> str:
    if for_date is None:
        for_date = date.today()

    current_locale = "ru" if locale == "ru" else "en"
    rnd = _day_random(sign, locale, for_date)
    energy_score = _score(rnd)
    lucky_time = rnd.choice(LUCKY_TIME_LINES[current_locale])
    prefix = f"{sign_emoji} " if sign_emoji else ""

    if current_locale == "ru":
        return (
            f"{prefix}{sign_label} · энергия {energy_score}/10 · "
            f"удачное время: {lucky_time}"
        )
    return (
        f"{prefix}{sign_label} · energy {energy_score}/10 · "
        f"lucky time: {lucky_time}"
    )


def generate_horoscope(
    sign: str,
    locale: str,
    period: str = "day",
    for_date: date | None = None,
) -> str:
    if for_date is None:
        for_date = date.today()

    current_locale = "ru" if locale == "ru" else "en"
    current_period = period if period in {"day", "week", "month"} else "day"
    seed_key = _period_seed_key(current_period, for_date)
    seed = f"{sign}-{seed_key}-{current_locale}-{current_period}"
    rnd = Random(seed)
    labels = SECTION_TEMPLATES[current_locale]
    period_text = PERIOD_LABELS[current_locale][current_period]

    energy = rnd.choice(ENERGY_LINES[current_locale])
    work = rnd.choice(WORK_LINES[current_locale])
    finance = rnd.choice(FINANCE_LINES[current_locale])
    love = rnd.choice(LOVE_LINES[current_locale])
    social = rnd.choice(SOCIAL_LINES[current_locale])
    health = rnd.choice(HEALTH_LINES[current_locale])
    lucky_time = rnd.choice(LUCKY_TIME_LINES[current_locale])
    avoid = rnd.choice(AVOID_LINES[current_locale])
    affirmation = rnd.choice(AFFIRMATION_LINES[current_locale])
    advice = rnd.choice(ADVICE_LINES[current_locale])

    energy_score = _score(rnd)
    work_score = _score(rnd)
    finance_score = _score(rnd)
    love_score = _score(rnd)
    health_score = _score(rnd)

    return (
        f"✨ {labels['header']} ({period_text})\n\n"
        f"• {labels['energy_title']} ({energy_score}/10): {energy}\n"
        f"• {labels['work_title']} ({work_score}/10): {work}\n"
        f"• {labels['finance_title']} ({finance_score}/10): {finance}\n"
        f"• {labels['love_title']} ({love_score}/10): {love}\n"
        f"• {labels['social_title']}: {social}\n"
        f"• {labels['health_title']} ({health_score}/10): {health}\n"
        f"• {labels['lucky_time_title']}: {lucky_time}\n"
        f"• {labels['avoid_title']}: {avoid}\n"
        f"• {labels['affirmation_title']}: {affirmation}\n"
        f"• {labels['advice_title']}: {advice}"
    )


def generate_daily_horoscope(sign: str, locale: str, for_date: date | None = None) -> str:
    return generate_horoscope(sign=sign, locale=locale, period="day", for_date=for_date)
