"""Generate marketing/weekly/*-base.png — modern cosmic / magic style (no temple motif)."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
WEEKLY_DIR = ROOT / "marketing" / "weekly"

WIDTH = 480
HEIGHT = 540


@dataclass(frozen=True)
class BaseTheme:
    slug: str
    top_rgb: tuple[int, int, int]
    mid_rgb: tuple[int, int, int]
    bottom_rgb: tuple[int, int, int]
    accent_rgb: tuple[int, int, int]
    accent2_rgb: tuple[int, int, int]
    seed: int


THEMES: tuple[BaseTheme, ...] = (
    BaseTheme(
        "health-madness",
        (8, 18, 42),
        (12, 48, 72),
        (4, 28, 38),
        (120, 255, 220),
        (180, 140, 255),
        11,
    ),
    BaseTheme(
        "love-week",
        (28, 8, 38),
        (62, 16, 58),
        (18, 6, 32),
        (255, 120, 190),
        (255, 200, 230),
        23,
    ),
    BaseTheme(
        "money-week",
        (6, 22, 18),
        (10, 52, 38),
        (4, 16, 24),
        (120, 255, 160),
        (255, 220, 120),
        37,
    ),
    BaseTheme(
        "karma-week",
        (14, 10, 42),
        (36, 22, 72),
        (10, 8, 28),
        (180, 150, 255),
        (120, 220, 255),
        53,
    ),
)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_color(
    c1: tuple[int, int, int],
    c2: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


def _vertical_gradient(theme: BaseTheme) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        if t < 0.55:
            local = t / 0.55
            color = _lerp_color(theme.top_rgb, theme.mid_rgb, local)
        else:
            local = (t - 0.55) / 0.45
            color = _lerp_color(theme.mid_rgb, theme.bottom_rgb, local)
        for x in range(WIDTH):
            px[x, y] = color
    return img


def _aurora_wash(base: Image.Image, theme: BaseTheme) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ar, ag, ab = theme.accent_rgb
    br, bg, bb = theme.accent2_rgb
    for band in range(4):
        cy = int(HEIGHT * (0.18 + band * 0.14))
        for step in range(6):
            alpha = 28 - step * 4
            rad_x = WIDTH // 2 + step * 18
            rad_y = 36 + step * 8
            mix = step / 5
            r = int(_lerp(ar, br, mix))
            g = int(_lerp(ag, bg, mix))
            b = int(_lerp(ab, bb, mix))
            draw.ellipse(
                (WIDTH // 2 - rad_x, cy - rad_y, WIDTH // 2 + rad_x, cy + rad_y),
                fill=(r, g, b, max(alpha, 8)),
            )
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=28))
    return Image.alpha_composite(base.convert("RGBA"), blurred)


def _star_field(size: tuple[int, int], seed: int, count: int = 120) -> Image.Image:
    rng = random.Random(seed)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    w, h = size
    for _ in range(count):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        rad = rng.choice((1, 1, 1, 2))
        alpha = rng.randint(60, 220)
        tint = rng.choice(((255, 255, 255), (220, 230, 255), (255, 230, 250)))
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(*tint, alpha))
    return layer


def _magic_ring(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int],
    *,
    segments: int = 48,
    gap_every: int = 6,
) -> None:
    for i in range(segments):
        if i % gap_every == 0:
            continue
        a1 = 2 * math.pi * i / segments
        a2 = 2 * math.pi * (i + 0.6) / segments
        x1 = cx + int(radius * math.cos(a1))
        y1 = cy + int(radius * math.sin(a1))
        x2 = cx + int(radius * math.cos(a2))
        y2 = cy + int(radius * math.sin(a2))
        draw.line((x1, y1, x2, y2), fill=(*color, 200), width=2)


def _draw_health_glyph(draw: ImageDraw.ImageDraw, cx: int, cy: int, theme: BaseTheme) -> None:
    ac = theme.accent_rgb
    for wave in range(3):
        pts = []
        for i in range(40):
            t = i / 39
            x = cx - 90 + int(180 * t)
            y = cy + int(22 * math.sin(t * math.pi * 3 + wave * 0.8))
            pts.append((x, y))
        draw.line(pts, fill=(*ac, 180 - wave * 30), width=3)
    draw.polygon(
        [
            (cx, cy - 58),
            (cx + 18, cy - 28),
            (cx + 52, cy - 24),
            (cx + 26, cy - 4),
            (cx + 34, cy + 30),
            (cx, cy + 14),
            (cx - 34, cy + 30),
            (cx - 26, cy - 4),
            (cx - 52, cy - 24),
            (cx - 18, cy - 28),
        ],
        outline=(*theme.accent2_rgb, 220),
    )


def _draw_love_glyph(draw: ImageDraw.ImageDraw, cx: int, cy: int, theme: BaseTheme) -> None:
    ac = theme.accent_rgb
    draw.pieslice((cx - 34, cy - 50, cx + 6, cy - 10), 0, 360, fill=(*ac, 210))
    draw.pieslice((cx - 6, cy - 50, cx + 34, cy - 10), 0, 360, fill=(*ac, 210))
    draw.polygon([(cx - 38, cy - 18), (cx, cy + 34), (cx + 38, cy - 18)], fill=(*ac, 230))
    for dx, dy in ((-70, -20), (70, -20), (0, -70)):
        draw.ellipse(
            (cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5),
            fill=(*theme.accent2_rgb, 180),
        )


def _draw_money_glyph(draw: ImageDraw.ImageDraw, cx: int, cy: int, theme: BaseTheme) -> None:
    ac, ac2 = theme.accent_rgb, theme.accent2_rgb
    draw.ellipse((cx - 52, cy - 52, cx + 52, cy + 52), outline=(*ac2, 220), width=3)
    draw.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), outline=(*ac, 200), width=2)
    draw.line((cx - 14, cy - 28, cx - 14, cy + 28), fill=(*ac2, 230), width=4)
    draw.arc((cx - 22, cy - 30, cx - 6, cy - 6), 90, 270, fill=(*ac2, 230), width=4)
    draw.arc((cx - 22, cy + 6, cx - 6, cy + 30), 270, 90, fill=(*ac2, 230), width=4)
    draw.line((cx + 6, cy - 18, cx + 22, cy - 18), fill=(*ac, 220), width=3)
    draw.line((cx + 6, cy + 2, cx + 22, cy + 2), fill=(*ac, 220), width=3)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = cx + int(58 * math.cos(rad))
        y1 = cy + int(58 * math.sin(rad))
        x2 = cx + int(72 * math.cos(rad))
        y2 = cy + int(72 * math.sin(rad))
        draw.line((x1, y1, x2, y2), fill=(*ac, 160), width=2)


def _hexagon_points(cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    return [
        (
            cx + radius * math.cos(math.radians(60 * i - 30)),
            cy + radius * math.sin(math.radians(60 * i - 30)),
        )
        for i in range(6)
    ]


def _draw_karma_glyph(draw: ImageDraw.ImageDraw, cx: int, cy: int, theme: BaseTheme) -> None:
    ac, ac2 = theme.accent_rgb, theme.accent2_rgb
    r = 44
    for offset in (-22, 22):
        draw.ellipse(
            (cx + offset - r, cy - r, cx + offset + r, cy + r),
            outline=(*ac, 210),
            width=3,
        )
    for i in range(8):
        a = math.radians(i * 45)
        x = cx + int(78 * math.cos(a))
        y = cy + int(78 * math.sin(a))
        draw.polygon(_hexagon_points(x, y, 7), outline=(*ac, 200), fill=(*ac2, 150))
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(*ac2, 240))


def _theme_glyph(draw: ImageDraw.ImageDraw, slug: str, cx: int, cy: int, theme: BaseTheme) -> None:
    if slug == "health-madness":
        _draw_health_glyph(draw, cx, cy, theme)
    elif slug == "love-week":
        _draw_love_glyph(draw, cx, cy, theme)
    elif slug == "money-week":
        _draw_money_glyph(draw, cx, cy, theme)
    elif slug == "karma-week":
        _draw_karma_glyph(draw, cx, cy, theme)


def _floating_orbs(draw: ImageDraw.ImageDraw, theme: BaseTheme) -> None:
    rng = random.Random(theme.seed + 7)
    ac, ac2 = theme.accent_rgb, theme.accent2_rgb
    for _ in range(10):
        x = rng.randint(40, WIDTH - 40)
        y = rng.randint(60, HEIGHT - 80)
        rad = rng.randint(10, 26)
        color = ac if rng.random() > 0.5 else ac2
        alpha = rng.randint(30, 70)
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(*color, alpha))


def render_base(theme: BaseTheme) -> Path:
    base = _vertical_gradient(theme).convert("RGBA")
    base = _aurora_wash(base, theme)
    stars = _star_field(base.size, theme.seed)
    base = Image.alpha_composite(base, stars)

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = WIDTH // 2, int(HEIGHT * 0.42)

    _floating_orbs(draw, theme)
    _magic_ring(draw, cx, cy, 118, theme.accent_rgb)
    _magic_ring(draw, cx, cy, 148, theme.accent2_rgb, segments=60, gap_every=5)

    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    ar, ag, ab = theme.accent_rgb
    gdraw.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=(ar, ag, ab, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=24))
    base = Image.alpha_composite(base, glow)

    glyph_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glyph_layer)
    _theme_glyph(gdraw, theme.slug, cx, cy, theme)
    base = Image.alpha_composite(base, glyph_layer)

    # Soft vignette
    vignette = Image.new("L", base.size, 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse((-80, -40, WIDTH + 80, HEIGHT + 120), fill=210)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=50))
    dark = Image.new("RGBA", base.size, (0, 0, 0, 255))
    base = Image.composite(base, dark, vignette)

    out = WEEKLY_DIR / f"{theme.slug}-base.png"
    base.convert("RGB").save(out, optimize=True)
    print(f"OK {out.name}")
    return out


def main() -> None:
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        render_base(theme)


if __name__ == "__main__":
    main()
