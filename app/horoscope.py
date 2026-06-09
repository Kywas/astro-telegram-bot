from datetime import date, time, timedelta
from dataclasses import dataclass
from random import Random

from app.astro_engine import build_astro_horoscope_context

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

GOAL_LABELS = {
    "ru": {
        "love": "любовь",
        "career": "карьера",
        "money": "деньги",
        "balance": "баланс",
    },
    "en": {
        "love": "love",
        "career": "career",
        "money": "money",
        "balance": "balance",
    },
}

RELATIONSHIP_LABELS = {
    "ru": {
        "single": "свободен(а)",
        "relationship": "в отношениях",
    },
    "en": {
        "single": "single",
        "relationship": "in a relationship",
    },
}

MOOD_ENERGY_LINES = {
    "ru": {
        "low": [
            "Энергия ниже обычного — лучше не распыляться и беречь силы.",
            "День лучше прожить в спокойном темпе, без лишнего давления на себя.",
        ],
        "high": [
            "Сильный подъём сил — хороший день для важных шагов и смелых решений.",
            "Энергия на пике: используй её для одного значимого дела.",
        ],
    },
    "en": {
        "low": [
            "Energy is lower than usual — avoid spreading yourself too thin.",
            "A calm pace without extra pressure on yourself will work best today.",
        ],
        "high": [
            "Strong energy rise — a good day for meaningful steps and bold choices.",
            "Peak energy: channel it into one significant task.",
        ],
    },
}

MOOD_HEALTH_LINES = {
    "ru": {
        "low": [
            "Тело просит заботы: сон, вода и короткие паузы важнее скорости.",
            "Снизь нагрузку и добавь восстановление — это ускорит возвращение сил.",
        ],
        "high": [
            "Хорошее самочувствие поддержит активный день — не забывай про отдых.",
            "Тонус высокий, но умеренность в нагрузке сохранит баланс.",
        ],
    },
    "en": {
        "low": [
            "Your body asks for care: sleep, water, and short breaks beat pushing harder.",
            "Reduce load and add recovery — it will restore your energy faster.",
        ],
        "high": [
            "Good well-being supports an active day — still leave room for rest.",
            "High tone is helpful, but moderation keeps your balance.",
        ],
    },
}

GOAL_FOCUS_LINES = {
    "ru": {
        "love": [
            "Сегодня сердце и близость важнее формальных задач — инвестируй внимание в людей.",
            "Эмоциональная открытость может принести больше, чем суета в делах.",
        ],
        "career": [
            "Профессиональный фокус сегодня особенно уместен — двигай ключевой проект.",
            "Карьерный импульс сильнее обычного: выбирай задачи с долгосрочным эффектом.",
        ],
        "money": [
            "Финансовая ясность сегодня важнее спешки — планируй и считай спокойно.",
            "День подходит для аккуратных денежных решений и пересмотра приоритетов.",
        ],
        "balance": [
            "Лучший результат даст равномерный ритм между делами, отдыхом и общением.",
            "Сегодня выигрывает баланс — не перекачивай одну сферу в ущерб другим.",
        ],
    },
    "en": {
        "love": [
            "Heart and closeness matter more than formal tasks today — invest attention in people.",
            "Emotional openness may bring more than rushing through chores.",
        ],
        "career": [
            "Professional focus is especially useful today — move your key project forward.",
            "Career momentum is stronger than usual: choose tasks with long-term impact.",
        ],
        "money": [
            "Financial clarity beats rush today — plan and calculate calmly.",
            "A good day for careful money decisions and priority review.",
        ],
        "balance": [
            "An even rhythm across work, rest, and connection brings the best result.",
            "Balance wins today — do not overload one area at the expense of others.",
        ],
    },
}

GOAL_ADVICE_LINES = {
    "ru": {
        "love": "Сделай один искренний шаг к близости — разговор, сообщение или внимание.",
        "career": "Выдели 60–90 минут на задачу, которая реально двигает карьеру.",
        "money": "Проверь один финансовый пункт: подписка, бюджет или отложенный платёж.",
        "balance": "Распредели день на три блока: дело, отдых, общение — без перегибов.",
    },
    "en": {
        "love": "Take one sincere step toward closeness — a talk, message, or gesture of care.",
        "career": "Block 60–90 minutes for the task that truly moves your career.",
        "money": "Review one financial item: subscription, budget, or pending payment.",
        "balance": "Split the day into three blocks: work, rest, connection — without extremes.",
    },
}


@dataclass(frozen=True)
class PersonalizationContext:
    goal: str | None = None
    relationship_status: str | None = None
    mood_score: int | None = None
    gender: str | None = None

    def seed_suffix(self) -> str:
        return (
            f"{self.goal or '-'}|{self.relationship_status or '-'}"
            f"|{self.mood_score if self.mood_score is not None else '-'}"
            f"|{self.gender or '-'}"
        )

    def has_data(self) -> bool:
        return bool(self.goal or self.relationship_status or self.mood_score is not None)


def personalization_from_profile(profile) -> PersonalizationContext | None:
    if profile is None:
        return None
    ctx = PersonalizationContext(
        goal=profile.goal,
        relationship_status=profile.relationship_status,
        mood_score=profile.mood_score,
        gender=profile.gender,
    )
    return ctx if ctx.has_data() else None


def _period_seed_key(period: str, for_date: date) -> str:
    if period == "week":
        week_start = for_date - timedelta(days=for_date.weekday())
        return week_start.isoformat()
    if period == "month":
        month_start = for_date.replace(day=1)
        return month_start.isoformat()
    return for_date.isoformat()


def _day_random(
    sign: str,
    locale: str,
    for_date: date,
    personalization: PersonalizationContext | None = None,
) -> Random:
    current_locale = "ru" if locale == "ru" else "en"
    suffix = personalization.seed_suffix() if personalization else "-"
    seed = f"{sign}-{for_date.isoformat()}-{current_locale}-day-{suffix}"
    return Random(seed)


def _mood_bucket(mood_score: int | None) -> str | None:
    if mood_score is None:
        return None
    if mood_score <= 3:
        return "low"
    if mood_score >= 8:
        return "high"
    return None


def _section_score(rnd: Random, mood_score: int | None, *, boost: int = 0) -> int:
    if mood_score is None:
        low, high = 5, 10
    elif mood_score <= 3:
        low, high = 3, 6
    elif mood_score <= 6:
        low, high = 4, 8
    else:
        low, high = 6, 10
    return max(1, min(10, rnd.randint(low, high) + boost))


def _goal_boosts(goal: str | None) -> dict[str, int]:
    boosts = {"energy": 0, "work": 0, "finance": 0, "love": 0, "health": 0}
    if goal == "love":
        boosts["love"] = 2
    elif goal == "career":
        boosts["work"] = 2
        boosts["energy"] = 1
    elif goal == "money":
        boosts["finance"] = 2
    elif goal == "balance":
        boosts["energy"] = 1
        boosts["health"] = 1
    return boosts


def _pick_love_line(
    rnd: Random,
    locale: str,
    relationship_status: str | None,
) -> str:
    lines = LOVE_LINES[locale]
    if relationship_status == "single":
        return rnd.choice([lines[3], *lines[:3]])
    if relationship_status == "relationship":
        return rnd.choice(lines[:3])
    return rnd.choice(lines)


def _pick_energy_line(
    rnd: Random,
    locale: str,
    mood_score: int | None,
    goal: str | None,
) -> str:
    mood_bucket = _mood_bucket(mood_score)
    if mood_bucket and rnd.random() < 0.65:
        return rnd.choice(MOOD_ENERGY_LINES[locale][mood_bucket])
    if goal and goal in GOAL_FOCUS_LINES[locale] and rnd.random() < 0.5:
        return rnd.choice(GOAL_FOCUS_LINES[locale][goal])
    return rnd.choice(ENERGY_LINES[locale])


def _pick_health_line(rnd: Random, locale: str, mood_score: int | None) -> str:
    mood_bucket = _mood_bucket(mood_score)
    if mood_bucket and rnd.random() < 0.65:
        return rnd.choice(MOOD_HEALTH_LINES[locale][mood_bucket])
    return rnd.choice(HEALTH_LINES[locale])


def _pick_advice_line(rnd: Random, locale: str, goal: str | None) -> str:
    if goal and goal in GOAL_ADVICE_LINES[locale] and rnd.random() < 0.7:
        return GOAL_ADVICE_LINES[locale][goal]
    return rnd.choice(ADVICE_LINES[locale])


def _section_title(labels: dict[str, str], key: str, goal: str | None) -> str:
    title = labels[key]
    focus_map = {
        "love": "love_title",
        "career": "work_title",
        "money": "finance_title",
        "balance": "advice_title",
    }
    if goal and focus_map.get(goal) == key:
        return f"⭐ {title}"
    return title


def _personalization_banner(locale: str, ctx: PersonalizationContext) -> str:
    parts: list[str] = []
    if ctx.goal and ctx.goal in GOAL_LABELS[locale]:
        parts.append(f"фокус: {GOAL_LABELS[locale][ctx.goal]}" if locale == "ru" else f"focus: {GOAL_LABELS[locale][ctx.goal]}")
    if ctx.mood_score is not None:
        parts.append(
            f"настроение: {ctx.mood_score}/10"
            if locale == "ru"
            else f"mood: {ctx.mood_score}/10"
        )
    if ctx.relationship_status and ctx.relationship_status in RELATIONSHIP_LABELS[locale]:
        parts.append(RELATIONSHIP_LABELS[locale][ctx.relationship_status])
    if not parts:
        return ""
    prefix = "🎯 Персонально" if locale == "ru" else "🎯 Personalized"
    return f"{prefix} · " + " · ".join(parts)


def generate_home_teaser(
    sign: str,
    locale: str,
    *,
    sign_label: str,
    sign_emoji: str = "",
    for_date: date | None = None,
    personalization: PersonalizationContext | None = None,
) -> str:
    if for_date is None:
        for_date = date.today()

    current_locale = "ru" if locale == "ru" else "en"
    rnd = _day_random(sign, locale, for_date, personalization)
    boosts = _goal_boosts(personalization.goal if personalization else None)
    mood_score = personalization.mood_score if personalization else None
    energy_score = _section_score(rnd, mood_score, boost=boosts["energy"])
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
    *,
    personalization: PersonalizationContext | None = None,
    goal: str | None = None,
    relationship_status: str | None = None,
    mood_score: int | None = None,
    gender: str | None = None,
    profile=None,
    birth_date: date | None = None,
    birth_time: time | None = None,
    city: str | None = None,
    timezone_name: str | None = None,
) -> str:
    if personalization is None and any(v is not None for v in (goal, relationship_status, mood_score, gender)):
        personalization = PersonalizationContext(
            goal=goal,
            relationship_status=relationship_status,
            mood_score=mood_score,
            gender=gender,
        )
    if for_date is None:
        for_date = date.today()

    current_locale = "ru" if locale == "ru" else "en"
    current_period = period if period in {"day", "week", "month"} else "day"

    resolved_birth_date = birth_date
    resolved_birth_time = birth_time
    resolved_city = city
    resolved_timezone = timezone_name or "UTC"
    if profile is not None:
        if resolved_birth_date is None and getattr(profile, "birth_date", None):
            resolved_birth_date = profile.birth_date
        if resolved_birth_time is None:
            resolved_birth_time = getattr(profile, "birth_time", None)
        if resolved_city is None:
            resolved_city = getattr(profile, "city", None)
        if timezone_name is None and getattr(profile, "timezone", None):
            resolved_timezone = profile.timezone

    astro_ctx = None
    user_id = getattr(profile, "user_id", None) if profile is not None else None
    if resolved_birth_date is not None:
        astro_ctx = build_astro_horoscope_context(
            birth_date=resolved_birth_date,
            birth_time=resolved_birth_time,
            city=resolved_city,
            timezone_name=resolved_timezone,
            for_date=for_date,
            locale=current_locale,
            user_id=user_id,
        )

    seed_key = _period_seed_key(current_period, for_date)
    suffix = personalization.seed_suffix() if personalization else "-"
    seed = f"{sign}-{seed_key}-{current_locale}-{current_period}-{suffix}"
    rnd = Random(seed)
    labels = SECTION_TEMPLATES[current_locale]
    period_text = PERIOD_LABELS[current_locale][current_period]

    ctx_goal = personalization.goal if personalization else None
    ctx_rel = personalization.relationship_status if personalization else None
    ctx_mood = personalization.mood_score if personalization else None
    boosts = _goal_boosts(ctx_goal)

    energy = _pick_energy_line(rnd, current_locale, ctx_mood, ctx_goal)
    work = rnd.choice(WORK_LINES[current_locale])
    finance = rnd.choice(FINANCE_LINES[current_locale])
    love = _pick_love_line(rnd, current_locale, ctx_rel)
    social = rnd.choice(SOCIAL_LINES[current_locale])
    health = _pick_health_line(rnd, current_locale, ctx_mood)
    lucky_time = rnd.choice(LUCKY_TIME_LINES[current_locale])
    avoid = rnd.choice(AVOID_LINES[current_locale])
    affirmation = rnd.choice(AFFIRMATION_LINES[current_locale])
    advice = _pick_advice_line(rnd, current_locale, ctx_goal)

    energy_score = _section_score(rnd, ctx_mood, boost=boosts["energy"])
    work_score = _section_score(rnd, ctx_mood, boost=boosts["work"])
    finance_score = _section_score(rnd, ctx_mood, boost=boosts["finance"])
    love_score = _section_score(rnd, ctx_mood, boost=boosts["love"])
    health_score = _section_score(rnd, ctx_mood, boost=boosts["health"])

    if astro_ctx:
        adjustments = astro_ctx.score_adjustments
        energy_score = max(1, min(10, energy_score + adjustments.get("energy", 0)))
        work_score = max(1, min(10, work_score + adjustments.get("work", 0)))
        finance_score = max(1, min(10, finance_score + adjustments.get("finance", 0)))
        love_score = max(1, min(10, love_score + adjustments.get("love", 0)))
        health_score = max(1, min(10, health_score + adjustments.get("health", 0)))

    lines = [f"✨ {labels['header']} ({period_text})"]
    if astro_ctx:
        lines.extend(astro_ctx.summary_lines)
    if personalization and personalization.has_data():
        banner = _personalization_banner(current_locale, personalization)
        if banner:
            lines.append(banner)
    lines.extend(
        [
            "",
            f"• {_section_title(labels, 'energy_title', ctx_goal)} ({energy_score}/10): {energy}",
            f"• {_section_title(labels, 'work_title', ctx_goal)} ({work_score}/10): {work}",
            f"• {_section_title(labels, 'finance_title', ctx_goal)} ({finance_score}/10): {finance}",
            f"• {_section_title(labels, 'love_title', ctx_goal)} ({love_score}/10): {love}",
            f"• {labels['social_title']}: {social}",
            f"• {labels['health_title']} ({health_score}/10): {health}",
            f"• {labels['lucky_time_title']}: {lucky_time}",
            f"• {labels['avoid_title']}: {avoid}",
            f"• {labels['affirmation_title']}: {affirmation}",
            f"• {_section_title(labels, 'advice_title', ctx_goal)}: {advice}",
        ]
    )
    return "\n".join(lines)


def generate_daily_horoscope(
    sign: str,
    locale: str,
    for_date: date | None = None,
    *,
    personalization: PersonalizationContext | None = None,
) -> str:
    return generate_horoscope(
        sign=sign,
        locale=locale,
        period="day",
        for_date=for_date,
        personalization=personalization,
    )
