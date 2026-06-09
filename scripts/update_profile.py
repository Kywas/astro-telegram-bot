import asyncio
import sys

from aiogram import Bot

from app.bot import configure_public_profile
from app.config import load_settings
from scripts.verify_profile import _profile_text


async def main() -> None:
    settings = load_settings()
    print(f"FEEDBACK_USERNAME={settings.feedback_username!r}")

    bot = Bot(token=settings.bot_token)
    try:
        me = await bot.get_me()
        print(f"Bot: @{me.username} (id={me.id})")

        print("Updating public profile...")
        await configure_public_profile(bot)

        desc = await bot.get_my_description(language_code="ru")
        desc_text = _profile_text(desc, "description")
        print(f"\nru description ({len(desc_text)} chars):")
        print(desc_text or "(empty)")

        handle = settings.feedback_username
        if handle and f"@{handle}" not in desc_text:
            print(f"\nERROR: feedback @{handle} is missing from ru description", file=sys.stderr)
            raise SystemExit(1)

        print("\nOK: profile updated")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
