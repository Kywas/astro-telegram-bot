"""Weekly engagement posts — Monday & Friday 11:00 local time, themed blocks + inline buttons."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from app.jyotish_text import _lang
from app.text_format import b, p
from app.timezones import user_local_date_key, user_local_hhmm, user_local_weekday
from app.ui import send_formatted_message

if TYPE_CHECKING:
    from app.database import Database
    from app.jyotish_engine import JyotishChart

logger = logging.getLogger(__name__)

WEEKLY_DIGEST_TIME = "11:00"
WEEKLY_DIGEST_WEEKDAY = 0  # Monday
WEEKLY_DIGEST_FRIDAY_WEEKDAY = 4  # Friday

# First post goes out on launch day (bootstrap); regular Mon/Fri 11:00 from schedule Monday.
WEEKLY_DIGEST_LAUNCH_DATE = "2026-06-20"
WEEKLY_DIGEST_SCHEDULE_MONDAY = "2026-06-22"
WEEKLY_DIGEST_BOOTSTRAP_PERIOD = "weekly:bootstrap:health_madness:launch"
_LEGACY_BOOTSTRAP_DATES = ("2026-06-12",)

_WEEKLY_FRIDAY_INTRO: dict[str, tuple[str, str]] = {
    "health_madness": (
        "Пятница — проверим, как неделя отразилась на тебе 🌿",
        "Friday — let's see how the week landed for you 🌿",
    ),
    "love_week": (
        "Пятница — время для честного разговора с картой про близость 💞",
        "Friday — time for an honest chart check-in on closeness 💞",
    ),
    "money_week": (
        "Пятница — подведём итоги недели с деньгами 💸",
        "Friday — wrap up the week with your money patterns 💸",
    ),
    "karma_week": (
        "Пятница — что повторилось на этой неделе? 🪷",
        "Friday — what loop showed up this week? 🪷",
    ),
}

_WEEKLY_FRIDAY_BODY: dict[str, tuple[str, str]] = {
    "health_madness": (
        "В понедельник мы открыли тему здоровья и «типа безумия» в карте. "
        "Если блоки так и остались нетронутыми — самое время перед выходными.",
        "On Monday we opened health and your chart's «madness type». "
        "If you skipped the blocks — now's a good moment before the weekend.",
    ),
    "love_week": (
        "Тема недели — близость. Три кнопки ниже всё ещё про твою карту, не про «людей вообще».",
        "This week's theme is closeness. The three buttons below are still about your chart, not generic advice.",
    ),
    "money_week": (
        "Финансовая тема недели не сгорает в пятницу — нажми блок, если хочешь разбор по своим привычкам.",
        "The money theme doesn't expire on Friday — tap a block for a reading on your habits.",
    ),
    "karma_week": (
        "Кармические сюжеты любят повторяться к концу недели. Загляни в блок, который откликается.",
        "Karmic storylines often resurface by week's end. Tap the block that resonates.",
    ),
}

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_WEEKLY_MEDIA_DIR = _PROJECT_ROOT / "marketing" / "weekly"

# (theme_id, block_id) -> (builder_name, question_index)
_ANSWER_ROUTES: dict[tuple[str, str], tuple[str, int]] = {
    ("health_madness", "madness"): ("traits", 1),
    ("health_madness", "mental"): ("traits", 2),
    ("health_madness", "body"): ("health", 0),
    ("love_week", "bond"): ("family", 0),
    ("love_week", "partner"): ("family", 1),
    ("love_week", "home"): ("family", 3),
    ("money_week", "values"): ("finance", 0),
    ("money_week", "career"): ("finance", 1),
    ("money_week", "blocks"): ("finance", 4),
    ("karma_week", "theme"): ("karma", 0),
    ("karma_week", "past"): ("karma", 1),
    ("karma_week", "lesson"): ("karma", 2),
}


@dataclass(frozen=True)
class WeeklyBlock:
    block_id: str
    label_ru: str
    label_en: str


@dataclass(frozen=True)
class WeeklyTheme:
    theme_id: str
    media_name: str
    title_ru: str
    title_en: str
    paragraphs_ru: tuple[str, ...]
    paragraphs_en: tuple[str, ...]
    footer_ru: str
    footer_en: str
    blocks: tuple[WeeklyBlock, ...]


WEEKLY_THEMES: tuple[WeeklyTheme, ...] = (
    WeeklyTheme(
        theme_id="health_madness",
        media_name="health-madness.gif",
        title_ru="Здоровье: Твой тип безумия по натальной карте 👽",
        title_en="Health: Your «madness type» in the natal chart 👽",
        paragraphs_ru=(
            "Помню, когда я училась медитировать, мой учитель говорил: "
            "«Если взрослый человек не может просидеть 30 минут на коврике в тишине — он безумен… 🧘‍♀️»",
            "Ну что ж. Кажется, у каждого из нас есть свои скелеты в шкафу! "
            "А что самое интересное — они прописаны в натальной карте 🫡",
            "Да уж… Вопросы ниже не из простых, но ты держись!",
        ),
        paragraphs_en=(
            "When I was learning to meditate, my teacher said: "
            "«If an adult can't sit 30 minutes on a mat in silence — they're mad… 🧘‍♀️»",
            "Well then. Everyone has skeletons in the closet — "
            "and the interesting part is they're written in the natal chart 🫡",
            "Yeah… The questions below aren't easy, but hang in there!",
        ),
        footer_ru="◽️ Нажми блок — разбор по твоей карте (Premium ⭐)",
        footer_en="◽️ Tap a block — chart reading (Premium ⭐)",
        blocks=(
            WeeklyBlock("madness", "МОЙ ТИП БЕЗУМИЯ 👻", "MY TYPE OF MADNESS 👻"),
            WeeklyBlock("mental", "ПСИХИЧЕСКОЕ ЗДОРОВЬЕ В КАРТЕ", "MENTAL HEALTH IN THE CHART"),
            WeeklyBlock("body", "ОБЩЕЕ ЗДОРОВЬЕ 🌿", "GENERAL HEALTH 🌿"),
        ),
    ),
    WeeklyTheme(
        theme_id="love_week",
        media_name="love-week.gif",
        title_ru="Любовь: что карта шепчет про близость 💞",
        title_en="Love: what your chart whispers about closeness 💞",
        paragraphs_ru=(
            "Кто-то ищет «идеального» партнёра из Pinterest, а карта смотрит на то, "
            "кого ты реально выбираешь — и почему.",
            "Отношения — не экзамен на пятёрку, а зеркало: иногда приятное, иногда честное до боли.",
            "Три кнопки ниже — три разных угол. Не торопись, читай с чаем ☕",
        ),
        paragraphs_en=(
            "Some hunt for a «Pinterest-perfect» partner; the chart looks at who you actually choose — and why.",
            "Relationships aren't a grade exam — they're a mirror: sometimes warm, sometimes painfully honest.",
            "Three buttons below — three angles. No rush, read with tea ☕",
        ),
        footer_ru="◽️ Нажми блок — ответ по твоей карте (Premium ⭐)",
        footer_en="◽️ Tap a block — answer from your chart (Premium ⭐)",
        blocks=(
            WeeklyBlock("bond", "КАК СКЛАДЫВАЮТСЯ ОТНОШЕНИЯ 💞", "HOW RELATIONSHIPS WORK 💞"),
            WeeklyBlock("partner", "КОГО Я ПРИТЯГИВАЮ 👀", "WHO I ATTRACT 👀"),
            WeeklyBlock("home", "ДОМ И «СВОИ» 🏠", "HOME & YOUR PEOPLE 🏠"),
        ),
    ),
    WeeklyTheme(
        theme_id="money_week",
        media_name="money-week.gif",
        title_ru="Деньги: твой финансовый характер 💸",
        title_en="Money: your financial character 💸",
        paragraphs_ru=(
            "Кошелёк — не только цифры. Это ещё и «на что я готов», «от чего отказываюсь» и «почему опять купил это».",
            "Карта не выдаёт лотерейный билет, зато честно показывает привычки — и это полезнее.",
            "Выбери тему ниже — без осуждения, только наблюдение.",
        ),
        paragraphs_en=(
            "A wallet isn't just numbers — it's what you'll pay for, what you'll skip, and «why I bought that again».",
            "The chart won't hand you a lottery ticket, but it shows habits — often more useful.",
            "Pick a topic below — no judgment, just observation.",
        ),
        footer_ru="◽️ Посмотрим, как у тебя устроены деньги (Premium ⭐)",
        footer_en="◽️ Let's see how money works for you (Premium ⭐)",
        blocks=(
            WeeklyBlock("values", "МОИ ЦЕННОСТИ И ТРАТЫ 💰", "MY VALUES & SPENDING 💰"),
            WeeklyBlock("career", "РАБОТА И ДОХОД 🎯", "WORK & INCOME 🎯"),
            WeeklyBlock("blocks", "ЧТО МЕШАЕТ ДЕНЬГАМ 🧱", "WHAT BLOCKS MONEY 🧱"),
        ),
    ),
    WeeklyTheme(
        theme_id="karma_week",
        media_name="karma-week.gif",
        title_ru="Карма: повторяющиеся сюжеты жизни 🪷",
        title_en="Karma: life's repeating storylines 🪷",
        paragraphs_ru=(
            "Жизнь иногда как сериал, где ты уже видел эту серию — только декорации другие.",
            "Карма в боте — не приговор, а подсказка: «вот тут ты ходишь по кругу, пока не сменишь реакцию».",
            "Три блока — три слоя. Бережно к себе.",
        ),
        paragraphs_en=(
            "Life sometimes feels like a show you've watched before — just different scenery.",
            "Karma here isn't a verdict — it's a hint: «you loop here until the reaction shifts».",
            "Three blocks — three layers. Be gentle with yourself.",
        ),
        footer_ru="◽️ Что карта говорит про твои уроки (Premium ⭐)",
        footer_en="◽️ What your chart says about your lessons (Premium ⭐)",
        blocks=(
            WeeklyBlock("theme", "ГЛАВНАЯ КАРМИЧЕСКАЯ ТЕМА 🪷", "MAIN KARMIC THEME 🪷"),
            WeeklyBlock("past", "ПРОШЛОЕ И ПАМЯТЬ 🌙", "PAST & MEMORY 🌙"),
            WeeklyBlock("lesson", "УРОК САТУРНА ⏳", "SATURN'S LESSON ⏳"),
        ),
    ),
)


def _monday_of_week(for_date_key: str) -> date:
    d = date.fromisoformat(for_date_key)
    return d - timedelta(days=d.weekday())


def theme_for_date(for_date_key: str) -> WeeklyTheme:
    """Rotate themes from the first scheduled Monday; launch day uses health_madness bootstrap."""
    d = date.fromisoformat(for_date_key)
    epoch = date.fromisoformat(WEEKLY_DIGEST_SCHEDULE_MONDAY)
    if d < epoch:
        return WEEKLY_THEMES[0]
    week_monday = _monday_of_week(for_date_key)
    weeks_since = (week_monday - epoch).days // 7
    # Week 0 on schedule Monday = love_week (health_madness was sent on launch day).
    theme_index = (1 + weeks_since) % len(WEEKLY_THEMES)
    return WEEKLY_THEMES[theme_index]


def launch_theme() -> WeeklyTheme:
    return WEEKLY_THEMES[0]


def theme_by_id(theme_id: str) -> WeeklyTheme | None:
    for theme in WEEKLY_THEMES:
        if theme.theme_id == theme_id:
            return theme
    return None


def _media_path(theme: WeeklyTheme) -> Path | None:
    for ext in (theme.media_name, theme.media_name.replace(".gif", ".png"), theme.media_name.replace(".gif", ".jpg")):
        path = _WEEKLY_MEDIA_DIR / ext
        if path.is_file():
            return path
    return None


def _format_birth_line(profile, locale: str) -> str:
    if profile is None or profile.birth_date is None:
        return ""
    lang = _lang(locale)
    if lang == "ru":
        date_part = profile.birth_date.strftime("%d.%m.%Y")
    else:
        date_part = profile.birth_date.isoformat()
    parts = [date_part]
    if profile.birth_time is not None:
        parts.append(profile.birth_time.strftime("%H:%M"))
    city = (profile.city or "").strip()
    if city and city not in {"-", ""}:
        parts.append(city)
    return " · ".join(parts)


def weekly_profile_banner(locale: str, profile, chart: "JyotishChart | None") -> str:
    """One-line chart identity: sign, lagna, moon, birth date/time/city."""
    from app.astro_engine import sign_label
    from app.bot_context import SIGN_EMOJI

    lang = _lang(locale)
    if chart is not None:
        sun = chart.planets["SUN"]
        moon = chart.planets["MOON"]
        lagna_key = chart.lagna_sign
        sun_l = sign_label(locale, sun.sign)
        moon_l = sign_label(locale, moon.sign)
        lagna_l = sign_label(locale, lagna_key)
        sun_e = SIGN_EMOJI.get(sun.sign, "")
        moon_e = SIGN_EMOJI.get(moon.sign, "")
        lagna_e = SIGN_EMOJI.get(lagna_key, "")
        if lang == "ru":
            chart_line = (
                f"Солнце {sun_e} {sun_l} · Луна {moon_e} {moon_l} · Лагна {lagna_e} {lagna_l}"
            )
            head = f"🔮 Твоя карта: {chart_line}"
        else:
            chart_line = (
                f"Sun {sun_e} {sun_l} · Moon {moon_e} {moon_l} · Lagna {lagna_e} {lagna_l}"
            )
            head = f"🔮 Your chart: {chart_line}"
    elif profile is not None and profile.sign:
        sl = sign_label(locale, profile.sign)
        se = SIGN_EMOJI.get(profile.sign, "")
        if lang == "ru":
            head = f"🔮 Твой знак: {se} {sl}"
        else:
            head = f"🔮 Your sign: {se} {sl}"
    else:
        return ""

    birth = _format_birth_line(profile, locale)
    if birth:
        head += f"\n📅 {birth}"
    return head


def weekly_theme_hook(
    locale: str,
    theme_id: str,
    profile,
    chart: "JyotishChart | None",
) -> str:
    """Theme intro tied to this user's placements — not a generic template."""
    from app.astro_engine import sign_label

    lang = _lang(locale)
    if chart is None:
        if profile is not None and profile.sign:
            sl = sign_label(locale, profile.sign)
            if lang == "ru":
                return (
                    f"Ниже — не общий текст для всех, а разбор по твоему знаку ({sl}) "
                    f"и дате рождения."
                )
            return (
                f"This is not a one-size-fits-all post — it's built from your sign ({sl}) "
                f"and birth date."
            )
        return ""

    sun_l = sign_label(locale, chart.planets["SUN"].sign)
    lagna_l = sign_label(locale, chart.lagna_sign)
    venus_l = sign_label(locale, chart.planets["VENUS"].sign)
    moon_l = sign_label(locale, chart.planets["MOON"].sign)
    saturn_l = sign_label(locale, chart.planets["SATURN"].sign)

    hooks: dict[str, tuple[str, str]] = {
        "health_madness": (
            f"Сегодня — твоё «безумие» по карте: Солнце в {sun_l}, Лагна {lagna_l}. "
            f"Кнопки дают разбор только для тебя.",
            f"Today — your «madness type»: Sun in {sun_l}, Lagna {lagna_l}. "
            f"Buttons open a reading just for you.",
        ),
        "love_week": (
            f"Близость у тебя звучит иначе: Венера в {venus_l}, Луна в {moon_l}. "
            f"Три кнопки — три личных угла.",
            f"Closeness reads differently for you: Venus in {venus_l}, Moon in {moon_l}. "
            f"Three buttons — three personal angles.",
        ),
        "money_week": (
            f"Деньги в твоей карте: Солнце {sun_l}, ресурсы через Лагну {lagna_l}. "
            f"Кнопки — твои паттерны, не шаблон.",
            f"Money in your chart: Sun {sun_l}, resources through Lagna {lagna_l}. "
            f"Buttons show your patterns, not a template.",
        ),
        "karma_week": (
            f"Кармические сюжеты: Сатурн в {saturn_l}, Луна в {moon_l}. "
            f"Нажми блок — увидишь свой повторяющийся сценарий.",
            f"Karmic storylines: Saturn in {saturn_l}, Moon in {moon_l}. "
            f"Tap a block — your recurring plot.",
        ),
    }
    pair = hooks.get(theme_id)
    if pair is None:
        return ""
    return pair[0] if lang == "ru" else pair[1]


def build_weekly_post_text(
    locale: str,
    theme: WeeklyTheme,
    profile=None,
    chart: "JyotishChart | None" = None,
    *,
    slot: str = "monday",
) -> str:
    if slot == "friday":
        return build_weekly_friday_post_text(locale, theme, profile=profile, chart=chart)
    lang = _lang(locale)
    if lang == "ru":
        body_parts: list[str] = [b(theme.title_ru), *theme.paragraphs_ru]
        footer = theme.footer_ru
    else:
        body_parts = [b(theme.title_en), *theme.paragraphs_en]
        footer = theme.footer_en

    banner = weekly_profile_banner(locale, profile, chart)
    if banner:
        body_parts.insert(1, banner)

    hook = weekly_theme_hook(locale, theme.theme_id, profile, chart)
    if hook:
        body_parts.append(hook)

    body_parts.append(footer)
    return p(*body_parts)


def build_weekly_friday_post_text(
    locale: str,
    theme: WeeklyTheme,
    profile=None,
    chart: "JyotishChart | None" = None,
) -> str:
    lang = _lang(locale)
    intro = _WEEKLY_FRIDAY_INTRO.get(theme.theme_id, ("", ""))
    body = _WEEKLY_FRIDAY_BODY.get(theme.theme_id, ("", ""))
    title = intro[0] if lang == "ru" else intro[1]
    mid = body[0] if lang == "ru" else body[1]
    footer = theme.footer_ru if lang == "ru" else theme.footer_en

    parts: list[str] = [b(title)]
    banner = weekly_profile_banner(locale, profile, chart)
    if banner:
        parts.append(banner)
    if mid:
        parts.append(mid)
    hook = weekly_theme_hook(locale, theme.theme_id, profile, chart)
    if hook:
        parts.append(hook)
    parts.append(footer)
    return p(*parts)


def weekly_digest_keyboard(locale: str, theme: WeeklyTheme) -> InlineKeyboardMarkup:
    lang = _lang(locale)
    rows = [
        [
            InlineKeyboardButton(
                text=block.label_ru if lang == "ru" else block.label_en,
                callback_data=f"weekly:{theme.theme_id}:{block.block_id}",
            )
        ]
        for block in theme.blocks
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_weekly_digest_message(
    bot: Bot,
    user_id: int,
    *,
    locale: str,
    theme: WeeklyTheme,
    profile=None,
    chart: "JyotishChart | None" = None,
    slot: str = "monday",
) -> None:
    text = build_weekly_post_text(locale, theme, profile=profile, chart=chart, slot=slot)
    keyboard = weekly_digest_keyboard(locale, theme)
    media = _media_path(theme)
    if media is None:
        await send_formatted_message(bot, user_id, text, reply_markup=keyboard)
        return
    suffix = media.suffix.lower()
    try:
        if suffix in {".gif", ".mp4"}:
            await bot.send_animation(
                user_id,
                FSInputFile(media),
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        else:
            await bot.send_photo(
                user_id,
                FSInputFile(media),
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
    except Exception:
        logger.exception("weekly digest media send failed for user %s — text fallback", user_id)
        await send_formatted_message(bot, user_id, text, reply_markup=keyboard)


def build_weekly_block_answer(
    theme_id: str,
    block_id: str,
    chart,
    locale: str,
    *,
    style: str,
    profile=None,
) -> str | None:
    route = _ANSWER_ROUTES.get((theme_id, block_id))
    if route is None:
        return None
    builder_name, question_index = route
    from app.natal_sphere_qa import (
        build_family_answer,
        build_finance_answer,
        build_health_answer,
        build_karma_answer,
        build_traits_answer,
    )

    builders = {
        "traits": build_traits_answer,
        "health": build_health_answer,
        "family": build_family_answer,
        "finance": build_finance_answer,
        "karma": build_karma_answer,
    }
    builder = builders.get(builder_name)
    if builder is None:
        return None
    answer = builder(chart, locale, question_index, style=style)
    if answer is None:
        return None
    banner = weekly_profile_banner(locale, profile, chart)
    if banner:
        return f"{banner}\n\n{answer}"
    return answer


def _weekly_time_due(now_utc: datetime, timezone_name: str, *, bootstrap: bool) -> bool:
    hhmm = user_local_hhmm(now_utc, timezone_name)
    if bootstrap:
        return hhmm >= WEEKLY_DIGEST_TIME
    return hhmm == WEEKLY_DIGEST_TIME


async def _bootstrap_already_sent(db: "Database", user_id: int) -> bool:
    if await db.was_daily_sent(user_id, WEEKLY_DIGEST_BOOTSTRAP_PERIOD, "launch"):
        return True
    for legacy_date in _LEGACY_BOOTSTRAP_DATES:
        legacy_period = f"weekly:bootstrap:health_madness:{legacy_date}"
        if await db.was_daily_sent(user_id, legacy_period, legacy_date):
            return True
    return False


async def _send_weekly_to_user(
    db: "Database",
    bot: Bot,
    user,
    *,
    theme: WeeklyTheme,
    date_key: str,
    period: str,
    event_name: str,
    slot: str,
) -> bool:
    locale = user.language or "ru"
    chart = None
    try:
        from app.natal_sphere_qa import build_chart_from_profile

        chart = build_chart_from_profile(user)
    except Exception:
        logger.debug("weekly digest chart build skipped for user %s", user.user_id)
    try:
        await send_weekly_digest_message(
            bot,
            user.user_id,
            locale=locale,
            theme=theme,
            profile=user,
            chart=chart,
            slot=slot,
        )
        await db.mark_daily_sent(user.user_id, period, date_key)
        await db.log_event(user.user_id, event_name)
        return True
    except Exception:
        await db.log_event(user.user_id, f"{event_name}_failed")
        return False


async def _try_send_weekly_bootstrap(
    db: "Database",
    bot: Bot,
    user,
    now_utc: datetime,
) -> None:
    date_key = user_local_date_key(now_utc, user.timezone)
    if date_key != WEEKLY_DIGEST_LAUNCH_DATE:
        return
    if not _weekly_time_due(now_utc, user.timezone, bootstrap=True):
        return

    theme = launch_theme()
    if await _bootstrap_already_sent(db, user.user_id):
        return
    await _send_weekly_to_user(
        db,
        bot,
        user,
        theme=theme,
        date_key="launch",
        period=WEEKLY_DIGEST_BOOTSTRAP_PERIOD,
        event_name=f"weekly_digest_bootstrap_{theme.theme_id}_sent",
        slot="monday",
    )


async def send_weekly_bootstrap_now(db: "Database", bot: Bot) -> tuple[int, int]:
    """Admin/manual: send launch post immediately (ignores time-of-day)."""
    theme = launch_theme()
    sent = 0
    failed = 0
    for user in await db.get_weekly_digest_subscribers():
        if await _bootstrap_already_sent(db, user.user_id):
            continue
        ok = await _send_weekly_to_user(
            db,
            bot,
            user,
            theme=theme,
            date_key="launch",
            period=WEEKLY_DIGEST_BOOTSTRAP_PERIOD,
            event_name=f"weekly_digest_bootstrap_{theme.theme_id}_sent",
            slot="monday",
        )
        if ok:
            sent += 1
        else:
            failed += 1
    return sent, failed


async def _try_send_weekly_digest(
    db: "Database",
    bot: Bot,
    user,
    now_utc: datetime,
    *,
    weekday: int,
    slot: str,
    period_prefix: str,
    event_prefix: str,
) -> None:
    if user_local_weekday(now_utc, user.timezone) != weekday:
        return
    if not _weekly_time_due(now_utc, user.timezone, bootstrap=False):
        return

    date_key = user_local_date_key(now_utc, user.timezone)
    schedule_start = date.fromisoformat(WEEKLY_DIGEST_SCHEDULE_MONDAY)
    if date.fromisoformat(date_key) < schedule_start:
        return
    if date_key == WEEKLY_DIGEST_LAUNCH_DATE and slot == "friday":
        return

    theme = theme_for_date(date_key)
    period = period_prefix.format(theme_id=theme.theme_id, date_key=date_key)
    if await db.was_daily_sent(user.user_id, period, date_key):
        return

    await _send_weekly_to_user(
        db,
        bot,
        user,
        theme=theme,
        date_key=date_key,
        period=period,
        event_name=f"{event_prefix}_{theme.theme_id}_sent",
        slot=slot,
    )


async def send_due_weekly_digests(db: "Database", bot: Bot, now_utc: datetime) -> None:
    recipients = await db.get_weekly_digest_subscribers()
    slots = (
        (WEEKLY_DIGEST_WEEKDAY, "monday", "weekly:{theme_id}:{date_key}", "weekly_digest"),
        (
            WEEKLY_DIGEST_FRIDAY_WEEKDAY,
            "friday",
            "weekly:friday:{theme_id}:{date_key}",
            "weekly_digest_friday",
        ),
    )
    for user in recipients:
        await _try_send_weekly_bootstrap(db, bot, user, now_utc)
        for weekday, slot, period_prefix, event_prefix in slots:
            await _try_send_weekly_digest(
                db,
                bot,
                user,
                now_utc,
                weekday=weekday,
                slot=slot,
                period_prefix=period_prefix,
                event_prefix=event_prefix,
            )
