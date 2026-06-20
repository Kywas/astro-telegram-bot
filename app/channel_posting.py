"""Post messages to the linked Telegram channel."""
from __future__ import annotations

from pathlib import Path

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot_context import settings

BOT_LINK = "https://t.me/AstroPulsee_bot"
DEFAULT_CHANNEL_URL = "https://t.me/AstroPulse_Channel"


def normalize_channel_chat_id(raw: str) -> str | int:
    value = raw.strip()
    if not value:
        raise ValueError("empty_channel_id")
    if value.startswith("@"):
        return value
    if value.lstrip("-").isdigit():
        return int(value)
    return f"@{value}"


def channel_join_url(channel_id: str | None = None) -> str:
    raw = (channel_id or settings.channel_id or "").strip()
    if raw.startswith("@"):
        return f"https://t.me/{raw.lstrip('@')}"
    if raw and not raw.lstrip("-").isdigit():
        return f"https://t.me/{raw.lstrip('@')}"
    return DEFAULT_CHANNEL_URL


def channel_configured(channel_id: str | None = None) -> bool:
    value = channel_id if channel_id is not None else settings.channel_id
    return bool((value or "").strip())


def channel_bot_keyboard(*, label: str = "🚀 Открыть AstroPulse") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, url=BOT_LINK)],
        ]
    )


def channel_env_value(chat_id: int, username: str | None) -> str:
    return f"@{username}" if username else str(chat_id)


async def send_channel_text(
    bot: Bot,
    text: str,
    *,
    channel_id: str | None = None,
    parse_mode: ParseMode | None = ParseMode.HTML,
    reply_markup: InlineKeyboardMarkup | None = None,
    disable_web_page_preview: bool | None = True,
    with_bot_button: bool = False,
    button_label: str = "🚀 Открыть AstroPulse",
) -> Message:
    raw_id = (channel_id or settings.channel_id or "").strip()
    if not raw_id:
        raise RuntimeError("CHANNEL_ID is not set in .env")
    chat_id = normalize_channel_chat_id(raw_id)
    markup = reply_markup
    if with_bot_button and markup is None:
        markup = channel_bot_keyboard(label=button_label)
    return await bot.send_message(
        chat_id,
        text,
        parse_mode=parse_mode,
        reply_markup=markup,
        disable_web_page_preview=disable_web_page_preview,
    )


async def send_channel_photo(
    bot: Bot,
    photo_path: Path,
    caption: str,
    *,
    channel_id: str | None = None,
    parse_mode: ParseMode | None = ParseMode.HTML,
    reply_markup: InlineKeyboardMarkup | None = None,
    with_bot_button: bool = False,
    button_label: str = "🚀 Открыть AstroPulse",
) -> Message:
    raw_id = (channel_id or settings.channel_id or "").strip()
    if not raw_id:
        raise RuntimeError("CHANNEL_ID is not set in .env")
    if not photo_path.is_file():
        raise FileNotFoundError(str(photo_path))
    chat_id = normalize_channel_chat_id(raw_id)
    markup = reply_markup
    if with_bot_button and markup is None:
        markup = channel_bot_keyboard(label=button_label)
    return await bot.send_photo(
        chat_id,
        FSInputFile(photo_path),
        caption=caption,
        parse_mode=parse_mode,
        reply_markup=markup,
    )


async def send_channel_animation(
    bot: Bot,
    animation_path: Path,
    caption: str,
    *,
    channel_id: str | None = None,
    parse_mode: ParseMode | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
    with_bot_button: bool = False,
    button_label: str = "🚀 Открыть AstroPulse",
) -> Message:
    raw_id = (channel_id or settings.channel_id or "").strip()
    if not raw_id:
        raise RuntimeError("CHANNEL_ID is not set in .env")
    if not animation_path.is_file():
        raise FileNotFoundError(str(animation_path))
    chat_id = normalize_channel_chat_id(raw_id)
    markup = reply_markup
    if with_bot_button and markup is None:
        markup = channel_bot_keyboard(label=button_label)
    return await bot.send_animation(
        chat_id,
        FSInputFile(animation_path),
        caption=caption,
        parse_mode=parse_mode,
        reply_markup=markup,
    )
