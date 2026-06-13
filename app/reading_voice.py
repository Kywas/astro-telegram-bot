"""Engaging, human-sounding copy for compatibility readings."""
from __future__ import annotations

import re

from app.text_format import b, h, p


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _mode_key(mode: str) -> str:
    return mode if mode in {"love", "friendship", "work"} else "love"


def _score_tier(score: int) -> str:
    if score >= 85:
        return "high"
    if score >= 70:
        return "good"
    if score >= 55:
        return "mid"
    return "low"


def compat_score_hook(locale: str, score: int, mode: str, *, style: str = "plain") -> str:
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    tier = _score_tier(score)
    if style != "plain":
        if lang == "ru":
            return (
                f"Итоговая оценка {score}/100 (Swiss Ephemeris). "
                f"Ниже — разбор по шагам синастрии."
            )
        return (
            f"Composite score {score}/100 (Swiss Ephemeris). "
            f"Step-by-step synastry breakdown below."
        )

    hooks = {
        "ru": {
            "love": {
                "high": "Оценка высокая — романтически вы друг другу реально зашли. Разложу по полочкам, без занудства.",
                "good": "Картина тёплая — есть на что опереться в паре. Дальше по деталям, коротко и по делу.",
                "mid": "Не ромком и не мелодрама — как в жизни. Сейчас разберу, где тянет и где лучше поговорить.",
                "low": "Честно: в любви не всё просто. Но если дочитаешь — станет яснее, куда смотреть и где не додумывать.",
            },
            "friendship": {
                "high": "Оценка высокая — как друзья вы складываетесь легко. Разберу, почему так и что беречь.",
                "good": "Картина дружеская, ровная — есть опора. Дальше по деталям, без лишней философии.",
                "mid": "Не идеальная дружба из фильма, но живая. Сейчас разберу, где легко болтать, а где терпение.",
                "low": "Честно: дружба потребует усилий. Зато картина честная — лучше знать, чем додумывать молча.",
            },
            "work": {
                "high": "Оценка высокая — как коллеги вы в ударе. Разложу, кто за что силён и где не мешать друг другу.",
                "good": "Картина рабочая, продуктивная — есть на что опереться. Дальше по деталям, по делу.",
                "mid": "Не dream team, но и не офисный кошмар. Сейчас разберу роли, темп и где договориться.",
                "low": "Честно: в работе будет тереть. Зато ясно, где распределить задачи и не ждать телепатии.",
            },
        },
        "en": {
            "love": {
                "high": "High score — romantically you genuinely click. I'll break it down without the lecture.",
                "good": "Warm picture — plenty to lean on as a couple. Details ahead, kept short.",
                "mid": "Not a rom-com, not a soap — real life. I'll unpack pull and where to talk.",
                "low": "Straight talk: love won't be effortless. Read through and you'll see where to focus.",
            },
            "friendship": {
                "high": "High score — as friends you fit easily. I'll explain why and what's worth keeping.",
                "good": "Solid friendship baseline — something to lean on. Details ahead, no fluff.",
                "mid": "Not a movie friendship, but a real one. I'll show where chat flows and where patience helps.",
                "low": "Straight talk: friendship will take effort. At least the picture is honest.",
            },
            "work": {
                "high": "High score — strong as colleagues. I'll map strengths and where not to step on toes.",
                "good": "Productive picture — plenty to build on. Details ahead, businesslike.",
                "mid": "Not a dream team, not office hell. I'll unpack roles, pace, and where to agree.",
                "low": "Straight talk: work will rub. Clear where to split tasks and skip telepathy.",
            },
        },
    }
    return hooks[lang][mode_key][tier]


def compat_mode_intro(locale: str, mode: str, score: int, *, style: str = "plain") -> str:
    """Bold intro block — different story for love, friendship, and work."""
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    tier = _score_tier(score)
    if style != "plain":
        labels = {
            "ru": {"love": "💕 Любовь", "friendship": "🤝 Дружба", "work": "💼 Работа"},
            "en": {"love": "💕 Love", "friendship": "🤝 Friendship", "work": "💼 Work"},
        }
        if lang == "ru":
            return p(
                b(f"Режим: {labels[lang][mode_key]}"),
                h("Разбор ниже учитывает выбранную сферу — веса планет и акценты отличаются от других режимов."),
            )
        return p(
            b(f"Mode: {labels[lang][mode_key]}"),
            h("The breakdown below follows this sphere — planet weights and focus differ from other modes."),
        )

    content = {
        "ru": {
            "love": {
                "title": "💕 Любовь — про «мы на двоих»",
                "lead": (
                    "Смотрим не резюме, а химию: тянет ли, умеете ли говорить о чувствах "
                    "и не превращаетесь ли в игру «угадай, что я имел в виду»."
                ),
                "high": "По ощущениям — вы на одной волне. Главное не испортить это молчанием и «само догадается».",
                "good": "Между вами есть тепло — не идеальное, но настоящее. Остальное — привычки и честные разговоры.",
                "mid": "Притяжение есть, но и места, где легко не понять друг друга. Намёки тут не работают — только слова.",
                "low": "Легко не будет — зато картина честная. Лучше знать заранее, чем играть в телепатию до взрыва.",
            },
            "friendship": {
                "title": "🤝 Дружба — без романтики и drama",
                "lead": (
                    "Про то, можно ли болтать, молчать рядом и не чувствовать себя на экзамене. "
                    "Без «кто кому что должен» — просто: выручаете ли друг друга."
                ),
                "high": "Складывается естественно — как будто давно знакомы. Главное — не пропадать на полгода без «привет».",
                "good": "Дружеская опора есть. Разный темп сообщений — норма, если честно сказать «мне удобнее так».",
                "mid": "Подружиться можно, но придётся договариваться о темпе и ожиданиях. Это не слабость — это взрослость.",
                "low": "Дружба потребует усилий — не все сразу «свои». Зато видно, где не додумывать и где спросить прямо.",
            },
            "work": {
                "title": "💼 Работа — про задачи, а не про душу",
                "lead": (
                    "Коллеги, партнёры, проекты: кто тащит дедлайны, кто генерирует идеи "
                    "и где легко превратиться в «а я думал, ты сам»."
                ),
                "high": "Как команда — огонь. Главное — не смешивать роли и не делать всё «на энтузиазме без договорённости».",
                "good": "Работать вместе можно продуктивно. Распределите зоны — и меньше нервов на понятиях.",
                "mid": "Подходы разные — это не приговор, а повод проговорить роли. Иначе будет вечный «я так не понял».",
                "low": "Будет тереть — зато ясно, где нужны письменные договорённости, а не надежда на телепатию.",
            },
        },
        "en": {
            "love": {
                "title": "💕 Love — the «two of us» lens",
                "lead": (
                    "Not résumés — chemistry: pull, talking about feelings, "
                    "and not playing «guess what I meant»."
                ),
                "high": "You're in sync. Don't ruin it with silence and «they'll figure it out».",
                "good": "There's real warmth — not perfect, but there. Habits and honest talks do the rest.",
                "mid": "Pull exists, and spots to misread each other. Hints fail — use words.",
                "low": "Won't be effortless — honest picture. Better to know than telepath until blow-up.",
            },
            "friendship": {
                "title": "🤝 Friendship — no romance, less drama",
                "lead": (
                    "Can you chat, sit in silence, and not feel tested? "
                    "Not «who owes whom» — do you actually show up for each other."
                ),
                "high": "Flows naturally — like you've known each other. Don't vanish for six months without «hey».",
                "good": "Solid friend energy. Different text pace is fine if you say «this works for me».",
                "mid": "Friendship works — negotiate pace and expectations. That's adulting, not weakness.",
                "low": "Takes effort — not instant «your people». At least you see where to ask directly.",
            },
            "work": {
                "title": "💼 Work — tasks, not soul-searching",
                "lead": (
                    "Colleagues and projects: who hits deadlines, who sparks ideas, "
                    "and where «I thought you had it» lives."
                ),
                "high": "Strong as a team. Don't blur roles or run on vibes without agreements.",
                "good": "Productive together. Split zones — fewer nerves over assumptions.",
                "mid": "Different styles — not a verdict, a reason to define roles. Or endless «that's not what I meant».",
                "low": "Friction ahead — clear where you need written agreements, not telepathy.",
            },
        },
    }
    block = content[lang][mode_key]
    return p(b(block["title"]), h(block["lead"]), h(block[tier]))


def compat_mode_menu_guide(locale: str, mode: str, *, style: str = "plain") -> str:
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    if style != "plain":
        if lang == "ru":
            return "Разбор по 6 блокам — акценты зависят от выбранного режима."
        return "Six blocks — emphasis shifts with the mode you picked."
    guides = {
        "ru": {
            "love": "6 тем — как сезоны ромкома. Можно начать с любой, не обязательно с «кто вы».",
            "friendship": "6 тем — как разделы в групповом чате. Заходи с любой, главное — без фальши.",
            "work": "6 тем — как пункты в brief. Начни с того, что важно для вашей задачи.",
        },
        "en": {
            "love": "Six themes — rom-com seasons. Start anywhere, not necessarily «who you are».",
            "friendship": "Six themes — group-chat sections. Pick any, keep it real.",
            "work": "Six themes — brief bullets. Start with what matters for your project.",
        },
    }
    return guides[lang][mode_key]


def theme_menu_teaser(locale: str, theme_key: str, *, style: str = "plain", mode: str = "love") -> str:
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    if style != "plain":
        teasers = {
            "ru": {
                "overview": "Солнечные знаки, стихии, общий фон пары.",
                "attraction": "ASC/DSC, аспекты синастрии, Луна и Венера.",
                "bond": "Композитная карта, наложение домов, прогрессии.",
                "depth": "Лилит, Селена, кармические узлы, транзиты.",
                "symbols": "Число союза, расклад Таро на пару.",
                "result": "Сводная таблица +1/−1, рекомендации.",
            },
            "en": {
                "overview": "Sun signs, elements, pair baseline.",
                "attraction": "ASC/DSC, synastry aspects, Moon and Venus.",
                "bond": "Composite chart, house overlay, progressions.",
                "depth": "Lilith, Selena, lunar nodes, transits.",
                "symbols": "Union number, couple Tarot spread.",
                "result": "+1/−1 scorecard and recommendations.",
            },
        }
        return teasers[lang].get(theme_key, "")
    teasers = {
        "ru": {
            "love": {
                "overview": "Кто вы как пара и совпадает ли романтический темп.",
                "attraction": "Что тянет друг к другу — и где может укусить.",
                "bond": "Как живёте «мы», а не только «я и ты».",
                "depth": "То, о чём на первом свидании молчат (а зря).",
                "symbols": "Числа и карты — взгляд сбоку, иногда в точку.",
                "result": "Финал: одна мысль про вашу пару.",
            },
            "friendship": {
                "overview": "Вы как друзья — на одной ли волне без романтики.",
                "attraction": "Понимаете ли друг друга с полуслова — или объяснять три раза.",
                "bond": "Насколько можно на друг друга положиться — не только в хорошие дни.",
                "depth": "Где дружба может зацепить — обиды, ревность, дистанция.",
                "symbols": "Числа и карты — для любопытных, не для приговора.",
                "result": "Финал: стоит ли вкладываться в эту дружбу.",
            },
            "work": {
                "overview": "Вы как команда — кто за что и на одной ли скорости.",
                "attraction": "Как договариваетесь — или где «я так не понял».",
                "bond": "Общая цель и роли — кто тащит, кто генерирует.",
                "depth": "Где буксуете: дедлайны, контроль, разные стандарты.",
                "symbols": "Числа и карты — бонус, не KPI.",
                "result": "Финал: работать вместе — да или «лучше раздельно».",
            },
        },
        "en": {
            "love": {
                "overview": "Who you are as a couple and whether romantic rhythms match.",
                "attraction": "What pulls you in — and what might nip.",
                "bond": "Daily «we», not just «me and you».",
                "depth": "What people feel but rarely say on date one.",
                "symbols": "Numbers and cards — sideways glance, sometimes spot-on.",
                "result": "Wrap-up: one thought about your pair.",
            },
            "friendship": {
                "overview": "You as friends — same wavelength without romance.",
                "attraction": "Half-word understanding — or explaining three times.",
                "bond": "How much you can count on each other — not only on good days.",
                "depth": "Where friendship snags — hurt, jealousy, distance.",
                "symbols": "Numbers and cards — for the curious, not a verdict.",
                "result": "Wrap-up: worth investing in this friendship.",
            },
            "work": {
                "overview": "You as a team — who does what and same speed or not.",
                "attraction": "How you align — or where «that's not what I meant» lives.",
                "bond": "Shared goal and roles — who delivers, who sparks.",
                "depth": "Where you stall — deadlines, control, different standards.",
                "symbols": "Numbers and cards — bonus, not KPI.",
                "result": "Wrap-up: work together — yes or «better apart».",
            },
        },
    }
    return teasers[lang][mode_key].get(theme_key, "")


def theme_opening_hook(locale: str, theme_key: str, mode: str, score: int, *, style: str = "plain") -> str:
    lang = _lang(locale)
    if style != "plain":
        hooks = {
            "ru": {
                "overview": "Базовый уровень: знаки Солнца и баланс стихий.",
                "attraction": "ASC/DSC и ключевые аспекты синастрии.",
                "bond": "Композит, дома и прогрессии — структура союза.",
                "depth": "Кармические и транзитные маркеры.",
                "symbols": "Нумерология и Таро — дополнительный слой.",
                "result": "Сводка по всем шагам и итоговая рекомендация.",
            },
            "en": {
                "overview": "Baseline: Sun signs and element balance.",
                "attraction": "ASC/DSC and key synastry aspects.",
                "bond": "Composite, houses, and progressions — union structure.",
                "depth": "Karmic and transit markers.",
                "symbols": "Numerology and Tarot — an extra layer.",
                "result": "Full step summary and final recommendation.",
            },
        }
        return hooks[lang].get(theme_key, "")
    hooks = {
        "ru": {
            "love": {
                "overview": "Начнём с простого: кто вы как пара и на одной ли романтической волне.",
                "attraction": "Самое живое — что вас реально цепляет (и где щекотит).",
                "bond": "Теперь быт вдвоём: привычки, «мы» и куда это катится.",
                "depth": "Поглубже — про то, что обычно не говорят вслух на первом свидании.",
                "symbols": "Немного магии: числа и карты — не закон, но иногда попадают.",
                "result": "Финал про любовь. Одна понятная мысль — без воды.",
            },
            "friendship": {
                "overview": "Начнём с простого: вы как друзья — совпадает ли темп и юмор.",
                "attraction": "Самое живое — как вы общаетесь: легко болтать или нужны объяснения.",
                "bond": "Можно ли на вас положиться — не только когда всё весело.",
                "depth": "Честно — где дружба может зацепить: дистанция, обиды, «ты пропал».",
                "symbols": "Немного магии для любопытных — не замена разговору.",
                "result": "Финал про дружбу. Одна мысль — стоит ли беречь контакт.",
            },
            "work": {
                "overview": "Начнём с простого: вы как команда — кто за что и на одной ли скорости.",
                "attraction": "Самое живое — как договариваетесь и понимаете задачи.",
                "bond": "Общая цель: «мы в одной лодке» или «каждый сам за себя».",
                "depth": "Где буксуете — дедлайны, контроль, разные стандарты качества.",
                "symbols": "Бонус для любопытных — KPI всё равно в переговорах.",
                "result": "Финал про работу. Одна мысль — стоит ли тащить проект вместе.",
            },
        },
        "en": {
            "love": {
                "overview": "Starting simple — who you are as a couple and romantic sync.",
                "attraction": "The lively bit — what actually pulls you together.",
                "bond": "Daily life as a couple — routines, «we», and where it's heading.",
                "depth": "Getting honest — what rarely gets said on a first date.",
                "symbols": "A little magic — numbers and cards aren't law, but sometimes nail it.",
                "result": "Love wrap-up. One clear thought — no fluff.",
            },
            "friendship": {
                "overview": "Starting simple — you as friends, same pace and humor or not.",
                "attraction": "The lively bit — easy chat or need three explanations.",
                "bond": "Can you count on each other — not only when it's fun.",
                "depth": "Honest — where friendship snags: distance, hurt, «you ghosted».",
                "symbols": "A little magic for the curious — not a substitute for talking.",
                "result": "Friendship wrap-up. One thought — worth keeping contact.",
            },
            "work": {
                "overview": "Starting simple — you as a team, roles and speed.",
                "attraction": "The lively bit — how you align on tasks and talk.",
                "bond": "Shared goal: «same boat» or «everyone for themselves».",
                "depth": "Where you stall — deadlines, control, different quality bars.",
                "symbols": "Bonus for the curious — KPIs still live in negotiations.",
                "result": "Work wrap-up. One thought — worth the project together.",
            },
        },
    }
    mode_key = _mode_key(mode)
    base = hooks[lang][mode_key].get(theme_key, "")
    if theme_key == "result" and score >= 75 and lang == "ru":
        suffix = {
            "love": " Если совсем коротко — романтически складывается неплохо.",
            "friendship": " Если совсем коротко — дружить можно без героизма.",
            "work": " Если совсем коротко — как коллеги вы в плюсе.",
        }
        return f"{base}{suffix[mode_key]}"
    if theme_key == "result" and score >= 75:
        suffix = {
            "love": " Short version — romantically looking decent.",
            "friendship": " Short version — friendship works without heroics.",
            "work": " Short version — solid as colleagues.",
        }
        return f"{base}{suffix[mode_key]}"
    return base


def theme_next_teaser(locale: str, next_title: str, next_key: str, *, style: str = "plain", mode: str = "love") -> str:
    lang = _lang(locale)
    hint = theme_menu_teaser(locale, next_key, style=style, mode=mode)
    if style != "plain":
        if lang == "ru":
            return f"Далее: «{next_title}». {hint}"
        return f"Next: «{next_title}». {hint}"
    if lang == "ru":
        return f"Не устал? Дальше «{next_title}» — {hint.lower()}"
    return f"Still with me? Next «{next_title}» — {hint.lower()}"


def menu_pick_cta(locale: str, *, style: str = "plain", mode: str = "love") -> str:
    if style != "plain":
        if _lang(locale) == "ru":
            return "Выберите блок — внутри шаги синастрии с терминами и маркерами карты."
        return "Pick a block — each contains synastry steps with chart markers."
    mode_key = _mode_key(mode)
    ctas = {
        "ru": {
            "love": "6 тем — как сезоны ромкома. Можно не смотреть все серии подряд.",
            "friendship": "6 тем — как разделы в групповом чате. Заходи с любой, главное — без фальши.",
            "work": "6 тем — как пункты в brief. Начни с важного для вашей задачи.",
        },
        "en": {
            "love": "Six themes — rom-com seasons. You don't have to binge every episode.",
            "friendship": "Six themes — group-chat sections. Start anywhere, keep it real.",
            "work": "Six themes — brief bullets. Start with what matters for the project.",
        },
    }
    return ctas[_lang(locale)][mode_key]


def compatibility_summary_engaging(
    locale: str,
    score: int,
    *,
    style: str = "terms",
    mode: str = "love",
) -> str:
    plain = style == "plain"
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    if lang == "ru":
        if plain:
            summaries = {
                "love": {
                    "high": "Короче: романтически вы друг другу очень подходите. Берегите — и говорите вслух, не телепатией.",
                    "good": "Короче: в паре много опоры. На это можно опираться, а не только на «само как-нибудь».",
                    "mid": "Короче: не идеальная любовь, но при желании можно выстроить. Главное — не молчать.",
                    "low": "Короче: в романтике будет непросто. Зато картина честная — лучше знать заранее.",
                },
                "friendship": {
                    "high": "Короче: как друзья — огонь. Не пропадайте на полгода без «привет».",
                    "good": "Короче: дружеская опора есть. Разный темп сообщений — норма, если честно сказать.",
                    "mid": "Короче: подружиться можно, но договариваться о темпе — не слабость.",
                    "low": "Короче: дружба потребует усилий. Зато видно, где спросить прямо.",
                },
                "work": {
                    "high": "Короче: как коллеги — в ударе. Роли распределите — и меньше «я так не понял».",
                    "good": "Короче: работать вместе продуктивно. Договорённости важнее энтузиазма.",
                    "mid": "Короче: не dream team, но и не кошмар. Проговорите роли — и легче.",
                    "low": "Короче: в работе будет тереть. Письменные договорённости — ваш друг.",
                },
            }
            return summaries[mode_key][_score_tier(score)]
        if score >= 85:
            return "Общий фон: очень высокая совместимость — сильная база для союза."
        if score >= 70:
            return "Общий фон: хорошая совместимость — много точек опоры."
        if score >= 55:
            return "Общий фон: смешанная картина — и гармония, и зоны роста."
        return "Общий фон: непростая связь — терпение и диалог обязательны."
    if plain:
        summaries = {
            "love": {
                "high": "Short version: romantically you fit really well. Hold onto that — say it out loud.",
                "good": "Short version: lots of support as a couple — something solid to lean on.",
                "mid": "Short version: not perfect love, but you can build something if you talk.",
                "low": "Short version: romance won't be easy — at least the picture is honest.",
            },
            "friendship": {
                "high": "Short version: great as friends. Don't ghost for six months.",
                "good": "Short version: solid friend energy. Different text pace is fine if you're honest.",
                "mid": "Short version: friendship works — negotiating pace isn't weakness.",
                "low": "Short version: friendship takes effort — at least you know where to ask directly.",
            },
            "work": {
                "high": "Short version: strong colleagues. Split roles — fewer «that's not what I meant».",
                "good": "Short version: productive together. Agreements beat vibes.",
                "mid": "Short version: not a dream team, not a nightmare. Define roles.",
                "low": "Short version: work will rub. Written agreements are your friend.",
            },
        }
        return summaries[mode_key][_score_tier(score)]
    if score >= 85:
        return "Overall: very high compatibility — a strong base for the bond."
    if score >= 70:
        return "Overall: good compatibility — many supportive links."
    if score >= 55:
        return "Overall: mixed picture — harmony and growth points together."
    return "Overall: challenging bond — patience and dialogue are essential."


_HUMANIZE_RU = (
    (r"^Итог:\s*", "Короче, "),
    (r"^В двух словах:\s*", "Короче, "),
    (r"простым языком", ""),
    (r"по-человечески", ""),
    (r"ниже —", "дальше —"),
    (r"ниже разберём", "сейчас разберу"),
    (r"имеет смысл", "можно"),
    (r"Подсказка:", "Кстати,"),
    (r"синастри\w*", "связь"),
    (r"композит\w*", "ваше «мы»"),
    (r"аспект\w*", "связь"),
    (r"стихи\w*", "тип темпа"),
    (r"натальн\w*", ""),
    (r"транзит\w*", "сейчас"),
    (r"прогресс\w*", "развитие"),
    (r"карм\w*", "урок"),
    (r"раху\b", "линия роста"),
    (r"кету\b", "старый сценарий"),
    (r"северный узел", "линия роста"),
    (r"южный узел", "старый сценарий"),
    (r"\bтрин\b", "легко"),
    (r"\bсекстил\w*", "мягко"),
    (r"\bквадрат\w*", "напряжённо"),
    (r"\bсоединени\w*", "сильно"),
    (r"\bоппозици\w*", "контрастно"),
    (r"личн\w* планет\w*", "важные темы"),
    (r"узлов\w*", "глубинные"),
    (r" — — ", " — "),
    (r"  +", " "),
)

_HUMANIZE_EN = (
    (r"^Bottom line:\s*", "Short version — "),
    (r"^In short:\s*", "Short version — "),
    (r"plain language", ""),
    (r"plain words", ""),
    (r"below —", "next —"),
    (r"below we", "I'll"),
    (r"Hint:", "By the way,"),
    (r"\bsynastr\w*", "bond"),
    (r"\bcomposite\b", "your «we»"),
    (r"\baspect\w*", "link"),
    (r"\belement\w*", "pace"),
    (r"\bnatal\b", ""),
    (r"\btransit\w*", "now"),
    (r"\bkarm\w*", "lesson"),
    (r"\brahu\b", "growth line"),
    (r"\betu\b", "old pattern"),
    (r"north node", "growth line"),
    (r"south node", "old pattern"),
    (r"\btrine\b", "easily"),
    (r"\bsextile\b", "gently"),
    (r"\bsquare\b", "tensely"),
    (r"\bconjunction\b", "strongly"),
    (r"\bopposition\b", "contrasts"),
    (r"personal planets?", "key themes"),
    (r"nodal\b", "deep"),
    (r" — — ", " — "),
    (r"  +", " "),
)


def humanize_compat_plain(text: str, locale: str) -> str:
    """Strip template-y phrasing and leftover jargon from plain compat text."""
    if not text.strip():
        return text
    table = _HUMANIZE_RU if _lang(locale) == "ru" else _HUMANIZE_EN
    result = text
    for pattern, replacement in table:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.MULTILINE)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()
