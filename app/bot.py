import asyncio
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import re
from urllib.parse import quote, unquote

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, InputProfilePhotoStatic, LabeledPrice
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.config import load_settings
from app.admin_middleware import AdminOnlyMiddleware
from app.ui_cleanup_middleware import DeleteUserInputMiddleware
from app.database import Database
from app.daily_sender import run_daily_loop
from app.evening_checkin import build_evening_response
from app.fsm_storage import SQLiteFsmStorage
from app.geo import resolve_city, warm_timezone_finder
from app.horoscope import (
    build_horoscope_share_text,
    generate_home_teaser,
    generate_horoscope,
    personalization_from_profile,
)
from app.http_proxy_session import HttpProxyAiohttpSession
from app.moon_calendar import (
    generate_moon_calendar_text,
    generate_moon_compact_table_text,
    generate_moon_table_text,
)
from app.natal import build_natal_summary
from app.states import CompatibilityCheck, MoonDetails, PartnerSetup, PreferencesSetup, ProfileSetup
from app.states import AdminPanel, DailySetup
from app.payments import (
    PayCurrency,
    available_payment_options,
    get_payment_option,
    parse_premium_payload,
    premium_payload,
)
from app.premium import (
    PREMIUM_PERIOD_DAYS,
    format_premium_until,
    is_premium_active,
)
from app.synastry import build_synastry, build_synastry_for_partner_profile
from app.timezones import (
    TIMEZONE_OPTIONS,
    default_timezone_for_locale,
    normalize_timezone,
    timezone_label_with_offset,
    user_local_date_key,
)
from app.zodiac import resolve_sun_sign


router = Router()
admin_router = Router()
settings = load_settings()
db = Database(settings.database_path)
FREE_PARTNER_LIMIT = 2
PREMIUM_PARTNER_LIMIT = 10
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOT_ICON_PATH = PROJECT_ROOT / "assets" / "bot_icon.jpg"

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

SIGN_EMOJI = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
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
            "/daily - настройка ежедневной рассылки\n"
            "/prefs - персональные настройки\n"
            "/prefssetup - пошаговая настройка профиля\n"
            "/stats - статистика бота (админ)\n"
            "/stars - баланс Stars бота (админ)\n"
            "/premium - статус Premium\n"
            "/buypremium - оформить Premium (Stars / ₽ / $)\n"
            "/about - что умеет бот\n"
            "/feedback - обратная связь\n"
            "/language - сменить язык\n"
            "/menu - показать кнопки меню\n"
            "/help - список команд"
        ),
        "about_block": (
            "🌌 AstroPulse\n"
            "Карманный астролог на эфемеридах.\n\n"
            "✨ Гороскоп на сегодня — бесплатно\n"
            "💞 Совместимость с полным профилем партнёра\n"
            "🌙 Лунный календарь и ежедневные напоминания\n"
            "🪐 Натальная карта по Swiss Ephemeris\n\n"
            "⭐ Premium: неделя и месяц, полная карта, луна 30 дней, "
            "безлимит совместимости — Stars / ₽ / $\n\n"
            "🌍 RU / EN"
        ),
        "about_show_commands": "Показать все команды",
        "feedback_title": "Обратная связь",
        "feedback_text": (
            "Напиши нам — идеи, баги, вопросы по Premium и оплате Stars.\n\n"
            "Контакт: @{contact}"
        ),
        "feedback_missing": "Обратная связь пока не настроена. Напиши /help.",
        "feedback_write_button": "✉️ Написать",
        "welcome": (
            "🌙 Добро пожаловать в AstroPulse.\n"
            "Звёзды ждут твою дату рождения ✨\n\n"
            "Введи её в формате ДД.ММ.ГГГГ:"
        ),
        "start_home": "🌙 Снова здесь...\nВыбери путь среди звёзд ✨",
        "home_streak": "🔥 Серия настроения: {streak} дн. подряд",
        "home_goal": "🎯 Цель: {goal}",
        "home_goal_unset": "🎯 Цель не выбрана — нажми «Цель» ниже",
        "home_relationship": "💞 Статус: {status}",
        "home_relationship_unset": "💞 Статус не выбран — нажми «Статус» ниже",
        "choose_goal_menu": "Выбери фокус прогноза — от него зависят акценты в текстах:",
        "choose_relationship_menu": "Выбери статус отношений — от него зависят акценты в прогнозах:",
        "choose_goal_onboarding": "🎯 Выбери фокус — от него зависят акценты в прогнозах:",
        "choose_relationship_onboarding": (
            "💞 Какой у тебя статус отношений?\n\n"
            "От этого зависят акценты в прогнозе про отношения."
        ),
        "relationship_saved_toast": "Статус: {status}",
        "goal_saved_toast": "Цель: {goal}",
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
        "choose_horoscope_period_free": "Бесплатно — только прогноз на сегодня. Неделя и месяц — в Premium.",
        "share_horoscope": "📤 Поделиться прогнозом",
        "back": "⬅ Назад",
        "crumb_root": "Главная",
        "crumb_horoscope": "Гороскоп",
        "crumb_moon": "Лунный календарь",
        "crumb_settings": "Настройки",
        "crumb_language": "Язык",
        "crumb_about": "О боте",
        "crumb_admin": "Админка",
        "crumb_profile_setup": "Настройка профиля",
        "crumb_daily": "Рассылка",
        "crumb_goal": "Цель",
        "crumb_relationship": "Статус",
        "moon_header": "Лунный календарь",
        "choose_moon_period": "Выбери период лунного календаря:",
        "moon_7_days": "7 дней",
        "moon_30_days": "30 дней ⭐",
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
        "compat_choose_partner": "Выбери сохранённого партнёра или добавь нового:",
        "compat_add_partner": "➕ Добавить партнёра",
        "compat_once": "Разовая проверка — понадобятся дата, время и город рождения партнёра.",
        "compat_manage": "🗂 Управление партнёрами",
        "compat_manage_hint": "Нажми на партнёра, чтобы удалить профиль:",
        "compat_ask_name": "Как зовут партнёра? (имя или nickname)",
        "compat_name_short": "Имя слишком короткое. Введи хотя бы 2 символа.",
        "compat_name_long": "Имя слишком длинное. Максимум 40 символов.",
        "compat_partner_saved": "Партнёр «{name}» сохранён.",
        "compat_partner_deleted": "Партнёр «{name}» удалён.",
        "compat_partner_limit": "Достигнут лимит {limit} партнёров. Удали лишние в управлении.",
        "compat_partner_limit_free": (
            "Без Premium можно сохранить до {limit} партнёров. "
            "Удали лишний профиль или активируй Premium для большего числа."
        ),
        "compat_mode_for_partner": "Режим для {name}:",
        "compat_result": (
            "💞 Совместимость · {mode}\n"
            "{sign_a} + {partner_name} ({sign_b})\n"
            "Оценка: {score}/100\n\n"
            "{details}"
        ),
        "mood_saved": "Настроение сохранено: {score}/10. Серия: {streak} дн.",
        "mood_invalid": "Укажи число от 1 до 10. Пример: /mood 7",
        "daily_enabled": "Ежедневная рассылка включена на {hhmm} ({tz}).",
        "daily_disabled": "Ежедневная рассылка выключена.",
        "daily_usage": "Открой ⚙ Настройки → ⏰ Рассылка или используй кнопки ниже.",
        "daily_menu_intro": "🌙 Гороскоп каждый день в выбранное локальное время.",
        "daily_status_on": "✅ Включена · каждый день в {hhmm} ({tz})",
        "daily_status_off": "⏸ Сейчас выключена · пояс: {tz}",
        "daily_choose_time": "Нажми время, чтобы включить или изменить:",
        "daily_btn_off": "🔕 Выключить рассылку",
        "daily_btn_custom": "🕐 Своё время",
        "daily_btn_timezone": "🌍 Часовой пояс",
        "daily_choose_timezone": "Выбери часовой пояс для рассылки:",
        "daily_timezone_set": "Часовой пояс: {tz}",
        "daily_custom_prompt": "Введи время в формате ЧЧ:ММ\nНапример: 09:30",
        "daily_invalid_time": "Неверное время. Используй формат ЧЧ:ММ, например 09:30",
        "daily_time_set": "Рассылка включена на {hhmm} ({tz})",
        "daily_retention_header": "🌙 Удержание и привычки",
        "evening_status_on": "🌆 Вечерний чек-ин · {hhmm} ({tz})",
        "evening_status_off": "🌆 Вечерний чек-ин выключен",
        "evening_streak_line": "🔥 Серия: {streak} дн. подряд",
        "evening_choose_time": "Выбери время вечернего чек-ина:",
        "evening_btn_setup": "🌆 Вечерний чек-ин",
        "evening_btn_off": "🔕 Выключить вечерний чек-ин",
        "evening_time_set": "Вечерний чек-ин включён на {hhmm} ({tz})",
        "evening_disabled": "Вечерний чек-ин выключен.",
        "lunar_status_on": "🌑 Лунные напоминания: вкл (ежедневно + фазы)",
        "lunar_status_off": "🌑 Лунные напоминания: выкл",
        "lunar_btn_on": "🌑 Включить лунные напоминания",
        "lunar_btn_off": "🔕 Выключить лунные напоминания",
        "lunar_enabled_toast": "Лунные напоминания включены",
        "lunar_disabled_toast": "Лунные напоминания выключены",
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
        "premium_active": "Premium активен до {until}.",
        "premium_inactive": "Premium не активен. Сейчас доступен базовый режим.",
        "premium_price_line": "💫 {price} Stars · {days} дней",
        "premium_prices_header": "Способы оплаты · {days} дней:",
        "premium_choose_payment": "Выбери способ оплаты:",
        "premium_fiat_disabled": "Оплата в ₽/$ не настроена. Доступны только Stars.",
        "payments_disabled": "Платежи временно отключены.",
        "premium_buy_intro": "Premium на {days} дней — {price} Stars.",
        "premium_buy_fail": "Не удалось открыть платёж. Проверь, что бот поддерживает Stars.",
        "premium_payment_ok": "Оплата прошла. Premium активен до {until}.",
        "premium_payment_error": "Оплата не прошла, попробуй ещё раз позже.",
        "premium_required_full_natal": "Полная натальная карта доступна в Premium.",
        "premium_required_horo_period": "Неделя и месяц доступны в Premium.",
        "premium_required_compat_daily_limit": "Лимит бесплатных совместимостей на сегодня исчерпан ({limit}/день).",
        "premium_required_moon_30": "Лунный календарь на 30 дней и разбор по дню — в Premium.",
        "premium_menu_title": "⭐ Premium",
        "premium_features": (
            "🌠 Что откроет Premium:\n\n"
            "🪐 Полная натальная карта\n"
            "✨ Гороскоп на неделю и месяц\n"
            "💫 Совместимость без лимита · до 10 партнёров\n"
            "📬 Недельный гороскоп в авторассылке\n"
            "🌙 Напоминание о фазах за 7 дней\n"
            "📅 Лунный календарь на 30 дней"
        ),
        "premium_buy_button": "🌟 Открыть Premium",
        "premium_renew_button": "🌟 Продлить Premium",
        "grant_usage": "Используй: /grantpremium <user_id> <days>. Пример: /grantpremium 123456789 30",
        "grant_done": "Premium выдан пользователю {user_id} на {days} дн.",
        "broadcast_usage": "Используй: /broadcast текст сообщения",
        "broadcast_done": "Рассылка завершена. Успешно: {ok}, ошибок: {fail}",
        "ping_text": "Сервис работает. UTC: {utc}",
        "admin_panel": "Админ-панель:",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_stars": "⭐ Stars",
        "admin_btn_broadcast": "📣 Broadcast",
        "admin_btn_grant": "🎁 Grant Premium",
        "admin_btn_ping": "🩺 Ping",
        "stars_title": "⭐ Баланс Telegram Stars бота",
        "stars_balance": "Текущий баланс: {amount} Stars",
        "stars_withdraw_hint": "Вывод через Fragment: от 1000 ⭐, новые начисления доступны через 21 день.",
        "stars_recent_title": "Последние операции:",
        "stars_empty_tx": "Пока нет операций.",
        "stars_error": "Не удалось получить баланс Stars: {error}",
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
        "city_not_found": "Город не найден. Укажи полное название, например: Казань, Россия",
        "city_geocode_error": "Не удалось определить город. Попробуй ещё раз или укажи «Город, страна».",
        "city_checking": "Проверяю город…",
        "wizard_save_error": "Не удалось сохранить данные. Попробуй ещё раз.",
        "city_resolved": "✅ {city} · {timezone}",
        "session_expired": "Сессия истекла. Начните заново командой /start.",
        "profile_saved": (
            "Профиль сохранен.\n"
            "Ваш знак зодиака: {sign}\n"
            "Используйте /today, чтобы получить гороскоп на сегодня."
        ),
        "fallback": "Я не понял сообщение. Используйте /help, чтобы увидеть команды.",
        "choose_language": "Выберите язык:",
        "language_updated": "Язык обновлен. Теперь я говорю по-русски.",
        "menu_hint": "🔮 Что шепчут звёзды сегодня?",
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
        "btn_goal": "🎯 Цель",
        "btn_relationship": "💞 Статус",
        "btn_about": "ℹ О боте",
        "btn_ref": "👥 Рефералка",
        "btn_premium": "⭐ Premium",
        "ref_title": "Реферальная программа",
        "ref_text": (
            "Твоя ссылка:\n{link}\n\n"
            "Приглашено: {count}\n"
            "Бонус за каждого: +7 дней premium"
        ),
        "ref_invalid": "Некорректный реферальный код.",
        "ref_attached": "Реферал привязан. Заверши профиль, чтобы начислить бонус пригласившему.",
        "ref_share_button": "📤 Открыть реферальную ссылку",
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
            "/daily - daily auto-send settings\n"
            "/prefs - personal preferences\n"
            "/prefssetup - profile setup wizard\n"
            "/stats - bot stats (admin)\n"
            "/stars - bot Stars balance (admin)\n"
            "/premium - Premium status\n"
            "/buypremium - buy Premium (Stars / ₽ / $)\n"
            "/about - bot capabilities\n"
            "/feedback - contact support\n"
            "/language - change language\n"
            "/menu - show menu buttons\n"
            "/help - command list"
        ),
        "about_block": (
            "🌌 AstroPulse\n"
            "Pocket astrologer powered by ephemerides.\n\n"
            "✨ Daily horoscope — free\n"
            "💞 Compatibility with full partner profile\n"
            "🌙 Moon calendar and daily lunar reminders\n"
            "🪐 Natal chart via Swiss Ephemeris\n\n"
            "⭐ Premium: week and month, full chart, 30-day moon, "
            "unlimited compatibility — Stars / ₽ / $\n\n"
            "🌍 RU / EN"
        ),
        "about_show_commands": "Show all commands",
        "feedback_title": "Feedback",
        "feedback_text": (
            "Message us with ideas, bugs, or questions about Premium and Stars.\n\n"
            "Contact: @{contact}"
        ),
        "feedback_missing": "Feedback is not configured yet. Try /help.",
        "feedback_write_button": "✉️ Message us",
        "welcome": (
            "🌙 Welcome to AstroPulse.\n"
            "The stars await your birth date ✨\n\n"
            "Enter it as DD.MM.YYYY:"
        ),
        "start_home": "🌙 You're back...\nChoose your path among the stars ✨",
        "home_streak": "🔥 Mood streak: {streak} days in a row",
        "home_goal": "🎯 Focus: {goal}",
        "home_goal_unset": "🎯 No focus selected — tap Focus below",
        "home_relationship": "💞 Status: {status}",
        "home_relationship_unset": "💞 Status not set — tap «Status» below",
        "choose_goal_menu": "Choose your forecast focus — it shapes the highlights in your texts:",
        "choose_relationship_menu": "Choose your relationship status — it shapes relationship highlights:",
        "choose_goal_onboarding": "🎯 Choose your focus — it shapes the highlights in your forecasts:",
        "choose_relationship_onboarding": (
            "💞 What is your relationship status?\n\n"
            "It shapes the relationship highlights in your forecast."
        ),
        "relationship_saved_toast": "Status: {status}",
        "goal_saved_toast": "Focus: {goal}",
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
        "choose_horoscope_period_free": "Free — daily forecast only. Week and month are Premium.",
        "share_horoscope": "📤 Share forecast",
        "back": "⬅ Back",
        "crumb_root": "Home",
        "crumb_horoscope": "Horoscope",
        "crumb_moon": "Moon calendar",
        "crumb_settings": "Settings",
        "crumb_language": "Language",
        "crumb_about": "About",
        "crumb_admin": "Admin",
        "crumb_profile_setup": "Profile setup",
        "crumb_daily": "Daily delivery",
        "crumb_goal": "Focus",
        "crumb_relationship": "Status",
        "moon_header": "Moon calendar",
        "choose_moon_period": "Choose moon calendar period:",
        "moon_7_days": "7 days",
        "moon_30_days": "30 days ⭐",
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
        "compat_choose_partner": "Choose a saved partner or add a new one:",
        "compat_add_partner": "➕ Add partner",
        "compat_once": "One-time check — you'll need the partner's date, time, and city of birth.",
        "compat_manage": "🗂 Manage partners",
        "compat_manage_hint": "Tap a partner to delete their profile:",
        "compat_ask_name": "What is your partner's name?",
        "compat_name_short": "Name is too short. Enter at least 2 characters.",
        "compat_name_long": "Name is too long. Maximum 40 characters.",
        "compat_partner_saved": "Partner \"{name}\" saved.",
        "compat_partner_deleted": "Partner \"{name}\" deleted.",
        "compat_partner_limit": "Partner limit reached: {limit}. Remove extras in manage.",
        "compat_partner_limit_free": (
            "Without Premium you can save up to {limit} partners. "
            "Remove one or activate Premium for more profiles."
        ),
        "compat_mode_for_partner": "Mode for {name}:",
        "compat_result": (
            "💞 Compatibility · {mode}\n"
            "{sign_a} + {partner_name} ({sign_b})\n"
            "Score: {score}/100\n\n"
            "{details}"
        ),
        "mood_saved": "Mood saved: {score}/10. Streak: {streak} days.",
        "mood_invalid": "Use a number from 1 to 10. Example: /mood 7",
        "daily_enabled": "Daily delivery is enabled at {hhmm} ({tz}).",
        "daily_disabled": "Daily delivery is disabled.",
        "daily_usage": "Open ⚙ Settings → ⏰ Daily or use the buttons below.",
        "daily_menu_intro": "🌙 Your horoscope every day at a chosen local time.",
        "daily_status_on": "✅ Enabled · every day at {hhmm} ({tz})",
        "daily_status_off": "⏸ Currently disabled · timezone: {tz}",
        "daily_choose_time": "Tap a time to enable or change:",
        "daily_btn_off": "🔕 Turn off delivery",
        "daily_btn_custom": "🕐 Custom time",
        "daily_btn_timezone": "🌍 Timezone",
        "daily_choose_timezone": "Choose your delivery timezone:",
        "daily_timezone_set": "Timezone: {tz}",
        "daily_custom_prompt": "Enter time as HH:MM\nExample: 09:30",
        "daily_invalid_time": "Invalid time. Use HH:MM format, e.g. 09:30",
        "daily_time_set": "Delivery enabled at {hhmm} ({tz})",
        "daily_retention_header": "🌙 Retention & habits",
        "evening_status_on": "🌆 Evening check-in · {hhmm} ({tz})",
        "evening_status_off": "🌆 Evening check-in disabled",
        "evening_streak_line": "🔥 Streak: {streak} days in a row",
        "evening_choose_time": "Choose your evening check-in time:",
        "evening_btn_setup": "🌆 Evening check-in",
        "evening_btn_off": "🔕 Turn off evening check-in",
        "evening_time_set": "Evening check-in enabled at {hhmm} ({tz})",
        "evening_disabled": "Evening check-in disabled.",
        "lunar_status_on": "🌑 Lunar reminders: on (daily + phases)",
        "lunar_status_off": "🌑 Lunar reminders: off",
        "lunar_btn_on": "🌑 Enable lunar reminders",
        "lunar_btn_off": "🔕 Disable lunar reminders",
        "lunar_enabled_toast": "Lunar reminders enabled",
        "lunar_disabled_toast": "Lunar reminders disabled",
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
        "premium_active": "Premium active until {until}.",
        "premium_inactive": "Premium is not active. You are using base mode.",
        "premium_price_line": "💫 {price} Stars · {days} days",
        "premium_prices_header": "Payment options · {days} days:",
        "premium_choose_payment": "Choose a payment method:",
        "premium_fiat_disabled": "Card payments in ₽/$ are not configured. Stars only.",
        "payments_disabled": "Payments are temporarily disabled.",
        "premium_buy_intro": "Premium for {days} days — {price} Stars.",
        "premium_buy_fail": "Failed to open payment form. Check Stars support for your bot.",
        "premium_payment_ok": "Payment completed. Premium active until {until}.",
        "premium_payment_error": "Payment failed, please try again later.",
        "premium_required_full_natal": "Full natal chart is available in Premium.",
        "premium_required_horo_period": "Week and month horoscopes are Premium features.",
        "premium_required_compat_daily_limit": "Free compatibility limit for today is reached ({limit}/day).",
        "premium_required_moon_30": "30-day moon calendar and day details are Premium features.",
        "premium_menu_title": "⭐ Premium",
        "premium_features": (
            "🌠 What Premium unlocks:\n\n"
            "🪐 Full natal chart\n"
            "✨ Weekly and monthly horoscope\n"
            "💫 Unlimited compatibility · up to 10 partners\n"
            "📬 Weekly horoscope in daily delivery\n"
            "🌙 Lunar phase reminders 7 days ahead\n"
            "📅 30-day moon calendar"
        ),
        "premium_buy_button": "🌟 Unlock Premium",
        "premium_renew_button": "🌟 Renew Premium",
        "grant_usage": "Use: /grantpremium <user_id> <days>. Example: /grantpremium 123456789 30",
        "grant_done": "Premium granted to user {user_id} for {days} days.",
        "broadcast_usage": "Use: /broadcast message text",
        "broadcast_done": "Broadcast finished. Success: {ok}, failed: {fail}",
        "ping_text": "Service is up. UTC: {utc}",
        "admin_panel": "Admin panel:",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_stars": "⭐ Stars",
        "admin_btn_broadcast": "📣 Broadcast",
        "admin_btn_grant": "🎁 Grant Premium",
        "admin_btn_ping": "🩺 Ping",
        "stars_title": "⭐ Bot Telegram Stars balance",
        "stars_balance": "Current balance: {amount} Stars",
        "stars_withdraw_hint": "Withdraw via Fragment: from 1000 ⭐, new earnings unlock after 21 days.",
        "stars_recent_title": "Recent transactions:",
        "stars_empty_tx": "No transactions yet.",
        "stars_error": "Failed to fetch Stars balance: {error}",
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
        "city_not_found": "City not found. Try the full name, e.g. Kazan, Russia",
        "city_geocode_error": "Could not resolve the city. Try again or use “City, country”.",
        "city_checking": "Looking up the city…",
        "wizard_save_error": "Could not save your data. Please try again.",
        "city_resolved": "✅ {city} · {timezone}",
        "session_expired": "Session expired. Please restart with /start.",
        "profile_saved": (
            "Profile saved.\n"
            "Your zodiac sign is: {sign}\n"
            "Use /today for your daily horoscope."
        ),
        "fallback": "I did not understand that. Use /help to see commands.",
        "choose_language": "Choose language:",
        "language_updated": "Language updated. I will speak English now.",
        "menu_hint": "🔮 What do the stars whisper today?",
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
        "btn_goal": "🎯 Focus",
        "btn_relationship": "💞 Status",
        "btn_about": "ℹ About",
        "btn_ref": "👥 Referral",
        "btn_premium": "⭐ Premium",
        "ref_title": "Referral program",
        "ref_text": (
            "Your link:\n{link}\n\n"
            "Invited users: {count}\n"
            "Bonus per invite: +7 premium days"
        ),
        "ref_invalid": "Invalid referral code.",
        "ref_attached": "Referral linked. Complete profile to reward your inviter.",
        "ref_share_button": "📤 Open referral link",
        "ref_reward_inviter": "🎉 A new user joined via your link. +7 premium days.",
    },
}


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
        "   · полная карта и луна на 30 дней\n"
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
        "   · full chart and 30-day moon\n"
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


def horoscope_period_keyboard(
    locale: str,
    *,
    premium_active: bool = False,
    share_url: str | None = None,
) -> InlineKeyboardMarkup:
    if locale == "ru":
        day_label, week_label, month_label = "Сегодня", "Неделя", "Месяц"
    else:
        day_label, week_label, month_label = "Today", "Week", "Month"

    rows: list[list[InlineKeyboardButton]] = []
    if premium_active:
        rows.append(
            [
                InlineKeyboardButton(text=day_label, callback_data="horo:day"),
                InlineKeyboardButton(text=week_label, callback_data="horo:week"),
                InlineKeyboardButton(text=month_label, callback_data="horo:month"),
            ]
        )
    else:
        rows.append([InlineKeyboardButton(text=day_label, callback_data="horo:day")])
        rows.append(
            [
                InlineKeyboardButton(text=f"⭐ {week_label}", callback_data="horo:week"),
                InlineKeyboardButton(text=f"⭐ {month_label}", callback_data="horo:month"),
            ]
        )
    if share_url:
        rows.append([InlineKeyboardButton(text=t(locale, "share_horoscope"), url=share_url)])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def build_referral_link(bot: Bot, user_id: int) -> str:
    ref_code = await db.ensure_ref_code(user_id)
    me = await bot.get_me()
    username = me.username or ""
    if username:
        return f"https://t.me/{username}?start=ref_{ref_code}"
    return f"ref_{ref_code}"


def parse_ref_code_from_start(payload: str) -> str | None:
    raw = unquote(payload.strip())
    if not raw.lower().startswith("ref_"):
        return None
    code = raw[4:].strip()
    return code or None


async def try_notify_referral_reward(user_id: int, bot: Bot | None) -> None:
    inviter_id = await db.reward_referral(user_id, bonus_days=7)
    if inviter_id is None or bot is None:
        return
    try:
        inviter_locale = await get_user_locale(inviter_id)
        await bot.send_message(inviter_id, t(inviter_locale, "ref_reward_inviter"))
    except Exception:
        pass


async def attach_referrer_from_start(
    *,
    invited_user_id: int,
    payload: str,
    locale: str,
    bot: Bot,
) -> None:
    ref_code = parse_ref_code_from_start(payload)
    if not ref_code:
        return
    inviter_id = await db.get_user_id_by_ref_code(ref_code)
    if inviter_id is None:
        await bot.send_message(invited_user_id, t(locale, "ref_invalid"))
        return
    linked = await db.set_referrer_if_empty(invited_user_id, inviter_id)
    if not linked:
        return
    await db.log_event(invited_user_id, "ref_linked")
    await bot.send_message(invited_user_id, t(locale, "ref_attached"))
    await try_notify_referral_reward(invited_user_id, bot)


def referral_panel_keyboard(locale: str, link: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if link.startswith("https://"):
        rows.append([InlineKeyboardButton(text=t(locale, "ref_share_button"), url=link)])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_telegram_share_url(*, text: str, url: str) -> str:
    return f"https://t.me/share/url?url={quote(url, safe='')}&text={quote(text, safe='')}"


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


def onboarding_relationship_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(locale, "rel_single"),
                    callback_data="onboard:rel:single",
                ),
                InlineKeyboardButton(
                    text=t(locale, "rel_relationship"),
                    callback_data="onboard:rel:relationship",
                ),
            ],
        ]
    )


def home_relationship_keyboard(locale: str, *, back_callback: str | None = "nav:home") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=t(locale, "rel_single"), callback_data="rel:set:single"),
            InlineKeyboardButton(text=t(locale, "rel_relationship"), callback_data="rel:set:relationship"),
        ],
    ]
    if back_callback:
        rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_goal_keyboard(locale: str, *, back_callback: str | None = "nav:home") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for goal_key, text_key in GOAL_TEXT_KEYS.items():
        rows.append(
            [
                InlineKeyboardButton(
                    text=t(locale, text_key),
                    callback_data=f"goal:set:{goal_key}",
                )
            ]
        )
    if back_callback:
        rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def show_relationship_onboarding_panel(
    locale: str,
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> None:
    text = t(locale, "choose_relationship_onboarding")
    keyboard = onboarding_relationship_keyboard(locale)
    if callback is not None:
        await edit_or_send(callback, text, inline_keyboard=keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


async def show_goal_onboarding_panel(
    locale: str,
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> None:
    text = t(locale, "choose_goal_onboarding")
    keyboard = home_goal_keyboard(locale, back_callback=None)
    if callback is not None:
        await edit_or_send(callback, text, inline_keyboard=keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


async def onboarding_step_needed(user_id: int) -> str | None:
    profile = await db.get_user(user_id)
    if not profile or not profile.sign:
        return None
    if not profile.relationship_status:
        return "relationship"
    if not profile.goal:
        return "goal"
    return None


async def resume_onboarding_if_needed(
    user_id: int,
    locale: str,
    state: FSMContext,
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> bool:
    step = await onboarding_step_needed(user_id)
    if step == "relationship":
        await state.set_state(ProfileSetup.waiting_relationship)
        await show_relationship_onboarding_panel(locale, message=message, callback=callback)
        return True
    if step == "goal":
        await state.set_state(ProfileSetup.waiting_goal)
        await show_goal_onboarding_panel(locale, message=message, callback=callback)
        return True
    return False


def admin_panel_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "admin_btn_stats"), callback_data="admin:stats"),
                InlineKeyboardButton(text=t(locale, "admin_btn_stars"), callback_data="admin:stars"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "admin_btn_broadcast"), callback_data="admin:broadcast"),
                InlineKeyboardButton(text=t(locale, "admin_btn_grant"), callback_data="admin:grant"),
            ],
            [InlineKeyboardButton(text=t(locale, "admin_btn_ping"), callback_data="admin:ping")],
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


DAILY_PRESET_TIMES = ("07:00", "08:00", "09:00", "10:00", "12:00", "18:00", "21:00")
EVENING_PRESET_TIMES = ("19:00", "20:00", "21:00", "22:00")


def sign_display(locale: str, sign: str) -> str:
    if locale == "ru":
        return SIGN_RU.get(sign, sign)
    return SIGN_EN.get(sign, sign)


GOAL_TEXT_KEYS = {
    "love": "goal_love",
    "career": "goal_career",
    "money": "goal_money",
    "balance": "goal_balance",
}


def relationship_display(locale: str, status: str | None) -> str:
    if status == "single":
        return t(locale, "rel_single")
    if status == "relationship":
        return t(locale, "rel_relationship")
    return "-"


def goal_display(locale: str, goal: str | None) -> str:
    if goal in GOAL_TEXT_KEYS:
        return t(locale, GOAL_TEXT_KEYS[goal])
    return "-"


async def build_home_panel_text(user_id: int, locale: str, *, variant: str = "menu") -> str:
    base = t(locale, "start_home" if variant == "start" else "menu_hint")
    profile = await db.get_user(user_id)
    if not profile or not profile.sign:
        return base

    lines = [
        base,
        generate_home_teaser(
            profile.sign,
            locale,
            sign_label=sign_display(locale, profile.sign),
            sign_emoji=SIGN_EMOJI.get(profile.sign, ""),
            personalization=personalization_from_profile(profile),
            profile=profile,
        ),
    ]
    if profile.relationship_status:
        lines.append(
            t(locale, "home_relationship", status=relationship_display(locale, profile.relationship_status))
        )
    else:
        lines.append(t(locale, "home_relationship_unset"))
    if profile.goal:
        lines.append(t(locale, "home_goal", goal=goal_display(locale, profile.goal)))
    else:
        lines.append(t(locale, "home_goal_unset"))
    if profile.mood_streak > 0:
        lines.append(t(locale, "home_streak", streak=str(profile.mood_streak)))
    return "\n\n".join(lines)


def resolve_user_timezone(profile, locale: str) -> str:
    if profile and profile.timezone:
        return normalize_timezone(profile.timezone)
    return default_timezone_for_locale(locale)


def daily_menu_keyboard(
    locale: str,
    *,
    enabled: bool,
    current_time: str,
    lunar_enabled: bool,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index in range(0, len(DAILY_PRESET_TIMES), 3):
        row: list[InlineKeyboardButton] = []
        for hhmm in DAILY_PRESET_TIMES[index : index + 3]:
            label = f"✓ {hhmm}" if enabled and hhmm == current_time else hhmm
            row.append(
                InlineKeyboardButton(text=label, callback_data=f"daily:set:{hhmm}")
            )
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "daily_btn_timezone"),
                callback_data="daily:timezone",
            )
        ]
    )
    if enabled:
        rows.append(
            [InlineKeyboardButton(text=t(locale, "daily_btn_off"), callback_data="daily:off")]
        )
    rows.append(
        [InlineKeyboardButton(text=t(locale, "daily_btn_custom"), callback_data="daily:custom")]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "evening_btn_setup"),
                callback_data="evening:panel",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=(
                    t(locale, "lunar_btn_off")
                    if lunar_enabled
                    else t(locale, "lunar_btn_on")
                ),
                callback_data="daily:lunar:toggle",
            )
        ]
    )
    rows.append(
        [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:settings")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def evening_menu_keyboard(
    locale: str,
    *,
    enabled: bool,
    current_time: str,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index in range(0, len(EVENING_PRESET_TIMES), 2):
        row: list[InlineKeyboardButton] = []
        for hhmm in EVENING_PRESET_TIMES[index : index + 2]:
            label = f"✓ {hhmm}" if enabled and hhmm == current_time else hhmm
            row.append(
                InlineKeyboardButton(text=label, callback_data=f"evening:set:{hhmm}")
            )
        rows.append(row)
    if enabled:
        rows.append(
            [InlineKeyboardButton(text=t(locale, "evening_btn_off"), callback_data="evening:off")]
        )
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="daily:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def daily_timezone_keyboard(locale: str, current_tz: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for tz_name, labels in TIMEZONE_OPTIONS:
        label = labels.get(locale, labels["en"])
        if tz_name == current_tz:
            label = f"✓ {label}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"daily:tz:{tz_name}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="daily:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def render_daily_panel(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    enabled = bool(profile and profile.daily_enabled)
    current_time = profile.daily_time if profile else "09:00"
    current_tz = resolve_user_timezone(profile, locale)
    tz_label = timezone_label_with_offset(locale, current_tz)
    status = (
        t(locale, "daily_status_on", hhmm=current_time, tz=tz_label)
        if enabled
        else t(locale, "daily_status_off", tz=tz_label)
    )
    evening_enabled = bool(profile and profile.evening_enabled)
    evening_time = profile.evening_time if profile else "20:00"
    evening_status = (
        t(locale, "evening_status_on", hhmm=evening_time, tz=tz_label)
        if evening_enabled
        else t(locale, "evening_status_off")
    )
    lunar_enabled = bool(profile.lunar_notify_enabled) if profile else True
    lunar_status = (
        t(locale, "lunar_status_on") if lunar_enabled else t(locale, "lunar_status_off")
    )
    extra_lines = [
        "",
        t(locale, "daily_retention_header"),
        evening_status,
        lunar_status,
    ]
    if profile and profile.mood_streak > 0:
        extra_lines.append(
            t(locale, "evening_streak_line", streak=str(profile.mood_streak))
        )
    text = (
        f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_daily'))}\n\n"
        f"{t(locale, 'daily_menu_intro')}\n\n"
        f"{status}\n\n"
        f"{t(locale, 'daily_choose_time')}\n"
        f"{chr(10).join(extra_lines)}"
    )
    return text, daily_menu_keyboard(
        locale,
        enabled=enabled,
        current_time=current_time,
        lunar_enabled=lunar_enabled,
    )


async def render_evening_panel(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    enabled = bool(profile and profile.evening_enabled)
    current_time = profile.evening_time if profile else "20:00"
    current_tz = resolve_user_timezone(profile, locale)
    tz_label = timezone_label_with_offset(locale, current_tz)
    status = (
        t(locale, "evening_status_on", hhmm=current_time, tz=tz_label)
        if enabled
        else t(locale, "evening_status_off")
    )
    streak_line = ""
    if profile and profile.mood_streak > 0:
        streak_line = f"\n{t(locale, 'evening_streak_line', streak=str(profile.mood_streak))}\n"
    text = (
        f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_daily'))}\n\n"
        f"{status}{streak_line}\n"
        f"{t(locale, 'evening_choose_time')}"
    )
    return text, evening_menu_keyboard(locale, enabled=enabled, current_time=current_time)


async def render_daily_timezone_panel(user_id: int, locale: str) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    current_tz = resolve_user_timezone(profile, locale)
    tz_label = timezone_label_with_offset(locale, current_tz)
    text = (
        f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_daily'))}\n\n"
        f"{t(locale, 'daily_choose_timezone')}\n\n"
        f"{tz_label}"
    )
    return text, daily_timezone_keyboard(locale, current_tz)


async def show_daily_panel(message: Message, user_id: int, locale: str) -> None:
    text, keyboard = await render_daily_panel(user_id, locale)
    await show_panel_from_message(message, text, reply_markup=keyboard)


async def show_daily_panel_callback(callback: CallbackQuery, user_id: int, locale: str) -> None:
    text, keyboard = await render_daily_panel(user_id, locale)
    await edit_or_send(callback, text, inline_keyboard=keyboard)


def home_panel_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "btn_today"), callback_data="nav:horo"),
                InlineKeyboardButton(text=t(locale, "btn_moon"), callback_data="nav:moon"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "btn_natal"), callback_data="nav:natal"),
                InlineKeyboardButton(text=t(locale, "btn_compat"), callback_data="nav:compat"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "btn_ref"), callback_data="nav:ref"),
                InlineKeyboardButton(text=t(locale, "btn_premium"), callback_data="nav:premium"),
            ],
            [
                InlineKeyboardButton(text=t(locale, "btn_goal"), callback_data="nav:goal"),
                InlineKeyboardButton(text=t(locale, "btn_relationship"), callback_data="nav:relationship"),
            ],
            [InlineKeyboardButton(text=t(locale, "btn_prefs"), callback_data="nav:settings")],
        ]
    )


def breadcrumb(locale: str, *parts: str) -> str:
    return " > ".join([t(locale, "crumb_root"), *parts])


def premium_menu_keyboard(locale: str, *, active: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for option in available_payment_options(settings):
        label = option.button_ru if locale == "ru" else option.button_en
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"premium:pay:{option.currency.value}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def premium_payment_keyboard(locale: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for option in available_payment_options(settings):
        label = option.button_ru if locale == "ru" else option.button_en
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"premium:pay:{option.currency.value}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:premium")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def premium_upsell_keyboard(locale: str, *, back_data: str = "nav:home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(locale, "btn_premium"), callback_data="nav:premium")],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data=back_data)],
        ]
    )


_USER_PANELS: dict[int, list[tuple[int, int]]] = {}


def _save_user_panel(user_id: int, chat_id: int, message_id: int) -> None:
    key = (chat_id, message_id)
    panels = _USER_PANELS.setdefault(user_id, [])
    if key in panels:
        panels.remove(key)
    panels.append(key)


def _get_user_panel(user_id: int) -> tuple[int, int] | None:
    panels = _USER_PANELS.get(user_id)
    if not panels:
        return None
    return panels[-1]


async def _delete_user_panels(
    bot: Bot,
    user_id: int,
    *,
    keep: tuple[int, int] | None = None,
) -> None:
    panels = list(_USER_PANELS.get(user_id, []))
    for chat_id, message_id in panels:
        if keep is not None and (chat_id, message_id) == keep:
            continue
        try:
            await bot.delete_message(chat_id, message_id)
        except TelegramBadRequest:
            pass
    if keep is None:
        _USER_PANELS.pop(user_id, None)
    else:
        _USER_PANELS[user_id] = [keep]


def _is_not_modified_error(exc: TelegramBadRequest) -> bool:
    return "message is not modified" in str(exc).lower()


async def show_ui_panel(
    *,
    bot: Bot,
    user_id: int,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    edit_message: Message | None = None,
    fallback_message: Message | None = None,
) -> None:
    targets: list[tuple[int, int]] = []
    if edit_message is not None:
        targets.append((edit_message.chat.id, edit_message.message_id))
    stored = _get_user_panel(user_id)
    if stored and stored not in targets:
        targets.append(stored)

    for target_chat_id, target_msg_id in targets:
        try:
            await bot.edit_message_text(
                text=text,
                chat_id=target_chat_id,
                message_id=target_msg_id,
                reply_markup=reply_markup,
            )
            await _delete_user_panels(bot, user_id, keep=(target_chat_id, target_msg_id))
            _save_user_panel(user_id, target_chat_id, target_msg_id)
            return
        except TelegramBadRequest as exc:
            if _is_not_modified_error(exc):
                await _delete_user_panels(bot, user_id, keep=(target_chat_id, target_msg_id))
                _save_user_panel(user_id, target_chat_id, target_msg_id)
                return

    await _delete_user_panels(bot, user_id)

    try:
        sent = await bot.send_message(chat_id, text, reply_markup=reply_markup)
        _save_user_panel(user_id, sent.chat.id, sent.message_id)
        return
    except TelegramBadRequest:
        if fallback_message is not None:
            sent = await fallback_message.answer(text=text, reply_markup=reply_markup)
            _save_user_panel(user_id, sent.chat.id, sent.message_id)
            return
        raise


async def delete_user_wizard_message(message: Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def show_panel_from_message(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    *,
    prefer_new: bool = False,
) -> None:
    user = message.from_user
    if user is None:
        return
    if prefer_new:
        await _delete_user_panels(message.bot, user.id)
    try:
        await show_ui_panel(
            bot=message.bot,
            user_id=user.id,
            chat_id=message.chat.id,
            text=text,
            reply_markup=reply_markup,
            fallback_message=message,
        )
    except Exception as e:
        await db.log_error(
            source="show_panel_from_message",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id}",
        )
        await _delete_user_panels(message.bot, user.id)
        sent = await message.answer(text=text, reply_markup=reply_markup)
        _save_user_panel(user.id, sent.chat.id, sent.message_id)


async def render_inline_panel(
    callback: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    await show_ui_panel(
        bot=callback.bot,
        user_id=user.id,
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=keyboard,
        edit_message=callback.message,
    )


async def edit_or_send(
    callback: CallbackQuery,
    text: str,
    *,
    inline_keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    await show_ui_panel(
        bot=callback.bot,
        user_id=user.id,
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=inline_keyboard,
        edit_message=callback.message,
    )


def get_locale(profile_language: str | None) -> str:
    return profile_language if profile_language in TEXTS else "en"


def t(locale: str, key: str, **kwargs: str) -> str:
    template = TEXTS[locale][key]
    if not kwargs:
        return template
    safe_kwargs = {
        name: value.replace("{", "{{").replace("}", "}}")
        for name, value in kwargs.items()
    }
    return template.format(**safe_kwargs)


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


def compat_mode_label(locale: str, mode: str) -> str:
    labels = {
        "ru": {"love": "Любовь", "friendship": "Дружба", "work": "Работа"},
        "en": {"love": "Love", "friendship": "Friendship", "work": "Work"},
    }
    lang = "ru" if locale == "ru" else "en"
    return labels[lang].get(mode, mode)


def partner_profile_limit(profile) -> int:
    if profile and is_premium_active(profile.premium_until):
        return PREMIUM_PARTNER_LIMIT
    return FREE_PARTNER_LIMIT


async def geocode_city_input(message: Message, city: str):
    try:
        await message.bot.send_chat_action(message.chat.id, "typing")
    except Exception:
        pass
    return await resolve_city(city, db)


def partner_limit_text(locale: str, profile, limit: int) -> str:
    if profile and is_premium_active(profile.premium_until):
        return t(locale, "compat_partner_limit", limit=str(limit))
    return t(locale, "compat_partner_limit_free", limit=str(limit))


def partner_limit_keyboard(locale: str, profile) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if profile is None or not is_premium_active(profile.premium_until):
        rows.append([InlineKeyboardButton(text=t(locale, "btn_premium"), callback_data="nav:premium")])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def compat_daily_limit_reached(user_id: int, profile) -> bool:
    if is_premium_active(profile.premium_until):
        return False
    date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used = await db.count_events_for_day(user_id, "compat_result", date_key)
    return used >= 3


def compat_mode_keyboard(locale: str, *, back_data: str = "nav:compat") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "compat_mode_love"), callback_data="compatmode:love"),
                InlineKeyboardButton(
                    text=t(locale, "compat_mode_friendship"), callback_data="compatmode:friendship"
                ),
                InlineKeyboardButton(text=t(locale, "compat_mode_work"), callback_data="compatmode:work"),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data=back_data)],
        ]
    )


def compat_menu_keyboard(locale: str, partners) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for partner in partners:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{partner.name} · {get_sign_name(partner.sign, locale)}",
                    callback_data=f"compat:pick:{partner.id}",
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(text=t(locale, "compat_add_partner"), callback_data="compat:add")]
    )
    rows.append([InlineKeyboardButton(text=t(locale, "compat_once"), callback_data="compat:once")])
    if partners:
        rows.append([InlineKeyboardButton(text=t(locale, "compat_manage"), callback_data="compat:manage")])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def compat_manage_keyboard(locale: str, partners) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"🗑 {partner.name}",
                callback_data=f"compat:del:{partner.id}",
            )
        ]
        for partner in partners
    ]
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def compat_menu_text(locale: str, user_id: int) -> str:
    partners = await db.list_partners(user_id)
    return f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n{t(locale, 'compat_choose_partner')}"


async def show_compat_menu(*, user_id: int, locale: str, message: Message | None = None, callback: CallbackQuery | None = None) -> None:
    partners = await db.list_partners(user_id)
    text = await compat_menu_text(locale, user_id)
    keyboard = compat_menu_keyboard(locale, partners)
    if callback is not None:
        await render_inline_panel(callback, text, keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


async def show_compat_mode_panel(
    *,
    locale: str,
    intro: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    back_data: str = "nav:compat",
) -> None:
    keyboard = compat_mode_keyboard(locale, back_data=back_data)
    text = f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n{intro}\n\n{t(locale, 'choose_compat_mode')}"
    if callback is not None:
        await render_inline_panel(callback, text, keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


async def deliver_compat_result(
    *,
    user_id: int,
    locale: str,
    profile,
    syn,
    mode: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> None:
    partner_name = syn.partner_name or get_sign_name(syn.partner_sign, locale)
    result_text = t(
        locale,
        "compat_result",
        sign_a=get_sign_name(profile.sign, locale),
        partner_name=partner_name,
        sign_b=get_sign_name(syn.partner_sign, locale),
        mode=compat_mode_label(locale, mode),
        score=str(syn.score),
        details=syn.details,
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(locale, "btn_compat"), callback_data="nav:compat")],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )
    if callback is not None and callback.message is not None:
        await show_ui_panel(
            bot=callback.bot,
            user_id=user_id,
            chat_id=callback.message.chat.id,
            text=result_text,
            reply_markup=keyboard,
            edit_message=callback.message,
        )
    elif message is not None:
        await show_panel_from_message(message, result_text, reply_markup=keyboard)
    await db.log_event(user_id, "compat_result")


def compat_wizard_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
    )


async def run_once_compat_synastry(
    message: Message,
    state: FSMContext,
    *,
    locale: str,
    profile,
    partner_birth_date: date,
    partner_birth_time: time | None,
    city: str,
    location,
    mode: str,
    partner_label: str | None = None,
) -> None:
    user = message.from_user
    if user is None:
        return

    syn = build_synastry(
        locale,
        profile.sign or "",
        partner_birth_date,
        mode,
        user_birth_date=profile.birth_date,
        user_birth_time=profile.birth_time,
        user_city=profile.city,
        user_timezone=profile.timezone or "UTC",
        user_id=user.id,
        user_lat=profile.birth_lat,
        user_lon=profile.birth_lon,
        user_birth_timezone=profile.birth_timezone,
        partner_birth_time=partner_birth_time,
        partner_city=city,
        partner_timezone=location.timezone,
        partner_lat=location.lat,
        partner_lon=location.lon,
        partner_birth_timezone=location.timezone,
        partner_name=partner_label or partner_birth_date.strftime("%d.%m.%Y"),
    )
    await state.clear()
    await deliver_compat_result(
        user_id=user.id,
        locale=locale,
        profile=profile,
        syn=syn,
        mode=mode,
        message=message,
    )


async def run_saved_partner_compat(
    *,
    user_id: int,
    locale: str,
    profile,
    partner_id: int,
    mode: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    state: FSMContext | None = None,
) -> bool:
    if await compat_daily_limit_reached(user_id, profile):
        limit_text = t(locale, "premium_required_compat_daily_limit", limit="3")
        if callback is not None:
            await edit_or_send(
                callback,
                limit_text,
                inline_keyboard=premium_upsell_keyboard(locale, back_data="nav:compat"),
            )
        elif message is not None:
            await show_panel_from_message(
                message,
                limit_text,
                reply_markup=premium_upsell_keyboard(locale, back_data="nav:compat"),
            )
        return False

    partner = await db.get_partner(user_id, partner_id)
    if partner is None:
        if callback is not None:
            await show_compat_menu(user_id=user_id, locale=locale, callback=callback)
        elif message is not None:
            await show_compat_menu(user_id=user_id, locale=locale, message=message)
        return False

    syn = build_synastry_for_partner_profile(locale, profile, partner, mode)
    if state is not None:
        await state.clear()
    await deliver_compat_result(
        user_id=user_id,
        locale=locale,
        profile=profile,
        syn=syn,
        mode=mode,
        message=message,
        callback=callback,
    )
    return True


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
        if payload:
            await attach_referrer_from_start(
                invited_user_id=user.id,
                payload=payload,
                locale=default_lang,
                bot=message.bot,
            )
        await state.clear()
        lang_sent = await message.answer(
            "Выбери язык / Choose language:",
            reply_markup=language_keyboard(prefix="startlang"),
        )
        _save_user_panel(user.id, lang_sent.chat.id, lang_sent.message_id)
        return

    language = await detect_locale_for_user(user.id, user.language_code)
    await db.upsert_user_identity(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language=language,
    )
    await db.ensure_ref_code(user.id)
    if payload:
        await attach_referrer_from_start(
            invited_user_id=user.id,
            payload=payload,
            locale=language,
            bot=message.bot,
        )
    await state.clear()
    try:
        if existing_profile.birth_date is None:
            await state.set_state(ProfileSetup.waiting_birth_date)
            panel_text = t(language, "welcome")
            await show_panel_from_message(
                message,
                panel_text,
                reply_markup=home_panel_keyboard(language),
                prefer_new=True,
            )
        elif await onboarding_step_needed(user.id):
            await resume_onboarding_if_needed(
                user.id,
                language,
                state,
                message=message,
            )
        else:
            panel_text = await build_home_panel_text(user.id, language, variant="start")
            await show_panel_from_message(
                message,
                panel_text,
                reply_markup=home_panel_keyboard(language),
                prefer_new=True,
            )
    except Exception as e:
        await db.log_error(
            source="start_handler",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id}",
        )
        if existing_profile.birth_date is None:
            await state.set_state(ProfileSetup.waiting_birth_date)
            fallback_text = t(language, "welcome")
        elif await onboarding_step_needed(user.id):
            await resume_onboarding_if_needed(user.id, language, state, message=message)
            return
        else:
            fallback_text = t(language, "start_home")
        sent = await message.answer(fallback_text, reply_markup=home_panel_keyboard(language))
        _save_user_panel(user.id, sent.chat.id, sent.message_id)


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
    await show_panel_from_message(message, t(locale, "help"), reply_markup=home_panel_keyboard(locale))


@router.message(Command("about"))
async def about_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await show_panel_from_message(
        message,
        f"{breadcrumb(locale, t(locale, 'crumb_about'))}\n\n{t(locale, 'about_block')}",
        reply_markup=about_commands_keyboard(locale),
    )


@router.message(Command("feedback"))
async def feedback_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    handle = _feedback_contact_handle()
    if not handle:
        await show_panel_from_message(
            message,
            t(locale, "feedback_missing"),
            reply_markup=home_panel_keyboard(locale),
        )
        return
    await show_panel_from_message(
        message,
        f"{breadcrumb(locale, t(locale, 'feedback_title'))}\n\n"
        f"{t(locale, 'feedback_text').format(contact=handle)}",
        reply_markup=feedback_keyboard(locale),
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
async def menu_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    if await onboarding_step_needed(user.id):
        await resume_onboarding_if_needed(user.id, locale, state, message=message)
        return
    await show_panel_from_message(
        message,
        await build_home_panel_text(user.id, locale),
        reply_markup=home_panel_keyboard(locale),
        prefer_new=True,
    )


@router.message(Command("ref"))
async def ref_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    link = await build_referral_link(message.bot, user.id)
    count = await db.get_referral_count(user.id)
    await show_panel_from_message(
        message,
        f"{breadcrumb(locale, t(locale, 'ref_title'))}\n\n"
        f"{t(locale, 'ref_text', link=link, count=str(count))}",
        reply_markup=referral_panel_keyboard(locale, link),
    )


async def _premium_panel_text(user_id: int, locale: str) -> str:
    profile = await db.get_user(user_id)
    active = bool(profile and is_premium_active(profile.premium_until))
    if active and profile:
        status_text = t(
            locale,
            "premium_active",
            until=format_premium_until(profile.premium_until, locale),
        )
    else:
        status_text = t(locale, "premium_inactive")
    prices_text = _premium_prices_text(locale)
    if prices_text:
        status_text = f"{status_text}\n\n{prices_text}"
    return (
        f"{breadcrumb(locale, t(locale, 'premium_menu_title'))}\n\n"
        f"{status_text}\n\n"
        f"{t(locale, 'premium_features')}"
    )


def _premium_prices_text(locale: str) -> str:
    options = available_payment_options(settings)
    if not options:
        return ""
    lines = [t(locale, "premium_prices_header", days=str(PREMIUM_PERIOD_DAYS))]
    for option in options:
        lines.append(option.panel_ru if locale == "ru" else option.panel_en)
    return "\n".join(lines)


def _parse_pay_currency(raw: str) -> PayCurrency | None:
    try:
        return PayCurrency(raw)
    except ValueError:
        return None


async def _send_premium_invoice(
    *,
    bot: Bot,
    chat_id: int,
    user_id: int,
    locale: str,
    currency: PayCurrency,
) -> bool:
    option = get_payment_option(settings, currency)
    if option is None:
        return False
    title, description = _premium_invoice_copy(locale)
    try:
        await bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=premium_payload(currency),
            provider_token=option.provider_token,
            currency=option.telegram_currency,
            prices=[LabeledPrice(label=f"Premium {PREMIUM_PERIOD_DAYS}d", amount=option.invoice_amount)],
        )
        await db.log_event(user_id, f"premium_invoice_sent:{currency.value}")
        return True
    except Exception:
        await db.log_event(user_id, f"premium_invoice_failed:{currency.value}")
        return False


async def _start_premium_checkout(
    *,
    bot: Bot,
    chat_id: int,
    user_id: int,
    locale: str,
    currency: PayCurrency | None = None,
) -> bool | None:
    options = available_payment_options(settings)
    if not options:
        return None
    if currency is None:
        if len(options) == 1:
            currency = options[0].currency
        else:
            return False
    return await _send_premium_invoice(
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
        locale=locale,
        currency=currency,
    )


def _premium_invoice_copy(locale: str) -> tuple[str, str]:
    if locale == "ru":
        return (
            f"AstroPulse Premium · {PREMIUM_PERIOD_DAYS} дн.",
            "Натальная карта, неделя/месяц, совместимость, луна на 30 дней, напоминания за 7 дней.",
        )
    return (
        f"AstroPulse Premium · {PREMIUM_PERIOD_DAYS} days",
        "Full natal chart, week/month horoscope, compatibility, 30-day moon, 7-day lunar alerts.",
    )


@router.message(Command("language"))
async def language_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await show_panel_from_message(
        message,
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
    await show_panel_from_message(
        message,
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
        if await resume_onboarding_if_needed(user.id, locale, state, callback=callback):
            return
        await edit_or_send(
            callback,
            await build_home_panel_text(user.id, locale),
            inline_keyboard=home_panel_keyboard(locale),
        )
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
        await state.clear()
        text, keyboard = await render_daily_panel(user.id, locale)
        await render_inline_panel(callback, text, keyboard)
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
        if await resume_onboarding_if_needed(user.id, locale, state, callback=callback):
            return
        await edit_or_send(
            callback,
            await build_home_panel_text(user.id, locale),
            inline_keyboard=home_panel_keyboard(locale),
        )
        return
    if action == "goal":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_goal'))}\n\n{t(locale, 'choose_goal_menu')}",
            home_goal_keyboard(locale),
        )
        return
    if action == "relationship":
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_relationship'))}\n\n{t(locale, 'choose_relationship_menu')}",
            home_relationship_keyboard(locale),
        )
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
        if callback.message is None:
            return
        profile = await db.get_user(user.id)
        if profile is None or not profile.sign:
            await edit_or_send(
                callback,
                t(locale, "complete_profile_first"),
                inline_keyboard=home_panel_keyboard(locale),
            )
            return
        await open_horoscope_for_user(
            bot=callback.bot,
            user_id=user.id,
            locale=locale,
            message=callback.message,
        )
        return
    if action == "compat":
        profile = await db.get_user(user.id)
        if profile is None or not profile.sign:
            await edit_or_send(
                callback,
                t(locale, "complete_profile_first"),
                inline_keyboard=home_panel_keyboard(locale),
            )
            return
        await state.clear()
        await show_compat_menu(user_id=user.id, locale=locale, callback=callback)
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
        link = await build_referral_link(callback.bot, user.id)
        count = await db.get_referral_count(user.id)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'ref_title'))}\n\n"
            f"{t(locale, 'ref_text', link=link, count=str(count))}",
            referral_panel_keyboard(locale, link),
        )
        return
    if action == "premium":
        profile = await db.get_user(user.id)
        active = bool(profile and is_premium_active(profile.premium_until))
        await render_inline_panel(
            callback,
            await _premium_panel_text(user.id, locale),
            premium_menu_keyboard(locale, active=active),
        )
        return
    if action == "natal":
        text, keyboard = await render_natal_for_user(user.id, locale)
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return


    if action == "daily":
        await state.clear()
        await show_daily_panel_callback(callback, user.id, locale)
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
        await show_panel_from_message(
            message,
            t(locale, "profile_not_found"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    if not profile.birth_date:
        await show_panel_from_message(
            message,
            t(locale, "profile_incomplete"),
            reply_markup=home_panel_keyboard(locale),
        )
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
    await show_panel_from_message(
        message,
        f"{t(locale, 'profile_title')}\n"
        f"{t(locale, 'profile_date')}: {birth_date_text}\n"
        f"{t(locale, 'profile_time')}: {birth_time}\n"
        f"{t(locale, 'profile_city')}: {profile.city}\n"
        f"{t(locale, 'profile_sign')}: {sign_name}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")]
            ]
        ),
    )


@router.message(Command("today"))
async def today_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await show_panel_from_message(
            message,
            t(locale, "complete_profile_first"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    await open_horoscope_for_user(
        bot=message.bot,
        user_id=user.id,
        locale=locale,
        message=message,
    )


async def _send_period_horoscope(
    *,
    bot: Bot,
    user_id: int,
    message: Message,
    locale: str,
    sign: str,
    period: str,
    profile=None,
) -> None:
    premium_active = is_premium_active(profile.premium_until if profile else None)
    if period in {"week", "month"} and not premium_active:
        await show_ui_panel(
            bot=bot,
            user_id=user_id,
            chat_id=message.chat.id,
            text=(
                f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n"
                f"{t(locale, 'premium_required_horo_period')}\n\n"
                f"{t(locale, 'premium_features')}"
            ),
            reply_markup=premium_upsell_keyboard(locale, back_data="nav:horo"),
            edit_message=message,
        )
        return

    sign_name = get_sign_name(sign, locale)
    if period == "week":
        header = t(locale, "week_header", sign=sign_name)
    elif period == "month":
        header = t(locale, "month_header", sign=sign_name)
    else:
        header = t(locale, "today_header", sign=sign_name)

    intro = ""
    if not premium_active and period == "day":
        intro = f"{t(locale, 'choose_horoscope_period_free')}\n\n"

    horoscope_text = generate_horoscope(
        sign=sign,
        locale=locale,
        period=period,
        personalization=personalization_from_profile(profile),
        profile=profile,
    )
    share_text = build_horoscope_share_text(
        sign=sign,
        sign_name=sign_name,
        sign_emoji=SIGN_EMOJI.get(sign, ""),
        locale=locale,
        period=period,
        profile=profile,
        personalization=personalization_from_profile(profile),
    )
    share_url = None
    if share_text:
        ref_link = await build_referral_link(bot, user_id)
        share_url = build_telegram_share_url(text=share_text, url=ref_link)

    await show_ui_panel(
        bot=bot,
        user_id=user_id,
        chat_id=message.chat.id,
        text=f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n{intro}{header}\n{horoscope_text}",
        reply_markup=horoscope_period_keyboard(locale, premium_active=premium_active, share_url=share_url),
        edit_message=message,
    )


async def open_horoscope_for_user(
    *,
    bot: Bot,
    user_id: int,
    locale: str,
    message: Message,
) -> None:
    profile = await db.get_user(user_id)
    if profile is None or not profile.sign:
        await show_panel_from_message(
            message,
            t(locale, "complete_profile_first"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    premium_active = is_premium_active(profile.premium_until)
    if premium_active:
        await show_ui_panel(
            bot=bot,
            user_id=user_id,
            chat_id=message.chat.id,
            text=f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n{t(locale, 'choose_horoscope_period')}",
            reply_markup=horoscope_period_keyboard(locale, premium_active=True),
            edit_message=message,
        )
        return

    await _send_period_horoscope(
        bot=bot,
        user_id=user_id,
        message=message,
        locale=locale,
        sign=profile.sign,
        period="day",
        profile=profile,
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
    premium_active = is_premium_active(profile.premium_until)
    profile_mode = "short" if profile.natal_mode == "short" else "full"
    normalized_mode = profile_mode if mode == "auto" else ("short" if mode == "short" else "full")
    notice = ""
    if normalized_mode == "full" and not premium_active:
        normalized_mode = "short"
        notice = t(locale, "premium_required_full_natal")
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
        timezone=profile.timezone,
        lat=profile.birth_lat,
        lon=profile.birth_lon,
        birth_timezone=profile.birth_timezone,
    )
    if notice:
        text = f"{notice}\n\n{text}"
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
        await edit_or_send(
            callback,
            await build_home_panel_text(user.id, locale),
            inline_keyboard=home_panel_keyboard(locale),
        )
        return

    if period not in {"day", "week", "month"}:
        period = "day"

    premium_active = is_premium_active(profile.premium_until)
    if period in {"week", "month"} and not premium_active:
        await callback.answer()
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_horoscope'))}\n\n"
            f"{t(locale, 'premium_required_horo_period')}\n\n"
            f"{t(locale, 'premium_features')}",
            premium_upsell_keyboard(locale, back_data="nav:horo"),
        )
        return

    await callback.answer()
    if callback.message and user:
        await _send_period_horoscope(
            bot=callback.bot,
            user_id=user.id,
            message=callback.message,
            locale=locale,
            sign=profile.sign,
            period=period,
            profile=profile,
        )


@router.message(Command("compat"))
async def compat_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await show_panel_from_message(
            message,
            t(locale, "complete_profile_first"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    await state.clear()
    await show_compat_menu(user_id=user.id, locale=locale, message=message)


@router.callback_query(F.data.startswith("compat:"))
async def compat_action_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await callback.answer()
        await edit_or_send(callback, t(locale, "complete_profile_first"), inline_keyboard=home_panel_keyboard(locale))
        return

    action = (callback.data or "").split(":", 1)[1]
    await callback.answer()

    if action == "add":
        count = await db.count_partners(user.id)
        limit = partner_profile_limit(profile)
        if count >= limit:
            await render_inline_panel(
                callback,
                f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n{partner_limit_text(locale, profile, limit)}",
                partner_limit_keyboard(locale, profile),
            )
            return
        await state.clear()
        await state.set_state(PartnerSetup.waiting_name)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n{t(locale, 'compat_ask_name')}",
            InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
            ),
        )
        return

    if action == "once":
        await state.clear()
        await state.update_data(compat_mode="love", compat_partner_id=None)
        await show_compat_mode_panel(
            locale=locale,
            intro=t(locale, "compat_once"),
            callback=callback,
        )
        return

    if action == "manage":
        partners = await db.list_partners(user.id)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n{t(locale, 'compat_manage_hint')}",
            compat_manage_keyboard(locale, partners),
        )
        return

    if action.startswith("pick:"):
        partner_id = int(action.split(":", 1)[1])
        partner = await db.get_partner(user.id, partner_id)
        if partner is None:
            await show_compat_menu(user_id=user.id, locale=locale, callback=callback)
            return
        await state.update_data(compat_mode="love", compat_partner_id=partner_id)
        await show_compat_mode_panel(
            locale=locale,
            intro=t(locale, "compat_mode_for_partner", name=partner.name),
            callback=callback,
        )
        return

    if action.startswith("del:"):
        partner_id = int(action.split(":", 1)[1])
        partner = await db.get_partner(user.id, partner_id)
        if partner is None:
            await show_compat_menu(user_id=user.id, locale=locale, callback=callback)
            return
        await db.delete_partner(user.id, partner_id)
        partners = await db.list_partners(user.id)
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n"
            f"{t(locale, 'compat_partner_deleted', name=partner.name)}",
            compat_manage_keyboard(locale, partners) if partners else compat_menu_keyboard(locale, partners),
        )
        return


@router.callback_query(F.data.startswith("compatmode:"))
async def compat_mode_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await callback.answer()
        return

    mode = (callback.data or "").split(":")[-1]
    if mode not in {"love", "friendship", "work"}:
        mode = "love"
    await state.update_data(compat_mode=mode)
    await callback.answer()

    data = await state.get_data()
    partner_id = data.get("compat_partner_id")
    if partner_id is not None:
        await run_saved_partner_compat(
            user_id=user.id,
            locale=locale,
            profile=profile,
            partner_id=int(partner_id),
            mode=mode,
            callback=callback,
            state=state,
        )
        return

    await state.set_state(CompatibilityCheck.waiting_partner_birth_date)
    await edit_or_send(
        callback,
        f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n"
        f"{t(locale, 'choose_compat_mode')}\n"
        f"{t(locale, 'compat_mode_saved', mode=compat_mode_label(locale, mode))}\n\n"
        f"{t(locale, 'ask_compat_date')}",
        inline_keyboard=compat_mode_keyboard(locale),
    )


@router.message(Command("moon"))
async def moon_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    await show_panel_from_message(
        message,
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
    await show_panel_from_message(message, text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("natal:mode:"))
async def natal_mode_callback_handler(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    mode = (callback.data or "").split(":")[-1]
    profile = await db.get_user(user.id)
    if mode == "full" and profile and not is_premium_active(profile.premium_until):
        await callback.answer()
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'natal_header'))}\n\n"
            f"{t(locale, 'premium_required_full_natal')}\n\n"
            f"{t(locale, 'premium_features')}",
            premium_upsell_keyboard(locale, back_data="nav:natal"),
        )
        return
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
        await edit_or_send(
            callback,
            await build_home_panel_text(user.id, locale),
            inline_keyboard=home_panel_keyboard(locale),
        )
        return

    if action == "7":
        text = generate_moon_table_text(locale=locale, days=7)
    elif action == "30":
        profile = await db.get_user(user.id)
        if profile is None or not is_premium_active(profile.premium_until):
            await render_inline_panel(
                callback,
                f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n"
                f"{t(locale, 'premium_required_moon_30')}\n\n"
                f"{t(locale, 'premium_features')}",
                premium_upsell_keyboard(locale, back_data="nav:moon"),
            )
            return
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
        profile = await db.get_user(user.id)
        if profile is None or not is_premium_active(profile.premium_until):
            await render_inline_panel(
                callback,
                f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n"
                f"{t(locale, 'premium_required_moon_30')}\n\n"
                f"{t(locale, 'premium_features')}",
                premium_upsell_keyboard(locale, back_data="nav:moon"),
            )
            return
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
    profile = await db.get_user(user.id)
    if profile is None or not is_premium_active(profile.premium_until):
        await state.clear()
        await show_panel_from_message(
            message,
            f"{t(locale, 'premium_required_moon_30')}\n\n{t(locale, 'premium_features')}",
            reply_markup=premium_upsell_keyboard(locale, back_data="nav:moon"),
        )
        return
    raw_text = (message.text or "").strip()
    if not re.match(r"^\d{2}\.\d{2}$", raw_text):
        await show_panel_from_message(
            message,
            f"{t(locale, 'invalid_day_month')}\n\n{t(locale, 'ask_moon_day_month')}",
            reply_markup=moon_period_keyboard(locale),
        )
        return

    target = _target_date_from_day_month(raw_text, datetime.now())
    if target is None:
        await show_panel_from_message(
            message,
            f"{t(locale, 'moon_date_out_of_range')}\n\n{t(locale, 'ask_moon_day_month')}",
            reply_markup=moon_period_keyboard(locale),
        )
        return

    text = generate_moon_calendar_text(locale=locale, for_date=target.date())
    await state.clear()
    await show_panel_from_message(
        message,
        f"{breadcrumb(locale, t(locale, 'crumb_moon'))}\n\n{t(locale, 'moon_header')}\n\n{text}",
        reply_markup=moon_period_keyboard(locale),
    )


async def save_user_mood(user_id: int, locale: str, score: int) -> int:
    profile = await db.get_user(user_id)
    tz = resolve_user_timezone(profile, locale)
    local_date = user_local_date_key(datetime.now(timezone.utc), tz)
    return await db.update_mood(user_id, score, local_date_key=local_date)


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
    streak = await save_user_mood(user.id, locale, score)
    await db.log_event(user.id, "mood_updated")
    await message.answer(
        t(locale, "mood_saved", score=str(score), streak=str(streak)),
        reply_markup=settings_keyboard(locale),
    )


@router.callback_query(F.data.startswith("checkin:mood:"))
async def checkin_mood_callback_handler(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    parts = (callback.data or "").split(":")
    if len(parts) < 3 or not parts[2].isdigit():
        await callback.answer()
        return
    score = int(parts[2])
    if score < 1 or score > 10:
        await callback.answer(t(locale, "mood_invalid"))
        return

    streak = await save_user_mood(user.id, locale, score)
    await db.log_event(user.id, "evening_checkin_done")
    profile = await db.get_user(user.id)
    tz = resolve_user_timezone(profile, locale)
    local_date = date.fromisoformat(user_local_date_key(datetime.now(timezone.utc), tz))
    response_text = build_evening_response(
        locale,
        score,
        streak,
        profile=profile,
        for_date=local_date,
    )
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(response_text)


@router.callback_query(F.data.startswith("evening:"))
async def evening_settings_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    locale = await get_user_locale(user.id)
    parts = (callback.data or "").split(":")
    action = parts[1] if len(parts) > 1 else ""

    if action == "panel":
        await state.clear()
        await callback.answer()
        text, keyboard = await render_evening_panel(user.id, locale)
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return

    if action == "off":
        await db.set_evening_checkin(user.id, enabled=False)
        await db.log_event(user.id, "evening_off")
        await callback.answer(t(locale, "evening_disabled"))
        text, keyboard = await render_evening_panel(user.id, locale)
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return

    if action == "set" and len(parts) >= 4:
        hhmm = f"{parts[2]}:{parts[3]}"
        profile = await db.get_user(user.id)
        tz = resolve_user_timezone(profile, locale)
        await db.set_evening_checkin(user.id, enabled=True, evening_time=hhmm)
        await db.log_event(user.id, "evening_on")
        tz_label = timezone_label_with_offset(locale, tz)
        await callback.answer(t(locale, "evening_time_set", hhmm=hhmm, tz=tz_label))
        text, keyboard = await render_evening_panel(user.id, locale)
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return

    await callback.answer()


@router.callback_query(F.data.startswith("daily:"))
async def daily_settings_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    locale = await get_user_locale(user.id)
    parts = (callback.data or "").split(":")
    action = parts[1] if len(parts) > 1 else ""

    if action == "off":
        await db.set_daily_subscription(user.id, enabled=False)
        await db.log_event(user.id, "daily_off")
        await callback.answer(t(locale, "daily_disabled"))
        await show_daily_panel_callback(callback, user.id, locale)
        return

    if action == "set" and len(parts) >= 4:
        hhmm = f"{parts[2]}:{parts[3]}"
        profile = await db.get_user(user.id)
        tz = resolve_user_timezone(profile, locale)
        await db.set_daily_subscription(
            user.id,
            enabled=True,
            daily_time=hhmm,
            timezone_name=tz,
        )
        await db.log_event(user.id, "daily_on")
        tz_label = timezone_label_with_offset(locale, tz)
        await callback.answer(t(locale, "daily_time_set", hhmm=hhmm, tz=tz_label))
        await show_daily_panel_callback(callback, user.id, locale)
        return

    if action == "timezone":
        await state.clear()
        await callback.answer()
        text, keyboard = await render_daily_timezone_panel(user.id, locale)
        await edit_or_send(callback, text, inline_keyboard=keyboard)
        return

    if action == "tz" and len(parts) >= 3:
        tz_name = normalize_timezone(parts[2])
        await db.set_daily_timezone(user.id, tz_name)
        await db.log_event(user.id, "daily_timezone")
        tz_label = timezone_label_with_offset(locale, tz_name)
        await callback.answer(t(locale, "daily_timezone_set", tz=tz_label))
        await show_daily_panel_callback(callback, user.id, locale)
        return

    if action == "custom":
        await state.set_state(DailySetup.waiting_custom_time)
        await callback.answer()
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_daily'))}\n\n"
            f"{t(locale, 'daily_custom_prompt')}",
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(locale, "back"), callback_data="daily:panel")]
                ]
            ),
        )
        return

    if action == "lunar" and len(parts) >= 3 and parts[2] == "toggle":
        profile = await db.get_user(user.id)
        enabled_now = bool(profile.lunar_notify_enabled) if profile else True
        await db.set_lunar_notify(user.id, enabled=not enabled_now)
        await db.log_event(user.id, "lunar_notify_toggled")
        toast = (
            t(locale, "lunar_disabled_toast")
            if enabled_now
            else t(locale, "lunar_enabled_toast")
        )
        await callback.answer(toast)
        await show_daily_panel_callback(callback, user.id, locale)
        return

    if action == "panel":
        await state.clear()
        await callback.answer()
        await show_daily_panel_callback(callback, user.id, locale)
        return


@router.message(DailySetup.waiting_custom_time)
async def daily_custom_time_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    raw = (message.text or "").strip()
    if not re.match(r"^\d{2}:\d{2}$", raw):
        invalid = True
    else:
        hour_str, minute_str = raw.split(":")
        invalid = int(hour_str) > 23 or int(minute_str) > 59
    if invalid:
        await show_panel_from_message(
            message,
            f"{breadcrumb(locale, t(locale, 'crumb_settings'), t(locale, 'crumb_daily'))}\n\n"
            f"{t(locale, 'daily_custom_prompt')}\n\n"
            f"{t(locale, 'daily_invalid_time')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(locale, "back"), callback_data="daily:panel")]
                ]
            ),
        )
        return
    await state.clear()
    profile = await db.get_user(user.id)
    tz = resolve_user_timezone(profile, locale)
    await db.set_daily_subscription(
        user.id,
        enabled=True,
        daily_time=raw,
        timezone_name=tz,
    )
    await db.log_event(user.id, "daily_on")
    await show_daily_panel(message, user.id, locale)


@router.message(Command("daily"))
async def daily_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    parts = (message.text or "").strip().split()
    if len(parts) >= 3 and parts[1].lower() == "on" and re.match(r"^\d{2}:\d{2}$", parts[2]):
        profile = await db.get_user(user.id)
        tz = resolve_user_timezone(profile, locale)
        await db.set_daily_subscription(
            user.id,
            enabled=True,
            daily_time=parts[2],
            timezone_name=tz,
        )
        await db.log_event(user.id, "daily_on")
    elif len(parts) >= 2 and parts[1].lower() == "off":
        await db.set_daily_subscription(user.id, enabled=False)
        await db.log_event(user.id, "daily_off")
    await state.clear()
    await show_daily_panel(message, user.id, locale)


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
    tz_label = timezone_label_with_offset(locale, resolve_user_timezone(profile, locale))
    daily_status = f"on {profile.daily_time} ({tz_label})" if profile.daily_enabled else "off"
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


async def _complete_onboarding_with_goal(
    user_id: int,
    locale: str,
    goal: str,
    bot: Bot | None = None,
) -> None:
    await db.update_preferences(user_id, goal=goal)
    await db.log_event(user_id, "profile_completed")
    await try_notify_referral_reward(user_id, bot)


@router.callback_query(F.data.startswith("rel:set:"))
async def home_relationship_set_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    locale = await get_user_locale(user.id)
    relationship = (callback.data or "").split(":")[-1]
    if relationship not in {"single", "relationship"}:
        relationship = "single"
    status_label = t(
        locale,
        "rel_single" if relationship == "single" else "rel_relationship",
    )
    is_onboarding = await state.get_state() == ProfileSetup.waiting_relationship.state

    await state.clear()
    await db.update_preferences(user.id, relationship_status=relationship)
    await db.log_event(user.id, "relationship_set" if is_onboarding else "relationship_updated")
    await callback.answer(t(locale, "relationship_saved_toast", status=status_label))

    if is_onboarding:
        await state.set_state(ProfileSetup.waiting_goal)
        await edit_or_send(
            callback,
            t(locale, "choose_goal_onboarding"),
            inline_keyboard=home_goal_keyboard(locale, back_callback=None),
        )
        return

    await edit_or_send(
        callback,
        await build_home_panel_text(user.id, locale),
        inline_keyboard=home_panel_keyboard(locale),
    )


@router.callback_query(F.data.startswith("goal:set:"))
async def home_goal_set_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    locale = await get_user_locale(user.id)
    goal = (callback.data or "").split(":")[-1]
    if goal not in GOAL_TEXT_KEYS:
        goal = "balance"
    label = goal_display(locale, goal)
    is_onboarding = await state.get_state() == ProfileSetup.waiting_goal.state

    if is_onboarding:
        await state.clear()
        await _complete_onboarding_with_goal(user.id, locale, goal, callback.bot)
        await callback.answer(t(locale, "goal_saved_toast", goal=label))
        home_text = await build_home_panel_text(user.id, locale, variant="start")
        await edit_or_send(
            callback,
            home_text,
            inline_keyboard=home_panel_keyboard(locale),
        )
        return

    await state.clear()
    await db.update_preferences(user.id, goal=goal)
    await db.log_event(user.id, "goal_updated")
    await try_notify_referral_reward(user.id, callback.bot)
    await callback.answer(t(locale, "goal_saved_toast", goal=label))
    await edit_or_send(
        callback,
        await build_home_panel_text(user.id, locale),
        inline_keyboard=home_panel_keyboard(locale),
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
    await try_notify_referral_reward(user.id, callback.bot)
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
    await try_notify_referral_reward(user.id, message.bot)
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
    active = bool(profile and is_premium_active(profile.premium_until))
    await show_panel_from_message(
        message,
        await _premium_panel_text(user.id, locale),
        reply_markup=premium_menu_keyboard(locale, active=active),
    )


@router.message(Command("buypremium"))
async def buy_premium_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    if not available_payment_options(settings):
        await message.answer(t(locale, "payments_disabled"), reply_markup=settings_keyboard(locale))
        return
    checkout = await _start_premium_checkout(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=user.id,
        locale=locale,
    )
    if checkout is False:
        await show_panel_from_message(
            message,
            f"{t(locale, 'premium_choose_payment')}\n\n{_premium_prices_text(locale)}",
            reply_markup=premium_payment_keyboard(locale),
        )
        return
    if not checkout:
        await message.answer(t(locale, "premium_buy_fail"), reply_markup=settings_keyboard(locale))


@router.callback_query(F.data == "premium:buy")
async def premium_buy_callback(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await callback.answer()
    if callback.message is None:
        return
    profile = await db.get_user(user.id)
    active = bool(profile and is_premium_active(profile.premium_until))
    if not available_payment_options(settings):
        await render_inline_panel(
            callback,
            f"{await _premium_panel_text(user.id, locale)}\n\n{t(locale, 'payments_disabled')}",
            premium_menu_keyboard(locale, active=active),
        )
        return
    checkout = await _start_premium_checkout(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user.id,
        locale=locale,
    )
    if checkout is False:
        await render_inline_panel(
            callback,
            f"{await _premium_panel_text(user.id, locale)}\n\n{t(locale, 'premium_choose_payment')}",
            premium_payment_keyboard(locale),
        )
        return
    if not checkout:
        await render_inline_panel(
            callback,
            t(locale, "premium_buy_fail"),
            premium_menu_keyboard(locale, active=active),
        )


@router.callback_query(F.data.startswith("premium:pay:"))
async def premium_pay_callback(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    if callback.message is None:
        return
    currency = _parse_pay_currency((callback.data or "").split(":")[-1])
    if currency is None:
        await callback.answer(t(locale, "premium_buy_fail"), show_alert=True)
        return
    if not await _send_premium_invoice(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user.id,
        locale=locale,
        currency=currency,
    ):
        await callback.answer(t(locale, "premium_buy_fail"), show_alert=True)
        return
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query) -> None:
    locale = await get_user_locale(pre_checkout_query.from_user.id)
    currency = parse_premium_payload(pre_checkout_query.invoice_payload)
    option = get_payment_option(settings, currency) if currency else None
    if option is None:
        await pre_checkout_query.answer(
            ok=False,
            error_message=t(locale, "premium_payment_error"),
        )
        return
    if pre_checkout_query.currency != option.telegram_currency:
        await pre_checkout_query.answer(
            ok=False,
            error_message=t(locale, "premium_payment_error"),
        )
        return
    if pre_checkout_query.total_amount != option.invoice_amount:
        await pre_checkout_query.answer(
            ok=False,
            error_message=t(locale, "premium_payment_error"),
        )
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message) -> None:
    user = message.from_user
    if user is None or message.successful_payment is None:
        return
    locale = await get_user_locale(user.id)
    payment = message.successful_payment
    currency = parse_premium_payload(payment.invoice_payload)
    option = get_payment_option(settings, currency) if currency else None
    if option is None:
        await db.log_event(user.id, "premium_paid_invalid_payload")
        return
    if payment.currency != option.telegram_currency or payment.total_amount != option.invoice_amount:
        await db.log_event(user.id, "premium_paid_invalid_amount")
        return
    try:
        until_iso = await db.extend_premium(user.id, PREMIUM_PERIOD_DAYS)
        await db.log_event(user.id, f"premium_paid:{currency.value if currency else 'unknown'}")
        await show_panel_from_message(
            message,
            t(locale, "premium_payment_ok", until=format_premium_until(until_iso, locale)),
            reply_markup=home_panel_keyboard(locale),
        )
    except Exception:
        await db.log_event(user.id, "premium_paid_error")
        await show_panel_from_message(
            message,
            t(locale, "premium_payment_error"),
            reply_markup=home_panel_keyboard(locale),
        )


def _format_tx_datetime(value: datetime | int | float | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, datetime):
        dt = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
    return dt.strftime("%d.%m.%Y %H:%M UTC")


async def build_stars_report_text(bot: Bot, locale: str) -> str:
    try:
        if hasattr(bot, "get_my_star_balance"):
            balance = await bot.get_my_star_balance()
        else:
            from aiogram.methods import GetMyStarBalance

            balance = await bot(GetMyStarBalance())
        if hasattr(bot, "get_star_transactions"):
            tx_data = await bot.get_star_transactions(limit=10)
        else:
            from aiogram.methods import GetStarTransactions

            tx_data = await bot(GetStarTransactions(limit=10))

        lines = [
            t(locale, "stars_title"),
            t(locale, "stars_balance", amount=str(balance.amount)),
            t(locale, "stars_withdraw_hint"),
            "",
            t(locale, "stars_recent_title"),
        ]
        transactions = tx_data.transactions or []
        if not transactions:
            lines.append(t(locale, "stars_empty_tx"))
        else:
            for tx in reversed(transactions[-5:]):
                sign = "+" if tx.amount > 0 else ""
                when = _format_tx_datetime(tx.date)
                lines.append(f"• {when}: {sign}{tx.amount} ⭐")
        return "\n".join(lines)
    except Exception as exc:
        return t(locale, "stars_error", error=str(exc))


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
    until_iso = await db.extend_premium(target_user_id, max(1, days))
    await db.log_event(user.id, "grantpremium")
    await message.answer(
        t(
            locale,
            "grant_done",
            user_id=str(target_user_id),
            days=str(days),
        )
        + f"\nUntil: {format_premium_until(until_iso, locale)}",
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


@admin_router.message(Command("stars"))
async def stars_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    report = await build_stars_report_text(message.bot, locale)
    await message.answer(report, reply_markup=admin_panel_keyboard(locale))


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
        await edit_or_send(
            callback,
            await build_home_panel_text(user.id, locale),
            inline_keyboard=home_panel_keyboard(locale),
        )
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
    if action == "stars":
        report = await build_stars_report_text(callback.bot, locale)
        try:
            await render_inline_panel(callback, report, admin_panel_keyboard(locale))
        except Exception:
            if callback.message is not None:
                await callback.message.answer(report, reply_markup=admin_panel_keyboard(locale))
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
    until_iso = await db.extend_premium(target_user_id, max(1, days))
    await db.log_event(user.id, "grantpremium_panel")
    await state.clear()
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n"
        f"{t(locale, 'grant_done', user_id=str(target_user_id), days=str(days))}\n"
        f"Until: {format_premium_until(until_iso, locale)}",
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
        await show_panel_from_message(
            message,
            f"{t(locale, 'invalid_date')}\n\n{t(locale, 'ask_compat_date')}",
            reply_markup=compat_wizard_keyboard(locale),
        )
        return

    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await state.clear()
        await show_panel_from_message(
            message,
            t(locale, "complete_profile_first"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    await state.update_data(partner_birth_date=partner_birth_date.isoformat())
    await state.set_state(CompatibilityCheck.waiting_partner_birth_time)
    await show_panel_from_message(
        message,
        t(locale, "ask_time"),
        reply_markup=compat_wizard_keyboard(locale),
    )


@router.message(CompatibilityCheck.waiting_partner_birth_time)
async def compat_partner_birth_time_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    raw_text = (message.text or "").strip()
    if raw_text == "-":
        await state.update_data(partner_birth_time=None)
    else:
        try:
            birth_time = datetime.strptime(raw_text, "%H:%M").time()
        except ValueError:
            await show_panel_from_message(
                message,
                f"{t(locale, 'invalid_time')}\n\n{t(locale, 'ask_time')}",
                reply_markup=compat_wizard_keyboard(locale),
            )
            return
        await state.update_data(partner_birth_time=birth_time.isoformat(timespec="minutes"))

    await state.set_state(CompatibilityCheck.waiting_partner_city)
    await show_panel_from_message(
        message,
        t(locale, "ask_city"),
        reply_markup=compat_wizard_keyboard(locale),
    )


@router.message(CompatibilityCheck.waiting_partner_city)
async def compat_partner_city_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    if profile is None or not profile.sign:
        await state.clear()
        await show_panel_from_message(
            message,
            t(locale, "complete_profile_first"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    city = (message.text or "").strip()
    if len(city) < 2:
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_short')}\n\n{t(locale, 'ask_city')}",
            reply_markup=compat_wizard_keyboard(locale),
        )
        return

    data = await state.get_data()
    birth_date_iso = data.get("partner_birth_date")
    if not birth_date_iso:
        await state.clear()
        await show_panel_from_message(
            message,
            t(locale, "session_expired"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    mode = data.get("compat_mode", "love")
    partner_birth_date = date.fromisoformat(birth_date_iso)
    birth_time_iso = data.get("partner_birth_time")
    partner_birth_time = (
        datetime.strptime(birth_time_iso, "%H:%M").time() if birth_time_iso else None
    )

    if await compat_daily_limit_reached(user.id, profile):
        await state.clear()
        await show_panel_from_message(
            message,
            t(locale, "premium_required_compat_daily_limit", limit="3"),
            reply_markup=premium_upsell_keyboard(locale, back_data="nav:compat"),
        )
        return

    back_keyboard = compat_wizard_keyboard(locale)
    await show_panel_from_message(
        message,
        f"⏳ {t(locale, 'city_checking')}\n\n{t(locale, 'ask_city')}",
        reply_markup=back_keyboard,
    )

    try:
        location = await geocode_city_input(message, city)
    except Exception as e:
        await db.log_error(
            source="compat_partner_city_handler",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id} city={city!r}",
        )
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_geocode_error')}\n\n{t(locale, 'ask_city')}",
            reply_markup=back_keyboard,
        )
        return

    if location is None:
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_not_found')}\n\n{t(locale, 'ask_city')}",
            reply_markup=back_keyboard,
        )
        return

    await run_once_compat_synastry(
        message,
        state,
        locale=locale,
        profile=profile,
        partner_birth_date=partner_birth_date,
        partner_birth_time=partner_birth_time,
        city=city,
        location=location,
        mode=mode,
    )


@router.message(PartnerSetup.waiting_name)
async def partner_name_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    name = (message.text or "").strip()
    if len(name) < 2:
        await show_panel_from_message(
            message,
            f"{t(locale, 'compat_name_short')}\n\n{t(locale, 'compat_ask_name')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
            ),
        )
        return
    if len(name) > 40:
        await show_panel_from_message(
            message,
            f"{t(locale, 'compat_name_long')}\n\n{t(locale, 'compat_ask_name')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
            ),
        )
        return
    await state.update_data(partner_name=name)
    await state.set_state(PartnerSetup.waiting_birth_date)
    await show_panel_from_message(
        message,
        t(locale, "ask_compat_date"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
        ),
    )


@router.message(PartnerSetup.waiting_birth_date)
async def partner_birth_date_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    raw_text = (message.text or "").strip()
    try:
        birth_date = datetime.strptime(raw_text, "%d.%m.%Y").date()
    except ValueError:
        await show_panel_from_message(
            message,
            f"{t(locale, 'invalid_date')}\n\n{t(locale, 'ask_compat_date')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
            ),
        )
        return
    await state.update_data(partner_birth_date=birth_date.isoformat())
    await state.set_state(PartnerSetup.waiting_birth_time)
    await show_panel_from_message(message, t(locale, "ask_time"), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
    ))


@router.message(PartnerSetup.waiting_birth_time)
async def partner_birth_time_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    raw_text = (message.text or "").strip()
    if raw_text == "-":
        await state.update_data(partner_birth_time=None)
    else:
        try:
            birth_time = datetime.strptime(raw_text, "%H:%M").time()
        except ValueError:
            await show_panel_from_message(
                message,
                f"{t(locale, 'invalid_time')}\n\n{t(locale, 'ask_time')}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
                ),
            )
            return
        await state.update_data(partner_birth_time=birth_time.isoformat(timespec="minutes"))
    await state.set_state(PartnerSetup.waiting_city)
    await show_panel_from_message(message, t(locale, "ask_city"), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
    ))


@router.message(PartnerSetup.waiting_city)
async def partner_city_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    profile = await db.get_user(user.id)
    city = (message.text or "").strip()
    if len(city) < 2:
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_short')}\n\n{t(locale, 'ask_city')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
            ),
        )
        return

    data = await state.get_data()
    name = data.get("partner_name")
    birth_date_iso = data.get("partner_birth_date")
    if not name or not birth_date_iso:
        await state.clear()
        await show_panel_from_message(
            message,
            t(locale, "session_expired"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    birth_date = date.fromisoformat(birth_date_iso)
    birth_time_iso = data.get("partner_birth_time")
    birth_time = datetime.strptime(birth_time_iso, "%H:%M").time() if birth_time_iso else None

    count = await db.count_partners(user.id)
    limit = partner_profile_limit(profile)
    if count >= limit:
        await state.clear()
        await show_panel_from_message(
            message,
            f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n{partner_limit_text(locale, profile, limit)}",
            reply_markup=partner_limit_keyboard(locale, profile),
        )
        return

    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:compat")]]
    )
    await show_panel_from_message(
        message,
        f"⏳ {t(locale, 'city_checking')}\n\n{t(locale, 'ask_city')}",
        reply_markup=back_keyboard,
    )

    try:
        location = await geocode_city_input(message, city)
    except Exception as e:
        await db.log_error(
            source="partner_city_handler",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id} city={city!r}",
        )
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_geocode_error')}\n\n{t(locale, 'ask_city')}",
            reply_markup=back_keyboard,
        )
        return

    if location is None:
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_not_found')}\n\n{t(locale, 'ask_city')}",
            reply_markup=back_keyboard,
        )
        return

    sign = resolve_sun_sign(
        birth_date,
        birth_time,
        city=city,
        timezone_name=location.timezone,
        lat=location.lat,
        lon=location.lon,
        birth_timezone=location.timezone,
    )

    try:
        await db.add_partner(
            user.id,
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            city=city,
            tz_name=location.timezone,
            lat=location.lat,
            lon=location.lon,
            sign=sign,
        )
    except Exception as e:
        await db.log_error(
            source="partner_city_handler_save",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id} city={city!r}",
        )
        await show_panel_from_message(
            message,
            f"{t(locale, 'wizard_save_error')}\n\n{t(locale, 'ask_city')}",
            reply_markup=back_keyboard,
        )
        return

    await delete_user_wizard_message(message)
    await state.clear()
    partners = await db.list_partners(user.id)
    await show_panel_from_message(
        message,
        f"{breadcrumb(locale, t(locale, 'crumb_root'))}\n\n"
        f"{t(locale, 'city_resolved', city=location.display_name, timezone=location.timezone)}\n"
        f"{t(locale, 'compat_partner_saved', name=name)}\n\n"
        f"{t(locale, 'compat_choose_partner')}",
        reply_markup=compat_menu_keyboard(locale, partners),
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
        await show_panel_from_message(
            message,
            f"{t(locale, 'invalid_date')}\n\n{t(locale, 'welcome')}",
            reply_markup=home_panel_keyboard(locale),
        )
        return

    await state.update_data(birth_date=birth_date.isoformat())
    await state.set_state(ProfileSetup.waiting_birth_time)
    await show_panel_from_message(message, t(locale, "ask_time"), reply_markup=home_panel_keyboard(locale))


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
            await show_panel_from_message(
                message,
                f"{t(locale, 'invalid_time')}\n\n{t(locale, 'ask_time')}",
                reply_markup=home_panel_keyboard(locale),
            )
            return
        await state.update_data(birth_time=birth_time.isoformat(timespec="minutes"))

    await state.set_state(ProfileSetup.waiting_city)
    await show_panel_from_message(message, t(locale, "ask_city"), reply_markup=home_panel_keyboard(locale))


@router.message(ProfileSetup.waiting_city)
async def city_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return

    locale = await get_user_locale(user.id)
    city = (message.text or "").strip()
    if len(city) < 2:
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_short')}\n\n{t(locale, 'ask_city')}",
            reply_markup=home_panel_keyboard(locale),
        )
        return

    data = await state.get_data()
    birth_date_iso = data.get("birth_date")
    if not birth_date_iso:
        await state.clear()
        await show_panel_from_message(
            message,
            t(locale, "session_expired"),
            reply_markup=home_panel_keyboard(locale),
        )
        return

    birth_date = datetime.fromisoformat(birth_date_iso).date()
    birth_time_iso = data.get("birth_time")
    birth_time = datetime.strptime(birth_time_iso, "%H:%M").time() if birth_time_iso else None

    await show_panel_from_message(
        message,
        f"⏳ {t(locale, 'city_checking')}\n\n{t(locale, 'ask_city')}",
        reply_markup=home_panel_keyboard(locale),
    )

    try:
        location = await geocode_city_input(message, city)
    except Exception as e:
        await db.log_error(
            source="city_handler",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id} city={city!r}",
        )
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_geocode_error')}\n\n{t(locale, 'ask_city')}",
            reply_markup=home_panel_keyboard(locale),
        )
        return

    if location is None:
        await show_panel_from_message(
            message,
            f"{t(locale, 'city_not_found')}\n\n{t(locale, 'ask_city')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")]]
            ),
        )
        return

    sign = resolve_sun_sign(
        birth_date,
        birth_time,
        city=city,
        timezone_name=location.timezone,
        lat=location.lat,
        lon=location.lon,
        birth_timezone=location.timezone,
    )

    try:
        await db.update_profile(
            user_id=user.id,
            birth_date=birth_date,
            birth_time=birth_time,
            city=city,
            sign=sign,
            birth_lat=location.lat,
            birth_lon=location.lon,
            birth_timezone=location.timezone,
        )
    except Exception as e:
        await db.log_error(
            source="city_handler_save",
            error_type=type(e).__name__,
            message=str(e),
            context=f"user_id={user.id} city={city!r}",
        )
        await show_panel_from_message(
            message,
            f"{t(locale, 'wizard_save_error')}\n\n{t(locale, 'ask_city')}",
            reply_markup=home_panel_keyboard(locale),
        )
        return

    await delete_user_wizard_message(message)
    await state.set_state(ProfileSetup.waiting_relationship)
    await show_panel_from_message(
        message,
        f"{t(locale, 'city_resolved', city=location.display_name, timezone=location.timezone)}\n\n"
        f"{t(locale, 'choose_relationship_onboarding')}",
        reply_markup=onboarding_relationship_keyboard(locale),
    )


@router.message(ProfileSetup.waiting_relationship)
async def onboarding_relationship_waiting_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await show_relationship_onboarding_panel(locale, message=message)


@router.callback_query(F.data.startswith("onboard:rel:"))
async def onboarding_relationship_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None or callback.message is None:
        return
    if await state.get_state() != ProfileSetup.waiting_relationship.state:
        await callback.answer()
        return

    locale = await get_user_locale(user.id)
    relationship = (callback.data or "").split(":")[-1]
    if relationship not in {"single", "relationship"}:
        relationship = "single"
    status_label = t(
        locale,
        "rel_single" if relationship == "single" else "rel_relationship",
    )
    await db.update_preferences(user.id, relationship_status=relationship)
    await db.log_event(user.id, "relationship_set")
    await callback.answer(t(locale, "relationship_saved_toast", status=status_label))
    await state.set_state(ProfileSetup.waiting_goal)
    await show_goal_onboarding_panel(locale, callback=callback)


@router.message(ProfileSetup.waiting_goal)
async def onboarding_goal_waiting_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await show_goal_onboarding_panel(locale, message=message)


@router.message(F.text & ~F.text.startswith("/"))
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
        await menu_handler(message, state)
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
        await menu_handler(message, state)
        return

    await show_panel_from_message(
        message,
        t(locale, "fallback"),
        reply_markup=home_panel_keyboard(locale),
    )


async def run_bot() -> None:
    import logging

    logger = logging.getLogger(__name__)
    await db.init()
    session = HttpProxyAiohttpSession(settings.proxy_url) if settings.proxy_url else None
    if settings.proxy_url:
        logger.warning("BOT_PROXY is enabled: %s", settings.proxy_url)
    bot = Bot(token=settings.bot_token, session=session)
    try:
        me = await bot.get_me()
        logger.info("Connected to Telegram as @%s (id=%s)", me.username, me.id)
    except Exception as e:
        await db.log_error(
            source="startup_get_me",
            error_type=type(e).__name__,
            message=str(e),
        )
        logger.exception("Failed to connect to Telegram API on startup; polling may retry")
    try:
        await configure_public_profile(bot)
    except Exception as e:
        logger.exception("Failed to configure public profile")
        await db.log_error(
            source="configure_public_profile",
            error_type=type(e).__name__,
            message=str(e),
        )
    storage = SQLiteFsmStorage(settings.database_path)
    dp = Dispatcher(storage=storage)

    @dp.errors()
    async def on_error(event: ErrorEvent) -> None:
        import logging

        exc = event.exception
        update = event.update
        user_id = None
        chat_id = None
        if update.message and update.message.from_user:
            user_id = update.message.from_user.id
            chat_id = update.message.chat.id
        elif update.callback_query and update.callback_query.from_user:
            user_id = update.callback_query.from_user.id
            if update.callback_query.message:
                chat_id = update.callback_query.message.chat.id
        await db.log_error(
            source="dispatcher",
            error_type=type(exc).__name__,
            message=str(exc),
            context=f"user_id={user_id} update={update.update_id}",
        )
        logging.getLogger(__name__).exception("Unhandled bot error update_id=%s", update.update_id)
        if user_id is None or chat_id is None:
            return
        locale = await get_user_locale(user_id)
        try:
            await bot.send_message(
                chat_id,
                t(locale, "wizard_save_error"),
                reply_markup=home_panel_keyboard(locale),
            )
        except Exception:
            pass

    cleanup_middleware = DeleteUserInputMiddleware()
    router.message.middleware(cleanup_middleware)
    admin_router.message.middleware(cleanup_middleware)
    admin_router.message.middleware(
        AdminOnlyMiddleware(
            admin_ids=settings.admin_ids,
            deny_text=TEXTS["en"]["admin_only"],
        )
    )
    dp.include_router(admin_router)
    dp.include_router(router)
    asyncio.create_task(asyncio.to_thread(warm_timezone_finder))
    await bot.delete_webhook(drop_pending_updates=False)
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
