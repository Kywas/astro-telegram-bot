import asyncio
import sys

from aiogram import Bot

from app.config import load_settings


async def main() -> None:
    settings = load_settings()
    print(f"FEEDBACK_USERNAME={settings.feedback_username!r}")

    bot = Bot(token=settings.bot_token)
    try:
        me = await bot.get_me()
        print(f"Bot: @{me.username} (id={me.id})")

        for label, lang in (("default", None), ("ru", "ru"), ("en", "en")):
            kwargs = {} if lang is None else {"language_code": lang}
            short = await bot.get_my_short_description(**kwargs)
            desc = await bot.get_my_description(**kwargs)
            print(f"\n=== {label} short ({len(short or '')} chars) ===")
            print(short or "(empty)")
            print(f"\n=== {label} description ({len(desc or '')} chars) ===")
            print(desc or "(empty)")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
