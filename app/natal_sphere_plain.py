"""Plain-language structured answers for natal chart Q&A — simple, warm, a little humor."""
from __future__ import annotations

from app.astro_engine import sign_label
from app.jyotish_engine import JyotishChart, PlanetPlacement
from app.jyotish_text import LAGNA_ESSENCE, _derive_summary, _house_theme, _lang, _list_to_prose, _pl
from app.natal_qa_common import (
    StructuredQaAnswer,
    lord_of,
    make_brief,
    pick_markers,
    planets_in_house,
    rank_dignity,
)
from app.natal_qa_voice import (
    life_manifestation_echo,
    plain_area,
    plain_lord_line,
    plain_placement_line,
    plain_topic_hook,
    sanitize_plain_qa_text,
)


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


def _pack(
    locale: str,
    question: str,
    opening: str,
    detail: str,
    *,
    markers_chart: list,
    practice: str,
    roles: tuple[str, ...] = (),
) -> StructuredQaAnswer:
    hook = plain_topic_hook(locale, question)
    echo = life_manifestation_echo(locale, question, style="plain")
    chunks = [opening.strip()]
    if echo and echo.lower() not in opening.lower() and echo.lower() not in detail.lower():
        chunks.append(echo)
    chunks.append(detail.strip())
    body = sanitize_plain_qa_text(" ".join(chunks), locale)
    return StructuredQaAnswer(
        make_brief(locale, hook, body, style="plain"),
        pick_markers(locale, markers_chart, style="plain", roles=roles, limit=3),
        practice,
    )


def plain_finance(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    venus, jupiter, sun, saturn, mars, rahu = (
        chart.planets[k] for k in ("VENUS", "JUPITER", "SUN", "SATURN", "MARS", "RAHU")
    )
    lord2, lord10 = lord_of(chart, 2), lord_of(chart, 10)

    if idx == 0:
        opening = (
            "С деньгами у тебя не «просто счёт в банке» — это про то, что ты ценишь и куда вкладываешь душу."
            if lang == "ru"
            else "Money for you isn't just a bank balance — it's what you value and where you invest heart."
        )
        detail = f"{plain_placement_line(locale, venus)} {plain_placement_line(locale, jupiter)} {plain_lord_line(locale, chart, 2)}"
        practice = (
            "На неделю: три покупки — подпиши «нужно» или «настроение». Не суди себя, просто посмотри честно."
            if lang == "ru"
            else "This week: tag three spends «need» or «mood». No judgment — just look."
        )
        return _pack(locale, question, opening, detail, markers_chart=[venus, jupiter, lord2], practice=practice)

    if idx == 1:
        opening = (
            "Карьера — не только должность, а «зачем я встаю утром» (иногда без кофе это неочевидно)."
            if lang == "ru"
            else "Career isn't just a title — it's «why I get up» (sometimes unclear before coffee)."
        )
        detail = f"{plain_placement_line(locale, sun)} {plain_lord_line(locale, chart, 10)} {plain_placement_line(locale, saturn)}"
        practice = (
            "Один маленький шаг к делу на месяц — не героизм, а движение. Даже скучное письмо считается."
            if lang == "ru"
            else "One small work step this month counts — even a boring email."
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, lord10, saturn], practice=practice)

    if idx == 2:
        opening = (
            "Риск и «быстрые деньги» — соблазнительно, но у тебя есть своя скорость; форсировать не обязательно."
            if lang == "ru"
            else "Quick money is tempting — but you have your own pace; forcing it isn't required."
        )
        detail = f"{plain_placement_line(locale, mars)} {plain_placement_line(locale, rahu)} {plain_lord_line(locale, chart, 8)}"
        practice = (
            "Перед крупной тратой — пауза 24 часа и вопрос «это ценность или импульс?»"
            if lang == "ru"
            else "Before big spending — 24h pause: value or impulse?"
        )
        return _pack(locale, question, opening, detail, markers_chart=[mars, rahu, lord_of(chart, 8)], practice=practice)

    if idx == 3:
        opening = (
            "Долги и чужие ресурсы — тема «не только моё». Тут легко перепутать помощь и самоотдачу."
            if lang == "ru"
            else "Shared money and others' resources — easy to mix help with self-abandon."
        )
        detail = f"{plain_lord_line(locale, chart, 8)} {plain_placement_line(locale, saturn)}"
        practice = (
            "Если что-то «висит» — назови вслух сумму и срок. Магия начинается с ясности."
            if lang == "ru"
            else "If something «hangs» — say amount and deadline out loud. Clarity first."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 8), saturn], practice=practice)

    opening = (
        "Доход растёт не от молитвы к вселенной, а от связки «умею + не сливаю + не выгораю»."
        if lang == "ru"
        else "Income grows from «can do + don't leak + don't burn out» — not universe spam."
    )
    detail = f"{plain_lord_line(locale, chart, 11)} {plain_placement_line(locale, jupiter)}"
    practice = (
        "Запиши один источник дохода, который реально тянет — и один, который только съедает нервы."
        if lang == "ru"
        else "List one income source that pulls you up — and one that only eats nerves."
    )
    return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 11), jupiter], practice=practice)


def plain_karma(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    saturn, rahu, ketu, jupiter, moon = (
        chart.planets[k] for k in ("SATURN", "RAHU", "KETU", "JUPITER", "MOON")
    )

    if idx == 0:
        opening = (
            "Повторяющиеся «тяжёлые» сценарии — не наказание, а жизнь в режиме повтора, пока не сменишь реакцию."
            if lang == "ru"
            else "Repeating heavy scenes aren't punishment — life's on repeat until you change the reaction."
        )
        detail = f"{plain_lord_line(locale, chart, 8)} {plain_lord_line(locale, chart, 12)} {plain_placement_line(locale, saturn)}"
        practice = (
            "Заметь один «опять это» за неделю — и спроси: «что я делаю по-старому?» без самобичевания."
            if lang == "ru"
            else "Catch one «this again» this week — ask what you do the old way, without self-flagellation."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 8), saturn], practice=practice)

    if idx == 1:
        opening = (
            "Прошлое не обязано быть драмой — но иногда оно шепчет изнутри, особенно в тишине."
            if lang == "ru"
            else "The past needn't be drama — but sometimes it whispers from inside, especially in quiet."
        )
        detail = f"{plain_placement_line(locale, ketu)} {plain_placement_line(locale, moon)} {plain_lord_line(locale, chart, 12)}"
        practice = (
            "5 минут без телефона в день — звучит скучно, но мозг так «переваривает» старое."
            if lang == "ru"
            else "Five phone-free minutes daily — boring, but the brain digests the old that way."
        )
        return _pack(locale, question, opening, detail, markers_chart=[ketu, moon], practice=practice)

    if idx == 2:
        opening = (
            "Задержки и «не сейчас» — не всегда вселенная против тебя. Часто это проверка: созрел ли ты."
            if lang == "ru"
            else "Delays aren't always the universe against you — often a check: are you ready?"
        )
        detail = f"{plain_placement_line(locale, saturn)} {plain_lord_line(locale, chart, saturn.house)}"
        practice = (
            "Не обходи «скучный» труд — именно он потом неожиданно окупается (да, обидно, но часто так)."
            if lang == "ru"
            else "Don't skip «boring» work — it often pays back later (annoying, but true)."
        )
        return _pack(locale, question, opening, detail, markers_chart=[saturn], practice=practice)

    if idx == 3:
        opening = (
            "Тяга к новому и привычка отпускать старое — два разных двигателя. Важно не перепутать рост с побегом."
            if lang == "ru"
            else "Craving the new and letting go of the old are two engines — don't mix growth with escape."
        )
        detail = f"{plain_placement_line(locale, rahu)} {plain_placement_line(locale, ketu)}"
        practice = (
            "Перед резким решением спроси: «я расту или убегаю?» — честно, без Instagram-цитат."
            if lang == "ru"
            else "Before a sharp move ask: growing or running? Honestly, no quote graphics."
        )
        return _pack(locale, question, opening, detail, markers_chart=[rahu, ketu], practice=practice)

    opening = (
        "Осознанная жизнь — не только медитация, а выбор, который не стыдно объяснить близким."
        if lang == "ru"
        else "Conscious living isn't only meditation — it's choices you can explain to people you love."
    )
    detail = f"{plain_lord_line(locale, chart, 9)} {plain_placement_line(locale, jupiter)}"
    practice = (
        "Когда сценарий повторяется — измени реакцию на 10%, не ломая себя. Маленький поворот руля."
        if lang == "ru"
        else "When a pattern repeats — shift reaction 10%. Small steering wheel turn."
    )
    return _pack(locale, question, opening, detail, markers_chart=[jupiter, lord_of(chart, 9)], practice=practice)


def plain_traits(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, moon, mars, mercury = (chart.planets[k] for k in ("SUN", "MOON", "MARS", "MERCURY"))
    lagna = sign_label(locale, chart.lagna_sign)
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
    strengths, weaknesses, _, _ = _derive_summary(chart, lang)

    if idx == 0:
        opening = (
            f"С первого контакта ты читаешься как «{essence.lower()}» ({lagna}) — это не маска, а вход в жизнь."
            if lang == "ru"
            else f"First contact reads as «{essence.lower()}» ({lagna}) — not a mask, your entry into life."
        )
        detail = plain_lord_line(locale, chart, 1)
        practice = (
            "Неделю понаблюдай, как заходишь в новый разговор — там и живёт твой «первый кадр»."
            if lang == "ru"
            else "Watch how you enter new talks for a week — that's your «first frame»."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 1), sun], practice=practice)

    if idx == 1:
        opening = (
            "Стержень и напор — разные кнопки. Один отвечает «кто я», другой «давай уже»."
            if lang == "ru"
            else "Core and drive are different buttons — one is «who I am», other «let's go»."
        )
        detail = f"{plain_placement_line(locale, sun)} {plain_placement_line(locale, mars)}"
        practice = (
            "Заметь, когда действуешь на автопилоте (напор) vs осознанно (стержень) — разница удивляет."
            if lang == "ru"
            else "Notice autopilot drive vs conscious core — the gap surprises."
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, mars], practice=practice)

    if idx == 2:
        opening = (
            "Эмоции у тебя не «слабость» — это GPS, только иногда без интернета."
            if lang == "ru"
            else "Feelings aren't «weakness» — they're GPS, sometimes offline."
        )
        detail = f"{plain_placement_line(locale, moon)} {plain_lord_line(locale, chart, 4)}"
        practice = (
            "Вечером назови одну эмоцию дня — без оценки «правильно/неправильно»."
            if lang == "ru"
            else "Name one emotion each evening — no right/wrong score."
        )
        return _pack(locale, question, opening, detail, markers_chart=[moon, lord_of(chart, 4)], practice=practice)

    if idx == 3:
        opening = (
            "Как говоришь и как рискуешь — два канала, через которые мир тебя слышит (иногда громко)."
            if lang == "ru"
            else "How you talk and how you risk — two channels the world hears you through (sometimes loud)."
        )
        detail = f"{plain_placement_line(locale, mercury)} {plain_placement_line(locale, mars)} {plain_lord_line(locale, chart, 3)}"
        practice = (
            "Перед спором — один вдох. Дешевле, чем потом извиняться с пустым аккаунтом."
            if lang == "ru"
            else "One breath before an argument — cheaper than apologizing with an empty account."
        )
        return _pack(locale, question, opening, detail, markers_chart=[mars, mercury], practice=practice)

    opening = (
        "Сильные стороны — не медаль, а инструменты. Слабые — не проклятие, а зоны, где нужен режим."
        if lang == "ru"
        else "Strengths are tools, not medals. Weak spots need routine, not curse talk."
    )
    detail = (
        f"Сильнее всего: {_list_to_prose(strengths, lang)}. Сложнее: {_list_to_prose(weaknesses, lang)}."
        if lang == "ru"
        else f"Strongest: {_list_to_prose(strengths, lang)}. Trickier: {_list_to_prose(weaknesses, lang)}."
    )
    practice = (
        "Раз в неделю опирайся на одну сильную сторону сознательно — как на любимый инструмент."
        if lang == "ru"
        else "Once a week lean on one strength on purpose — like a favorite tool."
    )
    return _pack(locale, question, opening, detail, markers_chart=[sun] + planets_in_house(chart, 1)[:1], practice=practice)


def plain_lineage(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    moon, sun, jupiter = chart.planets["MOON"], chart.planets["SUN"], chart.planets["JUPITER"]

    if idx == 0:
        opening = (
            "Мама и «дом» внутри — не только стены, а то, как ты умеешь (или не умеешь) отдыхать в душе."
            if lang == "ru"
            else "Mother and inner home — not just walls, but how you rest inside."
        )
        detail = f"{plain_placement_line(locale, moon)} {plain_lord_line(locale, chart, 4)}"
        practice = (
            "Вспомни один тёплый жест заботы из детства — это язык твоей внутренней «мамы»."
            if lang == "ru"
            else "Recall one warm care gesture from childhood — your inner «mother» language."
        )
        return _pack(locale, question, opening, detail, markers_chart=[moon, lord_of(chart, 4)], practice=practice)

    if idx == 1:
        opening = (
            "Отец и авторитет — про правила, которые ты унаследовал… и те, что тихо переписываешь."
            if lang == "ru"
            else "Father and authority — rules you inherited… and ones you quietly rewrite."
        )
        detail = f"{plain_placement_line(locale, sun)} {plain_lord_line(locale, chart, 9)}"
        practice = (
            "Напиши один «закон» от старших — принимаешь или споришь? Без суда, просто честно."
            if lang == "ru"
            else "Write one «law» from elders — accept or argue? No trial, just honest."
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, lord_of(chart, 9)], practice=practice)

    if idx == 2:
        opening = (
            "Род — не только фамилия, а сценарии, которые передаются, как рецепт борща: с вариациями."
            if lang == "ru"
            else "Lineage isn't just a surname — scripts passed like soup recipes, with variations."
        )
        detail = f"{plain_lord_line(locale, chart, 4)} {plain_lord_line(locale, chart, 9)}"
        practice = (
            "Спроси старших одну историю рода — карта оживает, когда есть живой голос."
            if lang == "ru"
            else "Ask an elder one family story — the chart wakes up with a live voice."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 4), lord_of(chart, 9)], practice=practice)

    if idx == 3:
        opening = (
            "«Свои» — это не обязательно кровь, а люди, рядом с которыми можно выдохнуть."
            if lang == "ru"
            else "«Your people» aren't always blood — those you can exhale beside."
        )
        detail = f"{plain_placement_line(locale, moon)} {plain_placement_line(locale, jupiter)}"
        practice = (
            "Маленький ритуал «своих» — еда, звонок, фото. Не праздник, а якорь."
            if lang == "ru"
            else "A small «your people» ritual — food, call, photo. Anchor, not a party."
        )
        return _pack(locale, question, opening, detail, markers_chart=[moon, jupiter], practice=practice)

    opening = (
        "С родителями и родом не всегда «как в рекламе» — бывает дистанция, обида или слишком много ответственности."
        if lang == "ru"
        else "Parents and lineage aren't always ad-perfect — distance, hurt, or too much duty happens."
    )
    detail = f"{plain_placement_line(locale, moon)} {plain_placement_line(locale, chart.planets['SATURN'])}"
    practice = (
        "Назови вслух одну обиду без обвинения — первый шаг, не финал терапии."
        if lang == "ru"
        else "Name one hurt aloud without blame — first step, not therapy finale."
    )
    return _pack(locale, question, opening, detail, markers_chart=[moon, chart.planets["SATURN"]], practice=practice)


def plain_health(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, moon, mars, saturn = (chart.planets[k] for k in ("SUN", "MOON", "MARS", "SATURN"))

    if idx == 0:
        opening = (
            "Энергия — не бесконечный тариф. У тебя есть свой «бензин» и свой стиль его сливать."
            if lang == "ru"
            else "Energy isn't an unlimited plan — you have your fuel and your leak style."
        )
        detail = f"{plain_placement_line(locale, sun)} {plain_placement_line(locale, mars)} {plain_lord_line(locale, chart, 1)}"
        practice = (
            "Утром 5 минут движения — не подвиг, а «завести мотор»."
            if lang == "ru"
            else "Five minutes of movement each morning — start the engine, not a heroics."
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, mars], practice=practice)

    if idx == 1:
        opening = (
            "Режим — скучное слово, которое спасает, когда тело начинает слать смс «я устал»."
            if lang == "ru"
            else "Routine is a boring word that saves you when the body texts «I'm tired»."
        )
        detail = f"{plain_lord_line(locale, chart, 6)} {plain_placement_line(locale, saturn)}"
        practice = (
            "Один стабильный режим: сон или вода. Начни с одного, не с десяти."
            if lang == "ru"
            else "One stable habit: sleep or water. Start with one, not ten."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 6), saturn], practice=practice)

    if idx == 2:
        opening = (
            "Восстановление — не лень, а техобслуживание. Без него даже сильная машина стучит."
            if lang == "ru"
            else "Recovery isn't laziness — maintenance. Without it, even strong engines knock."
        )
        detail = f"{plain_placement_line(locale, moon)} {plain_lord_line(locale, chart, 4)}"
        practice = (
            "Запланируй «ничего не делать» — буквально в календарь. Иначе не случится."
            if lang == "ru"
            else "Schedule «do nothing» — literally in the calendar. Otherwise it won't happen."
        )
        return _pack(locale, question, opening, detail, markers_chart=[moon, lord_of(chart, 4)], practice=practice)

    if idx == 3:
        opening = (
            "Слабые места — не приговор, а напоминание: тут лучше не геройствовать."
            if lang == "ru"
            else "Weak spots aren't a verdict — a reminder not to hero here."
        )
        weak = [mars, saturn] + planets_in_house(chart, 6)[:1]
        detail = " ".join(plain_placement_line(locale, pl) for pl in weak[:2])
        practice = (
            "При симптомах — к врачу. Карта про профилактику и режим, не про Google-диагноз."
            if lang == "ru"
            else "Symptoms → doctor. Chart is prevention, not Dr. Google."
        )
        return _pack(locale, question, opening, detail, markers_chart=weak[:2], practice=practice)

    opening = (
        "Тело любит баланс: нагрузка + отдых. Когда одно без другого — начинается «ну я же сильный»."
        if lang == "ru"
        else "The body likes balance: load + rest. One without the other → «but I'm strong»."
    )
    detail = f"{plain_placement_line(locale, mars)} {plain_placement_line(locale, moon)}"
    practice = (
        "Неделя: умеренная нагрузка + один день полного отдыха. Без медалей."
        if lang == "ru"
        else "One week: moderate load + one full rest day. No medals."
    )
    return _pack(locale, question, opening, detail, markers_chart=[mars, moon], practice=practice)


def plain_purpose(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    sun, jupiter, saturn = chart.planets["SUN"], chart.planets["JUPITER"], chart.planets["SATURN"]
    strengths, _, _, opportunities = _derive_summary(chart, lang)
    lagna = sign_label(locale, chart.lagna_sign)

    if idx == 0:
        opening = (
            "Предназначение — не табличка на двери, а то, к чему возвращаешься, даже когда устал."
            if lang == "ru"
            else "Purpose isn't a door plaque — what you return to even when tired."
        )
        detail = f"{plain_lord_line(locale, chart, 9)} {plain_placement_line(locale, jupiter)}"
        practice = (
            "Спроси: «что я делаю, когда никто не смотрит и не платит?» — там часто и лежит ответ."
            if lang == "ru"
            else "Ask: «what do I do when no one's watching and no one's paying?»"
        )
        return _pack(locale, question, opening, detail, markers_chart=[jupiter, lord_of(chart, 9)], practice=practice)

    if idx == 1:
        opening = (
            "Таланты — не только «я рисую», а то, что у тебя получается легче, чем у соседа (и без понтов)."
            if lang == "ru"
            else "Talents aren't only «I draw» — what comes easier than for the neighbor, without showing off."
        )
        detail = f"Ярче всего: {_list_to_prose(strengths, lang)}. {plain_placement_line(locale, sun)}"
        practice = (
            "Один раз в неделю делай «сильное» дело на 20 минут — не на результат, на кайф."
            if lang == "ru"
            else "Once a week do a «strong» thing for 20 minutes — for joy, not outcome."
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, jupiter], practice=practice)

    if idx == 2:
        opening = (
            "Реализация — это когда внешнее «что я делаю» хотя бы иногда совпадает с внутренним «зачем»."
            if lang == "ru"
            else "Realization is when outer «what I do» sometimes matches inner «why»."
        )
        detail = f"{plain_lord_line(locale, chart, 10)} {plain_placement_line(locale, saturn)}"
        practice = (
            "Выбери одну сферу на квартал — не пять. Мультитаскинг убивает смысл."
            if lang == "ru"
            else "Pick one sphere for the quarter — not five. Multitasking kills meaning."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 10), saturn], practice=practice)

    if idx == 3:
        opening = (
            f"Ты входишь в мир как {lagna} — и это тоже часть «зачем я здесь», не только работа."
            if lang == "ru"
            else f"You enter the world as {lagna} — part of «why I'm here», not only work."
        )
        detail = f"{plain_placement_line(locale, sun)} {plain_placement_line(locale, jupiter)}"
        practice = (
            "Запиши три момента, когда чувствовал «я на месте» — ищи общий знаменатель."
            if lang == "ru"
            else "Write three «I'm in the right place» moments — find the pattern."
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, jupiter], practice=practice)

    opening = (
        f"Главная возможность сейчас — {opportunities}. Не обязана быть громкой, но стоит заметить."
        if lang == "ru"
        else f"Main opportunity now — {opportunities}. Needn't be loud, but worth noticing."
    )
    detail = plain_placement_line(locale, jupiter)
    practice = (
        "Один маленький шаг в эту сторону на этой неделе — микрошаг, не революция."
        if lang == "ru"
        else "One tiny step that way this week — micro, not revolution."
    )
    return _pack(locale, question, opening, detail, markers_chart=[jupiter], practice=practice)


def plain_dharma(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    jupiter, sun = chart.planets["JUPITER"], chart.planets["SUN"]

    if idx == 0:
        opening = (
            "Духовный путь — не обязательно монастырь. Иногда это честность в мелочах, которые никто не видит."
            if lang == "ru"
            else "Spiritual path isn't always a monastery — sometimes honesty in tiny unseen things."
        )
        detail = f"{plain_lord_line(locale, chart, 9)} {plain_placement_line(locale, jupiter)}"
        practice = (
            "Сегодня одно маленькое «правильно» без аудитории — это уже практика."
            if lang == "ru"
            else "One small «right» today with no audience — already practice."
        )
        return _pack(locale, question, opening, detail, markers_chart=[jupiter, lord_of(chart, 9)], practice=practice)

    if idx == 1:
        opening = (
            "Смысл — когда действие не против твоих ценностей, даже если никто не похлопает."
            if lang == "ru"
            else "Meaning is when action doesn't fight your values, even without applause."
        )
        detail = f"{plain_placement_line(locale, sun)} {plain_lord_line(locale, chart, 9)}"
        practice = (
            "Спроси: «если бы никто не узнал — я бы всё равно так поступил?»"
            if lang == "ru"
            else "Ask: «if no one knew — would I still act this way?»"
        )
        return _pack(locale, question, opening, detail, markers_chart=[sun, lord_of(chart, 9)], practice=practice)

    if idx == 2:
        opening = (
            "Вера в путь — не «всё будет хорошо», а «я не сдамся на полпути к себе»."
            if lang == "ru"
            else "Faith in the path isn't «all will be fine» — it's «I won't quit halfway to myself»."
        )
        detail = plain_placement_line(locale, jupiter)
        practice = (
            "Когда сомневаешься — вернись к одному человеку или делу, где чувствуешь правду."
            if lang == "ru"
            else "When doubting — return to one person or thing where you feel truth."
        )
        return _pack(locale, question, opening, detail, markers_chart=[jupiter], practice=practice)

    if idx == 3:
        opening = (
            "Честность с собой — самый непопулярный духовный практикум. Зато работает."
            if lang == "ru"
            else "Honesty with yourself — least popular spiritual gym. Works though."
        )
        detail = f"{plain_lord_line(locale, chart, 9)} {plain_placement_line(locale, chart.planets['SATURN'])}"
        practice = (
            "Признай одну маленькую правду, которую откладывал — без драмы, просто факт."
            if lang == "ru"
            else "Admit one small truth you've postponed — fact, no drama."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 9), chart.planets["SATURN"]], practice=practice)

    opening = (
        "Дхарма в быту — не только медитация, а «не вру себе в мелочах»."
        if lang == "ru"
        else "Dharma in daily life — not only meditation, but «don't lie to myself in small things»."
    )
    detail = f"{plain_lord_line(locale, chart, 9)} {plain_lord_line(locale, chart, 10)}"
    practice = (
        "Честность в одном маленьком деле сегодня — это дхарма, не только лотос."
        if lang == "ru"
        else "Honesty in one small deed today — dharma, not only lotus pose."
    )
    return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 9), lord_of(chart, 10)], practice=practice)


def plain_travel(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)
    rahu, jupiter, moon = chart.planets["RAHU"], chart.planets["JUPITER"], chart.planets["MOON"]

    if idx == 0:
        opening = (
            "Переезд — не «сбежать от проблем», а сменить декорации и посмотреть, что останется с тобой."
            if lang == "ru"
            else "Moving isn't «escaping problems» — new scenery, see what stays with you."
        )
        detail = f"{plain_placement_line(locale, rahu)} {plain_lord_line(locale, chart, 12)} {plain_lord_line(locale, chart, 9)}"
        practice = (
            "Список «что я ищу там» vs «что везу с собой» — коротко, на одной странице."
            if lang == "ru"
            else "List «what I seek there» vs «what I bring» — one page."
        )
        return _pack(locale, question, opening, detail, markers_chart=[rahu, lord_of(chart, 12)], practice=practice)

    if idx == 1:
        opening = (
            "Путешествия для тебя — не только отметки на карте, а перезагрузка нервной системы."
            if lang == "ru"
            else "Travel for you isn't only map pins — nervous system reboot."
        )
        detail = f"{plain_placement_line(locale, jupiter)} {plain_placement_line(locale, moon)}"
        practice = (
            "Один якорь дома в чемодане — запах, музыка, ритуал. Звучит sentimental, но помогает."
            if lang == "ru"
            else "One home anchor in the bag — scent, music, ritual. Sentimental, but helps."
        )
        return _pack(locale, question, opening, detail, markers_chart=[jupiter, moon], practice=practice)

    if idx == 2:
        opening = (
            "Чужие земли могут зажигать, а могут утомлять — у тебя свой тип «далеко»."
            if lang == "ru"
            else "Foreign lands can ignite or exhaust — you have your «far away» type."
        )
        detail = f"{plain_placement_line(locale, rahu)} {plain_lord_line(locale, chart, 9)}"
        practice = (
            "После поездки — один день «ничего» без планов. Иначе отпуск = просто другая работа."
            if lang == "ru"
            else "After a trip — one plan-free day. Otherwise vacation = different work."
        )
        return _pack(locale, question, opening, detail, markers_chart=[rahu, lord_of(chart, 9)], practice=practice)

    if idx == 3:
        opening = (
            "Дом vs дорога — не война, а баланс. Где корни, а где крылья."
            if lang == "ru"
            else "Home vs road — not war, balance. Where roots, where wings."
        )
        detail = f"{plain_lord_line(locale, chart, 4)} {plain_lord_line(locale, chart, 12)}"
        practice = (
            "Спроси: «мне нужен дом или движение сейчас?» — честный ответ экономит деньги."
            if lang == "ru"
            else "Ask: «do I need home or motion now?» — honest answer saves money."
        )
        return _pack(locale, question, opening, detail, markers_chart=[lord_of(chart, 4), lord_of(chart, 12)], practice=practice)

    opening = (
        "Эмиграция — большой шаг. Карта не говорит «да/нет», но показывает, где ты раскроешься, а где будешь скучать."
        if lang == "ru"
        else "Emigration is a big step. Chart won't say yes/no — but where you'll open vs miss home."
    )
    detail = f"{plain_placement_line(locale, rahu)} {plain_placement_line(locale, jupiter)}"
    practice = (
        "Пробный период или короткая поездка перед решением — не трусость, а разведка."
        if lang == "ru"
        else "Trial period or short trip before deciding — recon, not cowardice."
    )
    return _pack(locale, question, opening, detail, markers_chart=[rahu, jupiter], practice=practice)


def plain_upaya(chart: JyotishChart, locale: str, idx: int, question: str) -> StructuredQaAnswer:
    lang = _lang(locale)

    if idx == 0:
        focus = _debilitated(chart)[0] if _debilitated(chart) else chart.planets["SATURN"]
        opening = (
            "Гармонизация — не «купи камень и забудь». Сначала режим, честность и простые действия."
            if lang == "ru"
            else "Harmonizing isn't «buy a gem and forget». Routine and honesty first."
        )
        detail = f"Сейчас мягче всего поддержать: {plain_placement_line(locale, focus)}."
        practice = (
            "Без консультации — мантра и доброе дело безопаснее камня."
            if lang == "ru"
            else "Without consult — mantra and charity beat gems."
        )
        return _pack(locale, question, opening, detail, markers_chart=[focus], practice=practice)

    if idx == 1:
        focus = _strong(chart)[0] if _strong(chart) else chart.planets["JUPITER"]
        opening = (
            "Опора — там, где у тебя уже есть сила. Не чинить то, что и так держит."
            if lang == "ru"
            else "Support what already holds — don't fix what's fine."
        )
        detail = f"Опирайся на: {plain_placement_line(locale, focus)}."
        practice = (
            "Раз в неделю благодарность вслух — звучит cheesy, но переключает фокус."
            if lang == "ru"
            else "Weekly gratitude out loud — cheesy, but shifts focus."
        )
        return _pack(locale, question, opening, detail, markers_chart=[focus], practice=practice)

    if idx == 2:
        focus = _tense(chart)[0] if _tense(chart) else chart.planets["MARS"]
        opening = (
            "Снять напряжение — не «стать другим человеком», а чуть смягчить привычный удар."
            if lang == "ru"
            else "Ease tension — not «be someone else», soften the usual punch a bit."
        )
        detail = f"Тут аккуратнее: {plain_placement_line(locale, focus)}."
        practice = (
            "День без спешки и резких слов — мини-упайя, доступная бесплатно."
            if lang == "ru"
            else "A day without rush and sharp words — free mini-upaya."
        )
        return _pack(locale, question, opening, detail, markers_chart=[focus], practice=practice)

    if idx == 3:
        opening = (
            "Мантры и практики — как зарядка для головы: регулярность важнее громкости."
            if lang == "ru"
            else "Mantras and practice — brain gym: regularity beats volume."
        )
        detail = plain_placement_line(locale, chart.planets["JUPITER"])
        practice = (
            "2 минуты в день лучше, чем час раз в месяц «на героизме»."
            if lang == "ru"
            else "Two minutes daily beats one heroic hour monthly."
        )
        return _pack(locale, question, opening, detail, markers_chart=[chart.planets["JUPITER"]], practice=practice)

    opening = (
        "Камни — последний пункт списка, не первый. Сначала сон, слова и поведение."
        if lang == "ru"
        else "Gems are last on the list, not first. Sleep, words, behavior first."
    )
    detail = plain_placement_line(locale, chart.planets["VENUS"])
    practice = (
        "Если и камень — только после живого разговора с тем, кто в теме. Без импульса из рекламы."
        if lang == "ru"
        else "If gems at all — after talking to someone who knows. No ad impulse."
    )
    return _pack(locale, question, opening, detail, markers_chart=[chart.planets["VENUS"]], practice=practice)


def plain_popular(
    chart: JyotishChart,
    locale: str,
    idx: int,
    question: str,
    *,
    question_id: str,
) -> StructuredQaAnswer:
    lang = _lang(locale)
    strengths, weaknesses, _, opportunities = _derive_summary(chart, lang)
    lagna = sign_label(locale, chart.lagna_sign)
    essence = LAGNA_ESSENCE[lang][chart.lagna_sign]

    if question_id == "love":
        from app.family_qa_detail import build_family_structured
        return build_family_structured(chart, locale, 0, question, style="plain")
    if question_id == "career":
        return plain_finance(chart, locale, 1, question)
    if question_id == "money":
        return plain_finance(chart, locale, 0, question)

    if question_id == "theme":
        opening = (
            f"Главный сюжет жизни — не один дом, а то, куда утекает энергия. У тебя вход: {essence.lower()} ({lagna})."
            if lang == "ru"
            else f"Life's main plot — where energy leaks. Your entry: {essence.lower()} ({lagna})."
        )
        if chart.stellium_house:
            h = chart.stellium_house
            detail = f"Сейчас громче всего тема «{plain_area(locale, h)}» — как будто жизнь там ставит больше глав."
        elif chart.strong_houses:
            h = chart.strong_houses[0]
            detail = f"Ярче звучит {plain_area(locale, h)} — туда стоит смотреть в первую очередь."
        else:
            detail = "Сюжет распределён — ищи, где ты оживаешь без понтов."
        practice = (
            "Отметь, где тратишь больше всего сил — это и есть сериал, не фон."
            if lang == "ru"
            else "Note where you spend most energy — that's the show, not background."
        )
        return _pack(locale, question, opening, detail, markers_chart=[chart.planets["SUN"]], practice=practice)

    if question_id == "strength":
        opening = (
            "Сильные стороны — не для резюме, а для жизни, когда тяжело."
            if lang == "ru"
            else "Strengths aren't for résumés — for life when it's heavy."
        )
        detail = f"Опора: {_list_to_prose(strengths, lang)}."
        practice = (
            "Раз в неделю сознательно используй одну силу — как любимый lifehack."
            if lang == "ru"
            else "Once a week use one strength on purpose — favorite lifehack."
        )
        return _pack(locale, question, opening, detail, markers_chart=_strong(chart)[:2] or [chart.planets["SUN"]], practice=practice)

    opening = (
        f"Главная возможность — {opportunities}. Не обязана быть Instagram-worthy."
        if lang == "ru"
        else f"Main opportunity — {opportunities}. Needn't be Instagram-worthy."
    )
    detail = plain_placement_line(locale, chart.planets["JUPITER"])
    practice = (
        "Один маленький шаг в эту сторону на этой неделе."
        if lang == "ru"
        else "One small step that way this week."
    )
    return _pack(locale, question, opening, detail, markers_chart=[chart.planets["JUPITER"]], practice=practice)


def plain_house(
    chart: JyotishChart,
    locale: str,
    idx: int,
    question: str,
    *,
    house: int,
    focus: str = "default",
) -> StructuredQaAnswer:
    lang = _lang(locale)
    theme = plain_area(locale, house)
    in_h = planets_in_house(chart, house)
    lord_h = lord_of(chart, house)
    lagna_prefix = ""
    if house == 1 and idx == 0:
        lagna = sign_label(locale, chart.lagna_sign)
        essence = LAGNA_ESSENCE[lang][chart.lagna_sign]
        lagna_prefix = (
            f"С первого взгляда ты звучишь как «{essence.lower()}» ({lagna}). "
            if lang == "ru"
            else f"At first glance you read as «{essence.lower()}» ({lagna}). "
        )

    if focus == "strength":
        opening = (
            f"Где опора в «{theme}» — не медаль, а место, куда можно встать ногами."
            if lang == "ru"
            else f"Where you stand strong in «{theme}» — somewhere to plant your feet, not a trophy."
        )
        if in_h:
            best = max(in_h, key=rank_dignity)
            detail = lagna_prefix + plain_placement_line(locale, best)
            markers_chart = [best] + in_h[:1]
        else:
            detail = lagna_prefix + plain_lord_line(locale, chart, house)
            markers_chart = [lord_h]
        practice = (
            "Раз в неделю одно сознательное действие в этой теме — даже если оно скучное."
            if lang == "ru"
            else "Once a week one conscious act here — even if it's boring."
        )
    elif focus == "challenge":
        opening = (
            f"Что мешает в «{theme}» — не приговор, а сценарий, который любит повторяться."
            if lang == "ru"
            else f"What blocks «{theme}» — not a verdict, a script on rerun."
        )
        weak = [pl for pl in in_h if pl.dignity == "debilitated"] or [
            pl for pl in in_h if pl.key in {"MARS", "SATURN", "RAHU"}
        ]
        if weak:
            detail = lagna_prefix + plain_placement_line(locale, weak[0])
        elif not in_h:
            detail = lagna_prefix + plain_lord_line(locale, chart, house)
        else:
            pl = min(in_h, key=rank_dignity)
            detail = lagna_prefix + plain_placement_line(
                locale,
                pl,
                hint="нужна бережность" if lang == "ru" else "needs care",
            )
        practice = (
            "Назови вслух один повторяющийся сценарий — без суда, просто увидеть."
            if lang == "ru"
            else "Name one repeating scenario out loud — no trial, just see it."
        )
        markers_chart = (weak or in_h or [lord_h])[:2]
    else:
        opening = (
            f"Про «{theme}» — вот что карта подсвечивает в первую очередь."
            if lang == "ru"
            else f"On «{theme}» — what your chart spotlights first."
        )
        if in_h:
            bits = " ".join(plain_placement_line(locale, p) for p in in_h[:2])
            detail = lagna_prefix + bits + " " + plain_lord_line(locale, chart, house)
        else:
            detail = lagna_prefix + plain_lord_line(locale, chart, house)
        practice = (
            f"Неделя наблюдения: как «{theme}» проявляется в реальной жизни — без анализа, просто замечай."
            if lang == "ru"
            else f"Observe how «{theme}» shows up IRL for a week — notice, don't overthink."
        )
        markers_chart = in_h[:2] + [lord_h]

    return _pack(locale, question, opening, detail, markers_chart=markers_chart, practice=practice)


_PLAIN_BUILDERS = {
    "finance": plain_finance,
    "karma": plain_karma,
    "traits": plain_traits,
    "lineage": plain_lineage,
    "health": plain_health,
    "purpose": plain_purpose,
    "dharma": plain_dharma,
    "travel": plain_travel,
    "upaya": plain_upaya,
    "popular": plain_popular,
}


def build_plain_sphere_structured(
    block: str,
    chart: JyotishChart,
    locale: str,
    question_index: int,
    question: str,
    *,
    question_id: str = "",
) -> StructuredQaAnswer:
    idx = max(0, min(4, question_index))
    builder = _PLAIN_BUILDERS.get(block)
    if builder is None:
        raise ValueError(f"no plain builder for block: {block}")
    if block == "popular":
        return plain_popular(chart, locale, idx, question, question_id=question_id)
    return builder(chart, locale, idx, question)
