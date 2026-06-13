"""Step 1 compatibility: Sun sign and element pairing (classic synastry baseline)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

ZODIAC_SIGNS = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

SIGN_ELEMENTS = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

SIGN_LABELS = {
    "ru": {
        "Aries": "Овен",
        "Taurus": "Телец",
        "Gemini": "Близнецы",
        "Cancer": "Рак",
        "Leo": "Лев",
        "Virgo": "Дева",
        "Libra": "Весы",
        "Scorpio": "Скорпион",
        "Sagittarius": "Стрелец",
        "Capricorn": "Козерог",
        "Aquarius": "Водолей",
        "Pisces": "Рыбы",
    },
    "en": {sign: sign for sign in ZODIAC_SIGNS},
}

COMPATIBLE_ELEMENT_PAIRS = frozenset({("fire", "air"), ("air", "fire"), ("earth", "water"), ("water", "earth")})

ELEMENT_SIGNS = {
    "fire": ("Aries", "Leo", "Sagittarius"),
    "earth": ("Taurus", "Virgo", "Capricorn"),
    "air": ("Gemini", "Libra", "Aquarius"),
    "water": ("Cancer", "Scorpio", "Pisces"),
}

SCORE_DELTA = {
    "same_sign": 6,
    "opposite": 5,
    "same_element": 5,
    "compatible_elements": 4,
    "challenging_elements": 0,
}


class SunSignKind(StrEnum):
    SAME_SIGN = "same_sign"
    OPPOSITE = "opposite"
    SAME_ELEMENT = "same_element"
    COMPATIBLE_ELEMENTS = "compatible_elements"
    CHALLENGING_ELEMENTS = "challenging_elements"


@dataclass(frozen=True)
class SunSignCompat:
    user_sign: str
    partner_sign: str
    user_element: str
    partner_element: str
    kind: SunSignKind
    score_delta: int


def normalize_sign_key(sign: str | None) -> str | None:
    if not sign:
        return None
    if sign in SIGN_ELEMENTS:
        return sign
    for key, labels in SIGN_LABELS.items():
        for eng, label in labels.items():
            if label == sign:
                return eng
    return None


def _sign_index(sign: str) -> int:
    return ZODIAC_SIGNS.index(sign)


def are_opposite_signs(sign_a: str, sign_b: str) -> bool:
    if sign_a == sign_b:
        return False
    return abs(_sign_index(sign_a) - _sign_index(sign_b)) == 6


def classify_sun_sign_pair(sign_a: str, sign_b: str) -> SunSignKind:
    if sign_a == sign_b:
        return SunSignKind.SAME_SIGN
    if are_opposite_signs(sign_a, sign_b):
        return SunSignKind.OPPOSITE
    element_a = SIGN_ELEMENTS[sign_a]
    element_b = SIGN_ELEMENTS[sign_b]
    if element_a == element_b:
        return SunSignKind.SAME_ELEMENT
    if (element_a, element_b) in COMPATIBLE_ELEMENT_PAIRS:
        return SunSignKind.COMPATIBLE_ELEMENTS
    return SunSignKind.CHALLENGING_ELEMENTS


def analyze_sun_sign_compat(user_sign: str, partner_sign: str) -> SunSignCompat | None:
    user_key = normalize_sign_key(user_sign)
    partner_key = normalize_sign_key(partner_sign)
    if user_key is None or partner_key is None:
        return None
    kind = classify_sun_sign_pair(user_key, partner_key)
    return SunSignCompat(
        user_sign=user_key,
        partner_sign=partner_key,
        user_element=SIGN_ELEMENTS[user_key],
        partner_element=SIGN_ELEMENTS[partner_key],
        kind=kind,
        score_delta=SCORE_DELTA[kind.value],
    )


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _element_label(locale: str, element: str) -> str:
    lang = _lang(locale)
    labels = {
        "ru": {"fire": "Огонь", "earth": "Земля", "air": "Воздух", "water": "Вода"},
        "en": {"fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water"},
    }
    return labels[lang][element]


def _signs_in_element(locale: str, element: str) -> str:
    lang = _lang(locale)
    names = [SIGN_LABELS[lang][sign] for sign in ELEMENT_SIGNS[element]]
    return ", ".join(names)


def _pair_element_hint(locale: str, element_a: str, element_b: str) -> str:
    lang = _lang(locale)
    if lang == "ru":
        if {element_a, element_b} == {"fire", "air"}:
            return (
                "Огонь (Овен, Лев, Стрелец) хорошо сочетается с Воздухом "
                "(Близнецы, Весы, Водолей) — лёгкое взаимопонимание."
            )
        if {element_a, element_b} == {"earth", "water"}:
            return (
                "Земля (Телец, Дева, Козерог) гармонирует с Водой "
                "(Рак, Скорпион, Рыбы) — опора и эмоциональный контакт."
            )
        return (
            "Сочетаемые стихии дают взаимопонимание: Огонь + Воздух, Земля + Вода."
        )
    if {element_a, element_b} == {"fire", "air"}:
        return (
            "Fire (Aries, Leo, Sagittarius) pairs well with Air "
            "(Gemini, Libra, Aquarius) — easy mutual understanding."
        )
    if {element_a, element_b} == {"earth", "water"}:
        return (
            "Earth (Taurus, Virgo, Capricorn) harmonizes with Water "
            "(Cancer, Scorpio, Pisces) — stability and emotional depth."
        )
    return "Compatible elements support understanding: Fire + Air, Earth + Water."


def format_sun_sign_compat_section(locale: str, compat: SunSignCompat, *, style: str = "terms") -> str:
    from app.synastry_style import format_element_plain, use_synastry_terms

    lang = _lang(locale)
    user_name = SIGN_LABELS[lang][compat.user_sign]
    partner_name = SIGN_LABELS[lang][compat.partner_sign]
    user_elem = _element_label(locale, compat.user_element)
    partner_elem = _element_label(locale, compat.partner_element)

    lines: list[str] = []
    if lang == "ru":
        lines.append("☀️ Шаг 1. Солнечные знаки" if use_synastry_terms(style) else "☀️ Кто вы по знакам")
        if use_synastry_terms(style):
            lines.append(f"• {user_name} ({user_elem}) + {partner_name} ({partner_elem})")
        else:
            lines.append(
                f"• {user_name} + {partner_name} · "
                f"{format_element_plain(locale, compat.user_element)} и "
                f"{format_element_plain(locale, compat.partner_element)}"
            )
    else:
        lines.append("☀️ Step 1. Sun signs" if use_synastry_terms(style) else "☀️ Who you are by sign")
        if use_synastry_terms(style):
            lines.append(f"• {user_name} ({user_elem}) + {partner_name} ({partner_elem})")
        else:
            lines.append(
                f"• {user_name} + {partner_name} · "
                f"{format_element_plain(locale, compat.user_element)} and "
                f"{format_element_plain(locale, compat.partner_element)}"
            )

    kind = compat.kind
    plain = not use_synastry_terms(style)
    if kind == SunSignKind.SAME_SIGN:
        if lang == "ru":
            lines.append(
                "• Один знак — вы как два зеркала: быстро понимаете друг друга. "
                "Следите только, чтобы не повторять одни и те же косяки вдвоём."
                if plain
                else "• Один знак — усиливаете общие черты и быстро считываете друг друга. "
                "Следите, чтобы не застревать в одинаковых слепых зонах."
            )
        else:
            lines.append(
                "• Same sign — you're alike and read each other fast. "
                "Just watch you don't repeat the same mistakes together."
                if plain
                else "• Same sign — shared traits amplify and you read each other quickly. "
                "Watch for the same blind spots in tandem."
            )
    elif kind == SunSignKind.OPPOSITE:
        if lang == "ru":
            lines.append(
                f"• {user_name} и {partner_name} — противоположности. "
                "Магнит работает, но без разговоров легко устроить мини-шторм."
                if plain
                else f"• Противоположные знаки ({user_name} — {partner_name}) — "
                "сильное притяжение через контраст: вы тянетесь друг к другу, "
                "но без диалога легко спорить."
            )
        else:
            lines.append(
                f"• {user_name} and {partner_name} — very different. "
                "That pulls you together, but fights happen without honest talk."
                if plain
                else f"• Opposite signs ({user_name} — {partner_name}) — "
                "strong pull through contrast: magnetic, but friction grows without dialogue."
            )
        if not plain:
            lines.append(f"• {_pair_element_hint(locale, compat.user_element, compat.partner_element)}")
    elif kind == SunSignKind.SAME_ELEMENT:
        if lang == "ru":
            lines.append(
                "• Похожий темп — часто понимаете друг друга с полуслова. Удобно."
                if plain
                else f"• Одна стихия ({_element_label(locale, compat.user_element)}: "
                f"{_signs_in_element(locale, compat.user_element)}) — похожий темп и ценности, "
                "общие черты усиливаются."
            )
        else:
            lines.append(
                "• Similar pace and values — easier to understand each other."
                if plain
                else f"• Same element ({_element_label(locale, compat.user_element)}: "
                f"{_signs_in_element(locale, compat.user_element)}) — similar pace and values; "
                "shared traits amplify."
            )
    elif kind == SunSignKind.COMPATIBLE_ELEMENTS:
        if lang == "ru":
            lines.append(
                "• Ваши типы характера хорошо сочетаются — обычно легче договориться."
                if plain
                else f"• Сочетаемые стихии ({user_elem} + {partner_elem}) — "
                "естественное взаимопонимание и дополнение."
            )
        else:
            lines.append(
                "• Your character types fit well — agreements usually come easier."
                if plain
                else f"• Compatible elements ({user_elem} + {partner_elem}) — "
                "natural understanding and complement."
            )
        if not plain:
            lines.append(f"• {_pair_element_hint(locale, compat.user_element, compat.partner_element)}")
    else:
        if lang == "ru":
            lines.append(
                "• Разный темп — нужно больше терпения и объяснений, зато можно дополнять друг друга."
                if plain
                else f"• Разные стихии ({user_elem} и {partner_elem}) — меньше автоматической "
                "синхронности, зато вы дополняете друг друга, если договариваетесь."
            )
        else:
            lines.append(
                "• Different pace — more patience and explaining, but you can still complement each other."
                if plain
                else f"• Different elements ({user_elem} and {partner_elem}) — less automatic sync, "
                "but you can complement each other with clear agreements."
            )

    return "\n".join(lines)


def sun_sign_base_score(compat: SunSignCompat) -> int:
    """Standalone score when only Sun signs are available (no full chart)."""
    return max(40, min(88, 52 + compat.score_delta))
