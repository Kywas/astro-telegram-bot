"""Compatibility flow helpers."""
from datetime import date, datetime, time, timezone

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot_context import FREE_PARTNER_LIMIT, PREMIUM_PARTNER_LIMIT, SIGN_EN, SIGN_RU, db
from app.geo import resolve_city
from app.i18n import t
from app.keyboards import breadcrumb, compat_style_picker_keyboard, glossary_help_button, premium_upsell_keyboard
from app.premium import is_premium_active
from app.synastry import build_synastry, build_synastry_for_partner_profile
from app.synastry_style import resolve_compat_style
from app.text_format import b, format_report, h, p, screen_page
from app.ui import edit_or_send, render_inline_panel, show_panel_from_message, show_ui_panel
from app.zodiac import resolve_sun_sign

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
    rows.append(
        [InlineKeyboardButton(text=t(locale, "btn_compat_style"), callback_data="compat:style:picker:menu")]
    )
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
    del user_id
    return screen_page(
        breadcrumb(locale, t(locale, "crumb_root")),
        t(locale, "compat_choose_partner"),
    )


async def show_compat_menu(*, user_id: int, locale: str, message: Message | None = None, callback: CallbackQuery | None = None) -> None:
    partners = await db.list_partners(user_id)
    text = await compat_menu_text(locale, user_id)
    keyboard = compat_menu_keyboard(locale, partners)
    if callback is not None:
        await render_inline_panel(callback, text, keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


def compat_style_label(locale: str, style: str) -> str:
    if style == "plain":
        return t(locale, "natal_style_label_plain")
    return t(locale, "natal_style_label_terms")


async def render_compat_style_picker(
    user_id: int,
    locale: str,
    *,
    return_to: str = "menu",
) -> tuple[str, InlineKeyboardMarkup]:
    profile = await db.get_user(user_id)
    style = resolve_compat_style(profile)
    style_label = compat_style_label(locale, style)
    text = screen_page(
        breadcrumb(locale, t(locale, "crumb_root")),
        t(locale, "choose_compat_style"),
        t(locale, "natal_style_current", style=style_label),
    )
    return text, compat_style_picker_keyboard(locale, current_style=style, return_to=return_to)


async def show_compat_mode_panel(
    *,
    locale: str,
    intro: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    back_data: str = "nav:compat",
) -> None:
    keyboard = compat_mode_keyboard(locale, back_data=back_data)
    text = screen_page(
        breadcrumb(locale, t(locale, "crumb_root")),
        intro,
        t(locale, "choose_compat_mode"),
    )
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
    sign_a = get_sign_name(profile.sign, locale)
    sign_b = get_sign_name(syn.partner_sign, locale)
    mode_label = compat_mode_label(locale, mode)
    if locale == "ru":
        header = p(
            b(f"💞 Совместимость · {mode_label}"),
            h(f"{sign_a} + {partner_name} ({sign_b})"),
            b(f"Оценка: {syn.score}/100"),
        )
    else:
        header = p(
            b(f"💞 Compatibility · {mode_label}"),
            h(f"{sign_a} + {partner_name} ({sign_b})"),
            b(f"Score: {syn.score}/100"),
        )
    result_text = p(header, format_report(syn.details))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(locale, "btn_compat_style"), callback_data="compat:style:picker:menu")],
            [glossary_help_button(locale, "compat", "nav:compat")],
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
        style=resolve_compat_style(profile),
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

    syn = build_synastry_for_partner_profile(
        locale,
        profile,
        partner,
        mode,
        style=resolve_compat_style(profile),
    )
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

