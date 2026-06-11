import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiogram import Bot

from app.config import load_settings


def _profile_text(value: object | None, attr: str) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    text = getattr(value, attr, None)
    return text if isinstance(text, str) else str(value)


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
            short_text = _profile_text(short, "short_description")
            desc_text = _profile_text(desc, "description")
            print(f"\n=== {label} short ({len(short_text)} chars) ===")
            print(short_text or "(empty)")
            print(f"\n=== {label} description ({len(desc_text)} chars) ===")
            print(desc_text or "(empty)")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
