"""Admin commands and panel."""
from datetime import datetime, timezone

from aiogram import Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.admin_alerts import notify_admins
from app.bot_context import admin_router, db, settings
from app.i18n import t
from app.keyboards import admin_panel_keyboard, admin_users_keyboard, broadcast_confirm_keyboard, breadcrumb, home_panel_keyboard
from app.premium import format_premium_until
from app.services.admin_users import build_admin_users_page
from app.services.home import build_admin_stats_text, build_home_panel_text
from app.services.locale_users import get_user_locale
from app.states import AdminPanel
from app.ui import edit_or_send, render_inline_panel


def _ping_alerts_line(locale: str, user_id: int) -> str:
    if not settings.admin_ids:
        return t(locale, "ping_alerts_missing_env")
    if user_id in settings.admin_ids:
        return t(locale, "ping_alerts_ok", count=str(len(settings.admin_ids)))
    return t(
        locale,
        "ping_alerts_not_listed",
        ids=",".join(str(admin_id) for admin_id in settings.admin_ids),
        user_id=str(user_id),
    )


def _ping_panel_text(locale: str, user_id: int) -> str:
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return t(
        locale,
        "ping_text",
        utc=utc_now,
        alerts_line=_ping_alerts_line(locale, user_id),
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


async def _send_admin_users(
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    locale: str,
    page: int,
) -> None:
    text, page, total_pages = await build_admin_users_page(locale, page)
    keyboard = admin_users_keyboard(locale, page=page, total_pages=total_pages)
    if callback is not None:
        await render_inline_panel(callback, text, keyboard)
    elif message is not None:
        await message.answer(text, reply_markup=keyboard)


@admin_router.message(Command("users"))
async def users_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await _send_admin_users(message=message, locale=locale, page=0)


@admin_router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await message.answer(
        await build_admin_stats_text(locale),
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
    if until_iso is None:
        await message.answer(
            t(locale, "profile_not_found"),
            reply_markup=admin_panel_keyboard(locale),
        )
        return
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
    await message.answer(
        _ping_panel_text(locale, user.id),
        reply_markup=admin_panel_keyboard(locale),
    )


@admin_router.message(Command("adminalert"))
async def admin_alert_test_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    if user.id not in settings.admin_ids:
        await message.answer(t(locale, "admin_only"), reply_markup=admin_panel_keyboard(locale))
        return
    sent = await notify_admins(
        message.bot,
        settings.admin_ids,
        "🔔 Тест алерта админа\nЕсли видишь это — уведомления работают.",
    )
    await message.answer(
        f"Тест отправлен: {sent}/{len(settings.admin_ids)}",
        reply_markup=admin_panel_keyboard(locale),
    )


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


@admin_router.callback_query(F.data.regexp(r"^admin:users:\d+$"))
async def admin_users_page_callback(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    page = int((callback.data or "admin:users:0").rsplit(":", 1)[-1])
    await callback.answer()
    await _send_admin_users(callback=callback, locale=locale, page=page)


@admin_router.callback_query(F.data == "admin:panel")
async def admin_panel_back_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if user is None:
        return
    locale = await get_user_locale(user.id)
    await state.clear()
    await callback.answer()
    await render_inline_panel(
        callback,
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n{t(locale, 'admin_panel')}",
        admin_panel_keyboard(locale),
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
        await render_inline_panel(
            callback,
            await build_admin_stats_text(locale),
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
        await render_inline_panel(
            callback,
            _ping_panel_text(locale, user.id),
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
    if until_iso is None:
        await message.answer(
            t(locale, "profile_not_found"),
            reply_markup=admin_panel_keyboard(locale),
        )
        return
    await db.log_event(user.id, "grantpremium_panel")
    await state.clear()
    await message.answer(
        f"{breadcrumb(locale, t(locale, 'crumb_admin'))}\n\n"
        f"{t(locale, 'grant_done', user_id=str(target_user_id), days=str(days))}\n"
        f"Until: {format_premium_until(until_iso, locale)}",
        reply_markup=admin_panel_keyboard(locale),
    )

