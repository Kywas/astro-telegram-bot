import asyncio
from datetime import datetime, timedelta, timezone
import re

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import LabeledPrice
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.config import load_settings
from app.admin_middleware import AdminOnlyMiddleware
from app.database import Database
from app.daily_sender import run_daily_loop
from app.horoscope import generate_horoscope
from app.http_proxy_session import HttpProxyAiohttpSession
from app.moon_calendar import (
    generate_moon_calendar_text,
    generate_moon_compact_table_text,
    generate_moon_table_text,
)
from app.natal import build_natal_summary
from app.states import CompatibilityCheck, MoonDetails, PreferencesSetup, ProfileSetup
from app.states import AdminPanel
from app.premium import is_premium_active
from app.synastry import build_synastry
from app.zodiac import zodiac_sign


router = Router()
admin_router = Router()
settings = load_settings()
db = Database(settings.database_path)

SIGN_RU = {
    "Aries": "Овен",
    "Taurus": "Телец",
    "Gemini": "Близнецы",
    "Cancer": "Рак",
    "Leo": "Лев",
    "Virgo": "Дева",
    "Libra": "Весы",
    "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn": "Козерог",
    "Aquarius": "Водолей",
    "Pisces": "Рыбы",
}

SIGN_EN = {
    "Aries": "Aries",
    "Taurus": "Taurus",
    "Gemini": "Gemini",
    "Cancer": "Cancer",
    "Leo": "Leo",
    "Virgo": "Virgo",
    "Libra": "Libra",
    "Scorpio": "Scorpio",
    "Sagittarius": "Sagittarius",
    "Capricorn": "Capricorn",
    "Aquarius": "Aquarius",
    "Pisces": "Pisces",
}

TEXTS = {
    "ru": {
        "help": (
            "Команды:\n"
            "/start - запустить бота и заполнить профиль\n"
            "/profile - показать ваш профиль\n"
            "/today - гороскоп на сегодня\n"
            "/compat - совместимость с другим человеком\n"
            "/moon - лунный календарь\n"
            "/mood 1..10 - трекер настроения\n"
            "/daily on HH:MM | off - ежедневная рассылка\n"
            "/prefs - персональные настройки\n"
            "/prefssetup - пошаговая настройка профиля\n"
            "/stats - статистика бота (админ)\n"
            "/premium - статус premium\n"
            "/buypremium - купить premium (тестовый skeleton)\n"
            "/about - что умеет бот\n"
            "/language - сменить язык\n"
            "/menu - показать кнопки меню\n"
            "/help - список команд"
        ),
        "about_block": (
            "Что может делать этот бот?\n\n"
            "Бот для астропрогнозов и лунного календаря:\n\n"
            "Гороскоп:\n"
            "Сегодня\n"
            "Неделя\n"
            "Месяц\n\n"
            "Совместимость:\n"
            "Любовь\n"
            "Дружба\n"
            "Работа\n\n"
            "Лунный календарь:\n"
            "Сегодня\n"
            "7 дней\n"
            "30 дней\n"
            "Подробнее по дню\n\n"
            "Дополнительно:\n"
            "Трекер настроения\n"
            "Ежедневная рассылка\n"
            "Профиль и настройки\n"
            "RU / EN"
        ),
        "about_show_commands": "Показать все команды",
        "welcome": (
            "Добро пожаловать в Astro Bot.\n"
            "Контент носит развлекательный характер.\n\n"
            "Введите дату рождения в формате ДД.ММ.ГГГГ:"
        ),
        "start_home": "Главное меню готово. Выбери действие кнопками ниже.",
        "profile_not_found": "Профиль не найден. Сначала используйте /start.",
        "profile_incomplete": "Профиль заполнен не полностью. Используйте /start.",
        "profile_title": "Ваш профиль:",
        "profile_date": "Дата рождения",
        "profile_time": "Время рождения",
        "profile_city": "Город",
        "profile_sign": "Знак",
        "unknown_time": "неизвестно",
        "complete_profile_first": "Сначала заполните профиль через /start.",
        "today_header": "Гороскоп на сегодня для знака {sign}:",
        "week_header": "Гороскоп на неделю для знака {sign}:",
        "month_header": "Гороскоп на месяц для знака {sign}:",
        "natal_header": "Натальная карта",
        "natal_profile_missing": "Для натальной карты сначала заполни профиль через /start.",
        "btn_natal": "🪐 Натальная карта",
        "natal_mode_short": "⚡ Кратко",
        "natal_mode_full": "📚 Подробно",
        "choose_horoscope_period": "Выбери период гороскопа:",
        "back": "⬅ Назад",
        "crumb_root": "Главная",
        "crumb_horoscope": "Гороскоп",
        "crumb_moon": "Лунный календарь",
        "crumb_settings": "Настройки",
        "crumb_language": "Язык",
        "crumb_about": "О боте",
        "crumb_admin": "Админка",
        "crumb_profile_setup": "Настройка профиля",
        "moon_header": "Лунный календарь",
        "choose_moon_period": "Выбери период лунного календаря:",
        "moon_7_days": "7 дней",
        "moon_30_days": "30 дней",
        "moon_today": "Сегодня",
        "moon_details_day": "Подробнее по дню",
        "ask_moon_day_month": "Введи дату в формате ДД.ММ (например, 14.06):",
        "invalid_day_month": "Неверный формат. Используй ДД.ММ, например: 14.06",
        "moon_date_out_of_range": "Эта дата не попадает в текущие 30 дней. Введи дату из таблицы.",
        "ask_compat_date": "Введите дату рождения второго человека в формате ДД.ММ.ГГГГ:",
        "choose_compat_mode": "Выбери режим совместимости:",
        "compat_mode_love": "Любовь",
        "compat_mode_friendship": "Дружба",
        "compat_mode_work": "Работа",
        "compat_mode_saved": "Режим сохранен: {mode}. Теперь введи дату второго человека (ДД.ММ.ГГГГ).",
        "compat_result": (
            "Совместимость: {sign_a} + {sign_b}\n"
            "Режим: {mode}\n"
            "Оценка: {score}%\n\n"
            "{details}"
        ),
        "mood_saved": "Настроение сохранено: {score}/10. Следующие прогнозы станут точнее.",
        "mood_invalid": "Укажи число от 1 до 10. Пример: /mood 7",
        "daily_enabled": "Ежедневная рассылка включена на {hhmm} (UTC).",
        "daily_disabled": "Ежедневная рассылка выключена.",
        "daily_usage": "Используй: /daily on HH:MM или /daily off. Пример: /daily on 09:30",
        "prefs_text": (
            "Персональные настройки:\n"
            "• Пол: {gender}\n"
            "• Статус отношений: {relationship}\n"
            "• Фокус: {goal}\n"
            "• Рассылка: {daily_status}\n"
            "• Настроение: {mood}"
        ),
        "prefs_start": "Открыть пошаговую настройку",
        "stats_text": (
            "Статистика:\n"
            "• Пользователей: {total_users}\n"
            "• Подписок на рассылку: {daily_subscribers}\n"
            "• Premium пользователей: {premium_users}\n"
            "• Всего событий: {total_events}\n"
            "• Ошибок: {total_errors}"
        ),
        "admin_only": "Эта команда доступна только администратору.",
        "premium_active": "Premium активен до: {until}. Доступны расширенные функции.",
        "premium_inactive": "Premium не активен. Сейчас доступен базовый режим.",
        "payments_disabled": "Платежи временно отключены.",
        "premium_buy_intro": "Оформи premium на 30 дней за {price} Stars.",
        "premium_buy_fail": "Не удалось открыть платеж. Проверь, что бот поддерживает Stars.",
        "premium_payment_ok": "Оплата прошла. Premium активирован на 30 дней.",
        "premium_payment_error": "Оплата не прошла, попробуй еще раз позже.",
        "grant_usage": "Используй: /grantpremium <user_id> <days>. Пример: /grantpremium 123456789 30",
        "grant_done": "Premium выдан пользователю {user_id} на {days} дн.",
        "broadcast_usage": "Используй: /broadcast текст сообщения",
        "broadcast_done": "Рассылка завершена. Успешно: {ok}, ошибок: {fail}",
        "ping_text": "Сервис работает. UTC: {utc}",
        "admin_panel": "Админ-панель:",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_broadcast": "📣 Broadcast",
        "admin_btn_grant": "🎁 Grant Premium",
        "admin_btn_ping": "🩺 Ping",
        "admin_broadcast_prompt": "Введи текст для рассылки:",
        "admin_grant_prompt": "Введи: user_id days (пример: 123456789 30)",
        "broadcast_preview": "Предпросмотр рассылки:\n\n{text}",
        "broadcast_confirm_title": "Отправить это сообщение всем пользователям?",
        "broadcast_confirm": "✅ Подтвердить",
        "broadcast_cancel": "❌ Отмена",
        "broadcast_cancelled": "Рассылка отменена.",
        "profile_upgrade_done": "Доп. профиль сохранен: {gender}, {relationship}, фокус: {goal}.",
        "ask_gender": "Выбери пол: m/f/other",
        "ask_relationship": "Выбери статус: single/relationship",
        "ask_goal": "Фокус прогноза: love/career/money/balance",
        "choose_gender": "Шаг 1/3: выбери пол",
        "choose_relationship": "Шаг 2/3: выбери статус отношений",
        "choose_goal": "Шаг 3/3: выбери фокус прогноза",
        "gender_m": "Мужчина",
        "gender_f": "Женщина",
        "gender_other": "Другое",
        "rel_single": "Свободен(а)",
        "rel_relationship": "В отношениях",
        "goal_love": "Любовь",
        "goal_career": "Карьера",
        "goal_money": "Деньги",
        "goal_balance": "Баланс",
        "invalid_date": "Неверный формат даты. Используйте ДД.ММ.ГГГГ, например: 14.02.2001",
        "ask_time": "Введите время рождения в формате ЧЧ:ММ (или отправьте '-' если не знаете):",
        "invalid_time": "Неверный формат времени. Используйте ЧЧ:ММ, например: 09:30, или '-' если не знаете.",
        "ask_city": "Введите город рождения:",
        "city_short": "Название города слишком короткое, попробуйте еще раз.",
        "session_expired": "Сессия истекла. Начните заново командой /start.",
        "profile_saved": (
            "Профиль сохранен.\n"
            "Ваш знак зодиака: {sign}\n"
            "Используйте /today, чтобы получить гороскоп на сегодня."
        ),
        "fallback": "Я не понял сообщение. Используйте /help, чтобы увидеть команды.",
        "choose_language": "Выберите язык:",
        "language_updated": "Язык обновлен. Теперь я говорю по-русски.",
        "menu_hint": "Меню кнопок открыто. Выберите действие:",
        "settings_title": "Настройки",
        "settings_hint": "Выбери раздел настроек:",
        "settings_btn_language": "🌐 Язык",
        "settings_btn_profile": "🧩 Профиль",
        "settings_btn_daily": "⏰ Рассылка",
        "settings_btn_help": "❓ Помощь",
        "btn_today": "🔮 Гороскоп",
        "btn_profile": "👤 Профиль",
        "btn_language": "🌐 Язык",
        "btn_help": "❓ Помощь",
        "btn_restart": "🔁 Заполнить профиль заново",
        "btn_compat": "💞 Совместимость",
        "btn_moon": "🌙 Лунный календарь",
        "btn_prefs": "⚙ Настройки",
        "btn_about": "ℹ О боте",
        "btn_ref": "👥 Рефералка",
        "ref_title": "Реферальная программа",
        "ref_text": (
            "Твоя ссылка:\n{link}\n\n"
            "Приглашено: {count}\n"
            "Бонус за каждого: +7 дней premium"
        ),
        "ref_invalid": "Некорректный реферальный код.",
        "ref_attached": "Реферал привязан. Заверши профиль, чтобы начислить бонус пригласившему.",
        "ref_reward_inviter": "🎉 По твоей ссылке пришел новый пользователь. +7 дней premium.",
    },
    "en": {
        "help": (
            "Commands:\n"
            "/start - start bot and fill profile\n"
            "/profile - show your profile\n"
            "/today - daily horoscope\n"
            "/compat - compatibility with another person\n"
            "/moon - moon calendar\n"
            "/mood 1..10 - mood tracker\n"
            "/daily on HH:MM | off - daily auto-send\n"
            "/prefs - personal preferences\n"
            "/prefssetup - profile setup wizard\n"
            "/stats - bot stats (admin)\n"
            "/premium - premium status\n"
            "/buypremium - buy premium (test skeleton)\n"
            "/about - bot capabilities\n"
            "/language - change language\n"
            "/menu - show menu buttons\n"
            "/help - command list"
        ),
        "about_block": (
            "What can this bot do?\n\n"
            "Astrology bot with horoscopes and moon calendar:\n\n"
            "Horoscope:\n"
            "Today\n"
            "Week\n"
            "Month\n\n"
            "Compatibility:\n"
            "Love\n"
            "Friendship\n"
            "Work\n\n"
            "Moon calendar:\n"
            "Today\n"
            "7 days\n"
            "30 days\n"
            "Day details\n\n"
            "Extra:\n"
            "Mood tracker\n"
            "Daily delivery\n"
            "Profile and settings\n"
            "RU / EN"
        ),
        "about_show_commands": "Show all commands",
        "welcome": (
            "Welcome to Astro Bot.\n"
            "This is entertainment content.\n\n"
            "Enter your birth date in format DD.MM.YYYY:"
        ),
        "start_home": "Main menu is ready. Choose action with buttons below.",
        "profile_not_found": "Profile not found. Use /start first.",
        "profile_incomplete": "Profile is incomplete. Use /start to continue.",
        "profile_title": "Your profile:",
        "profile_date": "Date of birth",
        "profile_time": "Time of birth",
        "profile_city": "City",
        "profile_sign": "Sign",
        "unknown_time": "unknown",
        "complete_profile_first": "Please complete your profile first with /start.",
        "today_header": "Today for {sign}:",
        "week_header": "Weekly horoscope for {sign}:",
        "month_header": "Monthly horoscope for {sign}:",
        "natal_header": "Natal chart",
        "natal_profile_missing": "Please complete your profile via /start before natal chart.",
        "btn_natal": "🪐 Natal chart",
        "natal_mode_short": "⚡ Short",
        "natal_mode_full": "📚 Full",
        "choose_horoscope_period": "Choose horoscope period:",
        "back": "⬅ Back",
        "crumb_root": "Home",
        "crumb_horoscope": "Horoscope",
        "crumb_moon": "Moon calendar",
        "crumb_settings": "Settings",
        "crumb_language": "Language",
        "crumb_about": "About",
        "crumb_admin": "Admin",
        "crumb_profile_setup": "Profile setup",
        "moon_header": "Moon calendar",
        "choose_moon_period": "Choose moon calendar period:",
        "moon_7_days": "7 days",
        "moon_30_days": "30 days",
        "moon_today": "Today",
        "moon_details_day": "Day details",
        "ask_moon_day_month": "Enter date as DD.MM (for example, 14.06):",
        "invalid_day_month": "Invalid format. Use DD.MM, for example: 14.06",
        "moon_date_out_of_range": "This date is outside the current 30-day table. Use a date from the table.",
        "ask_compat_date": "Enter second person's birth date in DD.MM.YYYY format:",
        "choose_compat_mode": "Choose compatibility mode:",
        "compat_mode_love": "Love",
        "compat_mode_friendship": "Friendship",
        "compat_mode_work": "Work",
        "compat_mode_saved": "Mode saved: {mode}. Now enter second person's birth date (DD.MM.YYYY).",
        "compat_result": (
            "Compatibility: {sign_a} + {sign_b}\n"
            "Mode: {mode}\n"
            "Score: {score}%\n\n"
            "{details}"
        ),
        "mood_saved": "Mood saved: {score}/10. Upcoming forecasts will be more personalized.",
        "mood_invalid": "Use a number from 1 to 10. Example: /mood 7",
        "daily_enabled": "Daily delivery is enabled at {hhmm} (UTC).",
        "daily_disabled": "Daily delivery is disabled.",
        "daily_usage": "Use: /daily on HH:MM or /daily off. Example: /daily on 09:30",
        "prefs_text": (
            "Personal preferences:\n"
            "• Gender: {gender}\n"
            "• Relationship: {relationship}\n"
            "• Focus: {goal}\n"
            "• Daily: {daily_status}\n"
            "• Mood: {mood}"
        ),
        "prefs_start": "Open setup wizard",
        "stats_text": (
            "Stats:\n"
            "• Users: {total_users}\n"
            "• Daily subscribers: {daily_subscribers}\n"
            "• Premium users: {premium_users}\n"
            "• Total events: {total_events}\n"
            "• Errors: {total_errors}"
        ),
        "admin_only": "This command is available to admin only.",
        "premium_active": "Premium active until: {until}. Extended features are enabled.",
        "premium_inactive": "Premium is not active. You are using base mode.",
        "payments_disabled": "Payments are temporarily disabled.",
        "premium_buy_intro": "Buy premium for 30 days at {price} Stars.",
        "premium_buy_fail": "Failed to open payment form. Check Stars support for your bot.",
        "premium_payment_ok": "Payment completed. Premium activated for 30 days.",
        "premium_payment_error": "Payment failed, please try again later.",
        "grant_usage": "Use: /grantpremium <user_id> <days>. Example: /grantpremium 123456789 30",
        "grant_done": "Premium granted to user {user_id} for {days} days.",
        "broadcast_usage": "Use: /broadcast message text",
        "broadcast_done": "Broadcast finished. Success: {ok}, failed: {fail}",
        "ping_text": "Service is up. UTC: {utc}",
        "admin_panel": "Admin panel:",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_broadcast": "📣 Broadcast",
        "admin_btn_grant": "🎁 Grant Premium",
        "admin_btn_ping": "🩺 Ping",
        "admin_broadcast_prompt": "Send broadcast text:",
        "admin_grant_prompt": "Enter: user_id days (example: 123456789 30)",
        "broadcast_preview": "Broadcast preview:\n\n{text}",
        "broadcast_confirm_title": "Send this message to all users?",
        "broadcast_confirm": "✅ Confirm",
        "broadcast_cancel": "❌ Cancel",
        "broadcast_cancelled": "Broadcast cancelled.",
        "profile_upgrade_done": "Extra profile saved: {gender}, {relationship}, focus: {goal}.",
        "ask_gender": "Choose gender: m/f/other",
        "ask_relationship": "Choose status: single/relationship",
        "ask_goal": "Forecast focus: love/career/money/balance",
        "choose_gender": "Step 1/3: choose gender",
        "choose_relationship": "Step 2/3: choose relationship status",
        "choose_goal": "Step 3/3: choose forecast focus",
        "gender_m": "Male",
        "gender_f": "Female",
        "gender_other": "Other",
        "rel_single": "Single",
        "rel_relationship": "In relationship",
        "goal_love": "Love",
        "goal_career": "Career",
        "goal_money": "Money",
        "goal_balance": "Balance",
        "invalid_date": "Invalid date format. Use DD.MM.YYYY, for example: 14.02.2001",
        "ask_time": "Enter birth time in HH:MM (or send '-' if unknown):",
        "invalid_time": "Invalid time format. Use HH:MM, for example: 09:30, or '-' if unknown.",
        "ask_city": "Enter your birth city:",
        "city_short": "City name looks too short, please try again.",
        "session_expired": "Session expired. Please restart with /start.",
        "profile_saved": (
            "Profile saved.\n"
            "Your zodiac sign is: {sign}\n"
            "Use /today for your daily horoscope."
        ),
        "fallback": "I did not understand that. Use /help to see commands.",
        "choose_language": "Choose language:",
        "language_updated": "Language updated. I will speak English now.",
        "menu_hint": "Button menu is open. Choose action:",
        "settings_title": "Settings",
        "settings_hint": "Choose a settings section:",
        "settings_btn_language": "🌐 Language",
        "settings_btn_profile": "🧩 Profile",
        "settings_btn_daily": "⏰ Daily",
        "settings_btn_help": "❓ Help",
        "btn_today": "🔮 Horoscope",
        "btn_profile": "👤 Profile",
        "btn_language": "🌐 Language",
        "btn_help": "❓ Help",
        "btn_restart": "🔁 Refill profile",
        "btn_compat": "💞 Compatibility",
        "btn_moon": "🌙 Moon calendar",
        "btn_prefs": "⚙ Preferences",
        "btn_about": "ℹ About",
        "btn_ref": "👥 Referral",
        "ref_title": "Referral program",
        "ref_text": (
            "Your link:\n{link}\n\n"
            "Invited users: {count}\n"
            "Bonus per invite: +7 premium days"
        ),
        "ref_invalid": "Invalid referral code.",
        "ref_attached": "Referral linked. Complete profile to reward your inviter.",
        "ref_reward_inviter": "🎉 A new user joined via your link. +7 premium days.",
    },
}


def public_description_ru() -> str:
    return (
        "Точный астробот для ежедневных решений.\n\n"
        "Что внутри:\n"
        "• Персональный гороскоп: сегодня, неделя, месяц\n"
        "• Совместимость: любовь, дружба, работа\n"
        "• Лунный календарь: сегодня, 7 и 30 дней\n"
        "• Рекомендации на день: что делать и чего избегать\n"
        "• Трекер настроения + авто-рассылка\n\n"
        "Выбери язык RU/EN и начни с /start."
    )


def public_description_en() -> str:
    return (
        "Your practical astrology assistant for daily decisions.\n\n"
        "Inside:\n"
        "• Personal horoscope: today, week, month\n"
        "• Compatibility modes: love, friendship, work\n"
        "• Moon calendar: today, 7 and 30 days\n"
        "• Daily guidance: what to do and what to avoid\n"
        "• Mood tracker + auto-delivery\n\n"
        "Choose RU/EN and start with /start."
    )


async def configure_public_profile(bot: Bot) -> None:
    # Telegram shows these texts on the bot card before user presses Start.
    await bot.set_my_short_description(
        short_description="Гороскопы, совместимость и лунный календарь в одном боте",
        language_code="ru",
    )
    await bot.set_my_short_description(
        short_description="Horoscope, compatibility and moon calendar in one bot",
        language_code="en",
    )
    await bot.set_my_description(
        description=public_description_ru(),
        language_code="ru",
    )
    await bot.set_my_description(
        description=public_description_en(),
        language_code="en",
    )


def language_keyboard(prefix: str = "lang") -> InlineKeyboardMarkup:
    inline_rows = [
        [
            InlineKeyboardButton(text="Русский", callback_data=f"{prefix}:ru"),
            InlineKeyboardButton(text="English", callback_data=f"{prefix}:en"),
        ]
    ]
    if prefix == "lang":
        inline_rows.append([InlineKeyboardButton(text="⬅ Back", callback_data="nav:settings")])
    return InlineKeyboardMarkup(inline_keyboard=inline_rows)


def horoscope_period_keyboard(locale: str) -> InlineKeyboardMarkup:
    if locale == "ru":
        labels = [("Сегодня", "day"), ("Неделя", "week"), ("Месяц", "month")]
    else:
        labels = [("Today", "day"), ("Week", "week"), ("Month", "month")]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=labels[0][0], callback_data=f"horo:{labels[0][1]}"),
                InlineKeyboardButton(text=labels[1][0], callback_data=f"horo:{labels[1][1]}"),
                InlineKeyboardButton(text=labels[2][0], callback_data=f"horo:{labels[2][1]}"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )


def moon_period_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "moon_today"), callback_data="moon:today"),
                InlineKeyboardButton(text=t(locale, "moon_7_days"), callback_data="moon:7"),
                InlineKeyboardButton(text=t(locale, "moon_30_days"), callback_data="moon:30"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )


def prefs_gender_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "gender_m"), callback_data="prefgender:m"),
                InlineKeyboardButton(text=t(locale, "gender_f"), callback_data="prefgender:f"),
                InlineKeyboardButton(text=t(locale, "gender_other"), callback_data="prefgender:other"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:settings")],
        ]
    )


def prefs_relationship_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "rel_single"), callback_data="prefrel:single"),
                InlineKeyboardButton(
                    text=t(locale, "rel_relationship"),
                    callback_data="prefrel:relationship",
                ),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:settings")],
        ]
    )


def prefs_goal_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "goal_love"), callback_data="prefgoal:love"),
                InlineKeyboardButton(text=t(locale, "goal_career"), callback_data="prefgoal:career"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "goal_money"), callback_data="prefgoal:money"),
                InlineKeyboardButton(text=t(locale, "goal_balance"), callback_data="prefgoal:balance"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:settings")],
        ]
    )


def admin_panel_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "admin_btn_stats"), callback_data="admin:stats"),
                InlineKeyboardButton(text=t(locale, "admin_btn_ping"), callback_data="admin:ping"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "admin_btn_broadcast"), callback_data="admin:broadcast"),
                InlineKeyboardButton(text=t(locale, "admin_btn_grant"), callback_data="admin:grant"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )


def about_commands_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(locale, "about_show_commands"), callback_data="about:commands")],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )


def broadcast_confirm_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "broadcast_confirm"), callback_data="admin:broadcast_confirm"),
                InlineKeyboardButton(text=t(locale, "broadcast_cancel"), callback_data="admin:broadcast_cancel"),
            ]
        ]
    )


def settings_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(locale, "settings_btn_language"),
                    callback_data="settings:language",
                ),
                InlineKeyboardButton(
                    text=t(locale, "settings_btn_profile"),
                    callback_data="settings:profile",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(locale, "settings_btn_daily"),
                    callback_data="settings:daily",
                ),
                InlineKeyboardButton(
                    text=t(locale, "settings_btn_help"),
                    callback_data="settings:help",
                ),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )


def home_panel_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "btn_today"), callback_data="nav:horo"),
                InlineKeyboardButton(text=t(locale, "btn_moon"), callback_data="nav:moon"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "btn_natal"), callback_data="nav:natal"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "btn_ref"), callback_data="nav:ref"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "btn_prefs"), callback_data="nav:settings"),
                InlineKeyboardButton(text=t(locale, "btn_about"), callback_data="nav:about"),
            ],
        ]
    )


def breadcrumb(locale: str, *parts: str) -> str:
    return " > ".join([t(locale, "crumb_root"), *parts])


async def render_inline_panel(
    callback: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    if callback.message is None:
        return
    try:
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.answer(text=text, reply_markup=keyboard)


async def edit_or_send(
    callback: CallbackQuery,
    text: str,
    *,
    inline_keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    if callback.message is None:
        return
    if inline_keyboard is not None:
        try:
            await callback.message.edit_text(text=text, reply_markup=inline_keyboard)
            return
        except TelegramBadRequest:
            pass
    await callback.message.answer(text=text, reply_markup=inline_keyboard)


def get_locale(profile_language: str | None) -> str:
    return profile_language if profile_language in TEXTS else "en"


def t(locale: str, key: str, **kwargs: str) -> str:
    template = TEXTS[locale][key]
    return template.format(**kwargs) if kwargs else template


def _normalize_menu_text(text: str) -> str:
    # Remove emoji/punctuation noise so buttons work in different visual variants.
    cleaned = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().casefold()
    return cleaned


def _menu_action_from_text(text: str) -> str | None:
    normalized = _normalize_menu_text(text)

    aliases: dict[str, set[str]] = {
        "today": {
            "гороскоп",
            "horoscope",
        },
        "profile": {
            "профиль",
            "profile",
        },
        "language": {
            "язык",
            "language",
        },
        "help": {
            "помощь",
            "help",
        },
        "back": {
            "назад",
            "back",
        },
        "about": {
            "о боте",
            "about",
        },
        "prefs": {
            "preferences",
            "preferences",
            "настройки",
        },
        "compat": {
            "совместимость",
            "compatibility",
        },
        "moon": {
            "лунный календарь",
            "moon calendar",
        },
        "natal": {
            "натальная карта",
            "natal",
            "natal chart",
        },
        "restart": {
            "заполнить профиль заново",
            "refill profile",
            "restart",
        },
    }

    for action, words in aliases.items():
        if normalized in words:
            return action
    return None


def get_sign_name(sign: str | None, locale: str) -> str:
    if not sign:
        return "Unknown" if locale == "en" else "Неизвестно"
    sign_map = SIGN_RU if locale == "ru" else SIGN_EN
    return sign_map.get(sign, sign)


async def get_user_locale(user_id: int) -> str:
    profile = await db.get_user(user_id)
    return get_locale(profile.language if profile else None)


async def detect_locale_for_user(user_id: int, telegram_language_code: str | None) -> str:
    profile = await db.get_user(user_id)
    if profile and profile.language in TEXTS:
        return profile.language
    if telegram_language_code in TEXTS:
        return telegram_language_code
    return "en"


def _target_date_from_day_month(day_month: str, today: datetime) -> datetime | None:
    try:
        day_str, month_str = day_month.split(".")
        day = int(day_str)
        month = int(month_str)
    except ValueError:
        return None

    for year in [today.year, today.year + 1]:
        try:
            candidate = datetime(year, month, day)
        except ValueError:
            continue
        if 0 <= (candidate.date() - today.date()).days < 30:
            return candidate
    return None


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    payload = ""
    text = (message.text or "").strip()
    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            payload = parts[1].strip()

    existing_profile = await db.get_user(user.id)
    if existing_profile is None:
        default_lang = "ru" if (user.language_code or "").startswith("ru") else "en"
        await db.upsert_user_identity(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            language=default_lang,
        )
        await db.ensure_ref_code(user.id)
        if payload.startswith("ref_"):
            ref_code = payload[4:]
            inviter_id = await db.get_user_id_by_ref_code(ref_code)
            if inviter_id is None:
                await message.answer(t(default_lang, "ref_invalid"))
            else:
                linked = await db.set_referrer_if_empty(user.id, inviter_id)
                if linked:
                    await message.answer(t(default_lang, "ref_attached"))
        await state.clear()
        await message.answer(
            "Выбери язык / Choose language:",
            reply_markup=language_keyboard(prefix="startlang"),
        )
        return

    language = await detect_locale_for_user(user.id, user.language_code)
    await db.upsert_user_identity(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language=language,
    )
    await db.ensure_ref_code(user.id)
    if payload.startswith("ref_"):
        ref_code = payload[4:]
        inviter_id = await db.get_user_id_by_ref_code(ref_code)
        if inviter_id is None:
            await message.answer(t(language, "ref_invalid"))
        else:
            linked = await db.set_referrer_if_empty(user.id, inviter_id)
            if linked:
                await message.answer(t(language, "ref_attached"))
    await state.clear()
    if existing_profile.birth_date is None:
        await state.set_state(ProfileSetup.waiting_birth_date)
        await message.answer(t(language, "welcome"), reply_markup=home_panel_keyboard(language))
    else:
        await message.answer(t(language, "start_home"), reply_markup=home_panel_keyboard(language))


@router.callback_query(F.data.startswith("startlang:"))
async def start_language_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return

    lang = (callback.data or "").split(":")[-1]
    if lang not in TEXTS:
        lang = "en"

    await db.upsert_user_identity(user.id, user.username, user.first_name, lang)
    await db.set_user_language(user.id, lang)
    await state.clear()
    await state.set_state(ProfileSetup.waiting_birth_date)

    await callback.answer()
    await edit_or_send(callback, t(lang, "welcome"), inline_keyboard=home_panel_keyboard(lang))


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(t(locale, "help"), reply_markup=home_panel_keyboard(locale))


@router.message(Command("about"))
async def about_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_about'))}\n\n{t(locale, 'about_block')}",
        reply_markup=about_commands_keyboard(locale),
    )


@router.callback_query(F.data == "about:commands")
async def about_commands_callback(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await callback.answer()
    await edit_or_send(callback, t(locale, "help"), inline_keyboard=home_panel_keyboard(locale))


@router.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(t(locale, "menu_hint"), reply_markup=home_panel_keyboard(locale))


@router.message(Command("ref"))
async def ref_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    ref_code = await db.ensure_ref_code(user.id)
    count = await db.get_referral_count(user.id)
    me = await message.bot.get_me()
    username = me.username or ""
    link = f"https://t.me/{username}?start=ref_{ref_code}" if username else f"ref_{ref_code}"
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'ref_title'))}\n\n"
        f"{t(locale, 'ref_text', link=link, count=str(count))}",
        reply_markup=home_panel_keyboard(locale),
    )


@router.message(Command("language"))
async def language_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_language'))}\n\n"
        f"{t(locale, 'choose_language')}",
        reply_markup=language_keyboard(prefix="lang"),
    )


@router.message(Command("settings"))
async def settings_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_settings'))}\n\n{t(locale, 'settings_hint')}",
        reply_markup=settings_keyboard(locale),
    )


@router.callback_query(F.data.startswith("settings:"))
async def settings_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    action = (callback.data or "").split(":")[-1]
    await callback.answer()
    if callback.message is None:
        return

    if action == "back":
        await edit_or_send(callback, t(locale, "menu_hint"), inline_keyboard=home_panel_keyboard(locale))
        return
    if action == "language":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_language'))}\n\n"
            f"{t(locale, 'choose_language')}",
            language_keyboard(prefix="lang"),
        )
        return
    if action == "profile":
        await state.clear()
        await state.set_state(PreferencesSetup.waiting_gender)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_profile_setup'))}\n\n"
            f"{t(locale, 'choose_gender')}",
            prefs_gender_keyboard(locale),
        )
        return
    if action == "daily":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'))}\n\n{t(locale, 'daily_usage')}",
            settings_keyboard(locale),
        )
        return
    if action == "help":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'))}\n\n{t(locale, 'help')}",
            settings_keyboard(locale),
        )
        return
@router.callback_query(F.data.startswith("nav:"))
async def universal_nav_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    action = (callback.data or "").split(":")[-1]
    await callback.answer()
    if callback.message is None:
        return
    if action == "home":
        await state.clear()
        await edit_or_send(callback, t(locale, "menu_hint"), inline_keyboard=home_panel_keyboard(locale))
        return
    if action == "settings":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'))}\n\n{t(locale, 'settings_hint')}",
            settings_keyboard(locale),
        )
        return
    if action == "moon":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n{t(locale, 'choose_moon_period')}",
            moon_period_keyboard(locale),
        )
        return
    if action == "horo":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n{t(locale, 'choose_horoscope_period')}",
            horoscope_period_keyboard(locale),
        )
        return
    if action == "admin":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'admin_panel')}",
            admin_panel_keyboard(locale),
        )
        return
    if action == "about":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_about'))}\n\n{t(locale, 'about_block')}",
            about_commands_keyboard(locale),
        )
        return
    if action == "ref":
        ref_code = await db.ensure_ref_code(user.id)
        count = await db.get_referral_count(user.id)
        me = await callback.bot.get_me()
        username = me.username or ""
        link = f"https://t.me/{username}?start=ref_{ref_code}" if username else f"ref_{ref_code}"
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'ref_title'))}\n\n"
            f"{t(locale, 'ref_text', link=link, count=str(count))}",
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")]
                ]
            ),
        )
        return
    if action == "natal":
        text, keyboard = await render_natal_for_user(user.id, locale)
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return


    if action == "daily":
        await edit_or_send(callback, t(locale, "daily_usage"), inline_keyboard=settings_keyboard(locale))
        return
    if action == "help":
        await edit_or_send(callback, t(locale, "help"), inline_keyboard=settings_keyboard(locale))
        return


@router.callback_query(F.data.startswith("lang:"))
async def language_callback_handler(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return

    lang = (callback.data or "").split(":")[-1]
    if lang not in TEXTS:
        lang = "en"

    await db.upsert_user_identity(user.id, user.username, user.first_name, lang)
    await db.set_user_language(user.id, lang)
    await callback.answer()
    await edit_or_send(callback, t(lang, "language_updated"), inline_keyboard=settings_keyboard(lang))


@router.message(Command("profile"))
async def profile_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None:
        await message.answer(t(locale, "profile_not_found"), reply_markup=home_panel_keyboard(locale))
        return

    if not profile.birth_date:
        await message.answer(t(locale, "profile_incomplete"), reply_markup=home_panel_keyboard(locale))
        return

    birth_time = (
        profile.birth_time.isoformat(timespec="minutes")
        if profile.birth_time
        else t(locale, "unknown_time")
    )
    sign_name = get_sign_name(profile.sign, locale)
    birth_date_text = (
        profile.birth_date.strftime("%d.%m.%Y") if locale == "ru" else profile.birth_date.isoformat()
    )
    await message.answer(
        f"{t(locale, 'profile_title')}\n"
        f"{t(locale, 'profile_date')}: {birth_date_text}\n"
        f"{t(locale, 'profile_time')}: {birth_time}\n"
        f"{t(locale, 'profile_city')}: {profile.city}\n"
        f"{t(locale, 'profile_sign')}: {sign_name}",
        reply_markup=home_panel_keyboard(locale),
    )


@router.message(Command("today"))
async def today_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await message.answer(t(locale, "complete_profile_first"), reply_markup=home_panel_keyboard(locale))
        return

    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n{t(locale, 'choose_horoscope_period')}",
        reply_markup=horoscope_period_keyboard(locale),
    )


async def _send_period_horoscope(
    message: Message,
    locale: str,
    sign: str,
    period: str,
) -> None:
    sign_name = get_sign_name(sign, locale)
    if period == "week":
        header = t(locale, "week_header", sign=sign_name)
    elif period == "month":
        header = t(locale, "month_header", sign=sign_name)
    else:
        header = t(locale, "today_header", sign=sign_name)

    horoscope_text = generate_horoscope(sign=sign, locale=locale, period=period)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n{header}\n{horoscope_text}",
        reply_markup=horoscope_period_keyboard(locale),
    )


async def render_natal_for_user(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    return await render_natal_for_user_mode(user_id, locale, mode="full")


async def render_natal_for_user_mode(
    user_id: int,
    locale: str,
    mode: str = "full",
) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    if profile is None or profile.birth_date is None or not profile.sign:
        return t(locale, "natal_profile_missing"), home_panel_keyboard(locale)
    sign_name = get_sign_name(profile.sign, locale)
    profile_mode = "short" if profile.natal_mode == "short" else "full"
    normalized_mode = profile_mode if mode == "auto" else ("short" if mode == "short" else "full")
    text = build_natal_summary(
        locale=locale,
        sign_name=sign_name,
        sign_key=profile.sign,
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        city=profile.city or "-",
        relationship_status=profile.relationship_status,
        goal=profile.goal,
        mood_score=profile.mood_score,
        mode=normalized_mode,
    )
    return (
        f"{breadcrumb(locale, t(locale, 'natal_header'))}\n\n{text}",
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t(locale, "natal_mode_short"),
                        callback_data="natal:mode:short",
                    ),
                    InlineKeyboardButton(
                        text=t(locale, "natal_mode_full"),
                        callback_data="natal:mode:full",
                    ),
                ],
                [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
            ]
        ),
    )


@router.callback_query(F.data.startswith("horo:"))
async def horoscope_period_callback_handler(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await callback.answer()
        await edit_or_send(
            callback,
            t(locale, "complete_profile_first"),
            inline_keyboard=home_panel_keyboard(locale),
        )
        return

    period = (callback.data or "").split(":")[-1]
    if period == "back":
        await callback.answer()
        await edit_or_send(callback, t(locale, "menu_hint"), inline_keyboard=home_panel_keyboard(locale))
        return

    if period not in {"day", "week", "month"}:
        period = "day"

    await callback.answer()
    if callback.message:
        await _send_period_horoscope(
            message=callback.message,
            locale=locale,
            sign=profile.sign,
            period=period,
        )


@router.message(Command("compat"))
async def compat_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await message.answer(t(locale, "complete_profile_first"), reply_markup=home_panel_keyboard(locale))
        return

    await state.clear()
    await state.set_state(CompatibilityCheck.waiting_partner_birth_date)
    mode_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "compat_mode_love"), callback_data="compatmode:love"),
                InlineKeyboardButton(
                    text=t(locale, "compat_mode_friendship"), callback_data="compatmode:friendship"
                ),
                InlineKeyboardButton(text=t(locale, "compat_mode_work"), callback_data="compatmode:work"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )
    await state.update_data(compat_mode="love")
    await message.answer(t(locale, "choose_compat_mode"), reply_markup=mode_keyboard)
    await message.answer(
        t(locale, "ask_compat_date"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
            ]
        ),
    )


@router.callback_query(F.data.startswith("compatmode:"))
async def compat_mode_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    mode = (callback.data or "").split(":")[-1]
    if mode not in {"love", "friendship", "work"}:
        mode = "love"
    await state.update_data(compat_mode=mode)
    await callback.answer()
    await edit_or_send(
        callback,
        t(locale, "compat_mode_saved", mode=mode),
        inline_keyboard=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
            ]
        ),
    )


@router.message(Command("moon"))
async def moon_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n{t(locale, 'choose_moon_period')}",
        reply_markup=moon_period_keyboard(locale),
    )


@router.message(Command("natal"))
async def natal_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    text, keyboard = await render_natal_for_user_mode(user.id, locale, mode="auto")
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("natal:mode:"))
async def natal_mode_callback_handler(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    mode = (callback.data or "").split(":")[-1]
    await db.set_natal_mode(user.id, mode)
    await callback.answer()
    text, keyboard = await render_natal_for_user_mode(user.id, locale, mode=mode)
    await edit_or_send(callback, text, inline_keyboard=keyboard)


@router.callback_query(F.data.startswith("moon:"))
async def moon_period_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    action = (callback.data or "").split(":")[-1]
    await callback.answer()

    if callback.message is None:
        return

    if action == "back":
        await state.clear()
        await edit_or_send(callback, t(locale, "menu_hint"), inline_keyboard=home_panel_keyboard(locale))
        return

    if action == "7":
        text = generate_moon_table_text(locale=locale, days=7)
    elif action == "30":
        text = generate_moon_compact_table_text(locale=locale, days=30)
        details_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t(locale, "moon_details_day"), callback_data="moon:details")],
                [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:moon")],
            ]
        )
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n{t(locale, 'moon_header')}\n\n{text}",
            details_keyboard,
        )
        return
    elif action == "details":
        await state.set_state(MoonDetails.waiting_day_month)
        await edit_or_send(
            callback,
            t(locale, "ask_moon_day_month"),
            inline_keyboard=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:moon")],
                ]
            ),
        )
        return
    else:
        text = generate_moon_calendar_text(locale=locale)

    await edit_or_send(
        callback,
        f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n{t(locale, 'moon_header')}\n\n{text}",
        inline_keyboard=moon_period_keyboard(locale),
    )


@router.message(MoonDetails.waiting_day_month)
async def moon_details_day_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    raw_text = (message.text or "").strip()
    if not re.match(r"^\d{2}\.\d{2}$", raw_text):
        await message.answer(t(locale, "invalid_day_month"), reply_markup=moon_period_keyboard(locale))
        return

    target = _target_date_from_day_month(raw_text, datetime.now())
    if target is None:
        await message.answer(t(locale, "moon_date_out_of_range"), reply_markup=moon_period_keyboard(locale))
        return

    text = generate_moon_calendar_text(locale=locale, for_date=target.date())
    await state.clear()
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n{t(locale, 'moon_header')}\n\n{text}",
        reply_markup=moon_period_keyboard(locale),
    )


@router.message(Command("mood"))
async def mood_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    raw = (message.text or "").strip().split()
    if len(raw) != 2 or not raw[1].isdigit():
        await message.answer(t(locale, "mood_invalid"), reply_markup=settings_keyboard(locale))
        return
    score = int(raw[1])
    if score < 1 or score > 10:
        await message.answer(t(locale, "mood_invalid"), reply_markup=settings_keyboard(locale))
        return
    await db.update_mood(user.id, score)
    await db.log_event(user.id, "mood_updated")
    await message.answer(t(locale, "mood_saved", score=str(score)), reply_markup=settings_keyboard(locale))


@router.message(Command("daily"))
async def daily_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    parts = (message.text or "").strip().split()
    if len(parts) < 2:
        await message.answer(t(locale, "daily_usage"), reply_markup=settings_keyboard(locale))
        return
    action = parts[1].lower()
    if action == "off":
        await db.set_daily_subscription(user.id, enabled=False)
        await db.log_event(user.id, "daily_off")
        await message.answer(t(locale, "daily_disabled"), reply_markup=settings_keyboard(locale))
        return
    if action == "on" and len(parts) == 3 and re.match(r"^\d{2}:\d{2}$", parts[2]):
        hhmm = parts[2]
        await db.set_daily_subscription(user.id, enabled=True, daily_time=hhmm, timezone_name="UTC")
        await db.log_event(user.id, "daily_on")
        await message.answer(t(locale, "daily_enabled", hhmm=hhmm), reply_markup=settings_keyboard(locale))
        return
    await message.answer(t(locale, "daily_usage"), reply_markup=settings_keyboard(locale))


@router.message(Command("prefs"))
async def prefs_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None:
        await message.answer(t(locale, "profile_not_found"), reply_markup=settings_keyboard(locale))
        return
    daily_status = f"on {profile.daily_time} UTC" if profile.daily_enabled else "off"
    mood = str(profile.mood_score) if profile.mood_score is not None else "-"
    await message.answer(
        t(
            locale,
            "prefs_text",
            gender=profile.gender or "-",
            relationship=profile.relationship_status or "-",
            goal=profile.goal or "-",
            daily_status=daily_status,
            mood=mood,
        ),
        reply_markup=settings_keyboard(locale),
    )
    await message.answer(t(locale, "prefs_start"), reply_markup=prefs_gender_keyboard(locale))


@router.message(Command("prefssetup"))
async def prefs_setup_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await state.clear()
    await state.set_state(PreferencesSetup.waiting_gender)
    await message.answer(t(locale, "choose_gender"), reply_markup=prefs_gender_keyboard(locale))


@router.callback_query(F.data.startswith("prefgender:"))
async def prefs_gender_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    gender = (callback.data or "").split(":")[-1]
    if gender not in {"m", "f", "other"}:
        gender = "other"
    await state.update_data(pref_gender=gender)
    await state.set_state(PreferencesSetup.waiting_relationship)
    await callback.answer()
    await render_inline_panel(
        callback,
        f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_profile_setup'))}\n\n"
        f"{t(locale, 'choose_relationship')}",
        prefs_relationship_keyboard(locale),
    )


@router.callback_query(F.data.startswith("prefrel:"))
async def prefs_relationship_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    relationship = (callback.data or "").split(":")[-1]
    if relationship not in {"single", "relationship"}:
        relationship = "single"
    await state.update_data(pref_relationship=relationship)
    await state.set_state(PreferencesSetup.waiting_goal)
    await callback.answer()
    await render_inline_panel(
        callback,
        f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_profile_setup'))}\n\n"
        f"{t(locale, 'choose_goal')}",
        prefs_goal_keyboard(locale),
    )


@router.callback_query(F.data.startswith("prefgoal:"))
async def prefs_goal_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    goal = (callback.data or "").split(":")[-1]
    if goal not in {"love", "career", "money", "balance"}:
        goal = "balance"
    data = await state.get_data()
    gender = data.get("pref_gender")
    relationship = data.get("pref_relationship")
    await callback.answer()
    await state.clear()
    await db.update_preferences(
        user.id,
        gender=gender,
        relationship_status=relationship,
        goal=goal,
    )
    await db.log_event(user.id, "prefs_wizard_done")
    await edit_or_send(
        callback,
        t(
            locale,
            "profile_upgrade_done",
            gender=str(gender),
            relationship=str(relationship),
            goal=goal,
        ),
        inline_keyboard=settings_keyboard(locale),
    )


@router.message(Command("setprefs"))
async def setprefs_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    parts = (message.text or "").strip().split()
    if len(parts) != 4:
        await message.answer(
            f"{t(locale, 'ask_gender')}\n{t(locale, 'ask_relationship')}\n{t(locale, 'ask_goal')}\n"
            f"Format: /setprefs m single career",
            reply_markup=settings_keyboard(locale),
        )
        return
    _, gender, relationship, goal = parts
    await db.update_preferences(
        user.id,
        gender=gender.lower(),
        relationship_status=relationship.lower(),
        goal=goal.lower(),
    )
    await db.log_event(user.id, "prefs_updated")
    await message.answer(
        t(
            locale,
            "profile_upgrade_done",
            gender=gender,
            relationship=relationship,
            goal=goal,
        ),
        reply_markup=settings_keyboard(locale),
    )


@router.message(Command("premium"))
async def premium_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile and is_premium_active(profile.premium_until):
        await message.answer(
            t(locale, "premium_active", until=profile.premium_until or "-"),
            reply_markup=settings_keyboard(locale),
        )
    else:
        await message.answer(t(locale, "premium_inactive"), reply_markup=settings_keyboard(locale))


@router.message(Command("buypremium"))
async def buy_premium_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    if not settings.enable_payments:
        await message.answer(t(locale, "payments_disabled"), reply_markup=settings_keyboard(locale))
        return
    await message.answer(
        t(locale, "premium_buy_intro", price=str(settings.premium_price_stars)),
        reply_markup=settings_keyboard(locale),
    )
    try:
        await message.answer_invoice(
            title="Astro Premium 30 days",
            description="Extended horoscope, weekly delivery and advanced compatibility.",
            payload="premium_30d",
            currency="XTR",
            prices=[LabeledPrice(label="Premium 30d", amount=settings.premium_price_stars)],
        )
        await db.log_event(user.id, "premium_invoice_sent")
    except Exception:
        await db.log_event(user.id, "premium_invoice_failed")
        await message.answer(t(locale, "premium_buy_fail"), reply_markup=settings_keyboard(locale))


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query) -> None:
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    try:
        until = datetime.now(timezone.utc) + timedelta(days=30)
        await db.set_premium_until(user.id, until.isoformat())
        await db.log_event(user.id, "premium_paid")
        await message.answer(t(locale, "premium_payment_ok"), reply_markup=settings_keyboard(locale))
    except Exception:
        await db.log_event(user.id, "premium_paid_error")
        await message.answer(t(locale, "premium_payment_error"), reply_markup=settings_keyboard(locale))


@admin_router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    stats = await db.get_stats()
    await message.answer(
        t(
            locale,
            "stats_text",
            total_users=str(stats["total_users"]),
            daily_subscribers=str(stats["daily_subscribers"]),
            premium_users=str(stats["premium_users"]),
            total_events=str(stats["total_events"]),
            total_errors=str(stats["total_errors"]),
        ),
        reply_markup=admin_panel_keyboard(locale),
    )


@admin_router.message(Command("grantpremium"))
async def grant_premium_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    parts = (message.text or "").strip().split()
    if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
        await message.answer(t(locale, "grant_usage"), reply_markup=admin_panel_keyboard(locale))
        return
    target_user_id = int(parts[1])
    days = int(parts[2])
    until = datetime.now(timezone.utc) + timedelta(days=max(1, days))
    await db.set_premium_until(target_user_id, until.isoformat())
    await db.log_event(user.id, "grantpremium")
    await message.answer(
        t(locale, "grant_done", user_id=str(target_user_id), days=str(days)),
        reply_markup=admin_panel_keyboard(locale),
    )


@admin_router.message(Command("broadcast"))
async def broadcast_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    raw_text = (message.text or "").strip()
    payload = raw_text[len("/broadcast") :].strip() if raw_text.startswith("/broadcast") else ""
    if not payload:
        await message.answer(t(locale, "broadcast_usage"), reply_markup=admin_panel_keyboard(locale))
        return

    user_ids = await db.get_all_user_ids()
    ok = 0
    fail = 0
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, payload)
            ok += 1
        except Exception as e:
            fail += 1
            await db.log_error(
                source="broadcast",
                error_type=type(e).__name__,
                message=str(e),
                context=f"user_id={uid}",
            )
    await db.log_event(user.id, "broadcast")
    await message.answer(
        t(locale, "broadcast_done", ok=str(ok), fail=str(fail)),
        reply_markup=admin_panel_keyboard(locale),
    )


@admin_router.message(Command("ping"))
async def ping_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(t(locale, "ping_text", utc=utc_now), reply_markup=admin_panel_keyboard(locale))


@admin_router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'admin_panel')}",
        reply_markup=admin_panel_keyboard(locale),
    )


@admin_router.callback_query(F.data.startswith("admin:"))
async def admin_panel_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    action = (callback.data or "").split(":")[-1]
    await callback.answer()
    if callback.message is None:
        return

    if action == "back":
        await state.clear()
        await edit_or_send(callback, t(locale, "menu_hint"), inline_keyboard=home_panel_keyboard(locale))
        return
    if action == "stats":
        stats = await db.get_stats()
        await render_inline_panel(
            callback,
            t(
                locale,
                "stats_text",
                total_users=str(stats["total_users"]),
                daily_subscribers=str(stats["daily_subscribers"]),
                premium_users=str(stats["premium_users"]),
                total_events=str(stats["total_events"]),
                total_errors=str(stats["total_errors"]),
            ),
            admin_panel_keyboard(locale),
        )
        return
    if action == "ping":
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        await render_inline_panel(
            callback,
            t(locale, "ping_text", utc=utc_now),
            admin_panel_keyboard(locale),
        )
        return
    if action == "broadcast":
        await state.set_state(AdminPanel.waiting_broadcast_text)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'admin_broadcast_prompt')}",
            admin_panel_keyboard(locale),
        )
        return
    if action == "grant":
        await state.set_state(AdminPanel.waiting_grant_input)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'admin_grant_prompt')}",
            admin_panel_keyboard(locale),
        )
        return


@admin_router.message(AdminPanel.waiting_broadcast_text)
async def admin_broadcast_input_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    payload = (message.text or "").strip()
    if not payload:
        await message.answer(t(locale, "broadcast_usage"), reply_markup=admin_panel_keyboard(locale))
        return

    await state.update_data(broadcast_payload=payload)
    await state.set_state(AdminPanel.waiting_broadcast_confirm)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'broadcast_preview', text=payload)}",
        reply_markup=admin_panel_keyboard(locale),
    )
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'broadcast_confirm_title')}",
        reply_markup=broadcast_confirm_keyboard(locale),
    )


@admin_router.callback_query(F.data == "admin:broadcast_cancel")
async def admin_broadcast_cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await state.clear()
    await callback.answer()
    if callback.message:
        await render_inline_panel(
            callback,
            t(locale, "broadcast_cancelled"),
            admin_panel_keyboard(locale),
        )


@admin_router.callback_query(F.data == "admin:broadcast_confirm")
async def admin_broadcast_confirm_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    data = await state.get_data()
    payload = (data.get("broadcast_payload") or "").strip()
    if not payload:
        await state.clear()
        await callback.answer()
        if callback.message:
            await render_inline_panel(
                callback,
                t(locale, "broadcast_usage"),
                admin_panel_keyboard(locale),
            )
        return

    user_ids = await db.get_all_user_ids()
    ok = 0
    fail = 0
    for uid in user_ids:
        try:
            await callback.message.bot.send_message(uid, payload)
            ok += 1
        except Exception as e:
            fail += 1
            await db.log_error(
                source="broadcast",
                error_type=type(e).__name__,
                message=str(e),
                context=f"user_id={uid}",
            )
    await db.log_event(user.id, "broadcast_panel")
    await state.clear()
    await callback.answer()
    if callback.message:
        await render_inline_panel(
            callback,
            t(locale, "broadcast_done", ok=str(ok), fail=str(fail)),
            admin_panel_keyboard(locale),
        )


@admin_router.message(AdminPanel.waiting_broadcast_confirm)
async def admin_broadcast_waiting_confirm(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'broadcast_confirm_title')}",
        reply_markup=broadcast_confirm_keyboard(locale),
    )


@admin_router.message(AdminPanel.waiting_grant_input)
async def admin_grant_input_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    parts = (message.text or "").strip().split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        await message.answer(t(locale, "grant_usage"), reply_markup=admin_panel_keyboard(locale))
        return
    target_user_id = int(parts[0])
    days = int(parts[1])
    until = datetime.now(timezone.utc) + timedelta(days=max(1, days))
    await db.set_premium_until(target_user_id, until.isoformat())
    await db.log_event(user.id, "grantpremium_panel")
    await state.clear()
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n"
        f"{t(locale, 'grant_done', user_id=str(target_user_id), days=str(days))}",
        reply_markup=admin_panel_keyboard(locale),
    )


@router.message(CompatibilityCheck.waiting_partner_birth_date)
async def compat_birth_date_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    raw_text = (message.text or "").strip()
    try:
        partner_birth_date = datetime.strptime(raw_text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(
            t(locale, "invalid_date"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
                ]
            ),
        )
        return

    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await state.clear()
        await message.answer(t(locale, "complete_profile_first"), reply_markup=home_panel_keyboard(locale))
        return

    data = await state.get_data()
    mode = data.get("compat_mode", "love")
    syn = build_synastry(locale, profile.sign, partner_birth_date, mode)
    await state.clear()
    await message.answer(
        t(
            locale,
            "compat_result",
            sign_a=get_sign_name(profile.sign, locale),
            sign_b=get_sign_name(syn.partner_sign, locale),
            mode=mode,
            score=str(syn.score),
            details=syn.details,
        ),
        reply_markup=home_panel_keyboard(locale),
    )


@router.message(ProfileSetup.waiting_birth_date)
async def birth_date_handler(message: Message, state: FSMContext) -> None:
    raw_text = (message.text or "").strip()
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)

    try:
        birth_date = datetime.strptime(raw_text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(t(locale, "invalid_date"))
        return

    await state.update_data(birth_date=birth_date.isoformat())
    await state.set_state(ProfileSetup.waiting_birth_time)
    await message.answer(t(locale, "ask_time"))


@router.message(ProfileSetup.waiting_birth_time)
async def birth_time_handler(message: Message, state: FSMContext) -> None:
    raw_text = (message.text or "").strip()
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)

    if raw_text == "-":
        await state.update_data(birth_time=None)
    else:
        try:
            birth_time = datetime.strptime(raw_text, "%H:%M").time()
        except ValueError:
            await message.answer(t(locale, "invalid_time"))
            return
        await state.update_data(birth_time=birth_time.isoformat(timespec="minutes"))

    await state.set_state(ProfileSetup.waiting_city)
    await message.answer(t(locale, "ask_city"))


@router.message(ProfileSetup.waiting_city)
async def city_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    city = (message.text or "").strip()
    if len(city) < 2:
        await message.answer(t(locale, "city_short"))
        return

    data = await state.get_data()
    birth_date_iso = data.get("birth_date")
    if not birth_date_iso:
        await state.clear()
        await message.answer(t(locale, "session_expired"))
        return

    birth_date = datetime.fromisoformat(birth_date_iso).date()
    birth_time_iso = data.get("birth_time")
    birth_time = datetime.strptime(birth_time_iso, "%H:%M").time() if birth_time_iso else None
    sign = zodiac_sign(birth_date)

    await db.update_profile(
        user_id=user.id,
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        sign=sign,
    )
    await db.log_event(user.id, "profile_completed")
    inviter_id = await db.reward_referral(user.id, bonus_days=7, min_events=2)
    if inviter_id is not None:
        try:
            inviter_locale = await get_user_locale(inviter_id)
            await message.bot.send_message(inviter_id, t(inviter_locale, "ref_reward_inviter"))
        except Exception:
            pass
    await state.clear()
    sign_name = get_sign_name(sign, locale)
    await message.answer(
        t(locale, "profile_saved", sign=sign_name),
        reply_markup=home_panel_keyboard(locale),
    )


@router.message(F.text)
async def fallback_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    text = (message.text or "").strip()

    action = _menu_action_from_text(text)

    if text == t(locale, "btn_today") or action == "today":
        await today_handler(message)
        return
    if text == t(locale, "btn_profile") or action == "profile":
        await profile_handler(message)
        return
    if text == t(locale, "btn_language") or action == "language":
        await language_handler(message)
        return
    if text == t(locale, "btn_help") or action == "help":
        await help_handler(message)
        return
    if text == t(locale, "btn_about") or action == "about":
        await about_handler(message)
        return
    if text == t(locale, "btn_ref") or action == "ref":
        await ref_handler(message)
        return
    if text == t(locale, "btn_prefs") or action == "prefs":
        await settings_handler(message)
        return
    if text == t(locale, "btn_compat") or action == "compat":
        await compat_handler(message, state)
        return
    if text == t(locale, "btn_moon") or action == "moon":
        await moon_handler(message)
        return
    if text == t(locale, "btn_natal") or action == "natal":
        await natal_handler(message)
        return
    if text == t(locale, "btn_restart") or action == "restart":
        await start_handler(message, state)
        return
    if text == "/menu":
        await menu_handler(message)
        return
    if text == "/help":
        await help_handler(message)
        return
    if text == "/about":
        await about_handler(message)
        return
    if text == "/settings":
        await settings_handler(message)
        return
    if text == "/today":
        await today_handler(message)
        return
    if action == "back":
        await menu_handler(message)
        return

    await message.answer(t(locale, "fallback"))


async def run_bot() -> None:
    await db.init()
    session = HttpProxyAiohttpSession(settings.proxy_url) if settings.proxy_url else None
    bot = Bot(token=settings.bot_token, session=session)
    try:
        await configure_public_profile(bot)
    except Exception as e:
        await db.log_error(
            source="configure_public_profile",
            error_type=type(e).__name__,
            message=str(e),
        )
    dp = Dispatcher(storage=MemoryStorage())
    admin_router.message.middleware(
        AdminOnlyMiddleware(
            admin_ids=settings.admin_ids,
            deny_text=TEXTS["en"]["admin_only"],
        )
    )
    dp.include_router(router)
    dp.include_router(admin_router)
    await bot.delete_webhook(drop_pending_updates=True)
    daily_task = asyncio.create_task(run_daily_loop(db, bot))
    try:
        await dp.start_polling(bot)
    except Exception as e:
        await db.log_error(
            source="run_bot",
            error_type=type(e).__name__,
            message=str(e),
        )
        raise
    finally:
        daily_task.cancel()
