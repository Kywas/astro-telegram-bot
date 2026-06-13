"""Synastry: secondary progressions (temporary directions) for relationship timing."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import swisseph as swe

from app.forecast_text import _aspect_label
from app.sun_sign_compat import SIGN_LABELS, ZODIAC_SIGNS

PROGRESSION_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
PROGRESSION_BODIES = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
}

KEY_PAIRS = (
    ("SUN", "MOON"),
    ("SUN", "VENUS"),
    ("MOON", "VENUS"),
    ("VENUS", "MARS"),
    ("MOON", "MARS"),
)

ASPECTS = (
    ("conjunction", 0, 2.0),
    ("sextile", 60, 1.5),
    ("square", 90, 1.5),
    ("trine", 120, 2.0),
    ("opposition", 180, 2.0),
)

HARMONIOUS = frozenset({"conjunction", "trine", "sextile"})
TENSE = frozenset({"square", "opposition"})

MOON_SIGN_YEARS = 2.5

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "JUPITER": "Jupiter",
        "SATURN": "Saturn",
    },
}


@dataclass(frozen=True)
class ProgressedCrossLink:
    user_planet: str
    partner_planet: str
    aspect: str
    orb: float

    @property
    def tone(self) -> str:
        if self.aspect in HARMONIOUS:
            return "harmony"
        if self.aspect in TENSE:
            return "tension"
        return "neutral"


@dataclass(frozen=True)
class ProgressedMoonPhase:
    owner: str
    sign: str
    years_in_sign: float
    near_sign_change: bool
    natal_return: bool


@dataclass(frozen=True)
class ProgressionsAnalysis:
    reference_date: date
    user_age_years: float
    partner_age_years: float
    cross_links: tuple[ProgressedCrossLink, ...]
    moon_phases: tuple[ProgressedMoonPhase, ...]
    user_has_moon: bool
    partner_has_moon: bool

    @property
    def best_harmony(self) -> ProgressedCrossLink | None:
        for link in self.cross_links:
            if link.tone == "harmony":
                return link
        return None

    @property
    def best_tension(self) -> ProgressedCrossLink | None:
        for link in self.cross_links:
            if link.tone == "tension":
                return link
        return None

    @property
    def emotional_reset_active(self) -> bool:
        return any(phase.near_sign_change or phase.natal_return for phase in self.moon_phases)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _sign_name(locale: str, sign: str) -> str:
    return SIGN_LABELS[_lang(locale)][sign]


def _longitude_to_sign(longitude: float) -> str:
    normalized = longitude % 360.0
    index = int(normalized // 30) % 12
    return ZODIAC_SIGNS[index]


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


def _planet_longitude(julian_day: float, planet: str) -> float:
    coords, _ = swe.calc_ut(julian_day, PROGRESSION_BODIES[planet])
    return float(coords[0])


def _age_years(birth_date: date, reference_date: date) -> float:
    return (reference_date - birth_date).days / 365.25


def _progressed_jd(birth_julian_day: float, age_years: float) -> float:
    return birth_julian_day + age_years


def _progressed_chart(
    birth_julian_day: float,
    age_years: float,
    *,
    include_moon: bool,
) -> dict[str, float]:
    jd = _progressed_jd(birth_julian_day, age_years)
    keys = [key for key in PROGRESSION_PLANETS if key != "MOON" or include_moon]
    return {key: _planet_longitude(jd, key) for key in keys}


def _years_in_progressed_moon_sign(birth_julian_day: float, age_years: float) -> tuple[str, float]:
    jd_now = _progressed_jd(birth_julian_day, age_years)
    sign_now = _longitude_to_sign(_planet_longitude(jd_now, "MOON"))
    step = 0.05
    check_age = age_years
    while check_age > 0:
        check_age -= step
        jd = _progressed_jd(birth_julian_day, check_age)
        if _longitude_to_sign(_planet_longitude(jd, "MOON")) != sign_now:
            return sign_now, max(0.0, age_years - check_age - step)
    return sign_now, age_years


def _progressed_moon_phase(
    owner: str,
    birth_julian_day: float,
    age_years: float,
    natal_moon: float,
) -> ProgressedMoonPhase:
    sign, years_in = _years_in_progressed_moon_sign(birth_julian_day, age_years)
    jd_now = _progressed_jd(birth_julian_day, age_years)
    prog_moon = _planet_longitude(jd_now, "MOON")
    natal_return = _angle_diff(prog_moon, natal_moon) <= 1.5
    years_to_change = max(0.0, MOON_SIGN_YEARS - years_in)
    near_change = years_in < 0.45 or years_to_change < 0.45
    return ProgressedMoonPhase(
        owner=owner,
        sign=sign,
        years_in_sign=years_in,
        near_sign_change=near_change,
        natal_return=natal_return,
    )


def _cross_progressed_links(
    user_prog: dict[str, float],
    partner_prog: dict[str, float],
) -> list[ProgressedCrossLink]:
    links: list[ProgressedCrossLink] = []
    for user_planet, user_lon in user_prog.items():
        for partner_planet, partner_lon in partner_prog.items():
            aspect_info = _find_aspect(user_lon, partner_lon)
            if aspect_info is None:
                continue
            aspect, orb = aspect_info
            links.append(
                ProgressedCrossLink(
                    user_planet=user_planet,
                    partner_planet=partner_planet,
                    aspect=aspect,
                    orb=orb,
                )
            )

    def sort_key(link: ProgressedCrossLink) -> tuple[int, float]:
        pair = (link.user_planet, link.partner_planet)
        reverse_pair = (link.partner_planet, link.user_planet)
        priority = 0 if pair in KEY_PAIRS or reverse_pair in KEY_PAIRS else 1
        return (priority, link.orb)

    links.sort(key=sort_key)
    return links


def analyze_synastry_progressions(
    *,
    user_birth_date: date,
    partner_birth_date: date,
    user_julian_day: float,
    partner_julian_day: float,
    user_has_moon: bool,
    partner_has_moon: bool,
    reference_date: date | None = None,
) -> ProgressionsAnalysis:
    ref = reference_date or date.today()
    user_age = _age_years(user_birth_date, ref)
    partner_age = _age_years(partner_birth_date, ref)

    user_prog = _progressed_chart(user_julian_day, user_age, include_moon=user_has_moon)
    partner_prog = _progressed_chart(partner_julian_day, partner_age, include_moon=partner_has_moon)

    cross = _cross_progressed_links(user_prog, partner_prog)

    moon_phases: list[ProgressedMoonPhase] = []
    if user_has_moon:
        natal_moon = _planet_longitude(user_julian_day, "MOON")
        moon_phases.append(
            _progressed_moon_phase("user", user_julian_day, user_age, natal_moon)
        )
    if partner_has_moon:
        natal_moon = _planet_longitude(partner_julian_day, "MOON")
        moon_phases.append(
            _progressed_moon_phase("partner", partner_julian_day, partner_age, natal_moon)
        )

    return ProgressionsAnalysis(
        reference_date=ref,
        user_age_years=user_age,
        partner_age_years=partner_age,
        cross_links=tuple(cross[:6]),
        moon_phases=tuple(moon_phases),
        user_has_moon=user_has_moon,
        partner_has_moon=partner_has_moon,
    )


def progressions_score_delta(analysis: ProgressionsAnalysis) -> int:
    delta = 0
    if analysis.best_harmony is not None and analysis.best_harmony.orb <= 1.5:
        delta += 2
    elif analysis.best_harmony is not None:
        delta += 1
    if analysis.best_tension is not None and analysis.best_tension.orb <= 1.5:
        delta -= 1
    if analysis.emotional_reset_active:
        delta += 1
    return delta


def _link_interpretation(locale: str, link: ProgressedCrossLink, *, style: str) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    if link.tone == "harmony":
        if lang == "ru":
            if use_synastry_terms(style):
                return "благоприятный период развития — тема пары получает поддержку."
            return "хорошее время для развития связи — тема пары на вашей стороне."
        if use_synastry_terms(style):
            return "a favorable development phase — the pair theme gets support."
        return "a good time to grow the bond — the theme works in your favor."
    if lang == "ru":
        if use_synastry_terms(style):
            return "напряжённый этап — важные события потребуют диалога и гибкости."
        return "непростой этап — важные повороты лучше проходить через разговор."
    if use_synastry_terms(style):
        return "a tense phase — key events will need dialogue and flexibility."
    return "a challenging phase — turning points are best handled through talk."


def _format_cross_link(locale: str, link: ProgressedCrossLink, *, style: str) -> str:
    lang = _lang(locale)
    aspect = _aspect_label(locale, link.aspect)
    orb_part = f" ({link.orb:.1f}°)" if link.orb <= 1.5 else ""
    user_name = _planet_label(locale, link.user_planet)
    partner_name = _planet_label(locale, link.partner_planet)
    if lang == "ru":
        return (
            f"прогрессивное {user_name} ↔ прогрессивное {partner_name} партнёра, "
            f"{aspect}{orb_part}"
        )
    return f"progressed {user_name} ↔ partner's progressed {partner_name}, {aspect}{orb_part}"


def _moon_phase_lines(locale: str, phase: ProgressedMoonPhase, *, style: str) -> list[str]:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    sign = _sign_name(locale, phase.sign)
    if lang == "ru":
        owner = "ваша" if phase.owner == "user" else "партнёра"
    else:
        owner = "your" if phase.owner == "user" else "partner's"

    lines: list[str] = []
    if lang == "ru":
        if use_synastry_terms(style):
            lines.append(
                f"• Прогрессивная Луна ({owner}): {sign}, "
                f"в знаке ~{phase.years_in_sign:.1f} лет из ~{MOON_SIGN_YEARS}."
            )
        else:
            lines.append(
                f"• Эмоциональный цикл ({owner}): {sign}, "
                f"~{phase.years_in_sign:.1f} лет в текущем настроении."
            )
    elif use_synastry_terms(style):
        lines.append(
            f"• Progressed Moon ({owner}): {sign}, "
            f"~{phase.years_in_sign:.1f} of ~{MOON_SIGN_YEARS} years in sign."
        )
    else:
        lines.append(
            f"• Emotional cycle ({owner}): {sign}, "
            f"~{phase.years_in_sign:.1f} years in current mood."
        )

    if phase.natal_return:
        lines.append(
            "  ↳ Возвращение прогрессивной Луны к натальной — "
            "крупный эмоциональный цикл (~27 лет)."
            if lang == "ru"
            else "  ↳ Progressed Moon return to natal — major emotional cycle (~27 years)."
        )
    elif phase.near_sign_change:
        lines.append(
            "  ↳ Близко смена знака (~каждые 2,5 года) — период эмоциональной перезагрузки."
            if lang == "ru"
            else "  ↳ Near a sign change (~every 2.5 years) — emotional reset period."
        )
    return lines


def format_synastry_progressions_section(
    locale: str,
    analysis: ProgressionsAnalysis,
    *,
    style: str = "terms",
) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []
    ref = analysis.reference_date.strftime("%d.%m.%Y")

    if lang == "ru":
        lines.append(
            "⌛ Временные дирекции (прогрессии)"
            if use_synastry_terms(style)
            else "⌛ Как связь развивается во времени"
        )
        if use_synastry_terms(style):
            lines.append(
                f"Вторичные прогрессии на {ref}: 1 день после рождения = 1 год жизни. "
                "Сопоставляем прогрессивные карты партнёров."
            )
        else:
            lines.append(
                f"Срез на {ref}: как ваши «внутренние часы» пары совпадают сейчас."
            )
    else:
        lines.append(
            "⌛ Temporary directions (progressions)"
            if use_synastry_terms(style)
            else "⌛ How the bond evolves over time"
        )
        if use_synastry_terms(style):
            lines.append(
                f"Secondary progressions for {ref}: 1 day after birth = 1 year of life. "
                "We compare both partners' progressed charts."
            )
        else:
            lines.append(f"Snapshot for {ref}: how your inner pair timing aligns now.")

    lines.append("")
    if lang == "ru":
        lines.append(
            f"Возраст для прогрессий: вы ~{analysis.user_age_years:.1f} лет, "
            f"партнёр ~{analysis.partner_age_years:.1f} лет."
        )
    else:
        lines.append(
            f"Progressed age: you ~{analysis.user_age_years:.1f} years, "
            f"partner ~{analysis.partner_age_years:.1f} years."
        )

    lines.append("")
    lines.append(
        "Аспекты прогрессивных планет"
        if lang == "ru"
        else "Progressed planet aspects"
    )
    if not analysis.cross_links:
        lines.append(
            "• Точных прогрессивных аспектов между картами сейчас нет — "
            "развитие идёт через другие уровни."
            if lang == "ru"
            else "• No tight progressed cross-aspects now — development runs on other levels."
        )
    else:
        for link in analysis.cross_links[:4]:
            lines.append(f"• {_format_cross_link(locale, link, style=style)}.")
            lines.append(f"  {_link_interpretation(locale, link, style=style)}")

    lines.append("")
    lines.append(
        "Прогрессивная Луна"
        if lang == "ru"
        else "Progressed Moon"
    )
    if not analysis.moon_phases:
        lines.append(
            "• Для Луны нужно время рождения у обоих."
            if lang == "ru"
            else "• Birth time for both is required for the Moon."
        )
    else:
        for phase in analysis.moon_phases:
            lines.extend(_moon_phase_lines(locale, phase, style=style))

    return "\n".join(lines)
