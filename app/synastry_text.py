from __future__ import annotations


from app.forecast_text import _aspect_label

SynastryHit = tuple[float, str, str, str]

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
    },
}

MODE_INTRO = {
    "ru": {
        "love": "Фокус на близости, эмоциях и притяжении.",
        "friendship": "Фокус на общении, доверии и совместных интересах.",
        "work": "Фокус на совместной работе, ритме и ролях.",
    },
    "en": {
        "love": "Focus on closeness, emotions, and attraction.",
        "friendship": "Focus on communication, trust, and shared interests.",
        "work": "Focus on collaboration, pace, and roles.",
    },
}

MODE_LABELS = {
    "ru": {"love": "любовь", "friendship": "дружба", "work": "работа"},
    "en": {"love": "love", "friendship": "friendship", "work": "work"},
}

ASPECT_TONE = {
    "ru": {
        "love": {
            "trine": "сильная поддержка и притяжение",
            "sextile": "лёгкий контакт и взаимный интерес",
            "conjunction": "мощное усиление темы отношений",
            "square": "страсть и напряжение — нужен диалог",
            "opposition": "магнетизм через контраст",
        },
        "friendship": {
            "trine": "лёгкое взаимопонимание",
            "sextile": "комфортное общение",
            "conjunction": "сильная связь интересов",
            "square": "разные темпы — договаривайтесь",
            "opposition": "дополняете друг друга",
        },
        "work": {
            "trine": "продуктивное взаимодействие",
            "sextile": "удачный обмен идеями",
            "conjunction": "усиление общей цели",
            "square": "разные подходы — нужны роли",
            "opposition": "конструктивное напряжение",
        },
    },
    "en": {
        "love": {
            "trine": "strong support and attraction",
            "sextile": "easy contact and mutual interest",
            "conjunction": "powerful intensification of the bond",
            "square": "passion and tension — talk it through",
            "opposition": "magnetism through contrast",
        },
        "friendship": {
            "trine": "easy understanding",
            "sextile": "comfortable communication",
            "conjunction": "strong link of interests",
            "square": "different rhythms — negotiate",
            "opposition": "you complement each other",
        },
        "work": {
            "trine": "productive interaction",
            "sextile": "smooth idea exchange",
            "conjunction": "shared goal intensifies",
            "square": "different approaches — define roles",
            "opposition": "constructive tension",
        },
    },
}


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


def _aspect_tone(locale: str, aspect: str, mode: str) -> str:
    lang = _lang(locale)
    mode_key = mode if mode in ASPECT_TONE[lang] else "love"
    return ASPECT_TONE[lang][mode_key][aspect]


def _is_positive(aspect: str) -> bool:
    return aspect in {"trine", "sextile", "conjunction"}


def _is_challenging(aspect: str) -> bool:
    return aspect in {"square", "opposition"}


def format_synastry_aspect_line(
    locale: str,
    user_planet: str,
    partner_planet: str,
    aspect: str,
    mode: str,
    orb: float,
    *,
    bullet: str = "",
) -> str:
    user_name = _planet_label(locale, user_planet)
    partner_name = _planet_label(locale, partner_planet)
    aspect_label = _aspect_label(locale, aspect)
    orb_part = f" ({orb:.1f}°)" if orb <= 2.5 else ""
    tone = _aspect_tone(locale, aspect, mode)
    lang = _lang(locale)
    if lang == "ru":
        core = f"ваше {user_name}, {aspect_label} к {partner_name} партнёра{orb_part} — {tone}"
    else:
        core = f"your {user_name} {aspect_label} partner's {partner_name}{orb_part} — {tone}"
    if not bullet:
        return core
    return f"{bullet} {core}"


def format_synastry_advice(locale: str, mode: str, score: int) -> str:
    lang = _lang(locale)
    if lang == "ru":
        if mode == "love":
            if score >= 75:
                return "Опирайтесь на сильные связи и не принимайте напряжение на личный счёт."
            if score >= 55:
                return "Говорите прямо о чувствах — карты показывают и притяжение, и точки трения."
            return "Не форсируйте близость: сначала ясность, потом решения."
        if mode == "friendship":
            if score >= 75:
                return "Поддерживайте регулярный контакт — связь легко складывается."
            return "Уважайте разный темп и формат общения."
        if score >= 75:
            return "Закрепите роли и дедлайны — взаимодействие продуктивное."
        return "Сначала договоритесь о задачах, потом ускоряйтесь."

    if mode == "love":
        if score >= 75:
            return "Lean on your strong links and don't take tension personally."
        if score >= 55:
            return "Talk openly about feelings — the chart shows both pull and friction."
        return "Don't force closeness: clarity first, decisions second."
    if mode == "friendship":
        if score >= 75:
            return "Keep regular contact — the connection flows easily."
        return "Respect different rhythms and communication styles."
    if score >= 75:
        return "Define roles and deadlines — interaction is productive."
    return "Agree on tasks first, then pick up the pace."


def format_synastry_report(
    locale: str,
    *,
    mode: str,
    score: int,
    hits: list[SynastryHit],
    user_sign: str,
    partner_sign: str,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> str:
    lang = _lang(locale)
    mode_key = mode if mode in MODE_LABELS[lang] else "love"
    lines: list[str] = []

    if lang == "ru":
        lines.append(f"Расчёт: Swiss Ephemeris · режим «{MODE_LABELS[lang][mode_key]}»")
        lines.append(f"• {user_sign} + {partner_sign}")
    else:
        lines.append(f"Calculation: Swiss Ephemeris · {MODE_LABELS[lang][mode_key]} mode")
        lines.append(f"• {user_sign} + {partner_sign}")

    lines.append(MODE_INTRO[lang][mode_key])

    if not user_has_moon:
        lines.append(
            "• Ваше время рождения не указано — ваша Луна не учитывается."
            if lang == "ru"
            else "• Your birth time is missing — your Moon is not included."
        )
    if not partner_has_moon:
        lines.append(
            "• У партнёра нет времени рождения — Луна партнёра не учитывается."
            if lang == "ru"
            else "• Partner birth time is missing — partner Moon is not included."
        )

    if not hits:
        lines.append(
            "• Ярких межкартовых аспектов не найдено — связь более нейтральная."
            if lang == "ru"
            else "• No major cross-chart aspects — the connection is more neutral."
        )
    else:
        lines.append("")
        for orb, user_planet, partner_planet, aspect in hits[:4]:
            lines.append(
                format_synastry_aspect_line(
                    locale,
                    user_planet,
                    partner_planet,
                    aspect,
                    mode_key,
                    orb,
                )
            )

        positive = [hit for hit in hits if _is_positive(hit[3])][:2]
        challenging = [hit for hit in hits if _is_challenging(hit[3])][:2]

        if positive:
            tones = [_aspect_tone(locale, hit[3], mode_key) for hit in positive]
            label = "Сильные стороны" if lang == "ru" else "Strengths"
            lines.append("")
            lines.append(f"✅ {label}: {'; '.join(tones).capitalize()}.")

        if challenging:
            tones = [_aspect_tone(locale, hit[3], mode_key) for hit in challenging]
            label = "Точки роста" if lang == "ru" else "Growth points"
            lines.append(f"⚠️ {label}: {'; '.join(tones).capitalize()}.")

    lines.append("")
    lines.append("💡 " + ("Совет" if lang == "ru" else "Advice"))
    lines.append(format_synastry_advice(locale, mode_key, score))

    return "\n".join(lines)
