"""Inline panel UI: edit-or-send, panel tracking."""
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.bot_context import db

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

