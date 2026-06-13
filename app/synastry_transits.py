"""Step 9 synastry: transits through the combined synastry chart and year forecast."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from app.forecast_text import _aspect_label

SYNASTRY_TARGETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
KEY_TARGETS = frozenset({"SUN", "MOON", "VENUS", "MARS", "MERCURY"})

HARMONY_TRANSITERS = ("JUPITER", "VENUS")
TENSION_TRANSITERS = ("SATURN", "URANUS", "PLUTO")

HARMONIOUS_ASPECTS = frozenset({"conjunction", "trine", "sextile"})
TENSE_ASPECTS = frozenset({"square", "opposition"})

TRANSIT_BODIES = {
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
    "URANUS": swe.URANUS,
    "PLUTO": swe.PLUTO,
}

ASPECTS = (
    ("conjunction", 0, 8),
    ("sextile", 60, 6),
    ("square", 90, 7),
    ("trine", 120, 8),
    ("opposition", 180, 8),
)

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
        "URANUS": "Уран",
        "PLUTO": "Плутон",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
        "URANUS": "Uranus",
        "PLUTO": "Pluto",
    },
}

OWNER_LABELS = {
    "ru": {"user": "ваше", "partner": "партнёра"},
    "en": {"user": "your", "partner": "partner's"},
}

FORECAST_DAYS = 365
PEAK_WINDOW_DAYS = 14
MAX_CURRENT_HITS = 3
MAX_PEAK_WINDOWS = 2


@dataclass(frozen=True)
class SynastryTarget:
    owner: str
    planet: str
    longitude: float

    @property
    def weight(self) -> float:
        return 2.0 if self.planet in KEY_TARGETS else 1.5


@dataclass(frozen=True)
class TransitHit:
    transit_planet: str
    target: SynastryTarget
    aspect: str
    orb: float
    tone: str
    on_date: date

    @property
    def score(self) -> float:
        base = self.target.weight * max(0.5, 4.0 - self.orb)
        if self.transit_planet == "JUPITER" and self.tone == "harmony":
            base *= 1.2
        if self.transit_planet == "PLUTO" and self.tone == "tension":
            base *= 1.15
        return base


@dataclass(frozen=True)
class TransitWindow:
    start: date
    end: date
    score: float
    sample_hit: TransitHit | None


@dataclass(frozen=True)
class SynastryTransitAnalysis:
    current_harmony: tuple[TransitHit, ...]
    current_tension: tuple[TransitHit, ...]
    harmony_peaks: tuple[TransitWindow, ...]
    tension_peaks: tuple[TransitWindow, ...]
    forecast_start: date
    forecast_end: date


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _owner_label(locale: str, owner: str) -> str:
    return OWNER_LABELS[_lang(locale)][owner]


def _angle_diff(first: float, second: float) -> float:
    diff = abs(first - second) % 360.0
    return diff if diff <= 180 else 360.0 - diff


def _find_aspect(first: float, second: float) -> tuple[str, float] | None:
    diff = _angle_diff(first, second)
    best: tuple[str, float] | None = None
    for name, exact, orb in ASPECTS:
        delta = abs(diff - exact)
        if delta <= orb and (best is None or delta < best[1]):
            best = (name, delta)
    return best


def _local_noon_jd(for_date: date, timezone_name: str) -> float:
    tz = ZoneInfo(timezone_name)
    moment = datetime.combine(for_date, time(12, 0), tzinfo=tz).astimezone(timezone.utc)
    ut_hours = moment.hour + moment.minute / 60 + moment.second / 3600
    return swe.julday(moment.year, moment.month, moment.day, ut_hours)


def _transit_longitudes(julian_day: float) -> dict[str, float]:
    result: dict[str, float] = {}
    for key, body_id in TRANSIT_BODIES.items():
        coords, _ = swe.calc_ut(julian_day, body_id)
        result[key] = float(coords[0])
    return result


def _build_targets(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    *,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> tuple[SynastryTarget, ...]:
    targets: list[SynastryTarget] = []
    for planet in SYNASTRY_TARGETS:
        if planet == "MOON" and not user_has_moon:
            continue
        if planet in user_planets:
            targets.append(SynastryTarget("user", planet, user_planets[planet]))
    for planet in SYNASTRY_TARGETS:
        if planet == "MOON" and not partner_has_moon:
            continue
        if planet in partner_planets:
            targets.append(SynastryTarget("partner", planet, partner_planets[planet]))
    return tuple(targets)


def _scan_transits(
    on_date: date,
    timezone_name: str,
    targets: tuple[SynastryTarget, ...],
) -> tuple[list[TransitHit], list[TransitHit]]:
    jd = _local_noon_jd(on_date, timezone_name)
    transits = _transit_longitudes(jd)
    harmony: list[TransitHit] = []
    tension: list[TransitHit] = []

    for transit_key in HARMONY_TRANSITERS:
        for target in targets:
            aspect_info = _find_aspect(transits[transit_key], target.longitude)
            if aspect_info is None:
                continue
            aspect, orb = aspect_info
            if aspect not in HARMONIOUS_ASPECTS:
                continue
            harmony.append(
                TransitHit(
                    transit_planet=transit_key,
                    target=target,
                    aspect=aspect,
                    orb=orb,
                    tone="harmony",
                    on_date=on_date,
                )
            )

    for transit_key in TENSION_TRANSITERS:
        for target in targets:
            aspect_info = _find_aspect(transits[transit_key], target.longitude)
            if aspect_info is None:
                continue
            aspect, orb = aspect_info
            if aspect not in TENSE_ASPECTS:
                continue
            tension.append(
                TransitHit(
                    transit_planet=transit_key,
                    target=target,
                    aspect=aspect,
                    orb=orb,
                    tone="tension",
                    on_date=on_date,
                )
            )

    harmony.sort(key=lambda item: (-item.score, item.orb))
    tension.sort(key=lambda item: (-item.score, item.orb))
    return harmony, tension


def _daily_scores(
    start: date,
    days: int,
    timezone_name: str,
    targets: tuple[SynastryTarget, ...],
) -> tuple[list[tuple[date, float]], list[tuple[date, float]]]:
    harmony_daily: list[tuple[date, float]] = []
    tension_daily: list[tuple[date, float]] = []
    for offset in range(days + 1):
        day = start + timedelta(days=offset)
        harmony, tension = _scan_transits(day, timezone_name, targets)
        harmony_daily.append((day, sum(item.score for item in harmony)))
        tension_daily.append((day, sum(item.score for item in tension)))
    return harmony_daily, tension_daily


def _rolling_peak_windows(
    daily: list[tuple[date, float]],
    *,
    window_days: int,
    max_windows: int,
) -> tuple[TransitWindow, ...]:
    if len(daily) < window_days:
        return ()

    rolling: list[tuple[date, date, float]] = []
    for index in range(len(daily) - window_days + 1):
        chunk = daily[index : index + window_days]
        total = sum(score for _, score in chunk)
        if total <= 0:
            continue
        rolling.append((chunk[0][0], chunk[-1][0], total))

    rolling.sort(key=lambda item: item[2], reverse=True)
    chosen: list[TransitWindow] = []
    used_ranges: list[tuple[date, date]] = []

    for start, end, score in rolling:
        if len(chosen) >= max_windows:
            break
        if any(not (end < used_start or start > used_end) for used_start, used_end in used_ranges):
            continue
        chosen.append(TransitWindow(start=start, end=end, score=score, sample_hit=None))
        used_ranges.append((start, end))

    return tuple(chosen)


def analyze_synastry_transits(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    *,
    timezone_name: str,
    user_has_moon: bool,
    partner_has_moon: bool,
    reference_date: date | None = None,
) -> SynastryTransitAnalysis:
    today = reference_date or date.today()
    targets = _build_targets(
        user_planets,
        partner_planets,
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
    )
    current_harmony, current_tension = _scan_transits(today, timezone_name, targets)
    harmony_daily, tension_daily = _daily_scores(
        today,
        FORECAST_DAYS,
        timezone_name,
        targets,
    )
    harmony_peaks = _rolling_peak_windows(
        harmony_daily,
        window_days=PEAK_WINDOW_DAYS,
        max_windows=MAX_PEAK_WINDOWS,
    )
    tension_peaks = _rolling_peak_windows(
        tension_daily,
        window_days=PEAK_WINDOW_DAYS,
        max_windows=MAX_PEAK_WINDOWS,
    )

    return SynastryTransitAnalysis(
        current_harmony=tuple(current_harmony[:MAX_CURRENT_HITS]),
        current_tension=tuple(current_tension[:MAX_CURRENT_HITS]),
        harmony_peaks=harmony_peaks,
        tension_peaks=tension_peaks,
        forecast_start=today,
        forecast_end=today + timedelta(days=FORECAST_DAYS),
    )


def transits_score_delta(analysis: SynastryTransitAnalysis) -> int:
    harmony = len(analysis.current_harmony)
    tension = len(analysis.current_tension)
    delta = 0
    if harmony > tension:
        delta += min(3, harmony - tension + 1)
    elif tension > harmony:
        delta -= min(3, tension - harmony + 1)
    if analysis.harmony_peaks:
        delta += 1
    if analysis.tension_peaks and len(analysis.tension_peaks) > len(analysis.harmony_peaks):
        delta -= 1
    return delta


def _month_short(locale: str, month: int) -> str:
    if _lang(locale) == "ru":
        names = (
            "янв",
            "фев",
            "мар",
            "апр",
            "май",
            "июн",
            "июл",
            "авг",
            "сен",
            "окт",
            "ноя",
            "дек",
        )
        return names[month - 1]
    names = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )
    return names[month - 1]


def _format_date(locale: str, value: date) -> str:
    return f"{value.day} {_month_short(locale, value.month)} {value.year}"


def _format_date_range(locale: str, start: date, end: date) -> str:
    if start == end:
        return _format_date(locale, start)
    if start.year == end.year and start.month == end.month:
        month = _month_short(locale, start.month)
        return f"{start.day}–{end.day} {month} {start.year}"
    if start.year == end.year:
        return (
            f"{start.day} {_month_short(locale, start.month)} — "
            f"{end.day} {_month_short(locale, end.month)} {end.year}"
        )
    return f"{_format_date(locale, start)} — {_format_date(locale, end)}"


def _format_hit_line(locale: str, hit: TransitHit, *, style: str = "terms") -> str:
    from app.synastry_style import format_transit_hit_line

    return format_transit_hit_line(
        locale,
        transit_planet=hit.transit_planet,
        target_owner=hit.target.owner,
        target_planet=hit.target.planet,
        aspect=hit.aspect,
        style=style,
        transit_name=_planet_label(locale, hit.transit_planet),
        target_name=_planet_label(locale, hit.target.planet),
        owner_label=_owner_label(locale, hit.target.owner),
        aspect_label=_aspect_label(locale, hit.aspect),
    )


def format_synastry_step9_section(
    locale: str,
    analysis: SynastryTransitAnalysis,
    *,
    style: str = "terms",
) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append(
            "🔭 Шаг 9. Транзиты и прогноз развития"
            if use_synastry_terms(style)
            else "🔭 Шаг 9. Сейчас и ближайший год"
        )
        if use_synastry_terms(style):
            lines.append(
                "Транзиты через точки синастрической карты (обе натальные карты): "
                + _planet_label("ru", "JUPITER")
                + "/Венера — поддержка, Сатурн/Уран/Плутон — испытания."
            )
        else:
            lines.append(
                "Как текущий период и ближайшие месяцы поддерживают или проверяют вашу пару."
            )
    else:
        lines.append(
            "🔭 Step 9. Transits and growth forecast"
            if use_synastry_terms(style)
            else "🔭 Step 9. Now and the year ahead"
        )
        if use_synastry_terms(style):
            lines.append(
                "Transits to synastry chart points (both natal charts): "
                "Jupiter/Venus — support, Saturn/Uranus/Pluto — tests."
            )
        else:
            lines.append(
                "How the current period and coming months support or test your bond."
            )

    lines.append("")
    if lang == "ru":
        lines.append("📍 Сейчас")
        lines.append(
            f"Благоприятно: {_planet_label('ru', 'JUPITER')} и Венера к ключевым точкам синастрии."
            if use_synastry_terms(style)
            else "Благоприятно: периоды тепла и расширения для вашей пары."
        )
    else:
        lines.append("📍 Now")
        lines.append(
            "Favorable: Jupiter and Venus to key synastry points."
            if use_synastry_terms(style)
            else "Favorable: warm and expansive phases for your bond."
        )

    if analysis.current_harmony:
        for hit in analysis.current_harmony:
            lines.append(f"• ✓ {_format_hit_line(locale, hit, style=style).capitalize()}.")
    else:
        lines.append(
            "• Ярких гармоничных транзитов сейчас нет — опирайтесь на натальную совместимость."
            if lang == "ru"
            else "• No strong harmonious transits now — lean on natal compatibility."
        )

    lines.append("")
    if lang == "ru":
        lines.append("⚡ Испытания")
        lines.append(
            "Сатурн, Уран и Плутон по напряжённым аспектам (квадрат, оппозиция)."
            if use_synastry_terms(style)
            else "Периоды проверки, перемен и глубокой трансформации."
        )
    else:
        lines.append("⚡ Tests")
        lines.append(
            "Saturn, Uranus, and Pluto in tense aspects (square, opposition)."
            if use_synastry_terms(style)
            else "Periods of testing, change, and deep transformation."
        )

    if analysis.current_tension:
        for hit in analysis.current_tension:
            lines.append(f"• ⚠ {_format_hit_line(locale, hit, style=style).capitalize()}.")
    else:
        lines.append(
            "• Сильных напряжённых транзитов сейчас не видно — период спокойнее для пары."
            if lang == "ru"
            else "• No strong tense transits now — a calmer stretch for the pair."
        )

    lines.append("")
    period = _format_date_range(
        locale,
        analysis.forecast_start,
        analysis.forecast_end,
    )
    if lang == "ru":
        lines.append(f"📅 Карта на год вперёд ({period})")
        lines.append(
            f"Сканирование {FORECAST_DAYS} дней, окна по {PEAK_WINDOW_DAYS} дней — "
            "пики гармонии и напряжения."
        )
    else:
        lines.append(f"📅 One-year map ({period})")
        lines.append(
            f"{FORECAST_DAYS}-day scan, {PEAK_WINDOW_DAYS}-day windows — "
            "harmony and tension peaks."
        )

    lines.append("")
    if lang == "ru":
        lines.append("🌿 Пики гармонии")
    else:
        lines.append("🌿 Harmony peaks")

    if analysis.harmony_peaks:
        for window in analysis.harmony_peaks:
            label = _format_date_range(locale, window.start, window.end)
            lines.append(f"• {label}")
    else:
        lines.append(
            "• Выраженных «зелёных» окон за год не выделено — развитие через стабильный фон."
            if lang == "ru"
            else "• No strong harmony windows this year — steady background growth."
        )

    lines.append("")
    if lang == "ru":
        lines.append("🌑 Пики напряжения")
    else:
        lines.append("🌑 Tension peaks")

    if analysis.tension_peaks:
        for window in analysis.tension_peaks:
            label = _format_date_range(locale, window.start, window.end)
            lines.append(f"• {label}")
    else:
        lines.append(
            "• Резких «красных» периодов за год не видно — испытания скорее точечные."
            if lang == "ru"
            else "• No sharp tension peaks this year — tests are likely spotty."
        )

    return "\n".join(lines)
