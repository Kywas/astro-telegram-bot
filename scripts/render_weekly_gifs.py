"""Render marketing/weekly/*.gif from *-base.png — modern cosmic magic animation."""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
WEEKLY_DIR = ROOT / "marketing" / "weekly"

TARGET_WIDTH = 480
TARGET_HEIGHT = 540
FRAME_COUNT = 24
FRAME_MS = 100
PHOTO_OVERLAY_INTENSITY = 0.88
PHOTO_KEN_BURNS = 0.0
PHOTO_SHARPNESS = 1.06


def prepare_photo_base(source: Path, dest: Path) -> Path:
    """Center-crop and resize a photographic base to Telegram weekly size."""
    img = Image.open(source).convert("RGB")
    w, h = img.size
    scale = max(TARGET_WIDTH / w, TARGET_HEIGHT / h)
    nw, nh = int(w * scale), int(h * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - TARGET_WIDTH) // 2
    top = (nh - TARGET_HEIGHT) // 2
    img = img.crop((left, top, left + TARGET_WIDTH, top + TARGET_HEIGHT))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, optimize=True)
    return dest


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
    sparkle_anchor: tuple[float, float] = (0.5, 0.5)


THEMES: tuple[WeeklyGifTheme, ...] = (
    WeeklyGifTheme(
        "health-madness",
        (130, 240, 220),
        (255, 230, 160),
        (190, 150, 255),
        center_y=0.48,
        breath=0.022,
        photo_base=True,
        sparkle_anchor=(0.36, 0.54),
    ),
    WeeklyGifTheme(
        "love-week",
        (255, 160, 200),
        (255, 220, 200),
        (255, 120, 180),
        center_y=0.45,
        breath=0.02,
        photo_base=True,
        sparkle_anchor=(0.52, 0.46),
    ),
    WeeklyGifTheme(
        "money-week",
        (255, 210, 120),
        (255, 240, 200),
        (120, 255, 180),
        center_y=0.44,
        breath=0.018,
        photo_base=True,
        sparkle_anchor=(0.42, 0.58),
    ),
    WeeklyGifTheme(
        "karma-week",
        (190, 160, 255),
        (220, 240, 255),
        (150, 180, 255),
        center_y=0.46,
        breath=0.02,
        photo_base=True,
        sparkle_anchor=(0.48, 0.52),
    ),
)


def _attenuate_layer(layer: Image.Image, factor: float) -> Image.Image:
    if factor >= 0.999:
        return layer
    r, g, b, a = layer.split()
    a = a.point(lambda x: int(x * factor))
    return Image.merge("RGBA", (r, g, b, a))


def _apply_ken_burns(frame: Image.Image, phase: float, amount: float = PHOTO_KEN_BURNS) -> Image.Image:
    """Subtle zoom + drift so the photo itself moves, not only overlays."""
    w, h = frame.size
    scale = 1.0 + amount * (0.5 + 0.5 * math.sin(phase))
    nw, nh = int(w * scale), int(h * scale)
    enlarged = frame.resize((nw, nh), Image.Resampling.LANCZOS)
    shift_x = int(6 * math.sin(phase * 0.85))
    shift_y = int(4 * math.cos(phase * 0.65))
    left = (nw - w) // 2 + shift_x
    top = (nh - h) // 2 + shift_y
    left = max(0, min(left, nw - w))
    top = max(0, min(top, nh - h))
    return enlarged.crop((left, top, left + w, top + h))


def _load_base(source: Path) -> Image.Image:
    if not source.is_file():
        raise FileNotFoundError(f"Missing source image: {source}")
    img = Image.open(source).convert("RGBA")
    if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
        tmp = source.parent / f".{source.stem}-resized.png"
        prepare_photo_base(source, tmp)
        img = Image.open(tmp).convert("RGBA")
    return img


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
    for step in range(6, 0, -1):
        alpha = int(14 * pulse * step / 6)
        rad = radius + step * 5
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(r, g, b, alpha))
    return overlay.filter(ImageFilter.GaussianBlur(radius=6))


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
            alpha = 22 + band * 6
            draw.polygon(points, fill=(ar, ag, ab, alpha))
    return layer.filter(ImageFilter.GaussianBlur(radius=5))


def _magic_ring_spin(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = w // 2, int(h * theme.center_y)
    r, g, b = theme.sparkle_rgb
    for ring_idx, (radius, count) in enumerate(((130, 14), (155, 10), (175, 6))):
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
        (0.18, 0.35, 2.6),
        (0.42, 0.28, 1.6),
        (0.68, 0.24, 2.2),
        (0.92, 0.42, 1.9),
        (0.05, 0.55, 2.0),
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
    return layer


def _floating_sparkles(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    """Sparkles orbiting near the focal point — all themes."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ax, ay = theme.sparkle_anchor
    cx, cy = int(w * ax), int(h * ay)
    sr, sg, sb = theme.sparkle_rgb
    gr, gg, gb = theme.glow_rgb
    orbit_specs = (
        (42, 0.0, 2.2),
        (58, 1.2, 1.7),
        (36, 2.4, 2.5),
        (68, 0.8, 1.4),
        (50, 3.1, 2.0),
        (74, 1.9, 1.6),
    )
    for idx, (radius, angle0, speed) in enumerate(orbit_specs):
        angle = angle0 + phase * speed * theme.ring_rotate
        x = cx + int(radius * math.cos(angle))
        y = cy + int(radius * 0.55 * math.sin(angle))
        bob = int(5 * math.sin(phase * 2.4 + idx))
        tw = 0.35 + 0.65 * abs(math.sin(phase * 3 + idx * 0.9))
        rad = 2 if tw < 0.6 else 3
        color = (gr, gg, gb) if idx % 2 == 0 else (sr, sg, sb)
        draw.ellipse(
            (x - rad, y + bob - rad, x + rad, y + bob + rad),
            fill=(*color, int(175 * tw)),
        )
        if tw > 0.7:
            draw.line((x - 4, y + bob, x + 4, y + bob), fill=(*color, int(90 * tw)), width=1)
            draw.line((x, y + bob - 4, x, y + bob + 4), fill=(*color, int(90 * tw)), width=1)
    return layer


def _drifting_particles(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    """Slow drifting dust motes across the frame."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    sr, sg, sb = theme.sparkle_rgb
    ar, ag, ab = theme.aurora_rgb
    specs = (
        (0.08, 0.18, 1.3, 0.0),
        (0.22, 0.32, 1.8, 1.1),
        (0.38, 0.12, 1.5, 2.3),
        (0.52, 0.28, 2.1, 0.7),
        (0.66, 0.15, 1.6, 1.8),
        (0.78, 0.38, 1.9, 2.9),
        (0.14, 0.48, 1.4, 3.5),
        (0.44, 0.52, 2.0, 4.1),
        (0.84, 0.58, 1.7, 1.4),
        (0.30, 0.62, 2.2, 2.6),
        (0.58, 0.72, 1.5, 3.8),
        (0.72, 0.82, 1.8, 0.5),
    )
    for idx, (rx, ry, speed, offset) in enumerate(specs):
        drift = (phase * speed + offset) % (2 * math.pi)
        x = int(w * rx + 22 * math.sin(drift))
        y = int(h * ry - 28 * math.cos(drift * 0.75))
        tw = 0.25 + 0.75 * abs(math.sin(phase * 2.5 + idx * 0.8))
        rad = 1 if tw < 0.5 else 2
        color = (sr, sg, sb) if idx % 3 else (ar, ag, ab)
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(*color, int(110 * tw)))
    return layer


def _light_streaks(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    """Two soft light streaks at different speeds."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    r, g, b = theme.glow_rgb
    for streak_idx, (y_base, speed, width) in enumerate(((0.22, 1.1, 40), (0.68, -0.9, 55))):
        progress = (phase * speed / (2 * math.pi)) % 1.0
        x_start = int(w * (-0.15 + 1.3 * progress))
        y = int(h * y_base + 12 * math.sin(phase + streak_idx))
        alpha = int(55 * abs(math.sin(progress * math.pi)))
        draw.line((x_start, y, x_start + width, y + 8), fill=(r, g, b, alpha), width=2)
    return layer


def _photo_sparkle_pulse(size: tuple[int, int], phase: float, theme: WeeklyGifTheme) -> Image.Image:
    """Subtle twinkle on photographic bases — anchor per theme."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ax, ay = theme.sparkle_anchor
    cx, cy = int(w * ax), int(h * ay)
    sr, sg, sb = theme.sparkle_rgb
    offsets = ((0, 0, 1.0), (14, -10, 1.3), (-12, 8, 1.1), (20, 6, 1.5), (-8, -14, 1.2))
    for idx, (dx, dy, speed) in enumerate(offsets):
        tw = 0.25 + 0.75 * abs(math.sin(phase * speed * 2 + idx))
        x = cx + dx + int(3 * math.sin(phase + idx))
        y = cy + dy + int(2 * math.cos(phase * 0.8 + idx))
        rad = 2 if tw < 0.55 else 3
        alpha = int(115 * tw)
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(sr, sg, sb, alpha))
        if tw > 0.72:
            draw.line((x - 4, y, x + 4, y), fill=(sr, sg, sb, alpha // 2), width=1)
            draw.line((x, y - 4, x, y + 4), fill=(sr, sg, sb, alpha // 2), width=1)
    return layer


def _compose_photo_layers(
    size: tuple[int, int],
    phase: float,
    theme: WeeklyGifTheme,
) -> Image.Image:
    """Sharp overlays only — no aurora/glow haze on photographic bases."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    spin_theme = WeeklyGifTheme(
        slug=theme.slug,
        glow_rgb=theme.glow_rgb,
        sparkle_rgb=theme.sparkle_rgb,
        aurora_rgb=theme.aurora_rgb,
        center_y=theme.center_y,
        ring_rotate=theme.ring_rotate * 1.35,
        breath=theme.breath,
        photo_base=theme.photo_base,
        sparkle_anchor=theme.sparkle_anchor,
    )
    for part in (
        _magic_ring_spin(size, phase, spin_theme),
        _sparkles(size, phase, theme),
        _floating_sparkles(size, phase, theme),
        _drifting_particles(size, phase, theme),
        _photo_sparkle_pulse(size, phase, theme),
        _shooting_star(size, phase, theme),
        _shooting_star(size, phase + math.pi * 0.55, theme),
    ):
        layer = Image.alpha_composite(layer, part)
    return layer


def _compose_magic_layers(
    size: tuple[int, int],
    phase: float,
    theme: WeeklyGifTheme,
    *,
    intensity: float = 1.0,
) -> Image.Image:
    """Stack aurora, glow, rings, particles — optional alpha scaling for photo bases."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    spin_theme = WeeklyGifTheme(
        slug=theme.slug,
        glow_rgb=theme.glow_rgb,
        sparkle_rgb=theme.sparkle_rgb,
        aurora_rgb=theme.aurora_rgb,
        center_y=theme.center_y,
        ring_rotate=theme.ring_rotate * 1.35,
        breath=theme.breath,
        photo_base=theme.photo_base,
        sparkle_anchor=theme.sparkle_anchor,
    )
    parts = (
        _aurora_sweep(size, phase, theme),
        _glow_overlay(size, phase, theme),
        _light_streaks(size, phase, theme),
        _magic_ring_spin(size, phase, spin_theme),
        _drifting_particles(size, phase, theme),
        _sparkles(size, phase, theme),
        _floating_sparkles(size, phase, theme),
        _shooting_star(size, phase, theme),
        _photo_sparkle_pulse(size, phase, theme),
    )
    for part in parts:
        if intensity < 0.999:
            part = _attenuate_layer(part, intensity)
        layer = Image.alpha_composite(layer, part)
    # Second shooting star offset in the loop
    star2_phase = phase + math.pi * 0.55
    star2 = _shooting_star(size, star2_phase, theme)
    if intensity < 0.999:
        star2 = _attenuate_layer(star2, intensity * 0.85)
    layer = Image.alpha_composite(layer, star2)
    return layer


def build_frames(base: Image.Image, theme: WeeklyGifTheme) -> list[Image.Image]:
    frames: list[Image.Image] = []
    for i in range(FRAME_COUNT):
        phase = (2 * math.pi * i) / FRAME_COUNT
        frame = base.copy()
        if theme.photo_base:
            if PHOTO_KEN_BURNS > 0:
                frame = _apply_ken_burns(frame, phase)
            frame = Image.alpha_composite(frame, _compose_photo_layers(frame.size, phase, theme))
            breath = 1.0 + theme.breath * 0.6 * math.sin(phase)
            frame = ImageEnhance.Brightness(frame).enhance(breath)
            frame = ImageEnhance.Sharpness(frame).enhance(PHOTO_SHARPNESS)
            frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
            continue
        frame = Image.alpha_composite(frame, _compose_magic_layers(frame.size, phase, theme))
        breath = 1.0 + theme.breath * math.sin(phase)
        frame = ImageEnhance.Brightness(frame).enhance(breath)
        contrast = 1.0 + 0.04 * math.sin(phase * 1.5)
        frame = ImageEnhance.Contrast(frame).enhance(contrast)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
    return frames


def render_theme(theme: WeeklyGifTheme, *, edition: int = 0) -> Path:
    source = WEEKLY_DIR / (f"{theme.slug}-base.png" if edition == 0 else f"{theme.slug}-e{edition}-base.png")
    output = WEEKLY_DIR / (f"{theme.slug}.gif" if edition == 0 else f"{theme.slug}-e{edition}.gif")
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
        for edition in range(3):
            source = WEEKLY_DIR / (
                f"{theme.slug}-base.png" if edition == 0 else f"{theme.slug}-e{edition}-base.png"
            )
            if not source.is_file():
                print(f"SKIP {theme.slug} e{edition} — missing {source.name}")
                continue
            render_theme(theme, edition=edition)


if __name__ == "__main__":
    main()
