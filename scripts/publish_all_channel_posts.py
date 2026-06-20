"""Publish all ready-made channel posts (GIF + caption) to the linked channel."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiogram import Bot

from app.channel_bulk_publish import publish_all_channel_posts
from app.config import load_settings


async def main() -> None:
    settings = load_settings()
    if not settings.channel_id:
        raise SystemExit("CHANNEL_ID is not set in .env")

    session = None
    if settings.proxy_url:
        from app.http_proxy_session import HttpProxyAiohttpSession

        session = HttpProxyAiohttpSession(settings.proxy_url)

    bot = Bot(token=settings.bot_token, session=session)
    try:
        report = await publish_all_channel_posts(bot)
        print(f"Done: ok={report.ok} fail={report.fail}")
        for line in report.failures:
            print(f"FAIL {line}", file=sys.stderr)
        if report.fail:
            raise SystemExit(1)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
