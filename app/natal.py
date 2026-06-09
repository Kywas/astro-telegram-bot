from __future__ import annotations

from datetime import date, time

from app.astro_engine import (
    ASPECT_LABELS,
    SIGN_ELEMENTS,
    build_natal_chart_data,
    longitude_to_sign,
    planet_label,
    sign_label,
)


PLANET_ICONS = {
    "SUN": "☉",
    "MOON": "☽",
    "MERCURY": "☿",
    "VENUS": "♀",
    "MARS": "♂",
    "JUPITER": "♃",
    "SATURN": "♄",
    "ASC": "↑",
}

PLANET_ORDER = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")

ELEMENT_LABELS = {
    "ru": {"fire": "огонь", "earth": "земля", "air": "воздух", "water": "вода"},
    "en": {"fire": "fire", "earth": "earth", "air": "air", "water": "water"},
}

PLANET_ROLES = {
    "ru": {
        "SUN": "ядро личности и жизненная цель",
        "MOON": "эмоции, потребности и привычные реакции",
        "MERCURY": "мышление, речь и способ учиться",
        "VENUS": "ценности, притяжение и эстетика",
        "MARS": "воля, напор и способ действовать",
        "JUPITER": "рост, вера и масштаб возможностей",
        "SATURN": "структура, дисциплина и зрелость",
        "ASC": "первое впечатление и стиль самопроявления",
    },
    "en": {
        "SUN": "core identity and life direction",
        "MOON": "emotions, needs, and habitual reactions",
        "MERCURY": "thinking, speech, and learning style",
        "VENUS": "values, attraction, and aesthetics",
        "MARS": "will, drive, and how you act",
        "JUPITER": "growth, faith, and sense of possibility",
        "SATURN": "structure, discipline, and maturity",
        "ASC": "first impression and outward style",
    },
}

ASPECT_TONE = {
    "ru": {
        "conjunction": "усиливает связанные темы и делает их центральными",
        "sextile": "даёт поддерживающий потенциал и лёгкие возможности",
        "trine": "работает естественно и гармонично",
        "square": "создаёт внутреннее напряжение, которое требует осознанности",
        "opposition": "тянет между полюсами и учит балансу",
    },
    "en": {
        "conjunction": "intensifies linked themes and makes them central",
        "sextile": "offers supportive potential and easy openings",
        "trine": "flows naturally and harmoniously",
        "square": "creates inner tension that asks for awareness",
        "opposition": "pulls between poles and teaches balance",
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _body_label(locale: str, key: str) -> str:
    if key == "ASC":
        return "Асцендент" if locale == "ru" else "Ascendant"
    return planet_label(locale, key)


def _degree_in_sign(longitude: float) -> tuple[str, float]:
    sign = longitude_to_sign(longitude)
    return sign, longitude % 30


def _placement_line(locale: str, key: str, longitude: float, *, detailed: bool) -> str:
    sign, degree = _degree_in_sign(longitude)
    icon = PLANET_ICONS.get(key, "•")
    lang = _lang(locale)
    sign_name = sign_label(locale, sign)
    element = ELEMENT_LABELS[lang][SIGN_ELEMENTS.get(sign, "air")]
    role = PLANET_ROLES[lang].get(key, key)
    base = f"{icon} {_body_label(locale, key)} — {sign_name} ({degree:.0f}°)"
    if not detailed:
        return base
    return f"{base}\n   {role.capitalize()}; акцент на стихии {element}." if lang == "ru" else (
        f"{base}\n   {role.capitalize()}; {element} emphasis."
    )


def _aspect_line(locale: str, hit) -> str:
    lang = _lang(locale)
    first = _body_label(locale, hit.planet_a)
    second = _body_label(locale, hit.planet_b)
    aspect = ASPECT_LABELS[lang].get(hit.aspect, hit.aspect)
    tone = ASPECT_TONE[lang].get(hit.aspect, "")
    if lang == "ru":
        return f"• {first} — {aspect} — {second}: {tone}."
    return f"• {first} — {aspect} — {second}: {tone}."


def _element_balance(locale: str, longitudes: dict[str, float], ascendant: float | None) -> str:
    lang = _lang(locale)
    counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    for longitude in longitudes.values():
        element = SIGN_ELEMENTS.get(longitude_to_sign(longitude), "air")
        counts[element] += 1
    if ascendant is not None:
        element = SIGN_ELEMENTS.get(longitude_to_sign(ascendant), "air")
        counts[element] += 1
    total = sum(counts.values()) or 1
    dominant = max(counts, key=lambda key: counts[key])
    dominant_label = ELEMENT_LABELS[lang][dominant]
    parts = [f"{ELEMENT_LABELS[lang][key]} {counts[key]}" for key in ("fire", "earth", "air", "water")]
    if lang == "ru":
        return f"Стихии: {', '.join(parts)}. Доминирует {dominant_label} ({counts[dominant]}/{total})."
    return f"Elements: {', '.join(parts)}. Dominant: {dominant_label} ({counts[dominant]}/{total})."


def _accuracy_notes(locale: str, chart: NatalChartData) -> list[str]:
    lang = _lang(locale)
    notes: list[str] = []
    if not chart.has_birth_time:
        notes.append(
            "Без времени рождения: Луна, асцендент и дома не рассчитываются; остальные планеты — на полдень местного времени."
            if lang == "ru"
            else "Without birth time: Moon, ascendant, and houses are omitted; other planets use local noon."
        )
    elif not chart.coordinates_available:
        notes.append(
            "Координаты города не найдены — асцендент недоступен. Уточни город в профиле."
            if lang == "ru"
            else "City coordinates missing — ascendant unavailable. Update your city in profile."
        )
    elif chart.has_birth_time and chart.moon_included and not chart.asc_included:
        notes.append(
            "Луна рассчитана по точному времени; для асцендента нужны координаты города."
            if lang == "ru"
            else "Moon uses exact birth time; ascendant still needs city coordinates."
        )
    return notes


def _calendar_sign_note(locale: str, calendar_sign: str | None, chart: NatalChartData) -> str | None:
    if not calendar_sign or calendar_sign == chart.sun_sign:
        return None
    lang = _lang(locale)
    calendar_name = sign_label(locale, calendar_sign)
    sun_name = sign_label(locale, chart.sun_sign)
    if lang == "ru":
        return (
            f"Календарный знак профиля: {calendar_name}. "
            f"По эфемеридам Солнце в {sun_name} — это точнее для карты."
        )
    return (
        f"Profile calendar sign: {calendar_name}. "
        f"Ephemeris Sun is in {sun_name} — that is used for the chart."
    )


def _format_chart(
    locale: str,
    chart: NatalChartData,
    *,
    birth_date: date,
    birth_time: time | None,
    city: str,
    calendar_sign: str | None,
    mode: str,
) -> str:
    lang = _lang(locale)
    compact = mode == "short"
    header = "Натальная карта" if lang == "ru" else "Natal chart"
    time_text = (
        birth_time.isoformat(timespec="minutes")
        if birth_time
        else ("неизвестно" if lang == "ru" else "unknown")
    )
    if lang == "ru":
        basics = (
            f"Дата рождения: {birth_date.strftime('%d.%m.%Y')}\n"
            f"Время: {time_text}\n"
            f"Город: {city}"
        )
        placements_title = "Ключевые положения" if compact else "Планеты в знаках"
        aspects_title = "Главные аспекты" if compact else "Натальные аспекты"
    else:
        basics = (
            f"Birth date: {birth_date.isoformat()}\n"
            f"Time: {time_text}\n"
            f"City: {city}"
        )
        placements_title = "Key placements" if compact else "Planetary placements"
        aspects_title = "Main aspects" if compact else "Natal aspects"

    placement_keys: list[str] = []
    for key in PLANET_ORDER:
        if key in chart.longitudes:
            placement_keys.append(key)
    if chart.asc_included and chart.ascendant is not None:
        if "MOON" in placement_keys:
            placement_keys.insert(placement_keys.index("MOON") + 1, "ASC")
        else:
            placement_keys.insert(placement_keys.index("SUN") + 1, "ASC")

    placement_lines = []
    for key in placement_keys:
        if key == "ASC" and chart.ascendant is not None:
            placement_lines.append(
                _placement_line(locale, "ASC", chart.ascendant, detailed=not compact)
            )
        elif key in chart.longitudes:
            placement_lines.append(
                _placement_line(locale, key, chart.longitudes[key], detailed=not compact)
            )

    aspect_limit = 3 if compact else 8
    aspect_lines = [_aspect_line(locale, hit) for hit in chart.aspects[:aspect_limit]]
    if not aspect_lines:
        aspect_lines = [
            "• Ярко выраженных аспектов в выбранном орбисе нет — карта более ровная."
            if lang == "ru"
            else "• No major aspects within orb — a steadier chart overall."
        ]

    blocks = [header, "", basics, "", placements_title, *placement_lines]
    blocks.extend(["", aspects_title, *aspect_lines])
    blocks.extend(["", _element_balance(locale, chart.longitudes, chart.ascendant)])

    notes = _accuracy_notes(locale, chart)
    calendar_note = _calendar_sign_note(locale, calendar_sign, chart)
    if calendar_note:
        notes.insert(0, calendar_note)
    if notes:
        note_title = "Важно" if lang == "ru" else "Notes"
        blocks.extend(["", note_title, *[f"• {note}" for note in notes]])

    text = "\n".join(blocks)
    if len(text) > 3900:
        text = text[:3890].rstrip() + "…"
    return text


def build_natal_summary(
    *,
    locale: str,
    sign_name: str,
    sign_key: str | None,
    birth_date: date,
    birth_time: time | None,
    city: str,
    relationship_status: str | None = None,
    goal: str | None = None,
    mood_score: int | None = None,
    mode: str = "full",
    timezone: str = "UTC",
    lat: float | None = None,
    lon: float | None = None,
    birth_timezone: str | None = None,
) -> str:
    del sign_name, relationship_status, goal, mood_score  # kept for caller compatibility
    chart = build_natal_chart_data(
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        timezone_name=timezone,
        lat=lat,
        lon=lon,
        birth_timezone=birth_timezone,
    )
    lang = _lang(locale)
    if chart is None:
        return (
            "Не удалось рассчитать натальную карту. Проверь дату, город и профиль через /start."
            if lang == "ru"
            else "Could not compute natal chart. Check date, city, and profile via /start."
        )
    return _format_chart(
        locale,
        chart,
        birth_date=birth_date,
        birth_time=birth_time,
        city=city,
        calendar_sign=sign_key,
        mode=mode,
    )
