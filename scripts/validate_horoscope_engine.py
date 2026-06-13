"""Validate horoscope transit engine against Swiss Ephemeris reference positions.

Step 1 accuracy check: natal longitudes and transit aspects match direct swe.calc_ut
and swe.houses output (same library Astro.com / AstroSeek use).
"""
from __future__ import annotations

import sys
from datetime import date, datetime, time, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import swisseph as swe

from app.astro_engine import (
    ASPECTS,
    PLANETS,
    _build_natal_forecast_longitudes,
    _collect_hits,
    _find_aspect,
    _local_moment_jd,
    _planet_longitude,
    build_astro_forecast,
)

# Reference: birth chart like Astro.com extended chart (Placidus, Swiss Ephemeris).
REFERENCE_BIRTH = {
    "birth_date": date(1990, 5, 15),
    "birth_time": time(14, 30),
    "timezone": "Europe/Moscow",
    "lat": 55.7558,
    "lon": 37.6173,
}

REFERENCE_TRANSIT = datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc)


def _jd(moment: datetime) -> float:
    ut_hours = moment.hour + moment.minute / 60.0 + moment.second / 3600.0
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def validate_natal_longitudes() -> None:
    longitudes, has_time, has_asc = _build_natal_forecast_longitudes(
        REFERENCE_BIRTH["birth_date"],
        REFERENCE_BIRTH["birth_time"],
        REFERENCE_BIRTH["timezone"],
        lat=REFERENCE_BIRTH["lat"],
        lon=REFERENCE_BIRTH["lon"],
    )
    natal_jd = _local_moment_jd(
        REFERENCE_BIRTH["birth_date"],
        REFERENCE_BIRTH["timezone"],
        hour=REFERENCE_BIRTH["birth_time"].hour,
        minute=REFERENCE_BIRTH["birth_time"].minute,
    )
    max_diff = 0.0
    for key in ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN"):
        direct = _planet_longitude(natal_jd, PLANETS[key])
        diff = abs(longitudes[key] - direct)
        max_diff = max(max_diff, diff)
        if diff > 0.001:
            raise SystemExit(f"FAIL: natal {key} diff {diff:.6f}°")
    _cusps, ascmc = swe.houses(natal_jd, REFERENCE_BIRTH["lat"], REFERENCE_BIRTH["lon"], b"P")
    asc_direct = float(ascmc[0])
    asc_diff = abs(longitudes["ASC"] - asc_direct)
    if asc_diff > 0.001:
        raise SystemExit(f"FAIL: ASC diff {asc_diff:.6f}°")
    if not has_time or not has_asc:
        raise SystemExit("FAIL: expected birth time and ASC in natal forecast points")
    print(f"Natal longitudes OK (max planet diff {max_diff:.6f}°, ASC diff {asc_diff:.6f}°)")


def validate_transit_hits_consistency() -> None:
    longitudes, _, _ = _build_natal_forecast_longitudes(
        REFERENCE_BIRTH["birth_date"],
        REFERENCE_BIRTH["birth_time"],
        REFERENCE_BIRTH["timezone"],
        lat=REFERENCE_BIRTH["lat"],
        lon=REFERENCE_BIRTH["lon"],
    )
    transit_jd = _jd(REFERENCE_TRANSIT)
    transit_longitudes = {key: _planet_longitude(transit_jd, PLANETS[key]) for key in PLANETS}
    hits = _collect_hits(
        longitudes,
        transit_longitudes,
        birth_time=REFERENCE_BIRTH["birth_time"],
        include_moon_transits=True,
    )
    if not hits:
        print("Transit hits: none within orbs at reference moment (OK if empty)")
        return
    orb, transit, natal, aspect = hits[0]
    direct_aspect = _find_aspect(transit_longitudes[transit], longitudes[natal])
    if direct_aspect is None:
        raise SystemExit(f"FAIL: top hit {transit}/{natal} not reproducible")
    if direct_aspect[0] != aspect:
        raise SystemExit(f"FAIL: aspect mismatch {aspect} vs {direct_aspect[0]}")
    print(f"Top transit hit OK: {transit} {aspect} {natal} (orb {orb:.2f}°)")


def validate_forecast_builds() -> None:
    forecast = build_astro_forecast(
        birth_date=REFERENCE_BIRTH["birth_date"],
        birth_time=REFERENCE_BIRTH["birth_time"],
        city="Moscow",
        timezone_name="Europe/Moscow",
        for_date=REFERENCE_TRANSIT.date(),
        locale="ru",
        period="day",
        lat=REFERENCE_BIRTH["lat"],
        lon=REFERENCE_BIRTH["lon"],
        birth_timezone=REFERENCE_BIRTH["timezone"],
    )
    if forecast is None:
        raise SystemExit("FAIL: build_astro_forecast returned None")
    if not forecast.summary_lines:
        raise SystemExit("FAIL: empty summary lines")
    if not any("ASC" in line or "Асцендент" in line or "транзит" in line.lower() for line in forecast.summary_lines):
        # footnote about personal chart should exist
        if not any(line.startswith("ℹ") for line in forecast.summary_lines):
            raise SystemExit("FAIL: missing personalization footnotes")
    print(
        f"Forecast OK: energy={forecast.energy.score}/10, "
        f"hits footnotes={sum(1 for line in forecast.summary_lines if line.startswith('ℹ'))}"
    )


def main() -> None:
    print("Horoscope engine validation (Swiss Ephemeris / Astro.com method)")
    print(f"Reference birth: {REFERENCE_BIRTH['birth_date']} {REFERENCE_BIRTH['birth_time']} Moscow")
    print(f"Reference transit: {REFERENCE_TRANSIT.isoformat()}")
    print(f"Aspect orbs: {ASPECTS}")
    print()
    validate_natal_longitudes()
    validate_transit_hits_consistency()
    validate_forecast_builds()
    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
