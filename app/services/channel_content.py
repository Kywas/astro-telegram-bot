"""Load ready-made channel posts from marketing/channel/posts/."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.bot_context import PROJECT_ROOT

POSTS_DIR = PROJECT_ROOT / "marketing" / "channel" / "posts"
AUTO_PUBLISH_STATUSES = frozenset({"published", "test", "ready"})
VALID_SLOTS = frozenset({"morning", "lunch", "evening"})


@dataclass(frozen=True)
class ChannelPostBundle:
    slug: str
    folder: Path
    caption: str
    gif_path: Path
    meta: dict


def _load_meta(post_dir: Path) -> dict:
    meta_path = post_dir / "meta.json"
    if not meta_path.is_file():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def find_post_dir(slug: str) -> Path | None:
    if not POSTS_DIR.is_dir():
        return None
    slug = slug.strip().lower()
    for post_dir in sorted(POSTS_DIR.iterdir()):
        if not post_dir.is_dir():
            continue
        meta = _load_meta(post_dir)
        meta_slug = str(meta.get("slug") or "").lower()
        if meta_slug == slug or slug in post_dir.name.lower():
            return post_dir
    return None


def list_post_slugs() -> list[str]:
    if not POSTS_DIR.is_dir():
        return []
    slugs: list[str] = []
    for post_dir in sorted(POSTS_DIR.iterdir()):
        if not post_dir.is_dir():
            continue
        meta = _load_meta(post_dir)
        slug = str(meta.get("slug") or post_dir.name.split("-", 1)[-1])
        slugs.append(slug)
    return slugs


def is_auto_publishable(meta: dict) -> bool:
    if meta.get("auto_publish") is False:
        return False
    status = str(meta.get("status") or "").strip().lower()
    if status == "draft":
        return False
    if status in AUTO_PUBLISH_STATUSES:
        return True
    return bool(meta.get("auto_publish"))


def post_slot(meta: dict) -> str:
    slot = str(meta.get("slot") or "").strip().lower()
    if slot in VALID_SLOTS:
        return slot
    day = str(meta.get("day") or "").strip().lower()
    if day in {"monday", "tuesday"}:
        return "morning"
    if day in {"thursday", "friday", "saturday"}:
        return "lunch"
    return "evening"


def iter_publishable_posts() -> list[tuple[str, str, dict]]:
    if not POSTS_DIR.is_dir():
        return []
    rows: list[tuple[str, str, dict]] = []
    for post_dir in sorted(POSTS_DIR.iterdir()):
        if not post_dir.is_dir():
            continue
        meta = _load_meta(post_dir)
        slug = str(meta.get("slug") or post_dir.name.split("-", 1)[-1])
        if not is_auto_publishable(meta):
            continue
        post_txt = post_dir / "post.txt"
        gif_path = post_dir / f"{slug}.gif"
        if not post_txt.is_file() or not gif_path.is_file():
            continue
        rows.append((slug, post_slot(meta), meta))
    return rows


def list_publishable_slugs_for_slot(slot: str) -> list[str]:
    slot = slot.strip().lower()
    return [slug for slug, post_slot_name, _ in iter_publishable_posts() if post_slot_name == slot]


def pick_slug_for_slot(slot: str, date_key: str) -> str:
    pool = list_publishable_slugs_for_slot(slot)
    if not pool:
        all_slugs = [slug for slug, _, _ in iter_publishable_posts()]
        if not all_slugs:
            known = ", ".join(list_post_slugs()) or "—"
            raise FileNotFoundError(f"No publishable channel posts for slot {slot}. Known: {known}")
        pool = all_slugs
    day_index = date.fromisoformat(date_key).toordinal()
    return pool[day_index % len(pool)]


def load_post_bundle(slug: str) -> ChannelPostBundle:
    post_dir = find_post_dir(slug)
    if post_dir is None:
        known = ", ".join(list_post_slugs()) or "—"
        raise FileNotFoundError(f"Unknown post slug: {slug}. Known: {known}")

    meta = _load_meta(post_dir)
    resolved_slug = str(meta.get("slug") or slug)
    post_txt = post_dir / "post.txt"
    if not post_txt.is_file():
        raise FileNotFoundError(f"Missing post.txt in {post_dir}")

    gif_path = post_dir / f"{resolved_slug}.gif"
    if not gif_path.is_file():
        raise FileNotFoundError(f"Missing GIF: {gif_path.name}")

    caption = post_txt.read_text(encoding="utf-8").strip()
    if not caption:
        raise ValueError(f"Empty post.txt in {post_dir}")

    return ChannelPostBundle(
        slug=resolved_slug,
        folder=post_dir,
        caption=caption,
        gif_path=gif_path,
        meta=meta,
    )
