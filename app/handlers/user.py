"""User-facing command and callback handlers."""
import asyncio
import logging
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote, unquote

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.admin_alerts import (
    notify_admins_bot_crashed,
    notify_admins_bot_started,
)
from app.admin_middleware import AdminOnlyMiddleware
from app.bot_context import (
    FREE_PARTNER_LIMIT,
    PREMIUM_PARTNER_LIMIT,
    SIGN_EMOJI,
    admin_router,
    db,
    router,
    settings,
)
from app.daily_sender import run_daily_loop
from app.evening_checkin import build_evening_response
from app.fsm_storage import SQLiteFsmStorage
from app.geo import resolve_city, warm_timezone_finder
from app.handlers import admin as _admin_handlers  # noqa: F401
from app.horoscope import (
    build_horoscope_share_text,
    generate_horoscope,
    personalization_from_profile,
)
from app.http_proxy_session import HttpProxyAiohttpSession
from app.i18n import TEXTS, get_locale, goal_display, relationship_display, sign_display, t
from app.keyboards import breadcrumb
from app.keyboards import (
    about_commands_keyboard,
    admin_panel_keyboard,
    home_goal_keyboard,
    home_panel_keyboard,
    home_relationship_keyboard,
    horoscope_period_keyboard,
    language_keyboard,
    moon_period_keyboard,
    onboarding_relationship_keyboard,
    prefs_gender_keyboard,
    prefs_goal_keyboard,
    prefs_relationship_keyboard,
    premium_menu_keyboard,
    premium_payment_keyboard,
    premium_upsell_keyboard,
    referral_panel_keyboard,
    settings_keyboard,
)
from app.profile_public import configure_public_profile, feedback_keyboard
from app.moon_calendar import (
    generate_moon_calendar_text,
    generate_moon_compact_table_text,
    generate_moon_table_text,
)
from app.natal import build_natal_summary
from app.payments import PayCurrency, available_payment_options, get_payment_option, parse_premium_payload
from app.premium import PREMIUM_PERIOD_DAYS, format_premium_until, is_premium_active
from app.premium_lifecycle import notify_admins_purchase
from app.services.compat import (
    compat_daily_limit_reached,
    compat_menu_text,
    compat_mode_keyboard,
    compat_wizard_keyboard,
    deliver_compat_result,
    geocode_city_input,
    get_sign_name,
    partner_limit_text,
    run_once_compat_synastry,
    run_saved_partner_compat,
    show_compat_menu,
    show_compat_mode_panel,
)
from app.services.daily_panels import (
    render_daily_panel,
    render_daily_timezone_panel,
    render_evening_panel,
    resolve_user_timezone,
    show_daily_panel,
    show_daily_panel_callback,
)
from app.services.dates import target_date_from_day_month
from app.services.home import build_home_panel_text
from app.services.locale_users import detect_locale_for_user, get_user_locale
from app.services.menu import _menu_action_from_text
from app.services.onboarding import (
    onboarding_step_needed,
    resume_onboarding_if_needed,
    show_goal_onboarding_panel,
    show_relationship_onboarding_panel,
)
from app.services.premium_panel import (
    _parse_pay_currency,
    _premium_panel_text,
    _premium_prices_text,
    _send_premium_invoice,
    _start_premium_checkout,
)
from app.services.referral import (
    attach_referrer_from_start,
    attach_start_source_from_start,
    build_referral_link,
    build_telegram_share_url,
    try_notify_referral_reward,
)
from app.states import (
    AdminPanel,
    CompatibilityCheck,
    DailySetup,
    MoonDetails,
    PartnerSetup,
    PreferencesSetup,
    ProfileSetup,
)
from app.timezones import user_local_date_key
from app.ui import (
    delete_user_wizard_message,
    edit_or_send,
    render_inline_panel,
    show_panel_from_message,
)
from app.ui_cleanup_middleware import DeleteUserInputMiddleware
from app.zodiac import resolve_sun_sign

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
            await attach_start_source_from_start(user.id, payload)
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
        await attach_start_source_from_start(user.id, payload)
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
        if await resume_onboarding_if_needed(user.id, locale, state, callback=callback):
            return
        await render_inline_panel(
            callback,
            f"{breadcrumb(locale, t(locale, 'crumb_goal'))}\n\n{t(locale, 'choose_goal_menu')}",
            home_goal_keyboard(locale),
        )
        return
    if action == "relationship":
        if await resume_onboarding_if_needed(user.id, locale, state, callback=callback):
            return
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
        if not is_admin(user.id, settings.admin_ids):
            await callback.answer(t(locale, "admin_only"), show_alert=True)
            return
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

    target = target_date_from_day_month(raw_text, datetime.now())
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
    trial_until = await db.grant_trial_if_eligible(user_id, settings.premium_trial_days)
    if trial_until and bot is not None:
        try:
            await bot.send_message(
                user_id,
                t(
                    locale,
                    "premium_trial_granted",
                    days=str(settings.premium_trial_days),
                    until=format_premium_until(trial_until, locale),
                ),
            )
            await db.log_event(user_id, "premium_trial_granted")
        except Exception:
            pass
    await try_notify_referral_reward(user_id, bot)


async def _try_finish_profile_if_ready(user_id: int, locale: str, bot: Bot | None) -> bool:
    if await db.has_event(user_id, "profile_completed"):
        return False
    profile = await db.get_user(user_id)
    if not profile or not profile.sign or not profile.relationship_status or not profile.goal:
        return False
    await _complete_onboarding_with_goal(user_id, locale, profile.goal, bot)
    return True


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

    finished = await _try_finish_profile_if_ready(user.id, locale, callback.bot)
    if not finished:
        await try_notify_referral_reward(user.id, callback.bot)
    home_text = await build_home_panel_text(
        user.id,
        locale,
        variant="start" if finished else "menu",
    )
    await edit_or_send(
        callback,
        home_text,
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
    await callback.answer(t(locale, "goal_saved_toast", goal=label))
    finished = await _try_finish_profile_if_ready(user.id, locale, callback.bot)
    if not finished:
        await try_notify_referral_reward(user.id, callback.bot)
    home_text = await build_home_panel_text(
        user.id,
        locale,
        variant="start" if finished else "menu",
    )
    await edit_or_send(
        callback,
        home_text,
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
    finished = await _try_finish_profile_if_ready(user.id, locale, callback.bot)
    if not finished:
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
    finished = await _try_finish_profile_if_ready(user.id, locale, message.bot)
    if not finished:
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
    charge_id = payment.telegram_payment_charge_id
    if charge_id and await db.has_payment_charge(charge_id):
        profile = await db.get_user(user.id)
        if profile and profile.premium_until:
            await show_panel_from_message(
                message,
                t(locale, "premium_payment_ok", until=format_premium_until(profile.premium_until, locale)),
                reply_markup=home_panel_keyboard(locale),
            )
        return
    until_iso = await db.extend_premium(user.id, PREMIUM_PERIOD_DAYS)
    if until_iso is None:
        await db.log_event(user.id, "premium_paid_no_user_row")
        await show_panel_from_message(
            message,
            t(locale, "profile_not_found"),
            reply_markup=home_panel_keyboard(locale),
        )
        return
    await db.log_event(user.id, f"premium_paid:{currency.value if currency else 'unknown'}")
    if charge_id:
        await db.record_payment_charge(charge_id, user.id)
    try:
        await notify_admins_purchase(
            message.bot,
            admin_ids=settings.admin_ids,
            buyer_id=user.id,
            buyer_username=user.username,
            buyer_first_name=user.first_name,
            currency=currency,
            telegram_currency=payment.currency,
            invoice_amount=payment.total_amount,
            until_iso=until_iso,
        )
    except Exception:
        await db.log_event(user.id, "premium_paid_admin_notify_failed")
    try:
        await show_panel_from_message(
            message,
            t(locale, "premium_payment_ok", until=format_premium_until(until_iso, locale)),
            reply_markup=home_panel_keyboard(locale),
        )
    except Exception:
        await db.log_event(user.id, "premium_paid_ui_failed")



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
    if text == t(locale, "btn_premium") or action == "premium":
        await premium_handler(message)
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
    admin_router.callback_query.middleware(
        AdminOnlyMiddleware(
            admin_ids=settings.admin_ids,
            deny_text=TEXTS["en"]["admin_only"],
        )
    )
    dp.include_router(admin_router)
    dp.include_router(router)
    asyncio.create_task(asyncio.to_thread(warm_timezone_finder))
    await bot.delete_webhook(drop_pending_updates=False)
    sent = await notify_admins_bot_started(bot, settings.admin_ids)
    if sent == 0 and settings.admin_ids:
        logger.warning(
            "Startup alert failed for all admins (%s). "
            "Ensure each admin sent /start to the bot.",
            ",".join(str(x) for x in settings.admin_ids),
        )
    elif not settings.admin_ids:
        logger.warning("Startup alert skipped: set ADMIN_IDS in .env")
    daily_task = asyncio.create_task(
        run_daily_loop(db, bot, admin_ids=settings.admin_ids)
    )
    try:
        await dp.start_polling(bot)
    except Exception as e:
        await db.log_error(
            source="run_bot",
            error_type=type(e).__name__,
            message=str(e),
        )
        await notify_admins_bot_crashed(
            bot,
            settings.admin_ids,
            error_type=type(e).__name__,
            message=str(e),
        )
        raise
    finally:
        daily_task.cancel()

