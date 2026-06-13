"""Structured natal Q&A for finance, karma, traits, lineage, health, purpose, dharma, travel, upaya, houses, popular."""
from __future__ import annotations

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import LAGNA_ESSENCE, _derive_summary, _house_theme, _lang, _list_to_prose, _pl
from app.natal_qa_common import (
    StructuredQaAnswer,
    dignity_note,
    lord_of,
    lord_of_house_note,
    make_brief,
    pick_markers,
    placement_label,
    planets_in_house,
    plain_area,
    rank_dignity,
    topic_frame,
)

_UPAYA = {
    "ru": {
        "SUN": "воскресенье, уважение к отцу, «Om Suryaya Namaha»",
        "MOON": "понедельник, забота о эмоциях, «Om Chandraya Namaha»",
        "MARS": "вторник, спорт без агрессии, «Om Mangalaya Namaha»",
        "MERCURY": "среда, обучение и ясная речь, «Om Budhaya Namaha»",
        "JUPITER": "четверг, наставники и щедрость, «Om Gurave Namaha»",
        "VENUS": "пятница, гармония и искусство, «Om Shukraya Namaha»",
        "SATURN": "суббота, дисциплина и служение, «Om Shanaye Namaha»",
        "RAHU": "суббота/среда, простота и дана",
        "KETU": "вторник/четверг, духовная практика, «Om Ketave Namaha»",
    },
    "en": {
        "SUN": "Sunday, respect for elders, «Om Suryaya Namaha»",
        "MOON": "Monday, emotional care, «Om Chandraya Namaha»",
        "MARS": "Tuesday, sport without aggression, «Om Mangalaya Namaha»",
        "MERCURY": "Wednesday, learning and clear speech, «Om Budhaya Namaha»",
        "JUPITER": "Thursday, teachers and generosity, «Om Gurave Namaha»",
        "VENUS": "Friday, harmony and art, «Om Shukraya Namaha»",
        "SATURN": "Saturday, discipline and service, «Om Shanaye Namaha»",
        "RAHU": "Saturday/Wednesday, simplicity and charity",
        "KETU": "Tuesday/Thursday, spiritual practice, «Om Ketave Namaha»",
    },
}

_GEM = {
    "ru": {
        "SUN": "рубин", "MOON": "жемчуг", "MARS": "красный коралл", "MERCURY": "изумруд",
        "JUPITER": "жёлтый сапфир", "VENUS": "алмаз", "SATURN": "синий сапфир",
        "RAHU": "гессонит", "KETU": "кошачий глаз",
    },
    "en": {
        "SUN": "ruby", "MOON": "pearl", "MARS": "red coral", "MERCURY": "emerald",
        "JUPITER": "yellow sapphire", "VENUS": "diamond", "SATURN": "blue sapphire",
        "RAHU": "hessonite", "KETU": "cat's eye",
    },
}


def _upaya(locale: str, key: str) -> str:
    lang = _lang(locale)
    return f"{_pl(locale, key)}: {_UPAYA[lang].get(key, '')}"


def _debilitated(chart: JyotishChart) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
    return [chart.planets[k] for k in order if chart.planets[k].dignity == "debilitated"]


def _strong(chart: JyotishChart) -> list[PlanetPlacement]:
    order = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN")
    return [chart.planets[k] for k in order if chart.planets[k].dignity in {"exalted", "own"}]


def _tense(chart: JyotishChart) -> list[PlanetPlacement]:
    seen: set[str] = set()
    out: list[PlanetPlacement] = []
    for pl in (*_debilitated(chart), chart.planets["SATURN"], chart.planets["RAHU"], chart.planets["MARS"]):
        if pl.key not in seen:
            seen.add(pl.key)
            out.append(pl)
    return out[:4]


def _venus_money(locale: str, venus: PlanetPlacement) -> str:
    lang = _lang(locale)
    sign = sign_label(locale, venus.sign)
    dig = dignity_note(locale, venus)
    if lang == "ru":
        tail = f" ({dig})" if dig else ""
        where = "в теме партнёрства" if venus.house == 7 else f"через {plain_area(locale, venus.house)}"
        return f"Венера в {sign}{tail}: тратишь и копишь {where}, когда чувствуешь качество и смысл"
    return f"Venus in {sign}: you spend/save via {plain_area(locale, venus.house)} when quality feels real"


def _jupiter_growth(locale: str, jupiter: PlanetPlacement) -> str:
    lang = _lang(locale)
    sign = sign_label(locale, jupiter.sign)
    if lang == "ru":
        return f"Юпитер в {sign}, {jupiter.house}-й дом — рост через {plain_area(locale, jupiter.house)}"
    return f"Jupiter in {sign}, house {jupiter.house} — growth through {plain_area(locale, jupiter.house)}"


# --- Finance ---

def _finance(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    venus, jupiter = chart.planets["VENUS"], chart.planets["JUPITER"]
    lord2, lord10, lord11 = lord_of(chart, 2), lord_of(chart, 10), lord_of(chart, 11)
    h2_sign = sign_label(locale, chart.house_signs[2])

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — по 2-му дому и Венере:", en="On «{topic}» — from house 2 and Venus:")
        body = f"{_venus_money(locale, venus)}. {_jupiter_growth(locale, jupiter)}. {lord_of_house_note(locale, chart, 2)}."
        if lang == "ru":
            practice = "Запиши три траты за неделю и отметь: «качество» или «привычка» — так увидишь свой денежный код."
        else:
            practice = "Log three expenses this week — mark «quality» or «habit» to see your money code."
        markers = (
            f"2-й дом · {h2_sign} · ценности и личные ресурсы" if lang == "ru"
            else f"2nd house · {h2_sign} · values and resources",
            placement_label(locale, venus, style=style, role="Венера" if lang == "ru" else "Venus"),
            placement_label(locale, lord2, style=style, role="Управитель 2-го" if lang == "ru" else "2nd lord"),
        )
    elif idx == 1:
        sun, saturn = chart.planets["SUN"], chart.planets["SATURN"]
        frame = topic_frame(locale, question, ru="На «{topic}» — 10-й дом и карьерная линия:", en="On «{topic}» — house 10 and career line:")
        packed = chart.house_planet_count.get(10, 0) >= 2
        if lang == "ru":
            extra = " 10-й насыщен — профессия судьбоносна." if packed else ""
            body = f"{lord_of_house_note(locale, chart, 10)}. Солнце: {plain_area(locale, sun.house)}; Сатурн: {plain_area(locale, saturn.house)}.{extra}"
            practice = "Выбери одно действие на месяц в сторону реализации — маленький, но конкретный шаг."
        else:
            extra = " Packed 10th — profession is fated." if packed else ""
            body = f"{lord_of_house_note(locale, chart, 10)}. Sun: {plain_area(locale, sun.house)}; Saturn: {plain_area(locale, saturn.house)}.{extra}"
            practice = "Pick one concrete career step this month."
        markers = pick_markers(locale, [lord10, sun, saturn], style=style, roles=("10-й" if lang == "ru" else "10th", "Солнце" if lang == "ru" else "Sun", "Сатурн" if lang == "ru" else "Saturn"))
    elif idx == 2:
        mars, rahu = chart.planets["MARS"], chart.planets["RAHU"]
        in5, in8 = planets_in_house(chart, 5), planets_in_house(chart, 8)
        frame = topic_frame(locale, question, ru="На «{topic}» — 5-й и 8-й дома, риск:", en="On «{topic}» — houses 5 and 8, risk:")
        risk = ""
        if mars.dignity == "debilitated":
            risk = " Марс ослаблен — импульсивные ставки опаснее обычного." if lang == "ru" else " Weak Mars — impulsive bets are riskier."
        body = f"5-й ({sign_label(locale, chart.house_signs[5])}) — спекуляция; 8-й ({sign_label(locale, chart.house_signs[8])}) — чужие ресурсы.{risk} Раху в {rahu.house}-м усиливает нестандартные ставки."
        practice = "Не вкладывай «последнее» — только сумму, потерю которой переживёшь спокойно." if lang == "ru" else "Never invest «last money» — only what you can lose calmly."
        pls = (in5 + in8 + [mars])[:3] or [lord_of(chart, 5)]
        markers = pick_markers(locale, pls, style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="На «{topic}» — 2-й, 11-й и Юпитер:", en="On «{topic}» — houses 2, 11, Jupiter:")
        body = f"{lord_of_house_note(locale, chart, 2)} {lord_of_house_note(locale, chart, 11)} {_jupiter_growth(locale, jupiter)}."
        practice = "Отметь, откуда реально приходил доход за год — карта про каналы, не про «удачу»." if lang == "ru" else "Note where income actually came from this year."
        markers = pick_markers(locale, [lord2, lord11, jupiter], style=style)
    else:
        saturn, rahu, mars = chart.planets["SATURN"], chart.planets["RAHU"], chart.planets["MARS"]
        frame = topic_frame(locale, question, ru="Что мешает («{topic}») — финансовые узлы:", en="What blocks («{topic}») — financial knots:")
        parts = []
        if saturn.dignity != "exalted":
            parts.append(f"Сатурн в {saturn.house}-м — задержки и страх нехватки" if lang == "ru" else f"Saturn in house {saturn.house} — delays and scarcity fear")
        if rahu.house in {2, 8, 11, 12}:
            parts.append(f"Раху в {rahu.house}-м — переоценка «быстрого дохода»" if lang == "ru" else f"Rahu in house {rahu.house} — overestimating «easy money»")
        if mars.dignity == "debilitated":
            parts.append("Марс ослаблен — импульсивные траты" if lang == "ru" else "Weak Mars — impulsive spending")
        body = ". ".join(parts) or ("Смотри повторяющиеся финансовые сценарии." if lang == "ru" else "Watch repeating money patterns.")
        practice = "Перед крупной тратой — пауза 24 часа и вопрос «это ценность или импульс?»" if lang == "ru" else "Before big spending — 24h pause: value or impulse?"
        markers = pick_markers(locale, [saturn, rahu, mars], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Karma ---

def _karma(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    saturn, rahu, ketu, jupiter, moon = (
        chart.planets[k] for k in ("SATURN", "RAHU", "KETU", "JUPITER", "MOON")
    )
    lord8, lord12 = lord_of(chart, 8), lord_of(chart, 12)

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — 8-й и 12-й дома:", en="On «{topic}» — houses 8 and 12:")
        body = f"{lord_of_house_note(locale, chart, 8)} {lord_of_house_note(locale, chart, 12)} Сатурн в {saturn.house}-м — урок терпения и ответственности."
        practice = "Заметь один повторяющийся «тяжёлый» сценарий — это маркер кармы, не наказание." if lang == "ru" else "Notice one repeating heavy pattern — karmic marker, not punishment."
        markers = pick_markers(locale, [lord8, lord12, saturn], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — Кету, 12-й и Луна:", en="On «{topic}» — Ketu, house 12, Moon:")
        body = f"Кету в {ketu.house}-м — отпускание прошлого; Луна в {sign_label(locale, moon.sign)} — память души. {lord_of_house_note(locale, chart, 12)}"
        if lang == "en":
            body = f"Ketu in house {ketu.house} — releasing the past; Moon in {sign_label(locale, moon.sign)} — soul memory. {lord_of_house_note(locale, chart, 12)}"
        practice = "5 минут тишины в день — без телефона; так Луна и Кету «переваривают» прошлое." if lang == "ru" else "5 minutes of silence daily — no phone."
        markers = pick_markers(locale, [ketu, moon, lord12], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — Сатурн как учитель:", en="On «{topic}» — Saturn as teacher:")
        dig = dignity_note(locale, saturn)
        body = f"Сатурн в {sign_label(locale, saturn.sign)}, {saturn.house}-й дом ({dig}) — задержки не блок, а проверка зрелости."
        if lang == "en":
            body = f"Saturn in {sign_label(locale, saturn.sign)}, house {saturn.house} ({dig}) — delays test maturity."
        practice = "Не обходи «скучный» труд — Сатурн награждает за честное усилие." if lang == "ru" else "Don't skip «boring» work — Saturn rewards honest effort."
        markers = pick_markers(locale, [saturn], style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="На «{topic}» — ось Раху/Кету:", en="On «{topic}» — Rahu/Ketu axis:")
        body = f"Раху в {rahu.house}-м — тяга к новому в {plain_area(locale, rahu.house)}; Кету в {ketu.house}-м — отпустить старое в {plain_area(locale, ketu.house)}."
        if lang == "en":
            body = f"Rahu in house {rahu.house} — craving new in {plain_area(locale, rahu.house)}; Ketu in house {ketu.house} — release old there."
        practice = "Спроси: «это рост (Раху) или бегство (Кету)?» — перед резким решением." if lang == "ru" else "Ask: growth (Rahu) or escape (Ketu)? before sharp moves."
        markers = pick_markers(locale, [rahu, ketu, lord8], style=style)
    else:
        lord9 = lord_of(chart, 9)
        frame = topic_frame(locale, question, ru="На «{topic}» — осознанная карма через 9-й:", en="On «{topic}» — conscious karma via house 9:")
        body = f"{lord_of_house_note(locale, chart, 9)} {_jupiter_growth(locale, jupiter)}."
        practice = "Когда сценарий повторяется — измени реакцию на 10%, не ломая себя." if lang == "ru" else "When a pattern repeats — shift reaction 10%."
        markers = pick_markers(locale, [jupiter, lord9, moon], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Traits ---

def _traits(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, moon, mars, mercury = (chart.planets[k] for k in ("SUN", "MOON", "MARS", "MERCURY"))
    lagna = sign_label(locale, chart.lagna_sign)
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
    strengths, weaknesses, _, _ = _derive_summary(chart, lang)

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — Лагна и 1-й дом:", en="On «{topic}» — Lagna and house 1:")
        in1 = planets_in_house(chart, 1)
        extra = f" В 1-м: {', '.join(_pl(locale, p.key) for p in in1[:2])}." if in1 else ""
        body = f"Лагна {lagna} — {essence}.{extra} {lord_of_house_note(locale, chart, 1)}"
        if lang == "en":
            body = f"Lagna {lagna} — {essence}.{extra} {lord_of_house_note(locale, chart, 1)}"
        practice = "На неделю заметь, как входишь в новый контакт — так проявляется Лагна." if lang == "ru" else "For a week, notice how you enter new contact."
        lord1 = lord_of(chart, 1)
        markers = pick_markers(locale, [lord1, sun] + in1[:1], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — Солнце и Марс:", en="On «{topic}» — Sun and Mars:")
        body = f"Солнце в {sign_label(locale, sun.sign)} ({dignity_note(locale, sun) or 'нейтрально'}) — стержень; Марс в {sign_label(locale, mars.sign)}, {mars.house}-й — напор."
        if lang == "en":
            body = f"Sun in {sign_label(locale, sun.sign)} — core; Mars in {sign_label(locale, mars.sign)}, house {mars.house} — drive."
        practice = "Заметь, когда действуешь «на автомате» (Марс) vs «осознанно» (Солнце)." if lang == "ru" else "Notice autopilot Mars vs conscious Sun."
        markers = pick_markers(locale, [sun, mars], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — Луна и 4-й дом:", en="On «{topic}» — Moon and house 4:")
        body = f"Луна в {sign_label(locale, moon.sign)}, {moon.house}-й — эмоции через {plain_area(locale, moon.house)}. {lord_of_house_note(locale, chart, 4)}"
        if lang == "en":
            body = f"Moon in {sign_label(locale, moon.sign)}, house {moon.house}. {lord_of_house_note(locale, chart, 4)}"
        practice = "Вечером назови одну эмоцию дня — без оценки." if lang == "ru" else "Name one emotion of the day each evening."
        markers = pick_markers(locale, [moon, lord_of(chart, 4)], style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="На «{topic}» — 3-й дом, речь и действие:", en="On «{topic}» — house 3, speech and action:")
        body = f"Марс в {mars.house}-м + Меркурий в {sign_label(locale, mercury.sign)} — как рискуешь и говоришь. {lord_of_house_note(locale, chart, 3)}"
        if lang == "en":
            body = f"Mars in house {mars.house} + Mercury in {sign_label(locale, mercury.sign)}. {lord_of_house_note(locale, chart, 3)}"
        practice = "Перед спором — пауза на вдох; так 3-й дом работает мягче." if lang == "ru" else "Before an argument — one breath pause."
        markers = pick_markers(locale, [mars, mercury, lord_of(chart, 3)], style=style)
    else:
        frame = topic_frame(locale, question, ru="На «{topic}» — врождённые качества:", en="On «{topic}» — inborn qualities:")
        body = f"Сильные: {_list_to_prose(strengths, lang)}. Сложнее: {_list_to_prose(weaknesses, lang)}."
        if lang == "en":
            body = f"Strengths: {_list_to_prose(strengths, lang)}. Harder: {_list_to_prose(weaknesses, lang)}."
        practice = "Раз в неделю опирайся на одну сильную сторону сознательно." if lang == "ru" else "Once a week, lean on one strength consciously."
        markers = pick_markers(locale, [sun] + planets_in_house(chart, 1)[:2], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Lineage ---

def _lineage(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    moon, sun, jupiter = chart.planets["MOON"], chart.planets["SUN"], chart.planets["JUPITER"]
    lord4, lord9 = lord_of(chart, 4), lord_of(chart, 9)

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — 4-й дом и Луна (мать):", en="On «{topic}» — house 4 and Moon (mother):")
        body = f"Луна в {sign_label(locale, moon.sign)}, {moon.house}-й — эмоциональная связь с материнской темой. {lord_of_house_note(locale, chart, 4)}"
        if lang == "en":
            body = f"Moon in {sign_label(locale, moon.sign)}, house {moon.house}. {lord_of_house_note(locale, chart, 4)}"
        practice = "Вспомни один тёплый жест заботы из детства — это язык твоей Луны." if lang == "ru" else "Recall one warm care gesture from childhood."
        markers = pick_markers(locale, [moon, lord4] + planets_in_house(chart, 4)[:1], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — 9-й дом и Солнце (отец):", en="On «{topic}» — house 9 and Sun (father):")
        body = f"Солнце в {sign_label(locale, sun.sign)}, {sun.house}-й — образ отца и авторитет. {lord_of_house_note(locale, chart, 9)}"
        if lang == "en":
            body = f"Sun in {sign_label(locale, sun.sign)}, house {sun.house}. {lord_of_house_note(locale, chart, 9)}"
        practice = "Напиши, какой «закон» ты унаследовал от отца/старших — принимаешь или пересматриваешь?" if lang == "ru" else "Write one «law» inherited from father/elders."
        markers = pick_markers(locale, [sun, lord9] + planets_in_house(chart, 9)[:1], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — 4-й и 9-й дома (род):", en="On «{topic}» — houses 4 and 9 (lineage):")
        body = f"Корни: {lord_of_house_note(locale, chart, 4)} Традиция: {lord_of_house_note(locale, chart, 9)} {_jupiter_growth(locale, jupiter)}."
        practice = "Спроси старших одну историю рода — карта оживает через память." if lang == "ru" else "Ask an elder one lineage story."
        markers = pick_markers(locale, [lord4, lord9, jupiter], style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="На «{topic}» — семейная опора:", en="On «{topic}» — family support:")
        body = f"Луна + Юпитер: {plain_area(locale, moon.house)} и {plain_area(locale, jupiter.house)}. {lord_of_house_note(locale, chart, 4)}"
        practice = "Создай маленький ритуал «своих» — еда, звонок, фото." if lang == "ru" else "Create a small «your people» ritual."
        markers = pick_markers(locale, [moon, jupiter, lord4], style=style)
    else:
        saturn, rahu = chart.planets["SATURN"], chart.planets["RAHU"]
        frame = topic_frame(locale, question, ru="Что мешает («{topic}») — род и родители:", en="What blocks («{topic}») — lineage:")
        parts = []
        if saturn.house in {4, 9} or moon.house in {4, 9}:
            parts.append("Сатурн/Луна в 4/9 — дистанция или тяжёлая ответственность в теме родителей" if lang == "ru" else "Saturn/Moon in 4/9 — distance or heavy duty with parents")
        if rahu.house in {4, 9}:
            parts.append("Раху — идеализация или разрыв с традицией" if lang == "ru" else "Rahu — idealization or break with tradition")
        body = ". ".join(parts) or ("Смотри повторяющиеся сценарии с родителями." if lang == "ru" else "Watch repeating parent scripts.")
        practice = "Назови вслух одну обиду без обвинения — первый шаг к исцелению." if lang == "ru" else "Name one hurt aloud without blame."
        markers = pick_markers(locale, [moon, sun, saturn], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Health ---

def _health(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, moon, mars, saturn = (chart.planets[k] for k in ("SUN", "MOON", "MARS", "SATURN"))
    lord1, lord6 = lord_of(chart, 1), lord_of(chart, 6)

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — 1-й дом и витальность:", en="On «{topic}» — house 1 and vitality:")
        body = f"Солнце в {sign_label(locale, sun.sign)} — огонь; Марс в {sign_label(locale, mars.sign)}, {mars.house}-й — напор. {lord_of_house_note(locale, chart, 1)}"
        if lang == "en":
            body = f"Sun in {sign_label(locale, sun.sign)}; Mars in {sign_label(locale, mars.sign)}, house {mars.house}. {lord_of_house_note(locale, chart, 1)}"
        practice = "Утром 5 минут движения — не подвиг, а запуск энергии." if lang == "ru" else "5 minutes of movement each morning."
        markers = pick_markers(locale, [sun, mars, lord1], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — 6-й дом и режим:", en="On «{topic}» — house 6 and routine:")
        body = f"{lord_of_house_note(locale, chart, 6)} Сатурн в {saturn.house}-м — где легко игнорировать сигналы тела."
        if lang == "en":
            body = f"{lord_of_house_note(locale, chart, 6)} Saturn in house {saturn.house} — where body signals get ignored."
        practice = "Один стабильный режим: сон или вода — начни с малого." if lang == "ru" else "One stable habit: sleep or water."
        markers = pick_markers(locale, [lord6, saturn] + planets_in_house(chart, 6)[:1], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — восстановление:", en="On «{topic}» — recovery:")
        body = f"Луна в {moon.house}-м — отдых через {plain_area(locale, moon.house)}. {lord_of_house_note(locale, chart, 4)}"
        practice = "Без восстановления даже сильная карта выгорает — запланируй «ничего не делать»." if lang == "ru" else "Schedule real rest."
        markers = pick_markers(locale, [moon, lord_of(chart, 4)], style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="На «{topic}» — слабые места:", en="On «{topic}» — weak spots:")
        weak = [pl for pl in [mars, saturn] + planets_in_house(chart, 6) + planets_in_house(chart, 8) if pl.dignity == "debilitated" or pl.key in {"SATURN", "MARS"}][:3]
        body = " ".join(f"{_pl(locale, pl.key)} в {pl.house}-м ({dignity_note(locale, pl) or '—'})." for pl in weak)
        practice = "При симптомах — к врачу; карта про профилактику и режим, не диагноз." if lang == "ru" else "See a doctor for symptoms; chart is for prevention."
        markers = pick_markers(locale, weak, style=style)
    else:
        frame = topic_frame(locale, question, ru="На «{topic}» — забота о теле:", en="On «{topic}» — body care:")
        body = f"Баланс: Марс (нагрузка) в {mars.house}-м, Луна (отдых) в {moon.house}-м. {lord_of_house_note(locale, chart, 6)}"
        practice = "Неделя: умеренная нагрузка + один день полного отдыха." if lang == "ru" else "One week: moderate load + one full rest day."
        markers = pick_markers(locale, [lord6, mars, moon], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Purpose ---

def _purpose(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, jupiter, saturn, mercury, venus = (
        chart.planets[k] for k in ("SUN", "JUPITER", "SATURN", "MERCURY", "VENUS")
    )
    lagna = sign_label(locale, chart.lagna_sign)
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
    strengths, weaknesses, risks, _ = _derive_summary(chart, lang)
    lord9, lord10 = lord_of(chart, 9), lord_of(chart, 10)

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — 9-й дом и дхарма:", en="On «{topic}» — house 9 and dharma:")
        body = f"Лагна {lagna} — {essence}. {lord_of_house_note(locale, chart, 9)} {_jupiter_growth(locale, jupiter)}."
        practice = "Спроси: «что я делаю, когда теряю счёт времени?» — подсказка пути." if lang == "ru" else "Ask: what makes you lose track of time?"
        markers = pick_markers(locale, [lord9, sun, jupiter], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — таланты (5-й дом):", en="On «{topic}» — talents (house 5):")
        body = f"Меркурий в {sign_label(locale, mercury.sign)}, Венера в {sign_label(locale, venus.sign)}. Сильные: {_list_to_prose(strengths, lang)}."
        practice = "Выдели 2 часа в неделю на то, что даётся легко — без цели «заработать»." if lang == "ru" else "2 hours weekly on what comes easily."
        markers = pick_markers(locale, [mercury, venus, lord_of(chart, 5)], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — реализация (10-й):", en="On «{topic}» — realization (house 10):")
        packed = chart.house_planet_count.get(10, 0) >= 2
        extra = " 10-й насыщен — профессия судьбоносна." if packed and lang == "ru" else (" Packed 10th." if packed else "")
        body = f"{lord_of_house_note(locale, chart, 10)} Солнце + Сатурн: стержень и дисциплина.{extra}"
        practice = "Один шаг к реализации на месяц — конкретный, измеримый." if lang == "ru" else "One measurable realization step this month."
        markers = pick_markers(locale, [lord10, sun, saturn], style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="Что помогает и мешает («{topic}»):", en="What helps and blocks («{topic}»):")
        body = f"Помогает: {_list_to_prose(strengths, lang)}. Мешает: {_list_to_prose(weaknesses, lang)}. Риск: {risks}."
        if lang == "en":
            body = f"Helps: {_list_to_prose(strengths, lang)}. Blocks: {_list_to_prose(weaknesses, lang)}. Risk: {risks}."
        practice = "Убери одно действие, которое «съедает» реализацию — не добавляй новое." if lang == "ru" else "Remove one action that eats realization."
        markers = pick_markers(locale, [jupiter, saturn], style=style)
    else:
        frame = topic_frame(locale, question, ru="На «{topic}» — куда вести энергию:", en="On «{topic}» — where to direct energy:")
        if chart.stellium_house:
            h, s = chart.stellium_house, sign_label(locale, chart.stellium_sign)
            body = f"Стеллиум в {s}, {h}-й дом — {_house_theme(locale, h)}: сюда главная энергия." if lang == "ru" else f"Stellium in {s}, house {h} — main energy here."
        elif chart.strong_houses:
            h = chart.strong_houses[0]
            body = f"Ярче всего {h}-й дом ({_house_theme(locale, h)}) — {chart.house_planet_count[h]} планет(ы)." if lang == "ru" else f"House {h} stands out — {chart.house_planet_count[h]} planet(s)."
        else:
            body = lord_of_house_note(locale, chart, 9)
        practice = "Выбери одну сферу на квартал — не пять одновременно." if lang == "ru" else "Pick one sphere for the quarter."
        markers = pick_markers(locale, [lord9, lord10, sun], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Dharma ---

def _dharma(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, jupiter, ketu, moon = chart.planets["SUN"], chart.planets["JUPITER"], chart.planets["KETU"], chart.planets["MOON"]
    lord9, lord12, lord10 = lord_of(chart, 9), lord_of(chart, 12), lord_of(chart, 10)

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — духовный путь (9-й):", en="On «{topic}» — spiritual path (house 9):")
        body = f"{lord_of_house_note(locale, chart, 9)} Юпитер: {_jupiter_growth(locale, jupiter)}. Солнце в {sun.house}-м — внутренний свет."
        practice = "5 минут утром: «ради чего встаю?» — без ответа, просто вопрос." if lang == "ru" else "5 morning minutes: «what do I rise for?»"
        markers = pick_markers(locale, [jupiter, sun, lord9], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — вера и смысл:", en="On «{topic}» — faith and meaning:")
        body = f"9-й в {sign_label(locale, chart.house_signs[9])}. {lord_of_house_note(locale, chart, 9)}"
        practice = "Запиши три ценности, которые не продаются за деньги." if lang == "ru" else "Write three values not for sale."
        markers = pick_markers(locale, [jupiter, lord9, sun], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — медитация (12-й):", en="On «{topic}» — meditation (house 12):")
        body = f"Кету в {ketu.house}-м, Луна в {moon.house}-м. {lord_of_house_note(locale, chart, 12)}"
        practice = "10 минут тишины в день — таймер, без цели «просветиться»." if lang == "ru" else "10 minutes silence daily."
        markers = pick_markers(locale, [ketu, moon, lord12], style=style)
    elif idx == 3:
        frame = topic_frame(locale, question, ru="На «{topic}» — уроки Юпитера и Кету:", en="On «{topic}» — Jupiter and Ketu lessons:")
        body = f"Юпитер — рост через {plain_area(locale, jupiter.house)}; Кету — отпустить в {plain_area(locale, ketu.house)}."
        if lang == "en":
            body = f"Jupiter — grow via {plain_area(locale, jupiter.house)}; Ketu — release in {plain_area(locale, ketu.house)}."
        practice = "Одна вещь «отпустить» и одна «приумножить» на неделю." if lang == "ru" else "One thing to release, one to grow this week."
        markers = pick_markers(locale, [jupiter, ketu, lord9], style=style)
    else:
        frame = topic_frame(locale, question, ru="На «{topic}» — дхарма в быту:", en="On «{topic}» — daily dharma:")
        body = f"9-й (смысл): {lord_of_house_note(locale, chart, 9)} 10-й (дело): {lord_of_house_note(locale, chart, 10)}"
        practice = "Честность в одном маленьком деле сегодня — это дхарма, не только медитация." if lang == "ru" else "Honesty in one small deed today."
        markers = pick_markers(locale, [lord9, lord10, jupiter], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Travel ---

def _travel(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    rahu, jupiter, moon = chart.planets["RAHU"], chart.planets["JUPITER"], chart.planets["MOON"]
    lord9, lord12 = lord_of(chart, 9), lord_of(chart, 12)
    abroad = chart.house_planet_count.get(12, 0) + chart.house_planet_count.get(9, 0) >= 2

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — 9-й и 12-й дома:", en="On «{topic}» — houses 9 and 12:")
        extra = " Тема переезда/эмиграции живая." if abroad and lang == "ru" else (" Relocation theme is alive." if abroad else "")
        body = f"Раху в {rahu.house}-м — тяга к «другому». {lord_of_house_note(locale, chart, 12)} {lord_of_house_note(locale, chart, 9)}{extra}"
        practice = "Составь список «за» и «против» переезда — карта не даёт да/нет, а условия." if lang == "ru" else "List pros/cons of relocation."
        markers = pick_markers(locale, [rahu, lord12, lord9], style=style)
    elif idx == 1:
        frame = topic_frame(locale, question, ru="На «{topic}» — дальние поездки:", en="On «{topic}» — long journeys:")
        body = f"9-й в {sign_label(locale, chart.house_signs[9])}. {_jupiter_growth(locale, jupiter)} {lord_of_house_note(locale, chart, 3)}"
        practice = "Запланируй одну поездку «для горизонта» — не только отпуск." if lang == "ru" else "Plan one horizon-expanding trip."
        markers = pick_markers(locale, [jupiter, lord9, lord_of(chart, 3)], style=style)
    elif idx == 2:
        frame = topic_frame(locale, question, ru="На «{topic}» — направления:", en="On «{topic}» — directions:")
        body = f"9-й ({sign_label(locale, chart.house_signs[9])}) + Раху в {sign_label(locale, rahu.sign)} — тянет к {_house_theme(locale, rahu.house).lower()}."
        practice = "Заметь, какие места во сне или в разговорах повторяются — это подсказка." if lang == "ru" else "Notice repeating places in dreams or talk."
        markers = pick_markers(locale, [rahu, jupiter, lord9], style=style)
    elif idx == 3:
        saturn = chart.planets["SATURN"]
        frame = topic_frame(locale, question, ru="Что мешает переезду («{topic}»):", en="What blocks relocation («{topic}»):")
        body = f"Сатурн в {saturn.house}-м — страх и ответственность; 4-й: {lord_of_house_note(locale, chart, 4)}"
        practice = "Назови один страх переезда вслух — часто он меньше, чем кажется." if lang == "ru" else "Name one relocation fear aloud."
        markers = pick_markers(locale, [saturn, lord12, lord_of(chart, 4)], style=style)
    else:
        frame = topic_frame(locale, question, ru="На «{topic}» — «дом» вдали:", en="On «{topic}» — home far away:")
        body = f"Луна в {moon.house}-м + 4-й: {lord_of_house_note(locale, chart, 4)} «Дом» — состояние, не только адрес."
        practice = "Создай один якорь дома в чемодане/комнате — запах, музыка, ритуал." if lang == "ru" else "Create one home anchor where you are."
        markers = pick_markers(locale, [moon, lord_of(chart, 4), lord12], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Upaya ---

def _upaya_block(chart, locale, idx, question, style) -> StructuredQaAnswer:
    lang = _lang(locale)
    strengths, _, risks, _ = _derive_summary(chart, lang)
    tense, strong, deb = _tense(chart), _strong(chart), _debilitated(chart)
    jupiter = chart.planets["JUPITER"]

    if idx == 0:
        frame = topic_frame(locale, question, ru="На «{topic}» — общие упайи:", en="On «{topic}» — general upayas:")
        hints = "; ".join(_upaya(locale, pl.key) for pl in tense[:2])
        body = f"Смягчать: {hints}. Риск карты: {risks}."
        if lang == "en":
            body = f"Soften: {hints}. Chart risk: {risks}."
        practice = "Один день недели — под «тяжёлую» планету: дана + простая мантра." if lang == "ru" else "One weekday for a tense planet: charity + mantra."
        markers = tuple(_upaya(locale, pl.key) for pl in tense[:3]) or (_upaya(locale, "JUPITER"),)
    elif idx == 1:
        targets = deb[:3] if deb else tense[:3]
        frame = topic_frame(locale, question, ru="На «{topic}» — смягчение планет:", en="On «{topic}» — softening planets:")
        body = "; ".join(_upaya(locale, pl.key) for pl in targets)
        practice = "Выбери одну планету и одну практику на месяц — не все сразу." if lang == "ru" else "Pick one planet, one practice for a month."
        markers = tuple(_upaya(locale, pl.key) for pl in targets)
    elif idx == 2:
        targets = strong[:3] if strong else [chart.planets["SUN"], jupiter]
        frame = topic_frame(locale, question, ru="На «{topic}» — усиление силы:", en="On «{topic}» — strengthening:")
        body = f"{'; '.join(_upaya(locale, pl.key) for pl in targets)}. Сильные: {_list_to_prose(strengths, lang)}."
        practice = "Четверг (Юпитер) — благодарность или знание кому-то." if lang == "ru" else "Thursday — gratitude or sharing knowledge."
        markers = tuple(_upaya(locale, pl.key) for pl in targets)
    elif idx == 3:
        targets = tense[:3] if tense else [jupiter, chart.planets["MOON"]]
        frame = topic_frame(locale, question, ru="На «{topic}» — дни и практики:", en="On «{topic}» — days and practices:")
        body = "; ".join(_upaya(locale, pl.key) for pl in targets)
        practice = "Регулярность важнее драматичных ритуалов." if lang == "ru" else "Regularity beats dramatic rituals."
        markers = tuple(_upaya(locale, pl.key) for pl in targets)
    else:
        focus = deb[0] if deb else tense[0]
        gem = _GEM[_lang(locale)].get(focus.key, "")
        frame = topic_frame(locale, question, ru="На «{topic}» — мантры и камни:", en="On «{topic}» — mantras and gems:")
        body = f"{_upaya(locale, focus.key)}. Камень традиции: {gem} — только после консультации с джйотиши."
        if lang == "en":
            body = f"{_upaya(locale, focus.key)}. Traditional gem: {gem} — only after jyotishi consult."
        practice = "Без консультации — мантра и дана безопаснее камня." if lang == "ru" else "Without consult — mantra and charity beat gems."
        markers = (_upaya(locale, focus.key), placement_label(locale, focus, style=style))

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- House sphere (12 houses x 3 questions) ---

def _house(chart, locale, idx, question, style, *, house: int, focus: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    h_sign = sign_label(locale, chart.house_signs[house])
    theme = _house_theme(locale, house)
    in_h = planets_in_house(chart, house)
    lord_h = lord_of(chart, house)
    best = max(in_h, key=rank_dignity) if in_h else lord_h

    if focus == "strength":
        frame = topic_frame(locale, question, ru="Где сила («{topic}»):", en="Where strength («{topic}»):")
        if in_h:
            body = (
                f"Опора — {_pl(locale, best.key)} в {sign_label(locale, best.sign)} "
                f"({dignity_note(locale, best) or ('устойчиво' if lang == 'ru' else 'steady')}). "
                f"{lord_of_house_note(locale, chart, house)}"
            )
        else:
            body = lord_of_house_note(locale, chart, house)
        practice = (
            f"Раз в неделю сознательно используй энергию {house}-го дома."
            if lang == "ru"
            else f"Once a week, use house {house} energy consciously."
        )
        markers = pick_markers(locale, ([best] + in_h)[:3], style=style)
    elif focus == "challenge":
        frame = topic_frame(locale, question, ru="Что мешает («{topic}»):", en="What blocks («{topic}»):")
        weak = [pl for pl in in_h if pl.dignity == "debilitated"] or [
            pl for pl in in_h if pl.key in {"MARS", "SATURN", "RAHU"}
        ]
        if weak:
            pl = weak[0]
            body = (
                f"Узел — {_pl(locale, pl.key)} в {sign_label(locale, pl.sign)}: "
                f"{dignity_note(locale, pl) or ('напряжение' if lang == 'ru' else 'tension')} "
                f"в теме «{theme}»."
            )
        elif not in_h:
            body = (
                f"Дом пуст — трения через управителя: {lord_of_house_note(locale, chart, house)}"
                if lang == "ru"
                else f"Empty house — friction via lord: {lord_of_house_note(locale, chart, house)}"
            )
        else:
            pl = min(in_h, key=rank_dignity)
            body = (
                f"Слабее звучит {_pl(locale, pl.key)} — {dignity_note(locale, pl) or ('нужна внимательность' if lang == 'ru' else 'needs care')}."
            )
        practice = (
            "Назови паттерн, который повторяется в этой сфере — без самоосуждения."
            if lang == "ru"
            else "Name the repeating pattern here."
        )
        markers = pick_markers(locale, (weak or in_h or [lord_h])[:3], style=style)
    else:
        if lang == "ru":
            frame = f"На «{question.strip().rstrip('?.!')}» — {house}-й дом ({h_sign}):"
        else:
            frame = f"On «{question.strip().rstrip('?.!')}» — house {house} ({h_sign}):"
        if in_h:
            names = ", ".join(f"{_pl(locale, p.key)} в {sign_label(locale, p.sign)}" for p in in_h[:2])
            body = f"{house}-й дом ({h_sign}, «{theme}»): {names}. {lord_of_house_note(locale, chart, house)}"
            if lang == "en":
                body = f"House {house} ({h_sign}, {theme}): {names}. {lord_of_house_note(locale, chart, house)}"
        else:
            body = (
                f"{house}-й ({h_sign}) без планет — тон задаёт {lord_of_house_note(locale, chart, house)}"
                if lang == "ru"
                else f"House {house} ({h_sign}) empty — tone from {lord_of_house_note(locale, chart, house)}"
            )
        practice = (
            f"Неделя наблюдения: как проявляется «{theme}» в жизни."
            if lang == "ru"
            else f"Observe how «{theme}» shows up for a week."
        )
        markers = pick_markers(locale, in_h[:2] + [lord_h], style=style)

    if house == 1 and idx == 0:
        essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
        lagna = sign_label(locale, chart.lagna_sign)
        prefix = f"Лагна {lagna} — {essence}. " if lang == "ru" else f"Lagna {lagna} — {essence}. "
        body = prefix + body

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


# --- Popular blocks ---

def _popular(chart, locale, idx, question, style, *, question_id: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    strengths, weaknesses, risks, opportunities = _derive_summary(chart, lang)
    lagna = sign_label(locale, chart.lagna_sign)
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]

    if question_id == "theme":
        frame = topic_frame(locale, question, ru="На «{topic}» — главный сюжет:", en="On «{topic}» — main storyline:")
        if chart.stellium_house:
            h, s = chart.stellium_house, sign_label(locale, chart.stellium_sign)
            body = f"Лагна {lagna} — {essence}. Стеллиум {s} в {h}-м — {_house_theme(locale, h)}: ключевая тема."
        elif chart.strong_houses:
            h = chart.strong_houses[0]
            body = f"Лагна {lagna} — {essence}. Ярче {h}-й дом — {chart.house_planet_count[h]} планет(ы)."
        else:
            body = f"Лагна {lagna} — {essence}."
        practice = "Отметь, где тратишь больше всего энергии — это и есть сюжет." if lang == "ru" else "Note where you spend most energy."
        markers = (f"Лагна · {lagna}" if lang == "ru" else f"Lagna · {lagna}",)
    elif question_id == "strength":
        frame = topic_frame(locale, question, ru="На «{topic}»:", en="On «{topic}»:")
        body = f"Сильные стороны — {_list_to_prose(strengths, lang)}."
        if chart.planets["SUN"].dignity == "exalted":
            body += " Солнце в силе — уверенный стержень." if lang == "ru" else " Exalted Sun — confident core."
        practice = "Опирайся на силу раз в неделю сознательно." if lang == "ru" else "Lean on strength weekly."
        markers = pick_markers(locale, _strong(chart)[:3] or [chart.planets["SUN"]], style=style)
    elif question_id == "love":
        from app.family_qa_detail import build_family_structured
        return build_family_structured(chart, locale, 0, question, style=style)
    elif question_id == "career":
        return _finance(chart, locale, 1, question, style)
    elif question_id == "money":
        return _finance(chart, locale, 0, question, style)
    else:
        frame = topic_frame(locale, question, ru="На «{topic}»:", en="On «{topic}»:")
        body = f"Главная возможность — {opportunities}."
        practice = "Один маленький шаг в эту сторону на этой неделе." if lang == "ru" else "One small step that way this week."
        markers = pick_markers(locale, [chart.planets["JUPITER"]], style=style)

    return StructuredQaAnswer(make_brief(locale, frame, body), markers, practice)


_BLOCK_BUILDERS = {
    "finance": _finance,
    "karma": _karma,
    "traits": _traits,
    "lineage": _lineage,
    "health": _health,
    "purpose": _purpose,
    "dharma": _dharma,
    "travel": _travel,
    "upaya": _upaya_block,
}


def build_natal_sphere_structured(
    block: str,
    chart: JyotishChart,
    locale: str,
    question_index: int,
    question: str,
    *,
    style: str = "terms",
    house: int | None = None,
    focus: str = "default",
    question_id: str = "",
) -> StructuredQaAnswer:
    idx = max(0, min(4, question_index))
    if block == "house":
        if house is None:
            raise ValueError("house required for block=house")
        return _house(chart, locale, idx, question, style, house=house, focus=focus)
    if block == "popular":
        return _popular(chart, locale, idx, question, style, question_id=question_id)
    builder = _BLOCK_BUILDERS.get(block)
    if builder is None:
        raise ValueError(f"unknown block: {block}")
    return builder(chart, locale, idx, question, style)
