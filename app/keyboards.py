"""Inline keyboard builders."""
from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot_context import DAILY_PRESET_TIMES, EVENING_PRESET_TIMES, GOAL_TEXT_KEYS, settings
from app.i18n import t
from app.payments import PayCurrency, available_payment_options
from app.premium import PREMIUM_PERIOD_DAYS
from app.timezones import TIMEZONE_OPTIONS, timezone_label_with_offset

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


def glossary_help_button(locale: str, topic: str, back_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=t(locale, "btn_glossary_help"),
        callback_data=f"glossary:{topic}:{back_data}",
    )


def natal_style_picker_keyboard(
    locale: str,
    *,
    current_style: str,
    part: int = 1,
) -> InlineKeyboardMarkup:
    style = "plain" if current_style == "plain" else "terms"
    plain_mark = "✓ " if style == "plain" else ""
    terms_mark = "✓ " if style == "terms" else ""
    back_data = f"natal:part:{part}" if part else "nav:home"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{plain_mark}{t(locale, 'natal_style_plain')}",
                    callback_data=f"natal:style:plain:{part}",
                ),
                InlineKeyboardButton(
                    text=f"{terms_mark}{t(locale, 'natal_style_terms')}",
                    callback_data=f"natal:style:terms:{part}",
                ),
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data=back_data)],
        ]
    )


def natal_part_keyboard(
    locale: str,
    *,
    part: int,
    premium_active: bool,
    current_style: str = "plain",
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if premium_active:
        part_labels = {
            "ru": ("① Каркас", "② Планеты", "③ Итог"),
            "en": ("① Core", "② Planets", "③ Summary"),
        }
        lang = "ru" if locale == "ru" else "en"
        labels = part_labels[lang]
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{'✓ ' if part == 1 else ''}{labels[0]}",
                    callback_data="natal:part:1",
                ),
                InlineKeyboardButton(
                    text=f"{'✓ ' if part == 2 else ''}{labels[1]}",
                    callback_data="natal:part:2",
                ),
                InlineKeyboardButton(
                    text=f"{'✓ ' if part == 3 else ''}{labels[2]}",
                    callback_data="natal:part:3",
                ),
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "btn_natal_sphere_qa"),
                callback_data=f"natal:qa:pick:{part}",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "btn_natal_style"),
                callback_data=f"natal:style:picker:{part}",
            )
        ]
    )
    rows.append([glossary_help_button(locale, "natal", f"natal:part:{part}")])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def natal_qa_popular_keyboard(locale: str, *, part: int) -> InlineKeyboardMarkup:
    from app.natal_sphere_qa import popular_blocks, popular_button_label

    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=popular_button_label(locale, block.id),
                callback_data=f"natal:qa:pop:{block.id}:{part}",
            )
        ]
        for block in popular_blocks(locale)
    ]
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "btn_natal_qa_family"),
                callback_data=f"natal:qa:family:{part}",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "btn_natal_qa_spheres"),
                callback_data=f"natal:qa:spheres:{part}",
            )
        ]
    )
    rows.append(
        [InlineKeyboardButton(text=t(locale, "back"), callback_data=f"natal:part:{part}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def natal_qa_family_keyboard(locale: str, *, part: int) -> InlineKeyboardMarkup:
    from app.natal_sphere_qa import family_questions, question_button_label

    rows = [
        [
            InlineKeyboardButton(
                text=question_button_label(q, max_len=48),
                callback_data=f"natal:qa:fam:{idx}:{part}",
            )
        ]
        for idx, q in enumerate(family_questions(locale))
    ]
    rows.append(
        [InlineKeyboardButton(text=t(locale, "back"), callback_data=f"natal:qa:pick:{part}")]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "natal_qa_back_to_chart"),
                callback_data=f"natal:part:{part}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def natal_qa_family_answer_keyboard(locale: str, *, part: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(locale, "natal_qa_other_questions"),
                    callback_data=f"natal:qa:family:{part}",
                )
            ],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data=f"natal:qa:pick:{part}")],
            [
                InlineKeyboardButton(
                    text=t(locale, "natal_qa_back_to_chart"),
                    callback_data=f"natal:part:{part}",
                )
            ],
        ]
    )


def natal_qa_spheres_keyboard(locale: str, *, part: int, page: int = 0) -> InlineKeyboardMarkup:
    from app.natal_sphere_qa import house_button_label

    rows: list[list[InlineKeyboardButton]] = []
    start_house = page * 6 + 1
    end_house = min(start_house + 5, 12)
    row: list[InlineKeyboardButton] = []
    for house in range(start_house, end_house + 1):
        row.append(
            InlineKeyboardButton(
                text=house_button_label(locale, house),
                callback_data=f"natal:qa:h:{house}:{part}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(text="◀", callback_data=f"natal:qa:page:{page - 1}:{part}")
        )
    if end_house < 12:
        nav.append(
            InlineKeyboardButton(text="▶", callback_data=f"natal:qa:page:{page + 1}:{part}")
        )
    if nav:
        rows.append(nav)

    rows.append(
        [InlineKeyboardButton(text=t(locale, "back"), callback_data=f"natal:qa:pick:{part}")]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "natal_qa_back_to_chart"),
                callback_data=f"natal:part:{part}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def natal_qa_questions_keyboard(
    locale: str,
    *,
    house: int,
    part: int,
) -> InlineKeyboardMarkup:
    from app.natal_sphere_qa import question_button_label, sphere_questions

    questions = sphere_questions(locale, house)
    rows = [
        [
            InlineKeyboardButton(
                text=question_button_label(q),
                callback_data=f"natal:qa:q:{house}:{idx}:{part}",
            )
        ]
        for idx, q in enumerate(questions)
    ]
    rows.append(
        [InlineKeyboardButton(text=t(locale, "back"), callback_data=f"natal:qa:spheres:{part}")]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=t(locale, "natal_qa_back_to_chart"),
                callback_data=f"natal:part:{part}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def natal_qa_popular_answer_keyboard(locale: str, *, part: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(locale, "back"), callback_data=f"natal:qa:pick:{part}")],
            [
                InlineKeyboardButton(
                    text=t(locale, "natal_qa_back_to_chart"),
                    callback_data=f"natal:part:{part}",
                )
            ],
        ]
    )


def natal_qa_answer_keyboard(locale: str, *, house: int, part: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(locale, "back"),
                    callback_data=f"natal:qa:h:{house}:{part}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(locale, "natal_qa_other_spheres"),
                    callback_data=f"natal:qa:spheres:{part}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(locale, "natal_qa_back_to_chart"),
                    callback_data=f"natal:part:{part}",
                )
            ],
        ]
    )


def horoscope_period_keyboard(
    locale: str,
    *,
    premium_active: bool = False,
    share_url: str | None = None,
    help_back: str = "nav:horo",
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
    rows.append([glossary_help_button(locale, "horo", help_back)])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def referral_panel_keyboard(locale: str, link: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if link.startswith("https://"):
        rows.append([InlineKeyboardButton(text=t(locale, "ref_share_button"), url=link)])
    rows.append([InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_telegram_share_url(*, text: str, url: str) -> str:
    return f"https://t.me/share/url?url={quote(url, safe='')}&text={quote(text, safe='')}"


def moon_period_keyboard(locale: str, *, help_back: str = "nav:moon") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "moon_today"), callback_data="moon:today"),
                InlineKeyboardButton(text=t(locale, "moon_7_days"), callback_data="moon:7"),
                InlineKeyboardButton(text=t(locale, "moon_30_days"), callback_data="moon:30"),
            ],
            [glossary_help_button(locale, "moon", help_back)],
            [InlineKeyboardButton(text=t(locale, "back"), callback_data="nav:home")],
        ]
    )


def moon_content_keyboard(locale: str, *, content_action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(locale, "moon_today"), callback_data="moon:today"),
                InlineKeyboardButton(text=t(locale, "moon_7_days"), callback_data="moon:7"),
                InlineKeyboardButton(text=t(locale, "moon_30_days"), callback_data="moon:30"),
            ],
            [glossary_help_button(locale, "moon", content_action)],
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
            [
                InlineKeyboardButton(text=t(locale, "admin_btn_users"), callback_data="admin:users:0"),
                InlineKeyboardButton(text=t(locale, "admin_btn_ping"), callback_data="admin:ping"),
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


def admin_users_keyboard(locale: str, *, page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if total_pages > 1:
        nav: list[InlineKeyboardButton] = []
        if page > 0:
            nav.append(
                InlineKeyboardButton(
                    text=t(locale, "admin_users_prev"),
                    callback_data=f"admin:users:{page - 1}",
                )
            )
        if page < total_pages - 1:
            nav.append(
                InlineKeyboardButton(
                    text=t(locale, "admin_users_next"),
                    callback_data=f"admin:users:{page + 1}",
                )
            )
        if nav:
            rows.append(nav)
    rows.append([InlineKeyboardButton(text=t(locale, "admin_users_back"), callback_data="admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


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

