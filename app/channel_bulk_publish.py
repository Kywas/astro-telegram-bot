"""Bulk channel publishing with Telegram flood-control handling."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter

from app.channel_posting import send_channel_animation
from app.services.channel_content import iter_publishable_posts, list_post_slugs, load_post_bundle

logger = logging.getLogger(__name__)

# GIF uploads to one channel hit limits faster than plain text (~20 msg/min).
DEFAULT_PAUSE_SECONDS = 6.0
MAX_FLOOD_RETRIES = 8


@dataclass(frozen=True)
class BulkPublishReport:
    ok: int
    fail: int
    failures: tuple[str, ...]


def bulk_publish_slugs(*, publishable_only: bool = False) -> list[str]:
    if publishable_only:
        return [slug for slug, _, _ in iter_publishable_posts()]
    return list_post_slugs()


async def publish_channel_bundle_with_retry(
    bot: Bot,
    slug: str,
    *,
    pause_after: float = DEFAULT_PAUSE_SECONDS,
) -> None:
    bundle = load_post_bundle(slug)
    for attempt in range(MAX_FLOOD_RETRIES + 1):
        try:
            await send_channel_animation(bot, bundle.gif_path, bundle.caption)
            if pause_after > 0:
                await asyncio.sleep(pause_after)
            return
        except TelegramRetryAfter as exc:
            if attempt >= MAX_FLOOD_RETRIES:
                raise
            wait = float(exc.retry_after) + 1.0
            logger.warning("Flood control for %s, sleeping %.0fs", slug, wait)
            await asyncio.sleep(wait)


async def publish_all_channel_posts(
    bot: Bot,
    *,
    slugs: list[str] | None = None,
    publishable_only: bool = False,
) -> BulkPublishReport:
    items = slugs if slugs is not None else bulk_publish_slugs(publishable_only=publishable_only)
    ok = 0
    fail = 0
    failures: list[str] = []
    for slug in items:
        try:
            await publish_channel_bundle_with_retry(bot, slug)
            ok += 1
        except Exception as exc:
            fail += 1
            failures.append(f"{slug}: {exc}")
            logger.exception("Failed to publish channel post %s", slug)
    return BulkPublishReport(ok=ok, fail=fail, failures=tuple(failures))
