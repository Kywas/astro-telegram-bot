"""One-time split of app/bot.py into modules. Run from repo root."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOT_PATH = ROOT / "app" / "bot.py"
lines = BOT_PATH.read_text(encoding="utf-8").splitlines(keepends=True)


def chunk(start: int, end: int) -> str:
    return "".join(lines[start - 1 : end])


# --- i18n.py ---
(ROOT / "app" / "i18n.py").write_text(
    '"""Localized strings and text helpers."""\n'
    "from app.bot_context import SIGN_EN, SIGN_RU\n\n"
    + chunk(128, 741)
    + "\n\n"
    + chunk(1201, 1226)
    + "\n\n"
    + chunk(1720, 1732)
    + "\n",
    encoding="utf-8",
)

# --- bot_context.py ---
(ROOT / "app" / "bot_context.py").write_text(
    '"""Shared bot runtime: routers, settings, database."""\n'
    "from pathlib import Path\n\n"
    "from aiogram import Router\n\n"
    "from app.config import load_settings\n"
    "from app.database import Database\n\n"
    "router = Router()\n"
    "admin_router = Router()\n"
    "settings = load_settings()\n"
    "db = Database(settings.database_path)\n\n"
    "FREE_PARTNER_LIMIT = 2\n"
    "PREMIUM_PARTNER_LIMIT = 10\n"
    "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
    "BOT_ICON_PATH = PROJECT_ROOT / \"assets\" / \"bot_icon.jpg\"\n\n"
    + chunk(83, 126)
    + "\n"
    + chunk(1197, 1198)
    + "\n\n"
    + chunk(1207, 1212)
    + "\n",
    encoding="utf-8",
)

# --- profile_public.py ---
(ROOT / "app" / "profile_public.py").write_text(
    '"""BotFather public profile (description, short description)."""\n'
    "import logging\n\n"
    "from aiogram import Bot\n"
    "from aiogram.types import FSInputFile, InputProfilePhotoStatic\n\n"
    "from app.bot_context import BOT_ICON_PATH, settings\n\n"
    + chunk(744, 860)
    + "\n",
    encoding="utf-8",
)

# --- ui.py ---
(ROOT / "app" / "ui.py").write_text(
    '"""Inline panel UI: edit-or-send, panel tracking."""\n'
    "from aiogram import Bot\n"
    "from aiogram.exceptions import TelegramBadRequest\n"
    "from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message\n\n"
    "from app.bot_context import db\n\n"
    + chunk(1553, 1717)
    + "\n",
    encoding="utf-8",
)

# --- keyboards.py ---
(ROOT / "app" / "keyboards.py").write_text(
    '"""Inline keyboard builders."""\n'
    "from urllib.parse import quote\n\n"
    "from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup\n\n"
    "from app.bot_context import DAILY_PRESET_TIMES, EVENING_PRESET_TIMES, settings\n"
    "from app.i18n import t\n"
    "from app.payments import PayCurrency, available_payment_options\n"
    "from app.premium import PREMIUM_PERIOD_DAYS\n"
    "from app.timezones import TIMEZONE_OPTIONS, timezone_label_with_offset\n\n"
    + chunk(862, 906)
    + chunk(959, 965)
    + "\n"
    + chunk(967, 1194)
    + "\n"
    + chunk(1295, 1550)
    + "\n",
    encoding="utf-8",
)

# --- services/home.py ---
(ROOT / "app" / "services").mkdir(exist_ok=True)
(ROOT / "app" / "services" / "__init__.py").write_text("", encoding="utf-8")

(ROOT / "app" / "services" / "home.py").write_text(
    '"""Home screen and admin stats text builders."""\n'
    "from app.bot_context import db\n"
    "from app.horoscope import generate_home_teaser, personalization_from_profile\n"
    "from app.i18n import goal_display, relationship_display, sign_display, t\n"
    "from app.bot_context import SIGN_EMOJI\n\n"
    + chunk(1229, 1286)
    + "\n",
    encoding="utf-8",
)

# --- services/locale_users.py ---
(ROOT / "app" / "services" / "locale_users.py").write_text(
    '"""User locale detection."""\n'
    "from app.bot_context import db\n"
    "from app.i18n import get_locale\n\n"
    + chunk(2080, 2110)
    + "\n",
    encoding="utf-8",
)

# --- services/menu.py ---
(ROOT / "app" / "services" / "menu.py").write_text(
    '"""Reply keyboard text → action mapping."""\n'
    "import re\n\n"
    + chunk(1735, 1806)
    + "\n",
    encoding="utf-8",
)

# --- services/referral.py ---
(ROOT / "app" / "services" / "referral.py").write_text(
    '"""Referral links and start payload attachment."""\n'
    "from aiogram import Bot\n\n"
    "from app.bot_context import db\n"
    "from app.i18n import t\n"
    "from app.start_payload import parse_ref_code_from_start, parse_start_source_from_start\n"
    "from app.services.locale_users import get_user_locale\n\n"
    + chunk(908, 956)
    + "\n\n"
    + chunk(967, 969)
    + "\n",
    encoding="utf-8",
)

# --- services/daily_panels.py ---
(ROOT / "app" / "services" / "daily_panels.py").write_text(
    '"""Daily/evening settings panel renderers."""\n'
    "from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message\n\n"
    "from app.bot_context import db\n"
    "from app.i18n import t\n"
    "from app.keyboards import (\n"
    "    daily_menu_keyboard,\n"
    "    daily_timezone_keyboard,\n"
    "    evening_menu_keyboard,\n"
    ")\n"
    "from app.ui import show_panel_from_message\n"
    "from app.timezones import timezone_label_with_offset\n\n"
    + chunk(1289, 1292)
    + "\n\n"
    + chunk(1393, 1481)
    + "\n",
    encoding="utf-8",
)

# --- services/compat.py ---
(ROOT / "app" / "services" / "compat.py").write_text(
    '"""Compatibility flow helpers."""\n'
    "from datetime import datetime, timezone\n\n"
    "from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message\n\n"
    "from app.bot_context import FREE_PARTNER_LIMIT, PREMIUM_PARTNER_LIMIT, db\n"
    "from app.geo import resolve_city\n"
    "from app.i18n import t\n"
    "from app.keyboards import (\n"
    "    compat_manage_keyboard,\n"
    "    compat_menu_keyboard,\n"
    "    compat_mode_keyboard,\n"
    "    compat_wizard_keyboard,\n"
    "    premium_upsell_keyboard,\n"
    ")\n"
    "from app.premium import is_premium_active\n"
    "from app.synastry import build_synastry, build_synastry_for_partner_profile\n"
    "from app.timezones import user_local_date_key\n"
    "from app.ui import show_panel_from_message\n"
    "from app.zodiac import resolve_sun_sign\n\n"
    + chunk(1801, 2077)
    + "\n",
    encoding="utf-8",
)

# --- services/onboarding.py ---
(ROOT / "app" / "services" / "onboarding.py").write_text(
    '"""Profile onboarding wizard helpers."""\n'
    "from aiogram.fsm.context import FSMContext\n"
    "from aiogram.types import CallbackQuery, Message\n\n"
    "from app.bot_context import db\n"
    "from app.i18n import t\n"
    "from app.keyboards import home_goal_keyboard, home_relationship_keyboard\n"
    "from app.states import ProfileSetup\n"
    "from app.ui import show_panel_from_message\n\n"
    + chunk(1073, 1130)
    + "\n",
    encoding="utf-8",
)

# --- services/premium_panel.py ---
(ROOT / "app" / "services" / "premium_panel.py").write_text(
    '"""Premium menu text and checkout helpers."""\n'
    "from aiogram import Bot\n"
    "from aiogram.types import LabeledPrice, Message\n\n"
    "from app.bot_context import db, settings\n"
    "from app.i18n import t\n"
    "from app.payments import (\n"
    "    PayCurrency,\n"
    "    get_payment_option,\n"
    "    parse_premium_payload,\n"
    "    premium_payload,\n"
    ")\n"
    "from app.premium import PREMIUM_PERIOD_DAYS, format_premium_until, is_premium_active\n"
    "from app.premium_lifecycle import notify_admins_purchase\n\n"
    + chunk(2317, 2418)
    + "\n",
    encoding="utf-8",
)

# --- handlers/admin.py ---
(ROOT / "app" / "handlers").mkdir(exist_ok=True)
(ROOT / "app" / "handlers" / "__init__.py").write_text(
    '"""Register all handler modules (side-effect imports)."""\n'
    "from app.handlers import admin as _admin  # noqa: F401\n"
    "from app.handlers import user as _user  # noqa: F401\n",
    encoding="utf-8",
)

admin_header = (
    '"""Admin commands and panel."""\n'
    "from datetime import datetime, timezone\n\n"
    "from aiogram import Bot, F\n"
    "from aiogram.filters import Command\n"
    "from aiogram.fsm.context import FSMContext\n"
    "from aiogram.types import CallbackQuery, Message\n\n"
    "from app.bot_context import admin_router, db\n"
    "from app.i18n import t\n"
    "from app.keyboards import admin_panel_keyboard, broadcast_confirm_keyboard, breadcrumb, home_panel_keyboard\n"
    "from app.premium import format_premium_until\n"
    "from app.services.home import build_admin_stats_text, build_home_panel_text\n"
    "from app.services.locale_users import get_user_locale\n"
    "from app.states import AdminPanel\n"
    "from app.ui import edit_or_send, render_inline_panel\n\n"
)

(ROOT / "app" / "handlers" / "admin.py").write_text(
    admin_header + chunk(3973, 4310) + "\n",
    encoding="utf-8",
)

# --- handlers/user.py --- all @router handlers + run_bot
user_header = (
    '"""User-facing command and callback handlers."""\n'
    "import asyncio\n"
    "import logging\n"
    "import re\n"
    "from datetime import date, datetime, time, timedelta, timezone\n"
    "from urllib.parse import quote, unquote\n\n"
    "from aiogram import Bot, Dispatcher, F\n"
    "from aiogram.filters import Command, CommandStart\n"
    "from aiogram.fsm.context import FSMContext\n"
    "from aiogram.types import ErrorEvent\n"
    "from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message\n\n"
    "from app.admin_alerts import (\n"
    "    notify_admins_bot_crashed,\n"
    "    notify_admins_bot_started,\n"
    ")\n"
    "from app.admin_middleware import AdminOnlyMiddleware\n"
    "from app.bot_context import (\n"
    "    FREE_PARTNER_LIMIT,\n"
    "    PREMIUM_PARTNER_LIMIT,\n"
    "    SIGN_EMOJI,\n"
    "    admin_router,\n"
    "    db,\n"
    "    router,\n"
    "    settings,\n"
    ")\n"
    "from app.daily_sender import run_daily_loop\n"
    "from app.evening_checkin import build_evening_response\n"
    "from app.fsm_storage import SQLiteFsmStorage\n"
    "from app.geo import resolve_city, warm_timezone_finder\n"
    "from app.handlers import admin as _admin_handlers  # noqa: F401\n"
    "from app.horoscope import (\n"
    "    build_horoscope_share_text,\n"
    "    generate_horoscope,\n"
    "    personalization_from_profile,\n"
    ")\n"
    "from app.http_proxy_session import HttpProxyAiohttpSession\n"
    "from app.i18n import TEXTS, get_locale, goal_display, relationship_display, sign_display, t\n"
    "from app.keyboards import breadcrumb\n"
    "from app.keyboards import (\n"
    "    about_commands_keyboard,\n"
    "    admin_panel_keyboard,\n"
    "    compat_mode_keyboard,\n"
    "    compat_wizard_keyboard,\n"
    "    feedback_keyboard,\n"
    "    home_goal_keyboard,\n"
    "    home_panel_keyboard,\n"
    "    home_relationship_keyboard,\n"
    "    horoscope_period_keyboard,\n"
    "    language_keyboard,\n"
    "    moon_period_keyboard,\n"
    "    onboarding_relationship_keyboard,\n"
    "    prefs_gender_keyboard,\n"
    "    prefs_goal_keyboard,\n"
    "    prefs_relationship_keyboard,\n"
    "    premium_menu_keyboard,\n"
    "    premium_payment_keyboard,\n"
    "    premium_upsell_keyboard,\n"
    "    referral_panel_keyboard,\n"
    "    settings_keyboard,\n"
    ")\n"
    "from app.moon_calendar import (\n"
    "    generate_moon_calendar_text,\n"
    "    generate_moon_compact_table_text,\n"
    "    generate_moon_table_text,\n"
    ")\n"
    "from app.natal import build_natal_summary\n"
    "from app.payments import PayCurrency, parse_premium_payload\n"
    "from app.premium import PREMIUM_PERIOD_DAYS, format_premium_until, is_premium_active\n"
    "from app.premium_lifecycle import notify_admins_purchase\n"
    "from app.profile_public import configure_public_profile\n"
    "from app.services.compat import (\n"
    "    compat_daily_limit_reached,\n"
    "    compat_menu_text,\n"
    "    deliver_compat_result,\n"
    "    geocode_city_input,\n"
    "    get_sign_name,\n"
    "    partner_limit_text,\n"
    "    run_once_compat_synastry,\n"
    "    run_saved_partner_compat,\n"
    "    show_compat_menu,\n"
    "    show_compat_mode_panel,\n"
    ")\n"
    "from app.services.daily_panels import (\n"
    "    render_daily_panel,\n"
    "    render_daily_timezone_panel,\n"
    "    render_evening_panel,\n"
    "    show_daily_panel,\n"
    "    show_daily_panel_callback,\n"
    "    resolve_user_timezone,\n"
    ")\n"
    "from app.services.home import build_home_panel_text\n"
    "from app.services.locale_users import detect_locale_for_user, get_user_locale\n"
    "from app.services.menu import _menu_action_from_text\n"
    "from app.services.onboarding import (\n"
    "    onboarding_step_needed,\n"
    "    resume_onboarding_if_needed,\n"
    "    show_goal_onboarding_panel,\n"
    "    show_relationship_onboarding_panel,\n"
    ")\n"
    "from app.services.premium_panel import (\n"
    "    _parse_pay_currency,\n"
    "    _premium_invoice_copy,\n"
    "    _premium_panel_text,\n"
    "    _premium_prices_text,\n"
    "    _send_premium_invoice,\n"
    "    _start_premium_checkout,\n"
    ")\n"
    "from app.services.referral import (\n"
    "    attach_referrer_from_start,\n"
    "    attach_start_source_from_start,\n"
    "    build_referral_link,\n"
    "    build_telegram_share_url,\n"
    "    try_notify_referral_reward,\n"
    ")\n"
    "from app.states import (\n"
    "    AdminPanel,\n"
    "    CompatibilityCheck,\n"
    "    DailySetup,\n"
    "    MoonDetails,\n"
    "    PartnerSetup,\n"
    "    PreferencesSetup,\n"
    "    ProfileSetup,\n"
    ")\n"
    "from app.timezones import user_local_date_key\n"
    "from app.ui import (\n"
    "    delete_user_wizard_message,\n"
    "    edit_or_send,\n"
    "    render_inline_panel,\n"
    "    show_panel_from_message,\n"
    ")\n"
    "from app.ui_cleanup_middleware import DeleteUserInputMiddleware\n"
    "from app.zodiac import resolve_sun_sign\n\n"
)

(ROOT / "app" / "handlers" / "user.py").write_text(
    user_header + chunk(2112, 3971) + "\n\n" + chunk(4313, 4958) + "\n\n" + chunk(4961, 5065) + "\n",
    encoding="utf-8",
)

# --- slim bot.py ---
(ROOT / "app" / "bot.py").write_text(
    '"""Bot entrypoint."""\n'
    "from app.handlers.user import run_bot\n"
    "from app.profile_public import configure_public_profile\n\n"
    "__all__ = [\"configure_public_profile\", \"run_bot\"]\n",
    encoding="utf-8",
)

print("Refactor files written. Run compileall to verify.")
