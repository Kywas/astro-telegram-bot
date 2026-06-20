"""Render marketing/channel/posts/*/*.gif from *-base.png — realistic photo + soft magic."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "marketing" / "channel" / "posts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.render_weekly_gifs import WeeklyGifTheme, build_frames, prepare_photo_base  # noqa: E402

FRAME_MS = 110


def _load_meta(post_dir: Path) -> dict:
    for name in ("meta.json", "meta.yaml"):
        meta_path = post_dir / name
        if meta_path.is_file():
            if name.endswith(".json"):
                return json.loads(meta_path.read_text(encoding="utf-8"))
            raise RuntimeError("Install PyYAML or use meta.json")
    raise FileNotFoundError(f"Missing meta.json in {post_dir}")


def _theme_from_meta(meta: dict) -> WeeklyGifTheme:
    gif = meta.get("gif") or {}
    slug = str(meta.get("slug") or "post")
    return WeeklyGifTheme(
        slug=slug,
        glow_rgb=tuple(gif.get("glow_rgb", [180, 200, 255])),
        sparkle_rgb=tuple(gif.get("sparkle_rgb", [255, 245, 220])),
        aurora_rgb=tuple(gif.get("aurora_rgb", [140, 160, 255])),
        center_y=float(gif.get("center_y", 0.42)),
        breath=float(gif.get("breath", 0.022)),
        photo_base=True,
        sparkle_anchor=tuple(gif.get("sparkle_anchor", [0.5, 0.45])),
    )


def find_post_dirs(*slugs: str) -> list[Path]:
    if not POSTS_DIR.is_dir():
        raise FileNotFoundError(f"Missing posts dir: {POSTS_DIR}")
    dirs = sorted(p for p in POSTS_DIR.iterdir() if p.is_dir())
    if not slugs:
        return dirs
    selected: list[Path] = []
    for slug in slugs:
        match = next(
            (
                d
                for d in dirs
                if slug in d.name or (_load_meta_safe(d).get("slug") == slug)
            ),
            None,
        )
        if match is None:
            raise FileNotFoundError(f"No post folder for slug: {slug}")
        selected.append(match)
    return selected


def _load_meta_safe(post_dir: Path) -> dict:
    try:
        return _load_meta(post_dir)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def render_post(post_dir: Path) -> Path:
    meta = _load_meta(post_dir)
    slug = str(meta.get("slug") or post_dir.name.split("-", 1)[-1])
    theme = _theme_from_meta(meta)
    source = post_dir / f"{slug}-base.png"
    if not source.is_file():
        raise FileNotFoundError(f"Missing photo base: {source}")
    prepared = post_dir / f".{slug}-prepared.png"
    prepare_photo_base(source, prepared)
    from PIL import Image

    base = Image.open(prepared).convert("RGBA")
    frames = build_frames(base, theme)
    output = post_dir / f"{slug}.gif"
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    size_kb = output.stat().st_size / 1024
    print(f"OK {output.relative_to(ROOT)} ({size_kb:.0f} KB, {len(frames)} frames)")
    if prepared.is_file():
        prepared.unlink()
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Render channel post GIFs")
    parser.add_argument("slugs", nargs="*", help="Post slug(s), e.g. energy-day")
    parser.add_argument("--all", action="store_true", help="Render every post folder")
    args = parser.parse_args()

    if args.all:
        post_dirs = find_post_dirs()
    elif args.slugs:
        post_dirs = find_post_dirs(*args.slugs)
    else:
        parser.error("Pass slug(s) or --all")

    for post_dir in post_dirs:
        render_post(post_dir)


if __name__ == "__main__":
    main()
