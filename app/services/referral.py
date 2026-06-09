"""Referral links and start payload attachment."""
from urllib.parse import quote

from aiogram import Bot

from app.bot_context import db
from app.i18n import t
from app.start_payload import parse_ref_code_from_start, parse_start_source_from_start
from app.services.locale_users import get_user_locale

async def build_referral_link(bot: Bot, user_id: int) -> str:
    ref_code = await db.ensure_ref_code(user_id)
    me = await bot.get_me()
    username = me.username or ""
    if username:
        return f"https://t.me/{username}?start=ref_{ref_code}"
    return f"ref_{ref_code}"


async def attach_start_source_from_start(user_id: int, payload: str) -> None:
    source = parse_start_source_from_start(payload)
    if not source:
        return
    if await db.set_start_source_if_empty(user_id, source):
        await db.log_event(user_id, f"start_source:{source}")


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
        invited = await db.get_user(invited_user_id)
        if invited is not None and invited.referrer_id is None:
            await bot.send_message(invited_user_id, t(locale, "ref_invalid"))
        return
    linked = await db.set_referrer_if_empty(invited_user_id, inviter_id)
    if not linked:
        return
    await db.log_event(invited_user_id, "ref_linked")
    await bot.send_message(invited_user_id, t(locale, "ref_attached"))


def build_telegram_share_url(*, text: str, url: str) -> str:
    return f"https://t.me/share/url?url={quote(url, safe='')}&text={quote(text, safe='')}"


