"""Publish all ready-made channel posts (GIF + caption) to the linked channel."""
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
from app.services.channel_content import list_post_slugs, load_post_bundle


async def main() -> None:
    settings = load_settings()
    if not settings.channel_id:
        raise SystemExit("CHANNEL_ID is not set in .env")

    slugs = list_post_slugs()
    if not slugs:
        raise SystemExit("No channel posts found in marketing/channel/posts/")

    session = None
    if settings.proxy_url:
        from app.http_proxy_session import HttpProxyAiohttpSession

        session = HttpProxyAiohttpSession(settings.proxy_url)

    bot = Bot(token=settings.bot_token, session=session)
    ok = 0
    fail = 0
    try:
        print(f"Publishing {len(slugs)} posts to {settings.channel_id}...")
        for slug in slugs:
            try:
                bundle = load_post_bundle(slug)
                msg = await send_channel_animation(
                    bot,
                    bundle.gif_path,
                    bundle.caption,
                )
                print(f"OK {bundle.slug} message_id={msg.message_id}")
                ok += 1
                await asyncio.sleep(2)
            except Exception as exc:
                fail += 1
                print(f"FAIL {slug}: {exc}", file=sys.stderr)
    finally:
        await bot.session.close()

    print(f"Done: ok={ok} fail={fail}")
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
