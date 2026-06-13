"""Compare local Swiss Ephemeris moon phases with USNO reference times.

USNO (U.S. Naval Observatory) publishes the same primary phases as NASA lunar
calculators. Run offline checks anytime; pass --online to also query:

  https://aa.usno.navy.mil/api/moon/phases/year?year=YYYY
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import swisseph as swe

from app.astro_engine import (
    LUNAR_DAY_MEAN_HOURS,
    MAJOR_PHASE_ELONGATION,
    _find_phase_jd,
    _lunar_day_start_jd,
)


def validate_lunar_day_lengths() -> None:
    """Each lunar day spans 12° of elongation; mean length ≈ 23h 38m."""
    new_moon_jd = utc_to_jd(datetime(2025, 6, 25, 10, 32, tzinfo=timezone.utc))
    lengths_hours: list[float] = []
    for day in range(1, 30):
        start = _lunar_day_start_jd(new_moon_jd, day)
        end = _lunar_day_start_jd(new_moon_jd, day + 1)
        lengths_hours.append((end - start) * 24.0)
    mean = sum(lengths_hours) / len(lengths_hours)
    min_h = min(lengths_hours)
    max_h = max(lengths_hours)
    print(
        f"Lunar day length: mean {mean:.2f}h (target {LUNAR_DAY_MEAN_HOURS:.2f}h), "
        f"range {min_h:.2f}–{max_h:.2f}h"
    )
    if abs(mean - LUNAR_DAY_MEAN_HOURS) > 0.5:
        raise SystemExit("FAIL: mean lunar day length drifted from synodic month/30")
    if (max_h - min_h) > 6.0:
        raise SystemExit(f"FAIL: lunar day length variation {max_h - min_h:.2f}h too wide")
    print("Lunar day lengths OK")

USNO_MAP = {
    "New Moon": "new_moon",
    "First Quarter": "first_quarter",
    "Full Moon": "full_moon",
    "Last Quarter": "last_quarter",
}

# Sample rows from USNO / NASA lunar phase tables (Universal Time).
OFFLINE_REFERENCE = [
    ("full_moon", datetime(2025, 6, 11, 7, 44, tzinfo=timezone.utc)),
    ("last_quarter", datetime(2025, 6, 18, 14, 20, tzinfo=timezone.utc)),
    ("new_moon", datetime(2025, 6, 25, 10, 32, tzinfo=timezone.utc)),
    ("first_quarter", datetime(2025, 7, 2, 19, 30, tzinfo=timezone.utc)),
    ("new_moon", datetime(2026, 6, 15, 2, 54, tzinfo=timezone.utc)),
]


def utc_to_jd(moment: datetime) -> float:
    ut_hours = moment.hour + moment.minute / 60.0 + moment.second / 3600.0
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def validate_offline(*, tolerance_min: float = 5.0) -> float:
    max_diff_min = 0.0
    for phase_key, usno_dt in OFFLINE_REFERENCE:
        target = MAJOR_PHASE_ELONGATION[phase_key]
        usno_jd = utc_to_jd(usno_dt)
        our_jd = _find_phase_jd(usno_jd, target, search_backward=True, window_days=2.0)
        diff_min = abs(our_jd - usno_jd) * 24.0 * 60.0
        max_diff_min = max(max_diff_min, diff_min)
        print(
            f"{phase_key:14} USNO {usno_dt.strftime('%Y-%m-%d %H:%M')} UTC "
            f"| diff {diff_min:.2f} min"
        )
    if max_diff_min > tolerance_min:
        raise SystemExit(f"FAIL: max diff {max_diff_min:.2f} min (> {tolerance_min} min)")
    print(f"Offline OK: max diff {max_diff_min:.2f} min")
    return max_diff_min


def usno_to_utc_jd(entry: dict) -> tuple[float, datetime]:
    dt = datetime(
        entry["year"],
        entry["month"],
        entry["day"],
        entry["hour"],
        entry["minute"],
        tzinfo=timezone.utc,
    )
    return utc_to_jd(dt), dt


def validate_online_year(year: int, *, sample: int = 12, tolerance_min: float = 5.0) -> float:
    url = f"https://aa.usno.navy.mil/api/moon/phases/year?year={year}"
    with urlopen(url, timeout=30) as resp:
        data = json.load(resp)

    max_diff_min = 0.0
    for entry in data["phasedata"][:sample]:
        key = USNO_MAP[entry["phase"]]
        target = MAJOR_PHASE_ELONGATION[key]
        usno_jd, usno_dt = usno_to_utc_jd(entry)
        our_jd = _find_phase_jd(usno_jd, target, search_backward=True, window_days=2.0)
        diff_min = abs(our_jd - usno_jd) * 24.0 * 60.0
        max_diff_min = max(max_diff_min, diff_min)
        print(
            f"{entry['phase']:14} USNO {usno_dt.strftime('%Y-%m-%d %H:%M')} UTC "
            f"| diff {diff_min:.2f} min"
        )
    if max_diff_min > tolerance_min:
        raise SystemExit(f"FAIL: max diff {max_diff_min:.2f} min (> {tolerance_min} min)")
    print(f"Online OK: max diff {max_diff_min:.2f} min")
    return max_diff_min


def main() -> None:
    validate_offline()
    validate_lunar_day_lengths()
    if "--online" in sys.argv:
        year = datetime.now().year
        for arg in sys.argv[1:]:
            if arg.isdigit():
                year = int(arg)
                break
        print(f"USNO API check — {year}")
        validate_online_year(year)


if __name__ == "__main__":
    main()
