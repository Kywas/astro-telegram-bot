"""Publish a ready-made channel post (GIF + caption) via Bot API."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiogram import Bot

from app.channel_posting import send_channel_animation
from app.config import load_settings
from app.services.channel_content import load_post_bundle


async def main() -> None:
    slug = (sys.argv[1] if len(sys.argv) > 1 else "energy-day").strip()
    settings = load_settings()
    if not settings.channel_id:
        raise SystemExit("CHANNEL_ID is not set in .env")

    bundle = load_post_bundle(slug)
    session = None
    if settings.proxy_url:
        from app.http_proxy_session import HttpProxyAiohttpSession

        session = HttpProxyAiohttpSession(settings.proxy_url)

    bot = Bot(token=settings.bot_token, session=session)
    try:
        msg = await send_channel_animation(
            bot,
            bundle.gif_path,
            bundle.caption,
        )
        print(f"OK published {bundle.slug} to {settings.channel_id} message_id={msg.message_id}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
