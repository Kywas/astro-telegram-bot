"""Step 3 synastry: chart overlay, aspect groups, and key planet pairs."""
from __future__ import annotations

from dataclasses import dataclass

from app.synastry_style import use_synastry_terms

SynastryHit = tuple[float, str, str, str]

HARMONIOUS_ASPECTS = frozenset({"conjunction", "trine", "sextile"})
TENSE_ASPECTS = frozenset({"square", "opposition"})

ASPECT_DEGREES = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}


@dataclass(frozen=True)
class KeyPairSpec:
    key: str
    planet_pairs: frozenset[tuple[str, str]]
    emoji: str
    title_ru: str
    title_en: str


KEY_PAIRS: tuple[KeyPairSpec, ...] = (
    KeyPairSpec(
        key="sun_moon",
        planet_pairs=frozenset({("SUN", "MOON"), ("MOON", "SUN")}),
        emoji="💞",
        title_ru="Солнце ↔ Луна — эмоциональная совместимость",
        title_en="Sun ↔ Moon — emotional compatibility",
    ),
    KeyPairSpec(
        key="venus_mars",
        planet_pairs=frozenset({("VENUS", "MARS"), ("MARS", "VENUS")}),
        emoji="🔥",
        title_ru="Венера ↔ Марс — сексуальная химия",
        title_en="Venus ↔ Mars — sexual chemistry",
    ),
    KeyPairSpec(
        key="mercury",
        planet_pairs=frozenset({("MERCURY", "MERCURY")}),
        emoji="🧠",
        title_ru="Меркурий ↔ Меркурий — интеллектуальное взаимопонимание",
        title_en="Mercury ↔ Mercury — intellectual understanding",
    ),
)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _is_harmonious(aspect: str) -> bool:
    return aspect in HARMONIOUS_ASPECTS


def _is_tense(aspect: str) -> bool:
    return aspect in TENSE_ASPECTS


def _hit_pair(hit: SynastryHit) -> tuple[str, str]:
    return hit[1], hit[2]


def find_best_key_pair_hit(hits: list[SynastryHit], spec: KeyPairSpec) -> SynastryHit | None:
    matching = [hit for hit in hits if _hit_pair(hit) in spec.planet_pairs]
    if not matching:
        return None
    return min(matching, key=lambda item: item[0])


def _used_hit_keys(hits: list[SynastryHit | None]) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    for hit in hits:
        if hit is None:
            continue
        _orb, user_planet, partner_planet, aspect = hit
        keys.add((user_planet, partner_planet, aspect))
    return keys


def _aspect_group_label(locale: str, aspect: str) -> str:
    lang = _lang(locale)
    degrees = ASPECT_DEGREES.get(aspect, 0)
    if lang == "ru":
        if _is_harmonious(aspect):
            return f"гармоничный ({degrees}°)"
        if _is_tense(aspect):
            return f"напряжённый ({degrees}°)"
        return f"{degrees}°"
    if _is_harmonious(aspect):
        return f"harmonious ({degrees}°)"
    if _is_tense(aspect):
        return f"tense ({degrees}°)"
    return f"{degrees}°"


def _capitalize_group(lang: str, group: str) -> str:
    if lang == "ru":
        return group[0].upper() + group[1:] if group else group
    return group.capitalize()


def _key_pair_interpretation(
    locale: str,
    spec: KeyPairSpec,
    hit: SynastryHit | None,
    *,
    mode: str,
    style: str = "terms",
) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    plain = not use_synastry_terms(style)
    if hit is None:
        if plain:
            messages = {
                "ru": {
                    "sun_moon": "Особой «резонансной» связки нет — эмоциональный фон спокойнее, смотрите на быт.",
                    "venus_mars": "Яркой «искры» тут нет — притяжение складывается из других тем, не только из химии.",
                    "mercury": "Без особой связки в разговоре — диалог возможен, но переспрашивайте, не додумывайте.",
                },
                "en": {
                    "sun_moon": "No special «resonance» link — emotional tone is calmer; watch daily life.",
                    "venus_mars": "No loud «spark» here — attraction builds through more than chemistry alone.",
                    "mercury": "No special talk link — dialogue works if you ask, don't assume.",
                },
            }
            return messages[lang][spec.key]
        messages = {
            "sun_moon": {
                "ru": "Точного аспекта Солнце↔Луна нет — эмоциональный фон спокойнее, опирайтесь на общий контекст.",
                "en": "No exact Sun↔Moon aspect — emotional tone is calmer; lean on the wider context.",
            },
            "venus_mars": {
                "ru": "Яркой связи Венера↔Марс нет — притяжение складывается из других тем карты.",
                "en": "No strong Venus↔Mars link — attraction builds through other chart themes.",
            },
            "mercury": {
                "ru": "Меркурий↔Меркурий без точного аспекта — диалог возможен, но стоит уточнять формулировки.",
                "en": "Mercury↔Mercury without an exact aspect — dialogue works if you clarify wording.",
            },
        }
        return messages[spec.key][lang]

    _orb, _user_planet, _partner_planet, aspect = hit
    harmonious = _is_harmonious(aspect)
    tense = _is_tense(aspect)

    if spec.key == "sun_moon":
        if plain:
            if lang == "ru":
                if harmonious:
                    return "Эмоции и характер сходятся — легче понимать, что партнёр чувствует."
                if tense:
                    return "Разный эмоциональный ритм — честность и терпение спасают."
                return "Эмоциональный контакт заметен — не всё нужно объяснять словами."
            if harmonious:
                return "Feelings and character align — easier to read each other."
            if tense:
                return "Different emotional rhythms — honesty and patience help."
            return "Emotional contact is there — not everything needs explaining."
        if lang == "ru":
            if harmonious:
                return "Резонанс Солнца и Луны — легче считывать эмоции и базовые потребности друг друга."
            if tense:
                return "Солнце↔Луна под напряжением — разный эмоциональный ритм, важна честность и терпение."
            return "Солнце и Луна связаны — эмоциональный контакт заметен."
        if harmonious:
            return "Sun and Moon resonate — easier to read each other's feelings and core needs."
        if tense:
            return "Sun↔Moon under tension — different emotional rhythms; honesty and patience help."
        return "Sun and Moon are linked — emotional contact is noticeable."

    if spec.key == "venus_mars":
        if plain:
            if mode == "work":
                if lang == "ru":
                    if harmonious:
                        return "Мотивация в деле совпадает — легче тянуть одну задачу."
                    if tense:
                        return "В работе разный темп — заранее разделите роли."
                    return "Динамика в совместных делах заметна."
                if harmonious:
                    return "Shared drive at work — easier to pull one task."
                if tense:
                    return "Different work pace — split roles early."
                return "Your working dynamic shows up clearly."
            if lang == "ru":
                if harmonious:
                    return "Притяжение и искра есть — телесный интерес не спишите на «просто привычку»."
                if tense:
                    return "Сильная химия и трение — не смешивайте страсть с обидами."
                return "Притяжение между вами заметно."
            if harmonious:
                return "Attraction and spark — don't write physical interest off as «just habit»."
            if tense:
                return "Strong chemistry and friction — don't mix passion with resentment."
            return "Attraction between you is noticeable."
        if mode == "work":
            if lang == "ru":
                if harmonious:
                    return "Венера↔Марс поддерживает совместную мотивацию и рабочий драйв."
                if tense:
                    return "Венера↔Марс даёт трение в темпе — заранее разделите роли."
                return "Связь Венера↔Марс влияет на рабочую динамику."
            if harmonious:
                return "Venus↔Mars supports shared motivation and work drive."
            if tense:
                return "Venus↔Mars adds pace friction — define roles early."
            return "Venus↔Mars shapes your working dynamic."
        if lang == "ru":
            if harmonious:
                return "Венера↔Марс — притяжение, искра и телесный интерес."
            if tense:
                return "Венера↔Марс — сильная химия и трение; не смешивайте страсть с обидами."
            return "Венера↔Марс заметно влияет на притяжение."
        if harmonious:
            return "Venus↔Mars — attraction, spark, and physical interest."
        if tense:
            return "Venus↔Mars — strong chemistry and friction; don't mix passion with resentment."
        return "Venus↔Mars noticeably shapes attraction."

    if plain:
        if lang == "ru":
            if harmonious:
                return "Разговор идёт легче — проще договориться и не перегибать."
            if tense:
                return "Разные стили мышления — переспрашивайте и фиксируйте договорённости."
            return "Стиль общения заметно влияет на пару."
        if harmonious:
            return "Talk flows easier — simpler to agree without overdoing it."
        if tense:
            return "Different thinking styles — re-check and confirm agreements."
        return "How you communicate shapes the bond."
    if lang == "ru":
        if harmonious:
            return "Меркурий↔Меркурий — легче договориться и понять логику друг друга."
        if tense:
            return "Разные стили мышления — переспрашивайте и фиксируйте договорённости письменно."
        return "Связь Меркуриев влияет на стиль общения."
    if harmonious:
        return "Mercury↔Mercury — easier to agree and follow each other's logic."
    if tense:
        return "Different thinking styles — re-check meaning and confirm agreements in writing."
    return "Mercury link shapes how you communicate."


def format_synastry_step3_section(
    locale: str,
    *,
    mode: str,
    hits: list[SynastryHit],
    user_has_moon: bool,
    partner_has_moon: bool,
    format_aspect_line,
    aspect_tone,
    style: str = "terms",
) -> str:
    lang = _lang(locale)
    mode_key = mode if mode in {"love", "friendship", "work"} else "love"
    lines: list[str] = []

    if use_synastry_terms(style):
        if lang == "ru":
            lines.append("🔗 Шаг 3. Синастрия — наложение карт")
            lines.append(
                "Натальные карты наложены друг на друга; ниже — углы между вашими "
                "планетами и планетами партнёра (Swiss Ephemeris)."
            )
            lines.append("")
            lines.append(
                "Гармоничные: соединение 0°, трин 120°, секстиль 60° — притяжение и поддержка."
            )
            lines.append("Напряжённые: квадрат 90°, оппозиция 180° — зоны роста и конфликта.")
        else:
            lines.append("🔗 Step 3. Synastry — chart overlay")
            lines.append(
                "Natal charts are overlaid; below are the angles between your planets "
                "and your partner's (Swiss Ephemeris)."
            )
            lines.append("")
            lines.append(
                "Harmonious: conjunction 0°, trine 120°, sextile 60° — pull and support."
            )
            lines.append("Tense: square 90°, opposition 180° — growth and friction zones.")
    else:
        if lang == "ru":
            lines.append("🔗 Как вы влияете друг на друга")
            lines.append("Где легко — и где лучше поговорить заранее.")
        else:
            lines.append("🔗 How you affect each other")
            lines.append("Where it's easy — and where to talk early.")

    if not use_synastry_terms(style):
        pass
    else:
        mode_intro_terms = {
            "ru": {
                "love": "Режим «любовь» — акцент на близости и притяжении.",
                "friendship": "Режим «дружба» — акцент на общении и доверии.",
                "work": "Режим «работа» — акцент на ролях и совместной задаче.",
            },
            "en": {
                "love": "Love mode — focus on closeness and attraction.",
                "friendship": "Friendship mode — focus on communication and trust.",
                "work": "Work mode — focus on roles and shared tasks.",
            },
        }
        lines.append(mode_intro_terms[lang][mode_key])

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

    key_hits: list[SynastryHit | None] = []
    lines.append("")
    for spec in KEY_PAIRS:
        if use_synastry_terms(style):
            title = spec.title_ru if lang == "ru" else spec.title_en
        elif spec.key == "sun_moon":
            title = "Эмоции и характер" if lang == "ru" else "Emotions and character"
        elif spec.key == "venus_mars":
            title = "Притяжение" if lang == "ru" else "Attraction"
        else:
            title = "Общение" if lang == "ru" else "Communication"
        lines.append(f"{spec.emoji} {title}")
        hit = find_best_key_pair_hit(hits, spec)
        key_hits.append(hit)
        if hit is not None:
            orb, user_planet, partner_planet, aspect = hit
            aspect_line = format_aspect_line(
                locale,
                user_planet,
                partner_planet,
                aspect,
                mode_key,
                orb,
                style=style,
            )
            if use_synastry_terms(style):
                group = _aspect_group_label(locale, aspect)
                lines.append(f"• {aspect_line.capitalize()} · {_capitalize_group(lang, group)}")
                interpretation = _key_pair_interpretation(
                    locale, spec, hit, mode=mode_key, style=style
                )
                lines.append(f"• {interpretation}")
            else:
                lines.append(f"• {aspect_line.capitalize()}.")
        else:
            interpretation = _key_pair_interpretation(
                locale, spec, hit, mode=mode_key, style=style
            )
            lines.append(f"• {interpretation}")

    used = _used_hit_keys(key_hits)
    other_hits = [
        hit
        for hit in sorted(hits, key=lambda item: item[0])
        if (hit[1], hit[2], hit[3]) not in used
    ]

    if other_hits:
        lines.append("")
        label = "Другие сильные связи" if lang == "ru" else "Other strong links"
        lines.append(f"{label}:")
        for hit in other_hits[: (3 if use_synastry_terms(style) else 2)]:
            orb, user_planet, partner_planet, aspect = hit
            lines.append(
                "• "
                + format_aspect_line(
                    locale,
                    user_planet,
                    partner_planet,
                    aspect,
                    mode_key,
                    orb,
                    style=style,
                ).capitalize()
            )

    if not hits:
        lines.append("")
        lines.append(
            "• Ярких межкартовых аспектов не найдено — связь более нейтральная."
            if lang == "ru"
            else "• No major cross-chart aspects — the connection is more neutral."
        )
    else:
        positive = [hit for hit in hits if _is_harmonious(hit[3])][:2]
        challenging = [hit for hit in hits if _is_tense(hit[3])][:2]
        if positive:
            tones = [aspect_tone(locale, hit[3], mode_key) for hit in positive]
            label = "Гармония" if lang == "ru" else "Harmony"
            lines.append("")
            lines.append(f"✅ {label}: {'; '.join(tones).capitalize()}.")
        if challenging:
            tones = [aspect_tone(locale, hit[3], mode_key) for hit in challenging]
            label = "Напряжение" if lang == "ru" else "Tension"
            lines.append(f"⚠️ {label}: {'; '.join(tones).capitalize()}.")

    return "\n".join(lines)
