"""Check VPS reachability of Telegram API (direct and via BOT_PROXY)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def _try_get_me(*, proxy_url: str | None, label: str) -> bool:
    from aiogram import Bot

    from app.config import load_settings

    settings = load_settings()
    session = None
    if proxy_url:
        from app.http_proxy_session import HttpProxyAiohttpSession

        session = HttpProxyAiohttpSession(proxy_url)
    bot = Bot(token=settings.bot_token, session=session)
    try:
        me = await bot.get_me()
        print(f"OK {label}: @{me.username} (id={me.id})")
        return True
    except Exception as exc:
        print(f"FAIL {label}: {type(exc).__name__}: {exc}")
        return False
    finally:
        await bot.session.close()


async def main() -> None:
    from app.config import load_settings

    settings = load_settings()
    print("Checking Telegram API from this server...")
    direct_ok = await _try_get_me(proxy_url=None, label="direct")
    if settings.proxy_url:
        proxy_ok = await _try_get_me(proxy_url=settings.proxy_url, label=f"proxy {settings.proxy_url}")
    else:
        proxy_ok = False
        print("SKIP proxy: BOT_PROXY is not set in .env")

    if direct_ok:
        print("\nDirect access works — proxy is optional.")
        return

    if proxy_ok:
        print("\nDirect access failed, but BOT_PROXY works. Keep BOT_PROXY in .env.")
        return

    print(
        "\nTelegram API is not reachable from this VPS (common on RU hosting like Timeweb).",
        file=sys.stderr,
    )
    print(
        "Fix: set BOT_PROXY in /opt/astro-telegram-bot/.env, for example:",
        file=sys.stderr,
    )
    print("  BOT_PROXY=socks5://127.0.0.1:1080", file=sys.stderr)
    print("  BOT_PROXY=http://user:pass@proxy-host:port", file=sys.stderr)
    print("Then: systemctl restart astrobot", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
