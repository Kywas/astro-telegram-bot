"""Unique photo bases for channel posts — no duplicate GIF sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageEnhance

from scripts.render_weekly_gifs import TARGET_HEIGHT, TARGET_WIDTH, prepare_photo_base

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "marketing" / "channel" / "posts"
WEEKLY_DIR = ROOT / "marketing" / "weekly"

# Keep original art for the first two launch posts.
LOCKED_SLUGS = frozenset({"energy-day", "quiet-mind"})

WEEKLY_FULL = (
    "health-madness.png",
    "love-week.png",
    "money-week.png",
    "karma-week.png",
)


def discover_source_pool() -> list[Path]:
    pool: list[Path] = []
    seen: set[str] = set()
    for path in sorted(WEEKLY_DIR.glob("*-base.png")):
        key = path.name.lower()
        if key not in seen:
            seen.add(key)
            pool.append(path)
    for name in WEEKLY_FULL:
        path = WEEKLY_DIR / name
        if path.is_file() and name.lower() not in seen:
            seen.add(name.lower())
            pool.append(path)
    if not pool:
        raise FileNotFoundError(f"No source images in {WEEKLY_DIR}")
    return pool


def variant_preset(index: int) -> dict[str, float | int | bool]:
    """Deterministic framing/color preset — 31+ unique combinations."""
    i = max(0, int(index))
    return {
        "crop_dx": ((i * 17) % 45) - 22,
        "crop_dy": ((i * 13) % 33) - 16,
        "flip": (i % 4) == 1,
        "zoom": 0.015 + (i % 6) * 0.011,
        "sat": 0.90 + (i % 8) * 0.022,
        "bright": 0.94 + (i % 5) * 0.018,
        "warm": (i % 7) - 3,
    }


def _apply_warm_tint(img: Image.Image, warm: int) -> Image.Image:
    if warm == 0:
        return img
    r, g, b = img.split()
    if warm > 0:
        r = r.point(lambda x: min(255, x + warm * 3))
        b = b.point(lambda x: max(0, x - warm * 2))
    else:
        w = abs(warm)
        b = b.point(lambda x: min(255, x + w * 3))
        r = r.point(lambda x: max(0, x - w * 2))
    return Image.merge("RGB", (r, g, b))


def prepare_photo_base_varied(source: Path, dest: Path, variant: int) -> Path:
    preset = variant_preset(variant)
    img = Image.open(source).convert("RGB")
    if preset["flip"]:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    w, h = img.size
    scale = max(TARGET_WIDTH / w, TARGET_HEIGHT / h) * (1.0 + float(preset["zoom"]))
    nw, nh = int(w * scale), int(h * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)

    left = (nw - TARGET_WIDTH) // 2 + int(preset["crop_dx"])
    top = (nh - TARGET_HEIGHT) // 2 + int(preset["crop_dy"])
    left = max(0, min(left, nw - TARGET_WIDTH))
    top = max(0, min(top, nh - TARGET_HEIGHT))
    img = img.crop((left, top, left + TARGET_WIDTH, top + TARGET_HEIGHT))

    img = _apply_warm_tint(img, int(preset["warm"]))
    img = ImageEnhance.Color(img).enhance(float(preset["sat"]))
    img = ImageEnhance.Brightness(img).enhance(float(preset["bright"]))

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, optimize=True)
    return dest


def assignment_for_index(index: int, pool_size: int) -> tuple[int, int]:
    """Return (source_index, variant_index) for sorted post folder index."""
    return index % pool_size, index


def default_assignment(slug: str, index: int, pool: list[Path]) -> dict[str, object]:
    src_idx, variant = assignment_for_index(index, len(pool))
    source = pool[src_idx]
    rel = source.relative_to(ROOT).as_posix()
    return {
        "base_source": rel,
        "base_variant": variant,
        "base_locked": slug in LOCKED_SLUGS,
    }


def _load_meta(post_dir: Path) -> dict:
    meta_path = post_dir / "meta.json"
    if not meta_path.is_file():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _save_meta(post_dir: Path, meta: dict) -> None:
    (post_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def ensure_post_base(post_dir: Path, *, force: bool = False) -> Path:
    """Build {slug}-base.png from meta base_source/base_variant if needed."""
    meta = _load_meta(post_dir)
    slug = str(meta.get("slug") or post_dir.name.split("-", 1)[-1])
    dest = post_dir / f"{slug}-base.png"

    if meta.get("base_locked") and dest.is_file() and not force:
        return dest

    pool = discover_source_pool()
    index = sorted(p.name for p in POSTS_DIR.iterdir() if p.is_dir()).index(post_dir.name)

    source_rel = str(meta.get("base_source") or "")
    variant = meta.get("base_variant")
    if not source_rel or variant is None:
        assignment = default_assignment(slug, index, pool)
        meta.update(assignment)
        source_rel = str(meta["base_source"])
        variant = int(meta["base_variant"])
        _save_meta(post_dir, meta)

    source = ROOT / Path(source_rel)
    if not source.is_file():
        raise FileNotFoundError(f"Missing base source: {source}")

    if slug in LOCKED_SLUGS and dest.is_file() and not force:
        return dest

    prepare_photo_base_varied(source, dest, int(variant))
    return dest


def assign_all_posts(*, force: bool = False) -> list[tuple[str, str, int]]:
    pool = discover_source_pool()
    rows: list[tuple[str, str, int]] = []
    post_dirs = sorted(p for p in POSTS_DIR.iterdir() if p.is_dir())

    for index, post_dir in enumerate(post_dirs):
        meta = _load_meta(post_dir)
        slug = str(meta.get("slug") or post_dir.name.split("-", 1)[-1])
        src_idx, variant = assignment_for_index(index, len(pool))
        source = pool[src_idx]
        rel = source.relative_to(ROOT).as_posix()

        if slug in LOCKED_SLUGS:
            meta["base_locked"] = True
            dest = post_dir / f"{slug}-base.png"
            if dest.is_file():
                rows.append((slug, "locked", -1))
                _save_meta(post_dir, meta)
                continue

        meta["base_source"] = rel
        meta["base_variant"] = variant
        meta["base_locked"] = slug in LOCKED_SLUGS
        _save_meta(post_dir, meta)

        if slug not in LOCKED_SLUGS or force:
            prepare_photo_base_varied(source, post_dir / f"{slug}-base.png", variant)

        rows.append((slug, rel, variant))

    return rows


def verify_unique_bases() -> tuple[bool, list[str]]:
    groups: dict[str, list[str]] = {}
    for path in sorted(POSTS_DIR.glob("*/*-base.png")):
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        groups.setdefault(digest, []).append(path.parent.name)
    dupes = [f"{folders} share same base" for folders in groups.values() if len(folders) > 1]
    return not dupes, dupes
