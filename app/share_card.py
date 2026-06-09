"""PNG forecast cards for sharing in Telegram."""

from __future__ import annotations

import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.horoscope import ShareForecastContext

CARD_WIDTH = 900
CARD_HEIGHT = 1200
MARGIN = 56

FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
)


def _load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_paths = [p for p in FONT_CANDIDATES if p != bold_path]
    paths = [bold_path, *regular_paths] if bold else regular_paths
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _draw_gradient_background(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    top = (18, 14, 42)
    bottom = (48, 36, 92)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)


def _draw_stars(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    points = (
        (80, 120), (760, 180), (140, 340), (820, 420), (220, 560),
        (680, 640), (90, 780), (740, 860), (360, 980), (540, 1040),
    )
    for x, y in points:
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 120))


def _wrap_text(text: str, width: int) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    return textwrap.wrap(cleaned, width=width)


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int],
    max_width_chars: int,
    line_gap: int = 10,
) -> int:
    x, y = xy
    lines = _wrap_text(text, max_width_chars)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y = bbox[3] + line_gap
    return y


def render_share_card(context: ShareForecastContext) -> bytes:
    image = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), color=(18, 14, 42))
    draw = ImageDraw.Draw(image)
    _draw_gradient_background(draw, CARD_WIDTH, CARD_HEIGHT)
    _draw_stars(draw, CARD_WIDTH, CARD_HEIGHT)

    title_font = _load_font(34, bold=True)
    sign_font = _load_font(52, bold=True)
    label_font = _load_font(28, bold=True)
    body_font = _load_font(28)
    small_font = _load_font(24)
    footer_font = _load_font(30, bold=True)

    accent = (236, 196, 90)
    muted = (196, 188, 220)
    white = (250, 248, 255)

    if context.locale == "ru":
        title = f"Астрологический прогноз · {context.period_label}"
        energy_label = "Общая энергия"
        advice_label = "Совет дня"
        lucky_label = "Удачное время"
        affirmation_label = "Аффirmация"
        footer = "AstroPulse"
    else:
        title = f"Astrological forecast · {context.period_label}"
        energy_label = "General energy"
        advice_label = "Advice of the day"
        lucky_label = "Lucky time"
        affirmation_label = "Affirmation"
        footer = "AstroPulse"

    y = MARGIN
    draw.text((MARGIN, y), title, font=title_font, fill=accent)
    y += 56

    sign_line = f"{context.sign_emoji} {context.sign_name}".strip()
    draw.text((MARGIN, y), sign_line, font=sign_font, fill=white)
    y += 84

    draw.text((MARGIN, y), energy_label, font=label_font, fill=accent)
    y += 42
    bar_x = MARGIN
    bar_y = y
    bar_w = CARD_WIDTH - MARGIN * 2
    bar_h = 18
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=9, fill=(70, 62, 110))
    fill_w = max(12, int(bar_w * context.energy_score / 10))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + fill_w, bar_y + bar_h), radius=9, fill=accent)
    y += 34
    draw.text((MARGIN, y), f"{context.energy_score}/10", font=body_font, fill=white)
    y += 48

    draw.text((MARGIN, y), advice_label, font=label_font, fill=accent)
    y += 42
    y = _draw_wrapped_text(
        draw,
        (MARGIN, y),
        context.advice,
        font=body_font,
        fill=white,
        max_width_chars=34,
    ) + 18

    draw.text((MARGIN, y), lucky_label, font=label_font, fill=accent)
    y += 42
    draw.text((MARGIN, y), context.lucky_time, font=body_font, fill=white)
    y += 48

    draw.text((MARGIN, y), affirmation_label, font=label_font, fill=accent)
    y += 42
    y = _draw_wrapped_text(
        draw,
        (MARGIN, y),
        context.affirmation,
        font=small_font,
        fill=muted,
        max_width_chars=38,
        line_gap=8,
    )

    draw.text((MARGIN, CARD_HEIGHT - MARGIN - 36), footer, font=footer_font, fill=accent)
    draw.text((MARGIN, CARD_HEIGHT - MARGIN - 72), "✦", font=sign_font, fill=muted)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()
