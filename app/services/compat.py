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
from app.synastry_style import resolve_compat_style, use_synastry_terms
from app.reading_voice import (
    compat_score_hook,
    menu_pick_cta,
    theme_menu_teaser,
    theme_next_teaser,
    theme_opening_hook,
)
from app.text_format import b, format_report, format_screen_body, h, labeled_block, p, screen_page
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


def compat_result_header(
    locale: str,
    profile,
    syn,
    mode: str,
    *,
    compact: bool = False,
    style: str | None = None,
) -> str:
    style = style or resolve_compat_style(profile)
    partner_name = syn.partner_name or get_sign_name(syn.partner_sign, locale)
    sign_a = get_sign_name(profile.sign, locale)
    sign_b = get_sign_name(syn.partner_sign, locale)
    mode_label = compat_mode_label(locale, mode)
    if compact:
        if use_synastry_terms(style):
            return p(
                b(f"💞 {mode_label} · {syn.score}/100"),
                h(f"{sign_a} + {partner_name} ({sign_b})"),
            )
        return p(
            b(f"💞 {mode_label}"),
            h(f"{sign_a} + {partner_name} ({sign_b})"),
        )
    score_hook = compat_score_hook(locale, syn.score, mode, style=style)
    if use_synastry_terms(style):
        if locale == "ru":
            return p(
                b(f"💞 Синастрия · {mode_label}"),
                h(f"{sign_a} + {partner_name} ({sign_b})"),
                b(f"Оценка: {syn.score}/100"),
                format_screen_body(score_hook),
            )
        return p(
            b(f"💞 Synastry · {mode_label}"),
            h(f"{sign_a} + {partner_name} ({sign_b})"),
            b(f"Score: {syn.score}/100"),
            format_screen_body(score_hook),
        )
    if locale == "ru":
        return p(
            b(f"💞 Совместимость · {mode_label}"),
            h(f"{sign_a} + {partner_name} ({sign_b})"),
            b(f"Оценка: {syn.score}/100"),
            format_screen_body(score_hook),
        )
    return p(
        b(f"💞 Compatibility · {mode_label}"),
        h(f"{sign_a} + {partner_name} ({sign_b})"),
        b(f"Score: {syn.score}/100"),
        format_screen_body(score_hook),
    )


def _compat_footer_rows(locale: str, partner_id: int, mode: str) -> list[list[InlineKeyboardButton]]:
    return [
        [InlineKeyboardButton(text=t(locale, "btn_compat_style"), callback_data="compat:style:picker:menu")],
        [glossary_help_button(locale, "compat", "nav:compat")],
        [InlineKeyboardButton(text=t(locale, "btn_compat"), callback_data="nav:compat")],
        [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
    ]


def compat_themes_menu_keyboard(
    locale: str,
    *,
    partner_id: int,
    mode: str,
    themes,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    buf: list[InlineKeyboardButton] = []
    for theme in themes:
        buf.append(
            InlineKeyboardButton(
                text=theme.title,
                callback_data=f"compat:topic:{partner_id}:{mode}:{theme.key}",
            )
        )
        if len(buf) == 2:
            rows.append(buf)
            buf = []
    if buf:
        rows.append(buf)
    rows.extend(_compat_footer_rows(locale, partner_id, mode))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def compat_theme_view_keyboard(
    locale: str,
    *,
    partner_id: int,
    mode: str,
    themes,
    active_key: str,
) -> InlineKeyboardMarkup:
    keys = [theme.key for theme in themes]
    try:
        index = keys.index(active_key)
    except ValueError:
        index = 0
    prev_key = keys[index - 1] if index > 0 else keys[-1]
    next_key = keys[index + 1] if index < len(keys) - 1 else keys[0]
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="◀",
                callback_data=f"compat:topic:{partner_id}:{mode}:{prev_key}",
            ),
            InlineKeyboardButton(
                text=t(locale, "btn_compat_themes"),
                callback_data=f"compat:topic:{partner_id}:{mode}:menu",
            ),
            InlineKeyboardButton(
                text="▶",
                callback_data=f"compat:topic:{partner_id}:{mode}:{next_key}",
            ),
        ],
    ]
    rows.extend(_compat_footer_rows(locale, partner_id, mode))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def render_compat_theme_menu(locale: str, profile, syn, mode: str, *, style: str | None = None) -> str:
    style = style or resolve_compat_style(profile)
    from app.reading_voice import compat_mode_intro, compat_mode_menu_guide, menu_pick_cta, theme_menu_teaser

    if use_synastry_terms(style):
        if locale == "ru":
            guide = (
                "Разбор по 6 блокам: от солнечных знаков до сводной таблицы. "
                "Внутри — шаги синастрии с терминами (ASC, аспекты, композит и т.д.)."
            )
        else:
            guide = (
                "Six blocks from Sun signs to the final scorecard. "
                "Inside — synastry steps with terms (ASC, aspects, composite, etc.)."
            )
    else:
        guide = compat_mode_menu_guide(locale, mode, style=style)
    theme_blocks = [
        labeled_block(theme.title, theme_menu_teaser(locale, theme.key, style=style, mode=mode))
        for theme in syn.themes
    ]
    return p(
        compat_result_header(locale, profile, syn, mode, style=style),
        compat_mode_intro(locale, mode, syn.score, style=style),
        format_screen_body(guide),
        *theme_blocks,
        format_screen_body(menu_pick_cta(locale, style=style, mode=mode)),
    )


def render_compat_theme_page(
    locale: str,
    profile,
    syn,
    mode: str,
    theme_key: str,
    *,
    style: str | None = None,
) -> str:
    style = style or resolve_compat_style(profile)
    themes = list(syn.themes)
    theme = next((item for item in themes if item.key == theme_key), themes[0])
    keys = [item.key for item in themes]
    try:
        index = keys.index(theme.key)
    except ValueError:
        index = 0
    next_theme = themes[(index + 1) % len(themes)]
    hook = theme_opening_hook(locale, theme.key, mode, syn.score, style=style)
    parts = [
        compat_result_header(locale, profile, syn, mode, compact=True, style=style),
    ]
    if hook:
        parts.append(format_screen_body(hook))
    parts.append(p(b(theme.title), format_report(theme.body)))
    if len(themes) > 1 and theme.key != "result" and use_synastry_terms(style):
        parts.append(
            format_screen_body(
                theme_next_teaser(locale, next_theme.title, next_theme.key, style=style, mode=mode),
            )
        )
    return p(*parts)


async def show_compat_theme_panel(
    *,
    user_id: int,
    locale: str,
    profile,
    syn,
    mode: str,
    partner_id: int,
    theme_key: str,
    callback: CallbackQuery,
) -> None:
    style = resolve_compat_style(profile)
    if theme_key == "menu" or not theme_key:
        text = render_compat_theme_menu(locale, profile, syn, mode, style=style)
        keyboard = compat_themes_menu_keyboard(
            locale,
            partner_id=partner_id,
            mode=mode,
            themes=syn.themes,
        )
    else:
        text = render_compat_theme_page(locale, profile, syn, mode, theme_key, style=style)
        keyboard = compat_theme_view_keyboard(
            locale,
            partner_id=partner_id,
            mode=mode,
            themes=syn.themes,
            active_key=theme_key,
        )
    if callback.message is not None:
        await show_ui_panel(
            bot=callback.bot,
            user_id=user_id,
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=keyboard,
            edit_message=callback.message,
        )


async def deliver_compat_result(
    *,
    user_id: int,
    locale: str,
    profile,
    syn,
    mode: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    partner_id: int = 0,
    theme_key: str = "menu",
) -> None:
    themes = tuple(syn.themes or ())

    if callback is not None and len(themes) > 1 and partner_id > 0:
        await show_compat_theme_panel(
            user_id=user_id,
            locale=locale,
            profile=profile,
            syn=syn,
            mode=mode,
            partner_id=partner_id,
            theme_key=theme_key,
            callback=callback,
        )
        await db.log_event(user_id, "compat_result")
        return

    header = compat_result_header(locale, profile, syn, mode, style=resolve_compat_style(profile))
    if len(themes) == 1:
        result_text = p(header, b(themes[0].title), format_report(themes[0].body))
    else:
        result_text = p(header, format_report(syn.details))
    keyboard = InlineKeyboardMarkup(inline_keyboard=_compat_footer_rows(locale, partner_id, mode))

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
        partner_id=partner_id,
    )
    return True

