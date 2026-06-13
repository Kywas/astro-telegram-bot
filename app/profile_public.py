"""BotFather public profile (description, short description)."""
import logging

from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputProfilePhotoStatic

from app.bot_context import BOT_ICON_PATH, settings
from app.i18n import t

def _feedback_contact_handle() -> str | None:
    return settings.feedback_username


def _feedback_profile_line(locale: str) -> str:
    handle = _feedback_contact_handle()
    if not handle:
        return ""
    if locale == "ru":
        return f"\n\n💬 Обратная связь\n@{handle}\n\n/help · /feedback"
    return f"\n\n💬 Feedback\n@{handle}\n\n/help · /feedback"


def public_description_ru() -> str:
    return (
        "🌌 AstroPulse — карманный астролог на эфемеридах.\n\n"
        "✨ Гороскоп на сегодня — бесплатно\n"
        "💞 Совместимость с полным профилем партнёра\n"
        "🌙 Лунный календарь и ежедневные напоминания\n"
        "🪐 Натальная карта по Swiss Ephemeris\n\n"
        "⭐ Premium — Telegram Stars\n"
        "   · неделя и месяц\n"
        "   · полная карта и лунный календарь (7 / 30 дней)\n"
        "   · безлимит совместимости\n"
        "   · оплата: Stars / ₽ / $\n\n"
        "🔮 /start · RU / EN"
        f"{_feedback_profile_line('ru')}"
    )


def public_description_en() -> str:
    return (
        "🌌 AstroPulse — pocket astrologer powered by ephemerides.\n\n"
        "✨ Daily horoscope — free\n"
        "💞 Compatibility with full partner profile\n"
        "🌙 Moon calendar and daily lunar reminders\n"
        "🪐 Natal chart via Swiss Ephemeris\n\n"
        "⭐ Premium — Telegram Stars\n"
        "   · week and month\n"
        "   · full chart and moon calendar (7 / 30 days)\n"
        "   · unlimited compatibility\n"
        "   · pay with Stars / ₽ / $\n\n"
        "🔮 /start · RU / EN"
        f"{_feedback_profile_line('en')}"
    )


def public_short_description_ru() -> str:
    return "🌌 AstroPulse — гороскоп · луна · карта · Premium"[:120]


def public_short_description_en() -> str:
    return "🌌 AstroPulse — horoscope · moon · chart · Premium"[:120]


def feedback_keyboard(locale: str) -> InlineKeyboardMarkup:
    handle = _feedback_contact_handle()
    rows: list[list[InlineKeyboardButton]] = []
    if handle:
        rows.append(
            [
                InlineKeyboardButton(
                    text=t(locale, "feedback_write_button"),
                    url=f"https://t.me/{handle}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def configure_public_profile(bot: Bot) -> None:
    import logging

    logger = logging.getLogger(__name__)
    short_ru = public_short_description_ru()
    short_en = public_short_description_en()
    desc_ru = public_description_ru()
    desc_en = public_description_en()

    profile_steps: tuple[tuple[str, object], ...] = (
        ("default short description", bot.set_my_short_description(short_description=short_ru)),
        ("default description", bot.set_my_description(description=desc_ru)),
        ("ru short description", bot.set_my_short_description(short_description=short_ru, language_code="ru")),
        ("en short description", bot.set_my_short_description(short_description=short_en, language_code="en")),
        ("ru description", bot.set_my_description(description=desc_ru, language_code="ru")),
        ("en description", bot.set_my_description(description=desc_en, language_code="en")),
    )
    for label, coro in profile_steps:
        try:
            await coro
            logger.info("Updated bot profile: %s", label)
        except Exception:
            logger.exception("Failed to update bot profile: %s", label)

    if hasattr(bot, "set_my_name"):
        for lang in ("ru", "en"):
            try:
                await bot.set_my_name(name="AstroPulse", language_code=lang)
                logger.info("Updated bot name for %s", lang)
            except Exception:
                logger.exception("Failed to update bot name for %s", lang)

    handle = _feedback_contact_handle()
    if handle:
        logger.info("Public profile configured with feedback @%s", handle)
    else:
        logger.warning("Public profile configured without FEEDBACK_USERNAME")

    if BOT_ICON_PATH.is_file() and hasattr(bot, "set_my_profile_photo"):
        try:
            await bot.set_my_profile_photo(
                photo=InputProfilePhotoStatic(photo=FSInputFile(BOT_ICON_PATH)),
            )
        except Exception:
            logger.exception("Failed to update bot profile photo")


