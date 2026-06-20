"""Render marketing/weekly/health-madness.gif — use render_weekly_gifs.py for all themes."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_weekly_gifs import WeeklyGifTheme, render_theme  # noqa: E402

if __name__ == "__main__":
    render_theme(
        WeeklyGifTheme(
            "health-madness",
            (120, 255, 220),
            (255, 255, 255),
            (160, 120, 255),
        )
    )
