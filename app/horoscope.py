from datetime import date, time
from dataclasses import dataclass

from app.astro_engine import AstroForecast, build_astro_forecast

SECTION_TEMPLATES = {
    "ru": {
        "header": "Астрологический прогноз",
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
        "unavailable": "Прогноз временно недоступен — проверьте дату рождения в профиле.",
        "details_header": "📋 Прогноз по сферам",
    },
    "en": {
        "header": "Astrological forecast",
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
        "unavailable": "Forecast is temporarily unavailable — check your birth date in profile.",
        "details_header": "📋 Life areas forecast",
    },
}

SECTION_ICONS = {
    "energy_title": "⚡",
    "work_title": "💼",
    "finance_title": "💰",
    "love_title": "❤️",
    "social_title": "👥",
    "health_title": "🌿",
    "lucky_time_title": "🕐",
    "avoid_title": "⚠️",
    "affirmation_title": "✨",
    "advice_title": "💡",
}

GOAL_FOCUS_KEYS = {
    "love": "love_title",
    "career": "work_title",
    "money": "finance_title",
    "balance": "advice_title",
}

DETAILS_DIVIDER = "──────────────────"

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


@dataclass(frozen=True)
class PersonalizationContext:
    goal: str | None = None
    relationship_status: str | None = None
    mood_score: int | None = None
    gender: str | None = None

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


def _is_focus_section(key: str, goal: str | None) -> bool:
    return bool(goal and GOAL_FOCUS_KEYS.get(goal) == key)


def _format_detail_block(
    labels: dict[str, str],
    key: str,
    text: str,
    *,
    goal: str | None,
    score: int | None = None,
) -> str:
    icon = SECTION_ICONS[key]
    title = labels[key]
    focus = "⭐ " if _is_focus_section(key, goal) else ""
    if score is not None:
        header = f"{focus}{icon} {title} · {score}/10"
    else:
        header = f"{focus}{icon} {title}"
    return f"{header}\n{text}"


def _personalization_banner(locale: str, ctx: PersonalizationContext) -> str:
    parts: list[str] = []
    if ctx.goal and ctx.goal in GOAL_LABELS[locale]:
        parts.append(
            f"фокус: {GOAL_LABELS[locale][ctx.goal]}"
            if locale == "ru"
            else f"focus: {GOAL_LABELS[locale][ctx.goal]}"
        )
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


def _resolve_birth_fields(
    profile,
    birth_date: date | None,
    birth_time: time | None,
    city: str | None,
    timezone_name: str | None,
) -> tuple[date | None, time | None, str | None, str, int | None, float | None, float | None]:
    resolved_birth_date = birth_date
    resolved_birth_time = birth_time
    resolved_city = city
    resolved_timezone = timezone_name or "UTC"
    resolved_lat = None
    resolved_lon = None
    user_id = None
    if profile is not None:
        user_id = getattr(profile, "user_id", None)
        if resolved_birth_date is None and getattr(profile, "birth_date", None):
            resolved_birth_date = profile.birth_date
        if resolved_birth_time is None:
            resolved_birth_time = getattr(profile, "birth_time", None)
        if resolved_city is None:
            resolved_city = getattr(profile, "city", None)
        resolved_lat = getattr(profile, "birth_lat", None)
        resolved_lon = getattr(profile, "birth_lon", None)
        if getattr(profile, "birth_timezone", None):
            resolved_timezone = profile.birth_timezone
        elif timezone_name is None and getattr(profile, "timezone", None):
            resolved_timezone = profile.timezone
    return (
        resolved_birth_date,
        resolved_birth_time,
        resolved_city,
        resolved_timezone,
        user_id,
        resolved_lat,
        resolved_lon,
    )


def _format_forecast(
    forecast: AstroForecast,
    locale: str,
    period: str,
    *,
    goal: str | None,
    personalization: PersonalizationContext | None,
) -> str:
    labels = SECTION_TEMPLATES[locale]
    period_suffix = {
        "ru": {"day": " · сегодня", "week": " · неделя", "month": " · месяц"},
        "en": {"day": " · today", "week": " · week", "month": " · month"},
    }
    header = forecast.summary_lines[0] + period_suffix[locale][period]
    lines = [header, *forecast.summary_lines[1:]]
    if personalization and personalization.has_data():
        banner = _personalization_banner(locale, personalization)
        if banner:
            lines.append(banner)

    detail_blocks = [
        _format_detail_block(
            labels, "energy_title", forecast.energy.text, goal=goal, score=forecast.energy.score
        ),
        _format_detail_block(
            labels, "work_title", forecast.work.text, goal=goal, score=forecast.work.score
        ),
        _format_detail_block(
            labels, "finance_title", forecast.finance.text, goal=goal, score=forecast.finance.score
        ),
        _format_detail_block(
            labels, "love_title", forecast.love.text, goal=goal, score=forecast.love.score
        ),
        _format_detail_block(labels, "social_title", forecast.social.text, goal=goal),
        _format_detail_block(
            labels, "health_title", forecast.health.text, goal=goal, score=forecast.health.score
        ),
        _format_detail_block(labels, "lucky_time_title", forecast.lucky_time, goal=goal),
        _format_detail_block(labels, "avoid_title", forecast.avoid, goal=goal),
        _format_detail_block(labels, "affirmation_title", forecast.affirmation, goal=goal),
        _format_detail_block(labels, "advice_title", forecast.advice, goal=goal),
    ]
    backdrop = "\n".join(lines)
    details = "\n\n".join(detail_blocks)
    return f"{backdrop}\n\n{DETAILS_DIVIDER}\n{labels['details_header']}\n\n{details}"


def generate_home_teaser(
    sign: str,
    locale: str,
    *,
    sign_label: str,
    sign_emoji: str = "",
    for_date: date | None = None,
    personalization: PersonalizationContext | None = None,
    profile=None,
    birth_date: date | None = None,
    birth_time: time | None = None,
    city: str | None = None,
    timezone_name: str | None = None,
) -> str:
    if for_date is None:
        for_date = date.today()

    current_locale = "ru" if locale == "ru" else "en"
    resolved_birth_date, resolved_birth_time, resolved_city, resolved_timezone, user_id, resolved_lat, resolved_lon = _resolve_birth_fields(
        profile,
        birth_date,
        birth_time,
        city,
        timezone_name,
    )
    relationship_status = personalization.relationship_status if personalization else None
    if profile is not None and relationship_status is None:
        relationship_status = getattr(profile, "relationship_status", None)

    forecast = build_astro_forecast(
        birth_date=resolved_birth_date,
        birth_time=resolved_birth_time,
        city=resolved_city,
        timezone_name=resolved_timezone,
        for_date=for_date,
        locale=current_locale,
        period="day",
        sign=sign,
        relationship_status=relationship_status,
        user_id=user_id,
        lat=resolved_lat,
        lon=resolved_lon,
        birth_timezone=getattr(profile, "birth_timezone", None) if profile else None,
    )

    prefix = f"{sign_emoji} " if sign_emoji else ""
    if forecast is None:
        if current_locale == "ru":
            return f"{prefix}{sign_label} · прогноз временно недоступен"
        return f"{prefix}{sign_label} · forecast temporarily unavailable"

    if current_locale == "ru":
        return (
            f"{prefix}{sign_label} · энергия {forecast.energy.score}/10 · "
            f"удачное время: {forecast.lucky_time}"
        )
    return (
        f"{prefix}{sign_label} · energy {forecast.energy.score}/10 · "
        f"lucky time: {forecast.lucky_time}"
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
    ctx_goal = personalization.goal if personalization else goal
    ctx_rel = personalization.relationship_status if personalization else relationship_status

    resolved_birth_date, resolved_birth_time, resolved_city, resolved_timezone, user_id, resolved_lat, resolved_lon = _resolve_birth_fields(
        profile,
        birth_date,
        birth_time,
        city,
        timezone_name,
    )

    forecast = build_astro_forecast(
        birth_date=resolved_birth_date,
        birth_time=resolved_birth_time,
        city=resolved_city,
        timezone_name=resolved_timezone,
        for_date=for_date,
        locale=current_locale,
        period=current_period,
        sign=sign,
        relationship_status=ctx_rel,
        user_id=user_id,
        lat=resolved_lat,
        lon=resolved_lon,
        birth_timezone=getattr(profile, "birth_timezone", None) if profile else None,
    )

    labels = SECTION_TEMPLATES[current_locale]
    if forecast is None:
        return labels["unavailable"]

    return _format_forecast(
        forecast,
        current_locale,
        current_period,
        goal=ctx_goal,
        personalization=personalization,
    )


SHARE_PERIOD_LABELS = {
    "ru": {"day": "сегодня", "week": "неделя", "month": "месяц"},
    "en": {"day": "today", "week": "week", "month": "month"},
}


def _truncate_share_line(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def build_horoscope_share_text(
    *,
    sign: str,
    sign_name: str,
    sign_emoji: str,
    locale: str,
    period: str,
    profile=None,
    personalization: PersonalizationContext | None = None,
    for_date: date | None = None,
) -> str | None:
    current_locale = "ru" if locale == "ru" else "en"
    current_period = period if period in {"day", "week", "month"} else "day"
    ctx_rel = personalization.relationship_status if personalization else None

    resolved_birth_date, resolved_birth_time, resolved_city, resolved_timezone, user_id, resolved_lat, resolved_lon = _resolve_birth_fields(
        profile,
        None,
        None,
        None,
        None,
    )

    forecast = build_astro_forecast(
        birth_date=resolved_birth_date,
        birth_time=resolved_birth_time,
        city=resolved_city,
        timezone_name=resolved_timezone,
        for_date=for_date or date.today(),
        locale=current_locale,
        period=current_period,
        sign=sign,
        relationship_status=ctx_rel,
        user_id=user_id,
        lat=resolved_lat,
        lon=resolved_lon,
        birth_timezone=getattr(profile, "birth_timezone", None) if profile else None,
    )
    if forecast is None:
        return None

    period_label = SHARE_PERIOD_LABELS[current_locale][current_period]
    sign_prefix = f"{sign_emoji} " if sign_emoji else ""
    advice = _truncate_share_line(forecast.advice)

    if current_locale == "ru":
        lines = [
            f"🔮 Мой астрологический прогноз · {period_label}",
            "",
            f"{sign_prefix}{sign_name} · энергия {forecast.energy.score}/10",
            f"💡 {advice}",
            f"🕐 Удачное время: {forecast.lucky_time}",
            "",
            "Персональный гороскоп в AstroPulse 👇",
        ]
    else:
        lines = [
            f"🔮 My astrological forecast · {period_label}",
            "",
            f"{sign_prefix}{sign_name} · energy {forecast.energy.score}/10",
            f"💡 {advice}",
            f"🕐 Lucky time: {forecast.lucky_time}",
            "",
            "Get your personal horoscope in AstroPulse 👇",
        ]
    return "\n".join(lines)


def generate_daily_horoscope(
    sign: str,
    locale: str,
    for_date: date | None = None,
    *,
    personalization: PersonalizationContext | None = None,
    profile=None,
) -> str:
    return generate_horoscope(
        sign=sign,
        locale=locale,
        period="day",
        for_date=for_date,
        personalization=personalization,
        profile=profile,
    )
