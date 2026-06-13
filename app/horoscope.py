from datetime import date, time
from dataclasses import dataclass

from app.astro_engine import AstroForecast, build_astro_forecast
from app.forecast_text import format_forecast_opening, format_score_word
from app.text_format import b, h, labeled_block, p, section_block

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

PERIOD_HEADERS = {
    "ru": {
        "day": "🌙 Прогноз на сегодня",
        "week": "🌙 Прогноз на неделю",
        "month": "🌙 Прогноз на месяц",
    },
    "en": {
        "day": "🌙 Forecast for today",
        "week": "🌙 Forecast for the week",
        "month": "🌙 Forecast for the month",
    },
}

PLAIN_PERIOD_HEADERS = {
    "ru": {
        "day": "💬 Прогноз на сегодня · простым языком",
        "week": "💬 Прогноз на неделю · простым языком",
        "month": "💬 Прогноз на месяц · простым языком",
    },
    "en": {
        "day": "💬 Forecast for today · plain language",
        "week": "💬 Forecast for the week · plain language",
        "month": "💬 Forecast for the month · plain language",
    },
}

DOMAIN_SECTION_KEYS = {
    "energy": "energy_title",
    "work": "work_title",
    "finance": "finance_title",
    "love": "love_title",
    "social": "social_title",
    "health": "health_title",
}

GOAL_DOMAIN_ORDER = {
    "love": ["energy", "love", "social"],
    "career": ["energy", "work", "finance"],
    "money": ["energy", "finance", "work"],
}

DEFAULT_DOMAIN_ORDER = ["energy", "love", "work"]

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


def resolve_horoscope_style(profile, *, default: str = "terms") -> str:
    if profile is None:
        return default
    style = getattr(profile, "horoscope_style", None) or getattr(profile, "natal_style", None) or default
    return "plain" if style == "plain" else "terms"


def _is_focus_section(key: str, goal: str | None) -> bool:
    return bool(goal and GOAL_FOCUS_KEYS.get(goal) == key)


def _collapse_prose(text: str) -> str:
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def _domains_for_goal(goal: str | None) -> list[str]:
    if goal and goal in GOAL_DOMAIN_ORDER:
        return GOAL_DOMAIN_ORDER[goal]
    return DEFAULT_DOMAIN_ORDER


def _summary_accent(summary_lines: list[str]) -> str | None:
    for line in summary_lines:
        if line.startswith("ℹ"):
            continue
        return line
    return None


def _summary_footnotes(summary_lines: list[str]) -> list[str]:
    return [line for line in summary_lines if line.startswith("ℹ")]


def _format_domain_block(
    labels: dict[str, str],
    domain: str,
    text: str,
    *,
    goal: str | None,
    score: int | None,
    locale: str,
) -> str:
    title_key = DOMAIN_SECTION_KEYS[domain]
    icon = SECTION_ICONS[title_key]
    title = labels[title_key]
    focus = "⭐ " if _is_focus_section(title_key, goal) else ""
    prose = _collapse_prose(text)
    if score is not None and domain == "energy":
        tone = format_score_word(score, locale)
        if locale == "ru":
            header = f"{focus}{icon} {title} · {tone} энергия"
        else:
            header = f"{focus}{icon} {title} · {tone} energy"
    else:
        header = f"{focus}{icon} {title}"
    return section_block(header, prose)


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


def _period_header(locale: str, period: str, *, style: str = "terms") -> str:
    if style == "plain":
        return PLAIN_PERIOD_HEADERS[locale][period]
    return PERIOD_HEADERS[locale][period]


def _format_forecast(
    forecast: AstroForecast,
    locale: str,
    period: str,
    *,
    goal: str | None,
    personalization: PersonalizationContext | None,
    style: str = "terms",
) -> str:
    labels = SECTION_TEMPLATES[locale]
    parts = [b(_period_header(locale, period, style=style))]

    opening = format_forecast_opening(
        locale,
        period,
        forecast.moon_sign,
        accent_line=_summary_accent(forecast.summary_lines),
        period_start=forecast.period_start,
        period_end=forecast.period_end,
        style=style,
    )
    parts.append(opening)

    if personalization and personalization.has_data():
        banner = _personalization_banner(locale, personalization)
        if banner:
            parts.append(banner)

    section_map = {
        "energy": forecast.energy,
        "work": forecast.work,
        "finance": forecast.finance,
        "love": forecast.love,
        "social": forecast.social,
        "health": forecast.health,
    }
    for domain in _domains_for_goal(goal):
        section = section_map[domain]
        parts.append(
            _format_domain_block(
                labels,
                domain,
                section.text,
                goal=goal,
                score=section.score,
                locale=locale,
            )
        )

    tip = _collapse_prose(forecast.advice)
    parts.append(labeled_block(f"💡 {labels['advice_title']}", tip))
    parts.append(labeled_block(f"⚠️ {labels['avoid_title']}", _collapse_prose(forecast.avoid)))
    parts.append(p(b(f"🕐 {labels['lucky_time_title']}"), h(forecast.lucky_time)))

    footnotes = _summary_footnotes(forecast.summary_lines)
    if footnotes:
        parts.append("\n".join(footnotes))

    return "\n\n".join(parts)


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

    resolved_style = resolve_horoscope_style(profile)

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
        style=resolved_style,
    )

    prefix = f"{sign_emoji} " if sign_emoji else ""
    if forecast is None:
        if current_locale == "ru":
            return f"{prefix}{sign_label} · прогноз временно недоступен"
        return f"{prefix}{sign_label} · forecast temporarily unavailable"

    energy_tone = format_score_word(forecast.energy.score, current_locale)
    if current_locale == "ru":
        return (
            f"{prefix}{sign_label} · {energy_tone} энергия · "
            f"удачное время: {forecast.lucky_time}"
        )
    return (
        f"{prefix}{sign_label} · {energy_tone} energy · "
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
    style: str | None = None,
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
    resolved_style = style or resolve_horoscope_style(profile)

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
        style=resolved_style,
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
        style=resolved_style,
    )


SHARE_PERIOD_LABELS = {
    "ru": {"day": "сегодня", "week": "неделя", "month": "месяц"},
    "en": {"day": "today", "week": "week", "month": "month"},
}


@dataclass(frozen=True)
class ShareForecastContext:
    sign_name: str
    sign_emoji: str
    period_label: str
    energy_score: int
    energy_text: str
    advice: str
    lucky_time: str
    affirmation: str
    locale: str


def _truncate_share_line(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def build_share_forecast_context(
    *,
    sign: str,
    sign_name: str,
    sign_emoji: str,
    locale: str,
    period: str,
    profile=None,
    personalization: PersonalizationContext | None = None,
    for_date: date | None = None,
    style: str | None = None,
) -> ShareForecastContext | None:
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
    resolved_style = style or resolve_horoscope_style(profile)

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
        style=resolved_style,
    )
    if forecast is None:
        return None

    return ShareForecastContext(
        sign_name=sign_name,
        sign_emoji=sign_emoji,
        period_label=SHARE_PERIOD_LABELS[current_locale][current_period],
        energy_score=forecast.energy.score,
        energy_text=forecast.energy.text,
        advice=forecast.advice,
        lucky_time=forecast.lucky_time,
        affirmation=forecast.affirmation,
        locale=current_locale,
    )


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
    context = build_share_forecast_context(
        sign=sign,
        sign_name=sign_name,
        sign_emoji=sign_emoji,
        locale=locale,
        period=period,
        profile=profile,
        personalization=personalization,
        for_date=for_date,
    )
    if context is None:
        return None

    sign_prefix = f"{context.sign_emoji} " if context.sign_emoji else ""
    advice = _truncate_share_line(context.advice)

    energy_tone = format_score_word(context.energy_score, context.locale)
    if context.locale == "ru":
        lines = [
            f"🔮 Мой астрологический прогноз · {context.period_label}",
            "",
            f"{sign_prefix}{context.sign_name} · {energy_tone} энергия",
            f"💡 {advice}",
            f"🕐 Удачное время: {context.lucky_time}",
            "",
            "Персональный гороскоп в AstroPulse 👇",
        ]
    else:
        lines = [
            f"🔮 My astrological forecast · {context.period_label}",
            "",
            f"{sign_prefix}{context.sign_name} · {energy_tone} energy",
            f"💡 {advice}",
            f"🕐 Lucky time: {context.lucky_time}",
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
