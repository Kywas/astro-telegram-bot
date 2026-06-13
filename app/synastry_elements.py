"""Step 6 synastry: elemental balance in both charts."""
from __future__ import annotations

from dataclasses import dataclass

from app.sun_sign_compat import SIGN_ELEMENTS, ZODIAC_SIGNS

ELEMENT_ORDER = ("fire", "earth", "air", "water")

COMPATIBLE_ELEMENT_PAIRS = frozenset({("fire", "air"), ("air", "fire"), ("earth", "water"), ("water", "earth")})

CHALLENGING_ELEMENT_PAIRS = frozenset({
    ("fire", "water"),
    ("water", "fire"),
    ("fire", "earth"),
    ("earth", "fire"),
    ("air", "water"),
    ("water", "air"),
    ("air", "earth"),
    ("earth", "air"),
})

ELEMENT_LABELS = {
    "ru": {"fire": "Огонь", "earth": "Земля", "air": "Воздух", "water": "Вода"},
    "en": {"fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water"},
}

ELEMENT_SIGNS = {
    "fire": ("Aries", "Leo", "Sagittarius"),
    "earth": ("Taurus", "Virgo", "Capricorn"),
    "air": ("Gemini", "Libra", "Aquarius"),
    "water": ("Cancer", "Scorpio", "Pisces"),
}


@dataclass(frozen=True)
class ElementProfile:
    counts: dict[str, int]
    total: int
    dominant: str
    missing: tuple[str, ...]


@dataclass(frozen=True)
class ElementBalance:
    user: ElementProfile
    partner: ElementProfile


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def longitude_to_sign(longitude: float) -> str:
    return ZODIAC_SIGNS[int(longitude / 30.0) % 12]


def build_element_profile(planets: dict[str, float]) -> ElementProfile:
    counts = {element: 0 for element in ELEMENT_ORDER}
    for longitude in planets.values():
        sign = longitude_to_sign(longitude)
        element = SIGN_ELEMENTS.get(sign, "air")
        counts[element] += 1
    total = sum(counts.values())
    dominant = max(ELEMENT_ORDER, key=lambda element: (counts[element], -ELEMENT_ORDER.index(element)))
    missing = tuple(element for element in ELEMENT_ORDER if counts[element] == 0)
    return ElementProfile(counts=counts, total=total, dominant=dominant, missing=missing)


def analyze_element_balance(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
) -> ElementBalance:
    return ElementBalance(
        user=build_element_profile(user_planets),
        partner=build_element_profile(partner_planets),
    )


def _element_label(locale: str, element: str) -> str:
    return ELEMENT_LABELS[_lang(locale)][element]


def _counts_line(locale: str, profile: ElementProfile, *, style: str = "terms") -> str:
    from app.synastry_style import format_element_plain, use_synastry_terms

    lang = _lang(locale)
    if use_synastry_terms(style):
        parts = [f"{_element_label(locale, e)} {profile.counts[e]}" for e in ELEMENT_ORDER]
    else:
        parts = [f"{format_element_plain(locale, e)} {profile.counts[e]}" for e in ELEMENT_ORDER]
    if lang == "ru":
        return " · ".join(parts) + f" (всего {profile.total})"
    return " · ".join(parts) + f" (total {profile.total})"


def _dominant_line(locale: str, profile: ElementProfile, *, style: str = "terms") -> str:
    from app.synastry_style import format_element_plain, use_synastry_terms

    lang = _lang(locale)
    if use_synastry_terms(style):
        element = _element_label(locale, profile.dominant)
        if lang == "ru":
            return f"Преобладает: {element}"
        return f"Dominant: {element}"
    element = format_element_plain(locale, profile.dominant)
    if lang == "ru":
        return f"Главное: {element}"
    return f"Main: {element}"


def _gap_insights(locale: str, balance: ElementBalance, *, style: str = "terms") -> list[str]:
    from app.synastry_style import format_element_plain, use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []
    for element in ELEMENT_ORDER:
        user_count = balance.user.counts[element]
        partner_count = balance.partner.counts[element]
        if use_synastry_terms(style):
            label = _element_label(locale, element)
        else:
            label = format_element_plain(locale, element)
        if user_count >= 2 and partner_count == 0:
            if lang == "ru":
                lines.append(
                    f"У партнёра мало «{label}», у вас больше — можете не понять друг друга с первого раза."
                    if not use_synastry_terms(style)
                    else f"У партнёра нет {label.lower()} в карте, у вас {user_count} — "
                    "возможны разные темпы и непонимание мотивации."
                )
            else:
                lines.append(
                    f"Your partner has little «{label}», you have more — "
                    "you may not get each other at first."
                    if not use_synastry_terms(style)
                    else f"Partner has no {label.lower()} planets, you have {user_count} — "
                    "different rhythms may need translation."
                )
        elif partner_count >= 2 and user_count == 0:
            if lang == "ru":
                lines.append(
                    f"У вас мало «{label}», у партнёра больше — не обесценивайте его/её способ жить."
                    if not use_synastry_terms(style)
                    else f"У вас нет {label.lower()}, у партнёра {partner_count} — "
                    "важно не обесценивать его/её способ действовать."
                )
            else:
                lines.append(
                    f"You have little «{label}», your partner has more — "
                    "don't dismiss their way of living."
                    if not use_synastry_terms(style)
                    else f"You have no {label.lower()}, partner has {partner_count} — "
                    "honor their way of moving through life."
                )
    return lines[:2]


def _complement_insights(locale: str, balance: ElementBalance, *, style: str = "terms") -> list[str]:
    from app.synastry_style import format_element_plain, use_synastry_terms

    lang = _lang(locale)
    user_dom = balance.user.dominant
    partner_dom = balance.partner.dominant
    if (user_dom, partner_dom) in COMPATIBLE_ELEMENT_PAIRS:
        if lang == "ru":
            if use_synastry_terms(style):
                return [
                    f"Доминанты дополняют друг друга ({_element_label(locale, user_dom)} + "
                    f"{_element_label(locale, partner_dom)}) — классическое взаимное усиление."
                ]
            return ["Вы хорошо дополняете друг друга — один тащит, другой подстраховывает. Как команда."]
        if use_synastry_terms(style):
            return [
                f"Dominants complement each other ({_element_label(locale, user_dom)} + "
                f"{_element_label(locale, partner_dom)}) — classic mutual support."
            ]
        return ["You complement each other well — what's easy for one may be hard for the other."]
    if user_dom == partner_dom:
        if lang == "ru":
            label = (
                format_element_plain(locale, user_dom)
                if not use_synastry_terms(style)
                else _element_label(locale, user_dom).lower()
            )
            return [
                f"У обоих много «{label}» — понимаете друг друга, но можете застрять в одних ошибках."
                if not use_synastry_terms(style)
                else f"Оба с сильным {_element_label(locale, user_dom).lower()} — "
                "понимаете друг друга, но риск одной «слепой зоны»."
            ]
        label = (
            format_element_plain(locale, user_dom)
            if not use_synastry_terms(style)
            else _element_label(locale, user_dom).lower()
        )
        return [
            f"You both have lots of «{label}» — you get each other, but may repeat the same mistakes."
            if not use_synastry_terms(style)
            else f"Both strong in {_element_label(locale, user_dom).lower()} — "
            "easy rapport, but shared blind spots are possible."
        ]
    if (user_dom, partner_dom) in CHALLENGING_ELEMENT_PAIRS:
        if lang == "ru":
            if use_synastry_terms(style):
                return [
                    f"Стихии {_element_label(locale, user_dom).lower()} и "
                    f"{_element_label(locale, partner_dom).lower()} тянут в разные стороны — "
                    "ищите середину и общий язык."
                ]
            return ["Темп разный — не спорьте, кто прав. Договоритесь, как жить с этим."]
        if use_synastry_terms(style):
            return [
                f"{_element_label(locale, user_dom)} and {_element_label(locale, partner_dom)} "
                "pull in different directions — find middle ground."
            ]
        return ["Different pace — look for compromise and speak plainly."]
    return []


def _balance_summary(locale: str, balance: ElementBalance, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    user_missing = set(balance.user.missing)
    partner_missing = set(balance.partner.missing)
    complements = 0
    for element in ELEMENT_ORDER:
        if balance.user.counts[element] >= 1 and element in partner_missing:
            complements += 1
        if balance.partner.counts[element] >= 1 and element in user_missing:
            complements += 1

    if not use_synastry_terms(style):
        if complements >= 2:
            return "Вы друг друга хорошо дополняете — одному легче там, где другому сложнее." if lang == "ru" else "You complement each other — what's easy for one is hard for the other."
        if not balance.user.missing and not balance.partner.missing:
            return "У каждого свой набор качеств, но вместе картина полная." if lang == "ru" else "Different mixes, but together the picture is full."
        return "Есть пробелы — не стесняйтесь говорить прямо, что для вас важно." if lang == "ru" else "Some gaps — say plainly what matters to you."

    if complements >= 2:
        if lang == "ru":
            return "Баланс пары: хорошее взаимное дополнение стихий — опора для устойчивости."
        return "Pair balance: strong elemental complement — a base for stability."

    if not balance.user.missing and not balance.partner.missing:
        if lang == "ru":
            return "Баланс пары: у обоих представлены все стихии — разнообразие и гибкость."
        return "Pair balance: both charts hold all four elements — variety and flexibility."

    if lang == "ru":
        return (
            "Баланс пары: есть пробелы в стихиях — сознательно подстраивайте "
            "темп и ожидания друг к другу."
        )
    return "Pair balance: some elemental gaps — adjust pace and expectations consciously."


def element_score_delta(balance: ElementBalance) -> int:
    user = balance.user
    partner = balance.partner
    delta = 0
    if (user.dominant, partner.dominant) in COMPATIBLE_ELEMENT_PAIRS:
        delta += 3
    elif user.dominant == partner.dominant and user.total >= 4:
        delta += 1

    complements = 0
    for element in ELEMENT_ORDER:
        if user.counts[element] >= 1 and element in partner.missing:
            complements += 1
        if partner.counts[element] >= 1 and element in user.missing:
            complements += 1
    if complements >= 2:
        delta += 2

    friction = 0
    for element in ELEMENT_ORDER:
        if user.counts[element] >= 2 and partner.counts[element] == 0:
            friction += 1
        if partner.counts[element] >= 2 and user.counts[element] == 0:
            friction += 1
    if friction >= 2:
        delta -= 2
    elif friction == 1:
        delta -= 1

    return delta


def format_synastry_step6_section(locale: str, balance: ElementBalance, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append("⚖️ Шаг 6. Баланс стихий" if use_synastry_terms(style) else "⚖️ Кто быстрый, кто спокойный")
        if use_synastry_terms(style):
            lines.append(
                "Считаем планеты в знаках каждой стихии (Солнце, Луна, Меркурий, "
                "Венера, Марс, Юпитер, Сатурн)."
            )
        else:
            lines.append(
                "Смотрю, кому ближе драйв, быт, болтовня и чувства — "
                "так видно, где вы на одной волне, а где «ты опять торопишься»."
            )
        if use_synastry_terms(style):
            lines.append(
                "Преобладание одной стихии у одного и её отсутствие у другого "
                "может давать непонимание; взаимное дополнение — опора пары."
            )
    else:
        lines.append("⚖️ Step 6. Element balance" if use_synastry_terms(style) else "⚖️ Who's fast, who's calm")
        if use_synastry_terms(style):
            lines.append(
                "We count planets in each element by sign (Sun, Moon, Mercury, "
                "Venus, Mars, Jupiter, Saturn)."
            )
        else:
            lines.append(
                "We compare energy, stability, talk, and feelings side by side."
            )
        if use_synastry_terms(style):
            lines.append(
                "One partner's dominant element missing in the other can cause friction; "
                "complement supports stability."
            )

    lines.append("")
    if lang == "ru":
        lines.append("👤 Вы:")
    else:
        lines.append("👤 You:")
    lines.append(f"• {_counts_line(locale, balance.user, style=style)}")
    lines.append(f"• {_dominant_line(locale, balance.user, style=style)}")

    lines.append("")
    if lang == "ru":
        lines.append("👤 Партнёр:")
    else:
        lines.append("👤 Partner:")
    lines.append(f"• {_counts_line(locale, balance.partner, style=style)}")
    lines.append(f"• {_dominant_line(locale, balance.partner, style=style)}")

    lines.append("")
    for insight in _gap_insights(locale, balance, style=style):
        lines.append(f"• {insight}")
    for insight in _complement_insights(locale, balance, style=style):
        lines.append(f"• {insight}")
    lines.append(f"• {_balance_summary(locale, balance, style=style)}")

    if use_synastry_terms(style):
        if lang == "ru":
            lines.append("")
            lines.append(
                "Подсказка: Огонь+Воздух и Земля+Вода — естественные пары; "
                "ноль планет в стихии — не «плохо», но тема требует внимания."
            )
        else:
            lines.append("")
            lines.append(
                "Hint: Fire+Air and Earth+Water pair naturally; "
                "zero planets in an element isn't “bad”, but needs awareness."
            )
    elif lang == "ru":
        lines.append("")
        lines.append("• Если чувствуете, что «не на одной волне» — это не приговор, просто скажите об этом.")
    else:
        lines.append("")
        lines.append("• If you feel out of sync — talk more plainly.")

    return "\n".join(lines)
