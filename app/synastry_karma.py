"""Step 8 synastry: lunar nodes (Rahu/Ketu) and karmic links."""
from __future__ import annotations

from dataclasses import dataclass

import swisseph as swe

from app.forecast_text import _aspect_label

PERSONAL_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS")
NODE_KEYS = ("RAHU", "KETU")

ASPECTS = (
    ("conjunction", 0, 8),
    ("sextile", 60, 6),
    ("square", 90, 7),
    ("trine", 120, 8),
    ("opposition", 180, 8),
)

HARMONIOUS = frozenset({"conjunction", "trine", "sextile"})
TENSE = frozenset({"square", "opposition"})

PLANET_LABELS = {
    "ru": {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "RAHU": "Раху (Северный узел)",
        "KETU": "Кету (Южный узел)",
    },
    "en": {
        "SUN": "Sun",
        "MOON": "Moon",
        "MERCURY": "Mercury",
        "VENUS": "Venus",
        "MARS": "Mars",
        "RAHU": "Rahu (North Node)",
        "KETU": "Ketu (South Node)",
    },
}


@dataclass(frozen=True)
class KarmicLink:
    kind: str
    node_owner: str
    node_key: str
    target_owner: str
    target_planet: str
    aspect: str
    orb: float


@dataclass(frozen=True)
class KarmicAnalysis:
    karmic_tasks: tuple[KarmicLink, ...]
    destined: tuple[KarmicLink, ...]

    @property
    def best_destined(self) -> KarmicLink | None:
        return self.destined[0] if self.destined else None

    @property
    def has_karmic_task(self) -> bool:
        return bool(self.karmic_tasks)


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _planet_label(locale: str, planet: str) -> str:
    return PLANET_LABELS[_lang(locale)].get(planet, planet)


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


def _lunar_nodes(julian_day: float) -> dict[str, float]:
    result, _ = swe.calc_ut(julian_day, swe.TRUE_NODE)
    rahu = float(result[0])
    return {"RAHU": rahu, "KETU": (rahu + 180.0) % 360.0}


def _cross_node_links(
    node_owner: str,
    nodes: dict[str, float],
    target_owner: str,
    planets: dict[str, float],
    *,
    include_moon: bool,
) -> list[KarmicLink]:
    links: list[KarmicLink] = []
    for node_key in NODE_KEYS:
        for planet_key in PERSONAL_PLANETS:
            if planet_key == "MOON" and not include_moon:
                continue
            if planet_key not in planets:
                continue
            aspect_info = _find_aspect(nodes[node_key], planets[planet_key])
            if aspect_info is None:
                continue
            aspect, orb = aspect_info
            kind = "destined" if (
                node_key == "RAHU"
                and planet_key in {"SUN", "MOON"}
                and aspect == "conjunction"
                and orb <= 6.0
            ) else "karmic_task"
            links.append(
                KarmicLink(
                    kind=kind,
                    node_owner=node_owner,
                    node_key=node_key,
                    target_owner=target_owner,
                    target_planet=planet_key,
                    aspect=aspect,
                    orb=orb,
                )
            )
    links.sort(key=lambda item: item.orb)
    return links


def analyze_karmic_synastry(
    user_planets: dict[str, float],
    partner_planets: dict[str, float],
    *,
    user_julian_day: float,
    partner_julian_day: float,
    user_has_moon: bool,
    partner_has_moon: bool,
) -> KarmicAnalysis:
    user_nodes = _lunar_nodes(user_julian_day)
    partner_nodes = _lunar_nodes(partner_julian_day)

    all_links: list[KarmicLink] = []
    all_links.extend(
        _cross_node_links(
            "user",
            user_nodes,
            "partner",
            partner_planets,
            include_moon=partner_has_moon,
        )
    )
    all_links.extend(
        _cross_node_links(
            "partner",
            partner_nodes,
            "user",
            user_planets,
            include_moon=user_has_moon,
        )
    )

    destined = tuple(link for link in all_links if link.kind == "destined")
    destined = tuple(sorted(destined, key=lambda item: item.orb))
    karmic_tasks = tuple(
        sorted(
            (link for link in all_links if link.kind == "karmic_task"),
            key=lambda item: item.orb,
        )
    )
    return KarmicAnalysis(karmic_tasks=karmic_tasks, destined=destined)


def karmic_score_delta(analysis: KarmicAnalysis) -> int:
    delta = 0
    if analysis.best_destined is not None:
        delta += 4 if analysis.best_destined.orb <= 3.0 else 3
    if analysis.has_karmic_task:
        delta += 2 if len(analysis.karmic_tasks) >= 2 else 1
    return delta


def _format_link_line(locale: str, link: KarmicLink, *, style: str = "terms") -> str:
    from app.synastry_style import use_synastry_terms

    if not use_synastry_terms(style):
        return _format_plain_karmic_link(locale, link)

    lang = _lang(locale)
    aspect_label = _aspect_label(locale, link.aspect)
    orb_part = f" ({link.orb:.1f}°)" if link.orb <= 2.5 else ""
    node_name = _planet_label(locale, link.node_key)
    target_name = _planet_label(locale, link.target_planet)

    if link.node_owner == "user":
        if lang == "ru":
            return (
                f"ваш {node_name}, {aspect_label} "
                f"к {target_name} партнёра{orb_part}"
            )
        return (
            f"your {node_name} {aspect_label} "
            f"partner's {target_name}{orb_part}"
        )

    if lang == "ru":
        return (
            f"{node_name} партнёра, {aspect_label} "
            f"к вашему {target_name}{orb_part}"
        )
    return (
        f"partner's {node_name} {aspect_label} "
        f"your {target_name}{orb_part}"
    )


def _node_role_plain(locale: str, link: KarmicLink) -> str:
    lang = _lang(locale)
    is_rahu = link.node_key == "RAHU"
    if link.node_owner == "user":
        if lang == "ru":
            return "ваша линия роста" if is_rahu else "ваш старый сценарий"
        return "your growth line" if is_rahu else "your old pattern"
    if lang == "ru":
        return "линия роста партнёра" if is_rahu else "старый сценарий партнёра"
    return "partner's growth line" if is_rahu else "partner's old pattern"


def _target_role_plain(locale: str, link: KarmicLink) -> str:
    from app.synastry_style import format_partner_planet, format_user_planet

    if link.node_owner == "user":
        return format_partner_planet(locale, link.target_planet, "plain")
    return format_user_planet(locale, link.target_planet, "plain")


def _format_plain_karmic_link(locale: str, link: KarmicLink) -> str:
    lang = _lang(locale)
    node = _node_role_plain(locale, link)
    target = _target_role_plain(locale, link)

    if lang == "ru":
        if link.aspect in HARMONIOUS:
            return f"{node.capitalize()} мягко цепляется за {target}"
        if link.aspect == "square":
            return f"{node.capitalize()} может задевать {target}"
        if link.aspect == "opposition":
            return f"{node.capitalize()} и {target} — магнит с двух сторон: тянет и бесит"
        return f"{node.capitalize()} заметно влияет на {target}"

    if link.aspect in HARMONIOUS:
        return f"{node.capitalize()} gently hooks into {target}"
    if link.aspect == "square":
        return f"{node.capitalize()} can sting {target}"
    if link.aspect == "opposition":
        return f"{node.capitalize()} and {target} — magnet from both sides: pull and friction"
    return f"{node.capitalize()} noticeably touches {target}"


def _plain_task_interpretation(locale: str, link: KarmicLink) -> str:
    lang = _lang(locale)
    if link.aspect in HARMONIOUS:
        if lang == "ru":
            return "Урок идёт мягче — можно меняться без драмы."
        return "The lesson lands softer — change without theatrics."
    if lang == "ru":
        if link.target_planet == "VENUS":
            return "В нежности легко зацепиться — лучше сказать, чем додумывать."
        if link.target_planet == "MERCURY":
            return "В разговорах легко не попасть — переспрашивайте, не угадывайте."
        if link.target_planet == "MOON":
            return "Эмоции могут накрывать — назовите чувство вслух."
        return "Тут лучше не копить — честный разговор дешевле молчания."
    if link.target_planet == "VENUS":
        return "Warmth can sting here — say it, don't guess."
    if link.target_planet == "MERCURY":
        return "Easy to miss each other in talk — ask, don't assume."
    if link.target_planet == "MOON":
        return "Feelings can flood — name them out loud."
    return "Don't stockpile — honest talk beats silence."


def _format_plain_karma_section(locale: str, analysis: KarmicAnalysis, *, mode: str = "love") -> str:
    from app.compat_mode_plain import mode_key as _mode_key

    lang = _lang(locale)
    mode_key = _mode_key(mode)
    lines: list[str] = []

    if lang == "ru":
        headers = {
            "love": "🪷 О чём обычно молчат",
            "friendship": "🪷 Где дружба может зацепиться",
            "work": "🪷 Где проект может поехать",
        }
        lines.append(headers[mode_key])
        intros = {
            "love": (
                "Темы, которые пара словно «принесла с собой» — не обязательно «судьба», "
                "но часто чувствуются телом, а не головой."
            ),
            "friendship": (
                "Темы, которые дружба словно «тащит из прошлого» — обиды, ревность, "
                "«ты пропал на полгода». Не приговор, но честно назвать полезно."
            ),
            "work": (
                "Темы, которые команда словно «тащит в проект» — контроль, дедлайны, "
                "«я тут главный». Не KPI, но если не проговорить — будет драма на созвоне."
            ),
        }
        lines.append(intros[mode_key])
    else:
        headers = {
            "love": "🪷 What's usually unsaid",
            "friendship": "🪷 Where friendship can snag",
            "work": "🪷 Where the project can derail",
        }
        lines.append(headers[mode_key])
        intros = {
            "love": (
                "Themes you seem to carry into the bond — not always «fate», "
                "but often felt in the gut, not the spreadsheet."
            ),
            "friendship": (
                "Themes friendship drags along — hurt, jealousy, «you ghosted for six months». "
                "Not a verdict, but naming them helps."
            ),
            "work": (
                "Themes the team drags into the project — control, deadlines, "
                "«I'm the boss here». Not KPIs, but unspoken drama kills calls."
            ),
        }
        lines.append(intros[mode_key])

    lines.append("")
    if lang == "ru":
        magnet_headers = {
            "love": "✨ Магнетизм «не просто так»",
            "friendship": "✨ «Не просто случайный друг»",
            "work": "✨ «Не просто случайный коллега»",
        }
        lines.append(magnet_headers[mode_key])
        magnet_intros = {
            "love": "Бывает ощущение, что встретились не случайно — или что жизнь вас проверяет на зрелость.",
            "friendship": (
                "Бывает ощущение, что вы «свои» с первого раза — "
                "или что дружба вас чему-то учит, даже когда бесит."
            ),
            "work": (
                "Бывает ощущение, что вы «с одного проекта» — "
                "или что вместе вас чему-то учат, даже когда спорите о Excel."
            ),
        }
        lines.append(magnet_intros[mode_key])
    else:
        magnet_headers = {
            "love": "✨ «Not just random» magnetism",
            "friendship": "✨ «Not just a random friend»",
            "work": "✨ «Not just a random colleague»",
        }
        lines.append(magnet_headers[mode_key])
        magnet_intros = {
            "love": "Sometimes it feels meant — or like life is testing how grown-up you can be together.",
            "friendship": (
                "Sometimes you feel «instant friends» — "
                "or like the friendship teaches you something, even when it annoys you."
            ),
            "work": (
                "Sometimes you feel «same project energy» — "
                "or like working together teaches you something, even when you argue about spreadsheets."
            ),
        }
        lines.append(magnet_intros[mode_key])

    if analysis.best_destined is None:
        no_destined = {
            "ru": {
                "love": (
                    "• Яркого «мы с судьбой» тут нет — и это нормально. "
                    "Можете быть глубокими просто потому что подходите, а не потому что «так в карте»."
                ),
                "friendship": (
                    "• Яркого «мы с судьбой, дружим вечно» тут нет — и это нормально. "
                    "Дружба может быть просто хорошей, без мистики."
                ),
                "work": (
                    "• Яркого «мы с судьбой, тащим стартап» тут нет — и это нормально. "
                    "Можете быть эффективными просто потому что роли совпали."
                ),
            },
            "en": {
                "love": (
                    "• No loud «we're fated» marker — and that's fine. "
                    "You can still go deep because you fit, not because a chart said so."
                ),
                "friendship": (
                    "• No loud «fated friends forever» marker — and that's fine. "
                    "Friendship can be good without mysticism."
                ),
                "work": (
                    "• No loud «fated co-founders» marker — and that's fine. "
                    "You can be effective because roles align."
                ),
            },
        }
        lines.append(no_destined[lang][mode_key])
    else:
        lines.append(
            f"• Есть линия «не просто случайность»: "
            f"{_format_plain_karmic_link(locale, analysis.best_destined)}."
            if lang == "ru"
            else f"• A «not just chance» thread: "
            f"{_format_plain_karmic_link(locale, analysis.best_destined)}."
        )
        felt_lines = {
            "ru": {
                "love": "• Ощущение, что встретились с задачей — не всегда легко, но живо.",
                "friendship": "• Ощущение, что дружба «не просто так» — иногда бесит, но не скучно.",
                "work": "• Ощущение, что вместе «не просто так» — иногда напряжно, но результат есть.",
            },
            "en": {
                "love": "• A sense you met with a task — not always easy, but alive.",
                "friendship": "• A sense the friendship isn't random — sometimes annoying, never boring.",
                "work": "• A sense you're together for a reason — tense sometimes, but productive.",
            },
        }
        lines.append(felt_lines[lang][mode_key])
        for link in analysis.destined[1:2]:
            lines.append(f"• ↳ {_format_plain_karmic_link(locale, link).capitalize()}.")

    lines.append("")
    if lang == "ru":
        lesson_headers = {
            "love": "🎯 Уроки, которые тянут на честность",
            "friendship": "🎯 Уроки, которые тянут на «давай поговорим»",
            "work": "🎯 Уроки, которые тянут на нормальный brief",
        }
        lines.append(lesson_headers[mode_key])
        lesson_intros = {
            "love": (
                "Не обязательно «карма прошлых жизней» — скорее темы, "
                "которые жизнь будет повторять, пока не научитесь по-новому."
            ),
            "friendship": (
                "Не обязательно «карма» — скорее темы, которые дружба будет повторять, "
                "пока не научитесь говорить «мне обидно» без passive-aggressive."
            ),
            "work": (
                "Не обязательно «карма» — скорее темы, которые проект будет повторять, "
                "пока не научитесь фиксировать «кто за что отвечает»."
            ),
        }
        lines.append(lesson_intros[mode_key])
    else:
        lesson_headers = {
            "love": "🎯 Lessons that ask for honesty",
            "friendship": "🎯 Lessons that ask for «let's talk»",
            "work": "🎯 Lessons that ask for a clear brief",
        }
        lines.append(lesson_headers[mode_key])
        lesson_intros = {
            "love": (
                "Not necessarily «past-life karma» — more like themes life repeats "
                "until you respond differently."
            ),
            "friendship": (
                "Not necessarily «karma» — themes friendship repeats "
                "until you can say «that hurt» without passive-aggressive."
            ),
            "work": (
                "Not necessarily «karma» — themes the project repeats "
                "until you write down «who owns what»."
            ),
        }
        lines.append(lesson_intros[mode_key])

    if not analysis.has_karmic_task:
        soft_lines = {
            "ru": {
                "love": "• Громких сюрпризов не видно — уроки мягче или проявятся через быт.",
                "friendship": "• Громких сюрпризов не видно — дружба может быть просто спокойной.",
                "work": "• Громких сюрпризов не видно — рабочая связка может быть ровной.",
            },
            "en": {
                "love": "• No loud surprises here — lessons are softer or show up in daily life.",
                "friendship": "• No loud surprises — friendship can stay calm and steady.",
                "work": "• No loud surprises — the work link can stay steady.",
            },
        }
        lines.append(soft_lines[lang][mode_key])
    else:
        for link in analysis.karmic_tasks[:3]:
            lines.append(
                f"• {_format_plain_karmic_link(locale, link).capitalize()}. "
                f"{_plain_task_interpretation(locale, link)}"
            )
        if len(analysis.karmic_tasks) > 3:
            extra = len(analysis.karmic_tasks) - 3
            extra_lines = {
                "ru": {
                    "love": f"• … и ещё {extra} похожих тем — не игнорируйте, но и не драматизируйте.",
                    "friendship": f"• … и ещё {extra} похожих тем — не копите, но и не устраивайте триллер.",
                    "work": f"• … и ещё {extra} похожих тем — зафиксируйте в задачах, не в passive-aggressive.",
                },
                "en": {
                    "love": f"• … plus {extra} similar themes — notice them, don't doom-scroll your bond.",
                    "friendship": f"• … plus {extra} similar themes — notice them, don't turn it into a drama.",
                    "work": f"• … plus {extra} similar themes — put them in tasks, not in side-eye on calls.",
                },
            }
            lines.append(extra_lines[lang][mode_key])

    return "\n".join(lines)


def _task_interpretation(locale: str, link: KarmicLink) -> str:
    lang = _lang(locale)
    if link.aspect in HARMONIOUS:
        if lang == "ru":
            return "узел поддерживает рост — задача проживается мягче, но ощутимо."
        return "the node supports growth — the lesson is noticeable but easier to integrate."
    if lang == "ru":
        return "узел создаёт напряжение — отношения тянут к переменам и честности."
    return "the node adds tension — the bond pushes change and honesty."


def format_synastry_step8_section(
    locale: str,
    analysis: KarmicAnalysis,
    *,
    style: str = "terms",
    mode: str = "love",
) -> str:
    from app.synastry_style import use_synastry_terms

    if not use_synastry_terms(style):
        return _format_plain_karma_section(locale, analysis, mode=mode)

    lang = _lang(locale)
    lines: list[str] = []

    if lang == "ru":
        lines.append("🪷 Шаг 8. Кармические показатели")
        lines.append(
            "Лунные узлы: Раху (Северный) и Кету (Южный) — темы кармы и "
            "направления роста в паре (тропик, True Node)."
        )
    else:
        lines.append("🪷 Step 8. Karmic indicators")
        lines.append(
            "Lunar nodes: Rahu (North) and Ketu (South) — karmic themes and "
            "growth direction (tropical True Node)."
        )

    lines.append("")
    if lang == "ru":
        lines.append("✨ «Предназначенная» связь")
        lines.append(
            "Северный узел (Раху) одного в соединении с Солнцем или Луной другого."
        )
    else:
        lines.append("✨ “Destined” bond")
        lines.append(
            "One partner's North Node (Rahu) conjunct the other's Sun or Moon."
        )

    if analysis.best_destined is None:
        lines.append(
            "• Точного соединения Раху↔Солнце/Луна не найдено — связь не обязана быть «судьбой», "
            "но может быть глубокой по другим показателям."
            if lang == "ru"
            else "• No exact Rahu↔Sun/Moon conjunction — the bond needn't be “fated”, "
            "but can still run deep through other factors."
        )
    else:
        lines.append(
            f"• {_format_link_line(locale, analysis.best_destined, style=style).capitalize()}."
        )
        if lang == "ru":
            lines.append(
                "• Признак сильной, «узловой» связи — будто вы встретились не случайно."
            )
        else:
            lines.append(
                "• A strong nodal bond — as if the meeting carries a sense of purpose."
            )
        for link in analysis.destined[1:2]:
            lines.append(f"• ↳ {_format_link_line(locale, link, style=style).capitalize()}.")

    lines.append("")
    if lang == "ru":
        lines.append("🎯 Кармическая задача")
        lines.append(
            "Узлы одного в аспекте к личным планетам другого — "
            "отношения несут урок и задачу."
        )
    else:
        lines.append("🎯 Karmic task")
        lines.append(
            "One partner's nodes aspecting the other's personal planets — "
            "the relationship carries a lesson."
        )

    if not analysis.has_karmic_task:
        lines.append(
            "• Ярких узловых аспектов к личным планетам нет — кармический урок мягче или "
            "раскрывается через другие шаги."
            if lang == "ru"
            else "• No strong nodal aspects to personal planets — the karmic lesson is lighter "
            "or shows through other steps."
        )
    else:
        for link in analysis.karmic_tasks[:3]:
            lines.append(f"• {_format_link_line(locale, link, style=style).capitalize()}.")
            lines.append(f"  ↳ {_task_interpretation(locale, link)}")
        if len(analysis.karmic_tasks) > 3:
            extra = len(analysis.karmic_tasks) - 3
            if lang == "ru":
                lines.append(f"• … и ещё {extra} узловых связей.")
            else:
                lines.append(f"• … plus {extra} more nodal links.")

    return "\n".join(lines)
