"""Render marketing/weekly/*.gif from *-base.png — modern cosmic magic animation."""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
WEEKLY_DIR = ROOT / "marketing" / "weekly"

TARGET_WIDTH = 480
FRAME_COUNT = 24
FRAME_MS = 110


@dataclass(frozen=True)
class WeeklyGifTheme:
    slug: str
    glow_rgb: tuple[int, int, int]
    sparkle_rgb: tuple[int, int, int]
    aurora_rgb: tuple[int, int, int]
    center_y: float = 0.42
    ring_rotate: float = 1.0
    breath: float = 0.05
    photo_base: bool = False


THEMES: tuple[WeeklyGifTheme, ...] = (
    WeeklyGifTheme(
        "health-madness",
        (130, 240, 220),
        (255, 230, 160),
        (190, 150, 255),
        center_y=0.48,
        breath=0.025,
        ring_rotate=0.35,
        photo_base=True,
    ),
    WeeklyGifTheme(
        "love-week",
        (255, 120, 190),
        (255, 240, 250),
        (255, 160, 220),
    ),
    WeeklyGifTheme(
        "money-week",
        (120, 255, 170),
        (255, 240, 180),
        (80, 220, 140),
    ),
    WeeklyGifTheme(
        "karma-week",
        (180, 150, 255),
        (220, 240, 255),
        (120, 200, 255),
    ),
)


def _load_base(source: Path) -> Image.Image:
    if not source.is_file():
        raise FileNotFoundError(f"Missing source image: {source}")
    img = Image.open(source).convert("RGBA")
    ratio = TARGET_WIDTH / img.width
    height = int(img.height * ratio)
    return img.resize((TARGET_WIDTH, height), Image.Resampling.LANCZOS)


def _glow_overlay(
    size: tuple[int, int],
    phase: float,
    theme: WeeklyGifTheme,
) -> Image.Image:
    w, h = size
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = w // 2
    cy = int(h * theme.center_y)
    pulse = 0.5 + 0.5 * math.sin(phase)
    radius = int(min(w, h) * (0.2 + 0.06 * pulse))
    r, g, b = theme.glow_rgb
    for step in range(10, 0, -1):
        alpha = int(22 * pulse * step / 10)
        rad = radius + step * 8
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(r, g, b, alpha))
    return overlay.filter(ImageFilter.GaussianBlur(radius=16))


def _aurora_sweep(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ar, ag, ab = theme.aurora_rgb
    for band in range(3):
        y = int(h * (0.12 + band * 0.08) + 12 * math.sin(phase + band))
        points = []
        for x in range(0, w + 20, 20):
            wave = 18 * math.sin(phase * 1.4 + x / 55 + band)
            points.append((x, y + wave))
        points.extend([(w, h), (0, h)])
        if len(points) >= 3:
            alpha = 35 + band * 10
            draw.polygon(points, fill=(ar, ag, ab, alpha))
    return layer.filter(ImageFilter.GaussianBlur(radius=14))


def _magic_ring_spin(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = w // 2, int(h * theme.center_y)
    r, g, b = theme.sparkle_rgb
    for ring_idx, (radius, count) in enumerate(((130, 12), (155, 8))):
        for i in range(count):
            angle = phase * theme.ring_rotate * (1 if ring_idx == 0 else -0.7) + i * (2 * math.pi / count)
            x = cx + int(radius * math.cos(angle))
            y = cy + int(radius * math.sin(angle))
            tw = 0.4 + 0.6 * abs(math.sin(phase * 2 + i))
            rad = 2 if tw < 0.7 else 3
            draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(r, g, b, int(140 * tw)))
    return layer


def _sparkles(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    specs = (
        (0.12, 0.1, 2.4),
        (0.28, 0.07, 1.9),
        (0.45, 0.05, 2.8),
        (0.62, 0.09, 2.1),
        (0.78, 0.11, 1.7),
        (0.35, 0.17, 1.5),
        (0.55, 0.15, 2.0),
        (0.88, 0.2, 2.3),
        (0.08, 0.22, 1.8),
    )
    sr, sg, sb = theme.sparkle_rgb
    gr, gg, gb = theme.glow_rgb
    for idx, (rx, ry, speed) in enumerate(specs):
        x = int(w * rx + 10 * math.sin(phase * speed + idx))
        y = int(h * ry - 14 * math.sin(phase * speed * 0.8 + idx * 0.7))
        twinkle = 0.3 + 0.7 * abs(math.sin(phase * 3 + idx * 1.1))
        alpha = int(190 * twinkle)
        rad = 2 if twinkle < 0.55 else 3
        color = (gr, gg, gb, alpha) if idx % 3 == 0 else (sr, sg, sb, alpha)
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=color)
        if twinkle > 0.75:
            draw.line((x - 5, y, x + 5, y), fill=(*color[:3], alpha // 2), width=1)
            draw.line((x, y - 5, x, y + 5), fill=(*color[:3], alpha // 2), width=1)
    return layer


def _shooting_star(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    progress = (phase / (2 * math.pi)) % 1.0
    if progress > 0.55:
        return layer
    t = progress / 0.55
    x = int(w * (0.1 + 0.75 * t))
    y = int(h * (0.08 + 0.12 * t))
    r, g, b = theme.sparkle_rgb
    draw.line((x - 28, y + 10, x, y), fill=(r, g, b, int(180 * (1 - t))), width=2)
    draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 220))
    return layer.filter(ImageFilter.GaussianBlur(radius=0.6))


def _floating_sparkles(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    """Extra gentle sparkles near the figure — health theme only."""
    if theme.slug != "health-madness":
        return Image.new("RGBA", size, (0, 0, 0, 0))
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = w // 2, int(h * theme.center_y)
    sr, sg, sb = theme.sparkle_rgb
    spots = (
        (cx + 38, cy - 14),
        (cx + 52, cy - 24),
        (cx - 58, cy - 38),
        (cx + 48, cy + 18),
        (cx - 42, cy - 58),
    )
    for idx, (x, y) in enumerate(spots):
        bob = int(4 * math.sin(phase * 2.2 + idx))
        tw = 0.35 + 0.65 * abs(math.sin(phase * 3 + idx * 0.9))
        rad = 2 if tw < 0.6 else 3
        draw.ellipse(
            (x - rad, y + bob - rad, x + rad, y + bob + rad),
            fill=(sr, sg, sb, int(170 * tw)),
        )
    return layer


def _photo_sparkle_pulse(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    """Subtle twinkle over the hand-light area on photographic bases."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = int(w * 0.38), int(h * 0.52)
    sr, sg, sb = theme.sparkle_rgb
    for idx, (dx, dy, speed) in enumerate(((0, 0, 1.0), (12, -8, 1.3), (-10, 6, 1.1), (18, 4, 1.5))):
        tw = 0.25 + 0.75 * abs(math.sin(phase * speed * 2 + idx))
        x = cx + dx + int(3 * math.sin(phase + idx))
        y = cy + dy + int(2 * math.cos(phase * 0.8 + idx))
        rad = 2 if tw < 0.55 else 3
        alpha = int(120 * tw)
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(sr, sg, sb, alpha))
        if tw > 0.7:
            draw.line((x - 4, y, x + 4, y), fill=(sr, sg, sb, alpha // 2), width=1)
            draw.line((x, y - 4, x, y + 4), fill=(sr, sg, sb, alpha // 2), width=1)
    return layer.filter(ImageFilter.GaussianBlur(radius=0.4))


def build_frames(base: Image.Image, theme: WeeklyGifTheme) -> list[Image.Image]:
    frames: list[Image.Image] = []
    for i in range(FRAME_COUNT):
        phase = (2 * math.pi * i) / FRAME_COUNT
        frame = base.copy()
        if theme.photo_base:
            frame = Image.alpha_composite(frame, _photo_sparkle_pulse(frame.size, phase, theme))
            breath = 1.0 + theme.breath * math.sin(phase)
            frame = ImageEnhance.Brightness(frame).enhance(breath)
            frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
            continue
        frame = Image.alpha_composite(frame, _aurora_sweep(frame.size, phase, theme))
        frame = Image.alpha_composite(frame, _glow_overlay(frame.size, phase, theme))
        frame = Image.alpha_composite(frame, _magic_ring_spin(frame.size, phase, theme))
        frame = Image.alpha_composite(frame, _sparkles(frame.size, phase, theme))
        frame = Image.alpha_composite(frame, _floating_sparkles(frame.size, phase, theme))
        frame = Image.alpha_composite(frame, _shooting_star(frame.size, phase, theme))
        breath = 1.0 + theme.breath * math.sin(phase)
        frame = ImageEnhance.Brightness(frame).enhance(breath)
        contrast = 1.0 + 0.04 * math.sin(phase * 1.5)
        frame = ImageEnhance.Contrast(frame).enhance(contrast)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
    return frames


def render_theme(theme: WeeklyGifTheme) -> Path:
    source = WEEKLY_DIR / f"{theme.slug}-base.png"
    output = WEEKLY_DIR / f"{theme.slug}.gif"
    base = _load_base(source)
    frames = build_frames(base, theme)
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
    print(f"OK {output.name} ({size_kb:.0f} KB, {len(frames)} frames)")
    return output


def main() -> None:
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        render_theme(theme)


if __name__ == "__main__":
    main()
