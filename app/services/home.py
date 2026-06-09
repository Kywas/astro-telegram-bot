"""Home screen and admin stats text builders."""
from app.bot_context import db
from app.horoscope import generate_home_teaser, personalization_from_profile
from app.i18n import goal_display, relationship_display, sign_display, t
from app.bot_context import SIGN_EMOJI

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
    lines.append(t(locale, "home_ref_promo"))
    return "\n\n".join(lines)


async def build_admin_stats_text(locale: str) -> str:
    stats = await db.get_stats()
    base = t(
        locale,
        "stats_text",
        total_users=str(stats["total_users"]),
        new_users_7d=str(stats["new_users_7d"]),
        new_users_30d=str(stats["new_users_30d"]),
        daily_subscribers=str(stats["daily_subscribers"]),
        premium_users=str(stats["premium_users"]),
        referrals_7d=str(stats["referrals_7d"]),
        referrals_30d=str(stats["referrals_30d"]),
        total_events=str(stats["total_events"]),
        errors_24h=str(stats["errors_24h"]),
        total_errors=str(stats["total_errors"]),
    )
    sources = await db.get_start_source_stats()
    if not sources:
        return base
    source_lines = [t(locale, "stats_sources_header")]
    for source_key, count in sources:
        label = (
            t(locale, "stats_source_direct")
            if source_key == "direct"
            else source_key
        )
        source_lines.append(
            t(locale, "stats_sources_line", source=label, count=str(count))
        )
    return base + "\n\n" + "\n".join(source_lines)

