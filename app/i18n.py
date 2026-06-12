"""Localized strings and text helpers."""
from app.bot_context import SIGN_EN, SIGN_RU

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
        "btn_glossary_help": "❓ Что это значит?",
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
            "• Новых за 7 дн.: {new_users_7d}\n"
            "• Новых за 30 дн.: {new_users_30d}\n"
            "• Подписок на рассылку: {daily_subscribers}\n"
            "• Premium активных: {premium_users}\n"
            "• Рефералов за 7 дн.: {referrals_7d}\n"
            "• Рефералов за 30 дн.: {referrals_30d}\n"
            "• Всего событий: {total_events}\n"
            "• Ошибок за 24 ч: {errors_24h}\n"
            "• Ошибок всего: {total_errors}"
        ),
        "stats_sources_header": "Источники (/start):",
        "stats_sources_line": "• {source}: {count}",
        "stats_source_direct": "без метки",
        "stats_errors_header": "Последние ошибки:",
        "stats_errors_line": "• {time} UTC · {source}: {error_type} — {message}",
        "stats_errors_empty": "• Записей нет",
        "home_ref_promo": "👥 Приведи друга — +7 дней Premium",
        "admin_only": "Эта команда доступна только администратору.",
        "premium_active": "Premium активен до {until}.",
        "premium_inactive": "Premium не активен. Сейчас доступен базовый режим.",
        "premium_price_line": "💫 {price} Stars · {days} дней",
        "premium_prices_header": "Способы оплаты · {days} дней:",
        "premium_choose_payment": "Выбери способ оплаты:",
        "premium_fiat_disabled": "Оплата в ₽/$ не настроена. Доступны только Stars.",
        "payments_disabled": "Платежи временно отключены.",
        "premium_buy_intro": "Premium на {days} дней — {price} Stars.",
        "premium_buy_fail": "Не удалось открыть платёж. Для ₽ нужен PAYMENT_PROVIDER_TOKEN (ЮKassa в BotFather).",
        "premium_payment_ok": "Оплата прошла. Premium активен до {until}.",
        "premium_payment_error": "Оплата не прошла, попробуй ещё раз позже.",
        "premium_trial_granted": (
            "🎁 Premium на {days} дней в подарок!\n\n"
            "Попробуй неделю и месяц, полную карту, луну на 30 дней и безлимит совместимости.\n"
            "Действует до {until}."
        ),
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
        "ping_text": "Сервис работает. UTC: {utc}\n{alerts_line}",
        "ping_alerts_ok": "Алерты: настроено {count} админ(ов), ты в списке",
        "ping_alerts_missing_env": "Алерты: ADMIN_IDS пуст — стартовые уведомления не отправляются",
        "ping_alerts_not_listed": "Алерты: ADMIN_IDS={ids}, твой id {user_id} не в списке",
        "admin_panel": "Админ-панель:",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_stars": "⭐ Stars",
        "admin_btn_broadcast": "📣 Broadcast",
        "admin_btn_grant": "🎁 Grant Premium",
        "admin_btn_users": "👥 Users",
        "admin_btn_ping": "🩺 Ping",
        "admin_users_header": "👥 Пользователи: {total} · стр. {page}/{pages}",
        "admin_users_line": "{index}. {user_id} · {username} · {name} · {sign} · {language} · {premium} · {source} · {created}",
        "admin_users_empty": "Пока нет пользователей.",
        "admin_users_prev": "◀️ Назад",
        "admin_users_next": "Вперёд ▶️",
        "admin_users_back": "← Админ-панель",
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
        "btn_glossary_help": "❓ What does this mean?",
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
            "• New in 7 days: {new_users_7d}\n"
            "• New in 30 days: {new_users_30d}\n"
            "• Daily subscribers: {daily_subscribers}\n"
            "• Active Premium: {premium_users}\n"
            "• Referrals in 7 days: {referrals_7d}\n"
            "• Referrals in 30 days: {referrals_30d}\n"
            "• Total events: {total_events}\n"
            "• Errors in 24h: {errors_24h}\n"
            "• Total errors: {total_errors}"
        ),
        "stats_sources_header": "Sources (/start):",
        "stats_sources_line": "• {source}: {count}",
        "stats_source_direct": "direct",
        "stats_errors_header": "Recent errors:",
        "stats_errors_line": "• {time} UTC · {source}: {error_type} — {message}",
        "stats_errors_empty": "• No entries",
        "home_ref_promo": "👥 Invite a friend — +7 days Premium",
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
        "premium_trial_granted": (
            "🎁 {days}-day Premium trial unlocked!\n\n"
            "Try week/month horoscopes, full chart, 30-day moon, and unlimited compatibility.\n"
            "Valid until {until}."
        ),
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
        "ping_text": "Service is up. UTC: {utc}\n{alerts_line}",
        "ping_alerts_ok": "Alerts: {count} admin(s) configured, you are listed",
        "ping_alerts_missing_env": "Alerts: ADMIN_IDS is empty — startup notifications are disabled",
        "ping_alerts_not_listed": "Alerts: ADMIN_IDS={ids}, your id {user_id} is not listed",
        "admin_panel": "Admin panel:",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_stars": "⭐ Stars",
        "admin_btn_broadcast": "📣 Broadcast",
        "admin_btn_grant": "🎁 Grant Premium",
        "admin_btn_users": "👥 Users",
        "admin_btn_ping": "🩺 Ping",
        "admin_users_header": "👥 Users: {total} · page {page}/{pages}",
        "admin_users_line": "{index}. {user_id} · {username} · {name} · {sign} · {language} · {premium} · {source} · {created}",
        "admin_users_empty": "No users yet.",
        "admin_users_prev": "◀️ Prev",
        "admin_users_next": "Next ▶️",
        "admin_users_back": "← Admin panel",
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

