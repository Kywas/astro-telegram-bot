"""Esoteric compatibility: relationship numerology from birth dates."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

SCORE_DELTA = {
    2: 3,
    6: 3,
    3: 2,
    9: 2,
    1: 2,
    5: 2,
    4: 1,
    7: 1,
    8: 0,
}

COMPAT_HINT = {
    "ru": {
        1: "лидерские отношения, возможны конфликты за власть",
        2: "гармония, но есть риск зависимости",
        3: "творческий союз с общими целями",
        4: "прочный фундамент, но может быть скучно",
        5: "динамичные, но нестабильные отношения",
        6: "семейная гармония, взаимная поддержка",
        7: "духовная связь, интеллектуальное притяжение",
        8: "материальный успех, но риск меркантильности",
        9: "кармическая связь с глубокой трансформацией",
    },
    "en": {
        1: "leadership dynamic — power struggles are possible",
        2: "harmony, but dependency risk",
        3: "creative union with shared goals",
        4: "solid foundation, but may feel dull",
        5: "dynamic yet unstable relationship",
        6: "family harmony and mutual support",
        7: "spiritual bond and intellectual attraction",
        8: "material success, but mercenary risk",
        9: "karmic bond with deep transformation",
    },
}

COMPAT_HINT_PLAIN = {
    "ru": {
        1: "оба тянутся к лидерству — возможны споры, кто главный",
        2: "мягко и спокойно, но легко слишком зависеть друг от друга",
        3: "вместе творите и двигаетесь к общим целям",
        4: "надёжно и стабильно, но без новизны может наскучить",
        5: "много движения и перемен — стабильность даётся труднее",
        6: "тепло дома и опора друг для друга",
        7: "близость через смысл, идеи и духовные темы",
        8: "хорошо в деньгах и делах, но следите, чтобы не всё свелось к выгоде",
        9: "сильная, «судьбоносная» связь — отношения меняют вас обоих",
    },
    "en": {
        1: "both lean toward leading — arguments over who's in charge are possible",
        2: "gentle and calm, but easy to become too dependent on each other",
        3: "you create together and move toward shared goals",
        4: "reliable and steady, but may feel dull without novelty",
        5: "lots of motion and change — stability is harder to keep",
        6: "warmth at home and support for each other",
        7: "closeness through meaning, ideas, and spiritual themes",
        8: "strong in money and work — watch that everything doesn't become transactional",
        9: "a strong, fated bond — the relationship transforms you both",
    },
}

LIFE_PATH_HINT = {
    "ru": {
        1: "лидер, самостоятельность",
        2: "дипломат, чувствительность",
        3: "творец, общение",
        4: "строитель, практичность",
        5: "искатель, свобода",
        6: "забота, семья",
        7: "аналитик, глубина",
        8: "организатор, результат",
        9: "гуманист, мудрость",
    },
    "en": {
        1: "leader, independence",
        2: "diplomat, sensitivity",
        3: "creator, communication",
        4: "builder, practicality",
        5: "seeker, freedom",
        6: "care, family",
        7: "analyst, depth",
        8: "organizer, results",
        9: "humanist, wisdom",
    },
}


@dataclass(frozen=True)
class NumerologyCompat:
    user_life_path: int
    partner_life_path: int
    compatibility_number: int
    user_digit_sum: int
    partner_digit_sum: int
    score_delta: int


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def reduce_to_single_digit(value: int) -> int:
    number = abs(value)
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    return number or 9


def birth_date_digit_sum(birth_date: date) -> int:
    raw = f"{birth_date.day:02d}{birth_date.month:02d}{birth_date.year}"
    return sum(int(char) for char in raw)


def life_path_number(birth_date: date) -> tuple[int, int]:
    digit_sum = birth_date_digit_sum(birth_date)
    return reduce_to_single_digit(digit_sum), digit_sum


def compatibility_number(user_path: int, partner_path: int) -> int:
    return reduce_to_single_digit(user_path + partner_path)


def analyze_relationship_numerology(
    user_birth_date: date,
    partner_birth_date: date,
) -> NumerologyCompat:
    user_path, user_raw = life_path_number(user_birth_date)
    partner_path, partner_raw = life_path_number(partner_birth_date)
    compat = compatibility_number(user_path, partner_path)
    return NumerologyCompat(
        user_life_path=user_path,
        partner_life_path=partner_path,
        compatibility_number=compat,
        user_digit_sum=user_raw,
        partner_digit_sum=partner_raw,
        score_delta=SCORE_DELTA.get(compat, 0),
    )


def numerology_score_delta(analysis: NumerologyCompat) -> int:
    return analysis.score_delta


def _format_date(locale: str, birth_date: date) -> str:
    if locale == "ru":
        return birth_date.strftime("%d.%m.%Y")
    return birth_date.strftime("%Y-%m-%d")


def _reduction_chain(raw_sum: int) -> str:
    parts = [str(raw_sum)]
    current = raw_sum
    while current > 9:
        current = sum(int(digit) for digit in str(current))
        parts.append(str(current))
    return "→".join(parts)


def format_synastry_numerology_section(
    locale: str,
    analysis: NumerologyCompat,
    *,
    user_birth_date: date,
    partner_birth_date: date,
    style: str = "terms",
) -> str:
    from app.synastry_style import use_synastry_terms

    lang = _lang(locale)
    lines: list[str] = []
    user_date = _format_date(lang, user_birth_date)
    partner_date = _format_date(lang, partner_birth_date)
    compat = analysis.compatibility_number

    if lang == "ru":
        lines.append(
            "🔢 Нумерология отношений"
            if use_synastry_terms(style)
            else "🔢 Числа вашей пары"
        )
        if use_synastry_terms(style):
            lines.append(
                "Складываем все цифры даты рождения каждого до одной цифры, "
                "затем суммируем числа пары — получаем число совместимости."
            )
        else:
            lines.append(
                "По датам рождения считаем два личных числа и одно общее для пары."
            )
    else:
        lines.append(
            "🔢 Relationship numerology"
            if use_synastry_terms(style)
            else "🔢 Your pair numbers"
        )
        if use_synastry_terms(style):
            lines.append(
                "Reduce all birth-date digits to one digit per person, "
                "then add both and reduce again — the compatibility number."
            )
        else:
            lines.append(
                "From birth dates we derive two personal numbers and one shared pair number."
            )

    lines.append("")
    if use_synastry_terms(style):
        lines.append(
            f"• Вы ({user_date}): сумма цифр {analysis.user_digit_sum} → "
            f"{_reduction_chain(analysis.user_digit_sum)} = {analysis.user_life_path}."
            if lang == "ru"
            else f"• You ({user_date}): digit sum {analysis.user_digit_sum} → "
            f"{_reduction_chain(analysis.user_digit_sum)} = {analysis.user_life_path}."
        )
        lines.append(
            f"• Партнёр ({partner_date}): сумма цифр {analysis.partner_digit_sum} → "
            f"{_reduction_chain(analysis.partner_digit_sum)} = {analysis.partner_life_path}."
            if lang == "ru"
            else f"• Partner ({partner_date}): digit sum {analysis.partner_digit_sum} → "
            f"{_reduction_chain(analysis.partner_digit_sum)} = {analysis.partner_life_path}."
        )
        lines.append(
            f"• Число совместимости: {analysis.user_life_path} + {analysis.partner_life_path} "
            f"= {analysis.user_life_path + analysis.partner_life_path} → {compat}."
            if lang == "ru"
            else f"• Compatibility number: {analysis.user_life_path} + {analysis.partner_life_path} "
            f"= {analysis.user_life_path + analysis.partner_life_path} → {compat}."
        )
    else:
        user_hint = LIFE_PATH_HINT[lang][analysis.user_life_path]
        partner_hint = LIFE_PATH_HINT[lang][analysis.partner_life_path]
        if lang == "ru":
            lines.append(f"• Ваше число: {analysis.user_life_path} ({user_hint}).")
            lines.append(f"• Число партнёра: {analysis.partner_life_path} ({partner_hint}).")
            lines.append(f"• Число пары: {compat}.")
        else:
            lines.append(f"• Your number: {analysis.user_life_path} ({user_hint}).")
            lines.append(f"• Partner's number: {analysis.partner_life_path} ({partner_hint}).")
            lines.append(f"• Pair number: {compat}.")

    hint_table = COMPAT_HINT if use_synastry_terms(style) else COMPAT_HINT_PLAIN
    lines.append("")
    if lang == "ru":
        lines.append(f"Интерпретация: {hint_table[lang][compat]}.")
    else:
        lines.append(f"Interpretation: {hint_table[lang][compat]}.")

    return "\n".join(lines)
