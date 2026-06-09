import asyncio
import sys

from aiogram import Bot

from app.config import load_settings


async def main() -> None:
    settings = load_settings()
    session = None
    if settings.proxy_url:
        from app.http_proxy_session import HttpProxyAiohttpSession

        session = HttpProxyAiohttpSession(settings.proxy_url)
    bot = Bot(token=settings.bot_token, session=session)
    try:
        me = await bot.get_me()
        print(f"OK @{me.username} id={me.id}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
