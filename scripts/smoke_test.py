"""Pre-deploy smoke checks: import critical modules and exercise key UI helpers."""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def offline_checks() -> None:
    from app.bot_context import db
    from app.keyboards import home_goal_keyboard, home_panel_keyboard
    from app.services.daily_panels import render_daily_panel
    from app.services.onboarding import onboarding_step_needed

    with tempfile.TemporaryDirectory() as tmp:
        db._db_path = str(Path(tmp) / "smoke.db")
        await db.init()
        await db.upsert_user_identity(1, "smoke", "Smoke", "ru")

        home_goal_keyboard("ru")
        home_panel_keyboard("ru")
        await render_daily_panel(1, "ru")
        await onboarding_step_needed(1)


async def telegram_check() -> None:
    from aiogram import Bot

    from app.config import load_settings

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


async def main() -> None:
    await offline_checks()
    print("OK offline smoke")
    await telegram_check()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
