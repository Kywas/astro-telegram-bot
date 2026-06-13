"""Direct-answer synthesis for natal chart Q&A."""
from __future__ import annotations

from dataclasses import dataclass

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import LAGNA_ESSENCE, _house_theme, _lang, _pl, _sign_line, _use_terms

_DIGNITY_RANK = {"exalted": 4, "own": 3, "neutral": 2, "debilitated": 1}


@dataclass(frozen=True)
class QaSynthFocus:
    houses: tuple[int, ...] = ()
    planet_keys: tuple[str, ...] = ()
    focus: str = "default"


def _planets_in_house(chart: JyotishChart, house: int) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")
    return [chart.planets[key] for key in order if chart.planets[key].house == house]


def _lord_placement(chart: JyotishChart, house: int) -> PlanetPlacement:
    return chart.planets[chart.house_lords[house]]


def _collect_placements(
    chart: JyotishChart,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
) -> list[PlanetPlacement]:
    seen: set[str] = set()
    out: list[PlanetPlacement] = []
    for house in houses:
        for pl in _planets_in_house(chart, house):
            if pl.key not in seen:
                seen.add(pl.key)
                out.append(pl)
        lord = _lord_placement(chart, house)
        if lord.key not in seen:
            seen.add(lord.key)
            out.append(lord)
    for key in planet_keys:
        if key not in seen:
            seen.add(key)
            out.append(chart.planets[key])
    return out


def _pick_focus_planet(
    chart: JyotishChart,
    placements: list[PlanetPlacement],
    *,
    houses: tuple[int, ...] = (),
    focus: str = "default",
) -> PlanetPlacement:
    if not placements:
        if houses:
            return _lord_placement(chart, houses[0])
        return chart.planets["SUN"]

    if focus == "strength":
        return max(placements, key=lambda p: _DIGNITY_RANK.get(p.dignity, 2))
    if focus == "challenge":
        weak = [p for p in placements if p.dignity == "debilitated"]
        if weak:
            return weak[0]
        return min(placements, key=lambda p: _DIGNITY_RANK.get(p.dignity, 2))
    return placements[0]


def _lagna_answer(locale: str, chart: JyotishChart, question: str, *, style: str) -> str | None:
    lang = _lang(locale)
    q = question.lower()
    lagna = sign_label(locale, chart.lagna_sign)
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
    if lang == "ru":
        if any(w in q for w in ("перв", "видят", "образ", "суть", "кто я", "начина")):
            if _use_terms(style):
                return f"При первой встрече тебя читают через Лагну в {lagna}: {essence}."
            return f"При первой встрече тебя воспринимают как человека с образом {lagna}: {essence}."
    elif any(w in q for w in ("first", "see me", "core", "who am", "begin")):
        if _use_terms(style):
            return f"At first contact people read your Lagna in {lagna}: {essence}."
        return f"At first contact people sense {lagna} — {essence}."
    return None


def _phrase_from_placement(
    locale: str,
    question: str,
    pl: PlanetPlacement,
    *,
    style: str,
) -> str:
    lang = _lang(locale)
    pname = _pl(locale, pl.key)
    sign = sign_label(locale, pl.sign)
    theme = _house_theme(locale, pl.house)
    core = _sign_line(locale, pl.key, pl.sign).rstrip(".")
    q = question.lower()

    dignity_tail = ""
    if pl.dignity == "exalted":
        dignity_tail = (
            " Это одна из сильных опор карты."
            if lang == "ru"
            else " This is one of the chart's strong anchors."
        )
    elif pl.dignity == "debilitated":
        dignity_tail = (
            " Здесь важна осознанность — тема не слабая, но требует внимания."
            if lang == "ru"
            else " Conscious attention helps — the theme is workable, not blocked."
        )

    if lang == "ru":
        if q.startswith("как ") or "как я" in q or "как склады" in q or "как отнош" in q or "как забот" in q or "как чувств" in q or "как жить" in q:
            return (
                f"Скорее всего — {core}: {pname} в {sign} связывает это с темой «{theme}»."
                f"{dignity_tail}"
            )
        if q.startswith("где") or " где " in q or "откуда" in q or "куда" in q[:5]:
            return (
                f"Это чаще проявляется через «{theme}»: {pname} в {sign} — {core}."
                f"{dignity_tail}"
            )
        if q.startswith("что") or q.startswith("кто") or "кого" in q or "какие" in q[:6]:
            return (
                f"Карта показывает: {core}; ключ — {pname} в {sign} в сфере «{theme}»."
                f"{dignity_tail}"
            )
        if "есть ли" in q or q.startswith("в чём") or "предназнач" in q:
            return (
                f"Да, линия есть: «{theme}» подсвечена — {pname} в {sign} {core}."
                f"{dignity_tail}"
            )
        if q.startswith("на что") or "обратить внимание" in q or "слаб" in q:
            return (
                f"Стоит замечать «{theme}» и качества {pname} в {sign}: {core}."
                f"{dignity_tail}"
            )
        if "мешает" in q or "риск" in q or "трен" in q or "сложн" in q:
            return (
                f"Типичное напряжение — в теме «{theme}»: {pname} в {sign} {core}."
                f"{dignity_tail}"
            )
        if "талант" in q or "сильн" in q or "опор" in q:
            return (
                f"Опора — {core}; это даёт {pname} в {sign} в «{theme}»."
                f"{dignity_tail}"
            )
        return (
            f"По карте: {core}; главный маркер — {pname} в {sign} («{theme}»)."
            f"{dignity_tail}"
        )

    if q.startswith("how") or "how do" in q or "how does" in q:
        return (
            f"Most likely — {core}: {pname} in {sign} ties this to {theme}."
            f"{dignity_tail}"
        )
    if q.startswith("where") or "who do" in q or "who suits" in q:
        return (
            f"This shows up through {theme}: {pname} in {sign} — {core}."
            f"{dignity_tail}"
        )
    if q.startswith("what") or q.startswith("who") or q.startswith("which"):
        return (
            f"The chart highlights: {core}; key marker — {pname} in {sign} in {theme}."
            f"{dignity_tail}"
        )
    if "is there" in q or q.startswith("what is my"):
        return (
            f"Yes — {theme} is lit up: {pname} in {sign} {core}."
            f"{dignity_tail}"
        )
    if "watch" in q or "weak" in q or "risk" in q or "friction" in q:
        return (
            f"Watch {theme} and {pname} in {sign}: {core}."
            f"{dignity_tail}"
        )
    if "strength" in q or "talent" in q or "anchor" in q:
        return (
            f"Your anchor — {core}; {pname} in {sign} in {theme} supports this."
            f"{dignity_tail}"
        )
    return (
        f"From the chart: {core}; main marker — {pname} in {sign} ({theme})."
        f"{dignity_tail}"
    )


def synthesize_direct_answer(
    chart: JyotishChart,
    locale: str,
    question: str,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    focus: str = "default",
    style: str = "terms",
    lagna_first: bool = False,
) -> str:
    if lagna_first:
        lagna_line = _lagna_answer(locale, chart, question, style=style)
        if lagna_line:
            return lagna_line

    placements = _collect_placements(chart, houses=houses, planet_keys=planet_keys)
    pl = _pick_focus_planet(chart, placements, houses=houses, focus=focus)
    return _phrase_from_placement(locale, question, pl, style=style)


def format_qa_body(
    locale: str,
    direct_answer: str,
    evidence: str,
    *,
    style: str = "terms",
) -> str:
    del style
    lang = _lang(locale)
    evidence = evidence.strip()
    if lang == "ru":
        block = f"💬 Ответ:\n{direct_answer.strip()}"
        if evidence:
            block += f"\n\n📊 Подробнее по карте:\n{evidence}"
        return block
    block = f"💬 Answer:\n{direct_answer.strip()}"
    if evidence:
        block += f"\n\n📊 Chart details:\n{evidence}"
    return block


def finish_qa_body(
    locale: str,
    question: str,
    chart: JyotishChart,
    evidence: str,
    *,
    houses: tuple[int, ...] = (),
    planet_keys: tuple[str, ...] = (),
    focus: str = "default",
    style: str = "terms",
    lagna_first: bool = False,
    direct_answer: str | None = None,
) -> str:
    answer = direct_answer or synthesize_direct_answer(
        chart,
        locale,
        question,
        houses=houses,
        planet_keys=planet_keys,
        focus=focus,
        style=style,
        lagna_first=lagna_first,
    )
    return format_qa_body(locale, answer, evidence, style=style)
