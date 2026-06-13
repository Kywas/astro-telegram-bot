"""Personal notes per focus block: practices, health, creativity."""

PHASE_KEYS = (
    "new_moon",
    "waxing_crescent",
    "first_quarter",
    "waxing_gibbous",
    "full_moon",
    "waning_gibbous",
    "last_quarter",
    "waning_crescent",
)

PHASE_ACCENT = {
    "ru": {
        "new_moon": {
            "color": "⚫",
            "label": "тишина и новый цикл",
            "affirmation": "Я открываю новый цикл с ясным намерением.",
        },
        "waxing_crescent": {
            "color": "🟢",
            "label": "рост и первые шаги",
            "affirmation": "Я уверенно делаю первые шаги к цели.",
        },
        "first_quarter": {
            "color": "🟡",
            "label": "действие и решимость",
            "affirmation": "Я действую спокойно и последовательно.",
        },
        "waxing_gibbous": {
            "color": "🔵",
            "label": "доводка и настройка",
            "affirmation": "Я улучшаю детали и сохраняю фокус.",
        },
        "full_moon": {
            "color": "🟣",
            "label": "пик и осознанность",
            "affirmation": "Я вижу результат и благодарю себя.",
        },
        "waning_gibbous": {
            "color": "🟠",
            "label": "делиться и отпускать напряжение",
            "affirmation": "Я делюсь опытом без давления на себя.",
        },
        "last_quarter": {
            "color": "🟤",
            "label": "упрощение и очищение",
            "affirmation": "Я отпускаю лишнее и освобождаю место.",
        },
        "waning_crescent": {
            "color": "⚪",
            "label": "отдых перед стартом",
            "affirmation": "Я восстанавливаюсь и готовлюсь к новому.",
        },
    },
    "en": {
        "new_moon": {
            "color": "⚫",
            "label": "quiet and a fresh cycle",
            "affirmation": "I open a new cycle with a clear intention.",
        },
        "waxing_crescent": {
            "color": "🟢",
            "label": "growth and first steps",
            "affirmation": "I take confident first steps toward my goal.",
        },
        "first_quarter": {
            "color": "🟡",
            "label": "action and resolve",
            "affirmation": "I act calmly and consistently.",
        },
        "waxing_gibbous": {
            "color": "🔵",
            "label": "refinement and tuning",
            "affirmation": "I refine details and keep my focus.",
        },
        "full_moon": {
            "color": "🟣",
            "label": "peak and awareness",
            "affirmation": "I see my progress and thank myself.",
        },
        "waning_gibbous": {
            "color": "🟠",
            "label": "sharing and easing tension",
            "affirmation": "I share experience without pressuring myself.",
        },
        "last_quarter": {
            "color": "🟤",
            "label": "simplifying and cleansing",
            "affirmation": "I release excess and make room.",
        },
        "waning_crescent": {
            "color": "⚪",
            "label": "rest before a new start",
            "affirmation": "I recover and prepare for what is next.",
        },
    },
}

PLAIN_PHASE_ACCENT = {
    "ru": {
        "new_moon": {"label": "тихий старт", "affirmation": "Сегодня я начинаю с одного простого шага."},
        "waxing_crescent": {"label": "нарастание сил", "affirmation": "Маленькие шаги складываются в результат."},
        "first_quarter": {"label": "время действовать", "affirmation": "Я делаю главное без спешки."},
        "waxing_gibbous": {"label": "доводка", "affirmation": "Я улучшаю то, что уже начал."},
        "full_moon": {"label": "пик дня", "affirmation": "Я замечаю, что уже получилось."},
        "waning_gibbous": {"label": "обмен и отклик", "affirmation": "Мне можно двигаться мягче."},
        "last_quarter": {"label": "убрать лишнее", "affirmation": "Я оставляю только нужное."},
        "waning_crescent": {"label": "пауза", "affirmation": "Отдых — часть моего прогресса."},
    },
    "en": {
        "new_moon": {"label": "quiet start", "affirmation": "Today I begin with one simple step."},
        "waxing_crescent": {"label": "building momentum", "affirmation": "Small steps add up."},
        "first_quarter": {"label": "time to act", "affirmation": "I do what matters without rushing."},
        "waxing_gibbous": {"label": "refinement", "affirmation": "I improve what I already started."},
        "full_moon": {"label": "peak moment", "affirmation": "I notice what already works."},
        "waning_gibbous": {"label": "exchange", "affirmation": "I can move more gently today."},
        "last_quarter": {"label": "trim excess", "affirmation": "I keep only what I need."},
        "waning_crescent": {"label": "pause", "affirmation": "Rest is part of my progress."},
    },
}

FOCUS_PERSONAL_HEADER = {
    "ru": {
        "practices": "📝 Практика дня",
        "health": "📝 Здоровье и уход",
        "creativity": "📝 Творческий совет",
    },
    "en": {
        "practices": "📝 Practice note",
        "health": "📝 Health & care",
        "creativity": "📝 Creative tip",
    },
}

PLAIN_FOCUS_PERSONAL_HEADER = {
    "ru": {
        "practices": "📝 На сегодня",
        "health": "📝 Про тело",
        "creativity": "📝 Идея дня",
    },
    "en": {
        "practices": "📝 For today",
        "health": "📝 Body care",
        "creativity": "📝 Idea of the day",
    },
}

# Короткое объяснение «почему так» — одно предложение
FOCUS_PHASE_HINT = {
    "ru": {
        "practices": {
            "new_moon": "Цикл только начался — хватит тишины и одной ясной мысли, героизм не нужен.",
            "waxing_crescent": "Энергия нарастает: короткая ежедневная практика сработает лучше редких «марафонов».",
            "first_quarter": "Хороший момент собраться — тело и внимание уже готовы к более собранной работе.",
            "waxing_gibbous": "Не хватает новых техник — углуби то, что уже даёт отклик.",
            "full_moon": "Эмоции обострены: завершай цикл спокойно, без перегруза и ночных экспериментов.",
            "waning_gibbous": "Пора делиться, но без давления — мягкость сейчас важнее результата.",
            "last_quarter": "Время упростить: оставь в практике только то, что реально наполняет.",
            "waning_crescent": "Организм и нервная система просят паузу — готовь почву для нового цикла.",
        },
        "health": {
            "new_moon": "Тело на перезагрузке — не лучший день для жёстких экспериментов с собой.",
            "waxing_crescent": "С каждым днём сил прибавляется: мягко подстраивай режим, не рви с места.",
            "first_quarter": "Хорошо идут умеренные нагрузки и простая еда — без подвига через «надо».",
            "waxing_gibbous": "Подстрой питание и сон — маленькие правки сейчас дают заметный эффект.",
            "full_moon": "Чувствительность выше: переедание и алкоголь ощущаются сильнее обычного.",
            "waning_gibbous": "Лёгкий разгрузочный день поможет телу отдохнуть без стресса для организма.",
            "last_quarter": "Убывающая Луна — время мягко отпустить лишнее в рационе и нагрузках.",
            "waning_crescent": "Восстановление важнее детокса: сон и простая еда — лучшая «процедура».",
        },
        "creativity": {
            "new_moon": "Сейчас сеешь идеи — не обязательно сразу делать большой проект.",
            "waxing_crescent": "Главное — начать: черновик лучше идеального плана в голове.",
            "first_quarter": "Фокус решает: одна доведённая задача лучше пяти начатых.",
            "waxing_gibbous": "Пора полировать — посмотри на работу свежим взглядом, как зритель.",
            "full_moon": "Эмоции на пике: покажи результат, но не принимай резких решений на всплеске.",
            "waning_gibbous": "Отклик других поможет увидеть слепые зоны — без сравнения с чужими успехами.",
            "last_quarter": "Смело убирай лишнее из проекта — останется только сильное.",
            "waning_crescent": "Не форсируй старт — дай голове отдохнуть, инсайты приходят в тишине.",
        },
    },
    "en": {
        "practices": {
            "new_moon": "The cycle is fresh — clarity beats volume; one intention is enough.",
            "waxing_crescent": "Energy is building: 10 minutes daily beats a rare hour-long session.",
            "first_quarter": "A good moment to gather focus — body and mind are ready for structure.",
            "waxing_gibbous": "Skip new techniques — deepen what already feels alive.",
            "full_moon": "Emotions run high: close the cycle gently, no overload or late experiments.",
            "waning_gibbous": "Share without pressure — softness matters more than measurable results.",
            "last_quarter": "Time to simplify: keep only what truly nourishes your practice.",
            "waning_crescent": "Your nervous system asks for pause — prepare ground for a new cycle.",
        },
        "health": {
            "new_moon": "Your body is resetting — not the best day for harsh experiments.",
            "waxing_crescent": "Strength grows daily: tune your routine gently, don’t shock the system.",
            "first_quarter": "Moderate movement and simple food work well — avoid pushing through guilt.",
            "waxing_gibbous": "Small tweaks to meals and sleep pay off noticeably now.",
            "full_moon": "Sensitivity is higher: overeating and alcohol hit harder than usual.",
            "waning_gibbous": "A light unloading day helps the body rest without stress.",
            "last_quarter": "Waning Moon — gently release excess in food and workload.",
            "waning_crescent": "Recovery beats detox: sleep and simple food are the best care.",
        },
        "creativity": {
            "new_moon": "You’re planting ideas — a big launch can wait.",
            "waxing_crescent": "Starting matters: a draft beats a perfect plan in your head.",
            "first_quarter": "Focus wins: one finished task beats five started ones.",
            "waxing_gibbous": "Polish time — look at your work as a viewer would.",
            "full_moon": "Emotions peak: show your work, but avoid sharp decisions on a high.",
            "waning_gibbous": "Feedback reveals blind spots — without comparing to others.",
            "last_quarter": "Cut the excess from the project — keep what’s strong.",
            "waning_crescent": "Don’t force a launch — rest feeds the next insight.",
        },
    },
}

PLAIN_FOCUS_PHASE_HINT = {
    "ru": {
        "practices": {
            "new_moon": "Не нужно много — хватит тишины и одной понятной мысли.",
            "waxing_crescent": "Лучше понемногу каждый день, чем редко и через силу.",
            "first_quarter": "Сейчас удобно собраться и сделать практику чуть серьёзнее.",
            "waxing_gibbous": "Не меняй всё — углуби то, что уже помогает.",
            "full_moon": "Эмоции ярче: завершай спокойно, без перегруза.",
            "waning_gibbous": "Можно делиться, но без давления на себя.",
            "last_quarter": "Оставь в практике только главное.",
            "waning_crescent": "Тело просит паузу — это нормально.",
        },
        "health": {
            "new_moon": "День для мягкого режима, не для жёстких экспериментов.",
            "waxing_crescent": "Силы растут — добавляй привычки постепенно.",
            "first_quarter": "Подойдут прогулки и простая еда.",
            "waxing_gibbous": "Маленькие правки в сне и еде уже помогают.",
            "full_moon": "Легче переесть — будь внимательнее к порциям.",
            "waning_gibbous": "Простой день без тяжёлой еды — хорошая разгрузка.",
            "last_quarter": "Время чуть упростить рацион.",
            "waning_crescent": "Сон сейчас важнее любого детокса.",
        },
        "creativity": {
            "new_moon": "Запиши идеи — большой старт может подождать.",
            "waxing_crescent": "Главное — начать, не жди идеала.",
            "first_quarter": "Один проект за раз — так проще довести до конца.",
            "waxing_gibbous": "Проверь работу: что можно улучшить?",
            "full_moon": "Покажи результат, но не решай резко на эмоциях.",
            "waning_gibbous": "Спроси мнение — без сравнения с другими.",
            "last_quarter": "Убери лишнее из плана.",
            "waning_crescent": "Отдых тоже часть творчества.",
        },
    },
    "en": {
        "practices": {
            "new_moon": "You don’t need much — quiet and one clear thought are enough.",
            "waxing_crescent": "A little every day beats rare forced sessions.",
            "first_quarter": "Good time to focus and take practice a step deeper.",
            "waxing_gibbous": "Don’t swap methods — deepen what works.",
            "full_moon": "Emotions run bright: finish calmly, no overload.",
            "waning_gibbous": "Share gently, without pressuring yourself.",
            "last_quarter": "Keep only what matters in your practice.",
            "waning_crescent": "Your body asks for pause — that’s OK.",
        },
        "health": {
            "new_moon": "A soft routine day, not harsh experiments.",
            "waxing_crescent": "Energy grows — add habits gradually.",
            "first_quarter": "Walks and simple food fit well.",
            "waxing_gibbous": "Small sleep and meal tweaks already help.",
            "full_moon": "Easier to overeat — watch portions.",
            "waning_gibbous": "A simple food day is a good unload.",
            "last_quarter": "Time to simplify meals a bit.",
            "waning_crescent": "Sleep beats any detox now.",
        },
        "creativity": {
            "new_moon": "Note ideas — a big launch can wait.",
            "waxing_crescent": "Start first, don’t wait for perfect.",
            "first_quarter": "One project at a time finishes faster.",
            "waxing_gibbous": "Check your work: what can improve?",
            "full_moon": "Show progress, don’t decide sharply on emotion.",
            "waning_gibbous": "Ask for feedback — skip comparison.",
            "last_quarter": "Trim excess from the plan.",
            "waning_crescent": "Rest is part of creating too.",
        },
    },
}

# Personal recommendations per focus × phase
FOCUS_PERSONAL_NOTES: dict[str, dict[str, dict[str, list[str]]]] = {
    "ru": {
        "practices": {
            "new_moon": [
                "🧘 Сядь удобно, 5–10 мин тишины: «Что я хочу в этом цикле?» — одна фраза",
                "🌬 Дыхание 4-4-6: вдох на 4, пауза 4, медленный выдох на 6",
                "📌 Запиши намерение на бумаге — так оно не растворится в суете",
            ],
            "waxing_crescent": [
                "🧘 Утром 10 мин — та же практика, что вчера: так растут привычки",
                "🌬 «Квадрат»: вдох 4 — задержка 4 — выдох 4 — задержка 4",
                "📌 Отметь в календаре: даже 7 минут считаются",
            ],
            "first_quarter": [
                "🧘 15 мин собранной практики: мантра, концентрация или медитация на дыхании",
                "🌬 2–3 мин «огонь»: быстрый вдох носом, сильный выдох ртом — только если нет головокружения",
                "📌 Перед началом спроси себя: «Зачем я сейчас сажусь?»",
            ],
            "waxing_gibbous": [
                "🧘 Не меняй технику — добавь глубины: медленнее, внимательнее",
                "🌬 Выдох в полтора-два раза длиннее вдоха — успокаивает и фокусирует",
                "📌 Заметь, что в практике уже работает — усили это",
            ],
            "full_moon": [
                "🧘 Медитация благодарности: 3 вещи, которые получились за цикл",
                "🌬 Дыши животом 5–7 мин — без цели «добиться просветления»",
                "📌 Заверши практику спокойно, не на адреналине",
            ],
            "waning_gibbous": [
                "🧘 Мягкая практика: растяжка, тихое сидение, без «надо успеть»",
                "🌬 На выдохе опускай плечи — «волна» расслабления",
                "📌 Можно рассказать близкому, что тебе помогло — без поучений",
            ],
            "last_quarter": [
                "🧘 5–7 мин «отпускание»: что в практике уже не нужно?",
                "🌬 С каждым выдохом представляй, как уходит лишнее напряжение",
                "📌 Оставь одну-две техники на цикл — не десять",
            ],
            "waning_crescent": [
                "🧘 Body scan перед сном: пройди вниманием от макушки до стоп",
                "🌬 Самое мягкое дыхание — без контроля и оценки",
                "📌 Новый длинный курс — после новолуния, не сейчас",
            ],
        },
        "health": {
            "new_moon": [
                "🥗 Простая еда: суп, овощи, немного белка — без тяжёлого на ночь",
                "😴 Ложись в привычное время: сон задаёт тон всему циклу",
                "💇 Стрижку и агрессивные процедуры лучше перенести на 1–2 дня",
            ],
            "waxing_crescent": [
                "💧 Стакан воды утром и между приёмами пищи — простой якорь",
                "🚶 20–30 мин прогулки уже считаются активностью",
                "💇 Растущая Луна: если стрижешь — для роста и объёма волос",
            ],
            "first_quarter": [
                "🏃 Тренировка в меру: пульс можно поднять, но без «добей себя»",
                "🥗 Белок + овощи в каждый приём — стабильная энергия",
                "💇 Маска или масло на кончики — питание на фазе роста",
            ],
            "waxing_gibbous": [
                "🥗 Меньше сахара и кофе «чтобы не уснуть» — тело и так на подъёме",
                "🛌 Следи за сном: 7–8 ч помогают не срываться на перекусы",
                "💇 Растущая Луна — удачное время для стрижки и укладки",
            ],
            "full_moon": [
                "🍵 Ешь медленнее, порции меньше — насыщение приходит с задержкой",
                "🚫 Алкоголь и острое сегодня ощущаются сильнее",
                "💇 Не экспериментируй с кардинальной сменой образа",
            ],
            "waning_gibbous": [
                "🥗 Разгрузочный день: каша, суп, салат, травяной чай",
                "🧖 Тёплая ванна или контрастный душ — без перегрева",
                "🚶 Прогулка на свежем воздухе помогает «переварить» неделю",
            ],
            "last_quarter": [
                "💧 Вода, зелень, меньше сладкого — мягкое очищение без голодания",
                "🥗 Убери из холодильника то, от чего срываешься автоматически",
                "💇 Убывающая Луна: стрижка помогает «укрепить» структуру волос",
            ],
            "waning_crescent": [
                "😴 Сон 8+ часов, если получается — лучше любого детокса",
                "🥗 Простая еда: не голодай и не перегружай желудок",
                "💇 Только мягкий уход — без кислот, агрессивного окрашивания",
            ],
        },
        "creativity": {
            "new_moon": [
                "📝 3 идеи в блокнот — без оценки «годится / не годится»",
                "🎨 Мини-доска настроения: 5 картинок или слов, как ты видишь цикл",
                "💬 «Я начинаю с малого — и этого достаточно»",
            ],
            "waxing_crescent": [
                "✏️ 20 мин черновика: текст, эскиз, набросок — главное движение",
                "🎯 Выбери один формат и попробуй, не пять сразу",
                "💬 «Несовершенный старт лучше идеального ожидания»",
            ],
            "first_quarter": [
                "🎯 Один проект в фокусе — остальное в список «потом»",
                "✂️ Вырежь лишнее из задачи: что можно сделать за 1–2 часа?",
                "💬 «Я довожу до формы, а не до идеала»",
            ],
            "waxing_gibbous": [
                "🔍 Прочитай/посмотри работу глазами зрителя — что бросается?",
                "🛠 Одна правка, которая сильнее всего улучшит результат",
                "💬 «Детали оживляют, перфекционизм тормозит»",
            ],
            "full_moon": [
                "🎉 Покажи другу, в stories или себе в дневнике — зафиксируй прогресс",
                "📸 Сохрани «до/после» — через месяц будет приятно",
                "💬 «Я вижу, сколько уже сделано»",
            ],
            "waning_gibbous": [
                "💬 Спроси 1–2 доверенных людей: «Что понятно? Что улучшить?»",
                "🙏 Отметь, за что благодарен в процессе — не только за результат",
                "💬 «Отклик — подсказка, не приговор»",
            ],
            "last_quarter": [
                "🗂️ Убери из проекта слабые куски — смело, но не импульсивно",
                "📋 Перепиши план на следующий цикл короче",
                "💬 «Меньше, но сильнее»",
            ],
            "waning_crescent": [
                "📓 5 мин дневника: какие мысли приходят, когда не форсируешь",
                "☁️ Brainstorm без обязательств — список «может быть когда-нибудь»",
                "💬 «Пауза — топливо для следующего витка»",
            ],
        },
    },
    "en": {
        "practices": {
            "new_moon": [
                "🧘 Sit comfortably, 5–10 min quiet: “What do I want this cycle?” — one phrase",
                "🌬 4-4-6 breath: inhale 4, pause 4, slow exhale 6",
                "📌 Write the intention on paper — so it doesn’t vanish in the rush",
            ],
            "waxing_crescent": [
                "🧘 10 min in the morning — same practice as yesterday: habits grow this way",
                "🌬 Box breath: inhale 4 — hold 4 — exhale 4 — hold 4",
                "📌 Mark it in your calendar: even 7 minutes count",
            ],
            "first_quarter": [
                "🧘 15 min focused practice: mantra, concentration, or breath meditation",
                "🌬 2–3 min “fire breath”: quick inhale, strong exhale — only if no dizziness",
                "📌 Before you start, ask: “Why am I sitting down now?”",
            ],
            "waxing_gibbous": [
                "🧘 Don’t swap techniques — add depth: slower, more attentive",
                "🌬 Exhale 1.5–2× longer than inhale — calms and focuses",
                "📌 Notice what already works in your practice — strengthen that",
            ],
            "full_moon": [
                "🧘 Gratitude meditation: 3 things that worked this cycle",
                "🌬 Belly breathing 5–7 min — no goal to “achieve enlightenment”",
                "📌 Finish calmly, not on adrenaline",
            ],
            "waning_gibbous": [
                "🧘 Gentle practice: stretch, quiet sitting, no “must finish”",
                "🌬 Drop shoulders on each exhale — a “wave” of release",
                "📌 You may share what helped you with someone close — without preaching",
            ],
            "last_quarter": [
                "🧘 5–7 min “release”: what in your practice is no longer needed?",
                "🌬 With each exhale, imagine extra tension leaving",
                "📌 Keep 1–2 techniques for the cycle — not ten",
            ],
            "waning_crescent": [
                "🧘 Body scan before sleep: attention from crown to feet",
                "🌬 The softest breath — no control, no judging",
                "📌 A new long course — after the new Moon, not now",
            ],
        },
        "health": {
            "new_moon": [
                "🥗 Simple food: soup, vegetables, some protein — nothing heavy at night",
                "😴 Sleep at your usual time: sleep sets the tone for the whole cycle",
                "💇 Postpone cuts and aggressive treatments for 1–2 days",
            ],
            "waxing_crescent": [
                "💧 A glass of water in the morning and between meals — an easy anchor",
                "🚶 A 20–30 min walk already counts as activity",
                "💇 Waxing Moon: if you cut — for growth and volume",
            ],
            "first_quarter": [
                "🏃 Train in moderation: raise pulse, but no “destroy yourself”",
                "🥗 Protein + vegetables each meal — steady energy",
                "💇 Mask or oil on ends — nourishment in the growth phase",
            ],
            "waxing_gibbous": [
                "🥗 Less sugar and coffee “to stay awake” — your body is already up",
                "🛌 Watch sleep: 7–8 h help avoid snack crashes",
                "💇 Waxing Moon — a good time for cut and styling",
            ],
            "full_moon": [
                "🍵 Eat slower, smaller portions — fullness comes with a delay",
                "🚫 Alcohol and spicy food hit harder today",
                "💇 Don’t experiment with a drastic image change",
            ],
            "waning_gibbous": [
                "🥗 Unloading day: porridge, soup, salad, herbal tea",
                "🧖 Warm bath or contrast shower — no overheating",
                "🚶 A walk outdoors helps “digest” the week",
            ],
            "last_quarter": [
                "💧 Water, greens, less sugar — gentle cleanse without fasting",
                "🥗 Remove from the fridge what triggers automatic bingeing",
                "💇 Waning Moon: a cut helps “strengthen” hair structure",
            ],
            "waning_crescent": [
                "😴 8+ hours sleep if you can — better than any detox",
                "🥗 Simple food: don’t starve and don’t overload the stomach",
                "💇 Gentle care only — no acids, harsh coloring",
            ],
        },
        "creativity": {
            "new_moon": [
                "📝 3 ideas in a notebook — no “good / bad” judging",
                "🎨 Tiny mood board: 5 images or words for how you see the cycle",
                "💬 “I start small — and that’s enough”",
            ],
            "waxing_crescent": [
                "✏️ 20 min draft: text, sketch, outline — movement matters most",
                "🎯 Pick one format and try it, not five at once",
                "💬 “An imperfect start beats perfect waiting”",
            ],
            "first_quarter": [
                "🎯 One project in focus — park the rest for later",
                "✂️ Trim the task: what can you do in 1–2 hours?",
                "💬 “I bring it into form, not into perfection”",
            ],
            "waxing_gibbous": [
                "🔍 Read/view your work as a viewer — what stands out?",
                "🛠 One edit that improves the result most",
                "💬 “Details bring life; perfectionism slows you down”",
            ],
            "full_moon": [
                "🎉 Show a friend, in stories, or in your journal — capture progress",
                "📸 Save a before/after — nice to see in a month",
                "💬 “I see how much is already done”",
            ],
            "waning_gibbous": [
                "💬 Ask 1–2 trusted people: “What’s clear? What to improve?”",
                "🙏 Note what you’re grateful for in the process — not only the outcome",
                "💬 “Feedback is a hint, not a verdict”",
            ],
            "last_quarter": [
                "🗂️ Cut weak parts from the project — boldly, not impulsively",
                "📋 Rewrite the next cycle’s plan shorter",
                "💬 “Less, but stronger”",
            ],
            "waning_crescent": [
                "📓 5 min journal: what thoughts come when you don’t force",
                "☁️ Obligation-free brainstorm — a “maybe someday” list",
                "💬 “Pause is fuel for the next turn”",
            ],
        },
    },
}

PLAIN_FOCUS_PERSONAL_NOTES: dict[str, dict[str, dict[str, list[str]]]] = {
    "ru": {
        "practices": {
            "new_moon": [
                "Помолчи 5–10 мин и сформулируй одну мысль на цикл.",
                "Подыши: вдох 4, пауза 4, выдох 6.",
                "Запиши намерение — так проще не забыть.",
            ],
            "waxing_crescent": [
                "Короткая утренняя пауза — та же практика, что вчера.",
                "Ровное дыхание «квадрат» 4×4.",
                "Даже 7 минут в день уже работают.",
            ],
            "first_quarter": [
                "15 мин сосредоточенной практики.",
                "Дыхание чуть активнее обычного — без перегруза.",
                "Перед началом спроси себя: зачем я это делаю?",
            ],
            "waxing_gibbous": [
                "Углуби то, что уже делаешь — медленнее и внимательнее.",
                "Выдох длиннее вдоха — помогает собраться.",
                "Не меняй метод, усили то, что откликается.",
            ],
            "full_moon": [
                "Спокойная благодарность себе — 3 вещи за цикл.",
                "Медленное дыхание животом 5–7 мин.",
                "Заверши без спешки и перегруза.",
            ],
            "waning_gibbous": [
                "Мягкая практика без напора.",
                "На выдохе опускай плечи.",
                "Можно рассказать близкому, что помогло.",
            ],
            "last_quarter": [
                "Короткая пауза «отпустить лишнее» 5–7 мин.",
                "Оставь 1–2 техники на цикл.",
            ],
            "waning_crescent": [
                "Тишина или расслабление перед сном.",
                "Body scan от макушки до стоп.",
                "Новый длинный курс — после новолуния.",
            ],
        },
        "health": {
            "new_moon": [
                "Лёгкая еда: суп, овощи, без тяжёлого на ночь.",
                "Ложись в привычное время.",
                "Стрижку и процедуры лучше отложить на 1–2 дня.",
            ],
            "waxing_crescent": [
                "Пей больше воды — стакан утром и между едой.",
                "20–30 мин прогулки уже полезны.",
                "На растущей Луне стрижка — для роста волос.",
            ],
            "first_quarter": [
                "Движение в меру — без «добей себя».",
                "Белок и овощи в каждый приём.",
                "Маска или масло на кончики — уход на рост.",
            ],
            "waxing_gibbous": [
                "Подстрой питание и сон — маленькие шаги.",
                "Меньше сахара и кофе «на силу».",
                "Стрижка на растущей — для объёма.",
            ],
            "full_moon": [
                "Ешь проще и медленнее — порции меньше.",
                "Алкоголь и острое сегодня ощущаются сильнее.",
                "Не меняй образ резко.",
            ],
            "waning_gibbous": [
                "Разгрузочный день: каша, суп, салат.",
                "Прогулка и тёплая ванна без перегрева.",
            ],
            "last_quarter": [
                "Мягкое очищение: вода, зелень, меньше сладкого.",
                "На убывающей стрижка укрепляет волосы.",
            ],
            "waning_crescent": [
                "Сон 8+ часов — лучше любого детокса.",
                "Простая еда, минимум агрессивных процедур.",
            ],
        },
        "creativity": {
            "new_moon": [
                "Запиши 3 идеи — без оценки.",
                "Короткое намерение: «с чего начну в этом цикле?»",
                "«Я начинаю с малого».",
            ],
            "waxing_crescent": [
                "Черновик 20 мин — главное начать.",
                "Один формат, не пять сразу.",
            ],
            "first_quarter": [
                "Один проект — главный.",
                "Что можно сделать за 1–2 часа сегодня?",
            ],
            "waxing_gibbous": [
                "Посмотри работу свежим взглядом.",
                "Одна правка, которая сильнее всего поможет.",
            ],
            "full_moon": [
                "Показать или отметить результат — зафиксировать прогресс.",
                "Не решай резко на эмоциях.",
            ],
            "waning_gibbous": [
                "Спросить мнение у 1–2 близких.",
                "Отклик — подсказка, не приговор.",
            ],
            "last_quarter": [
                "Убрать лишнее из планов — оставить сильное.",
                "Переписать план короче.",
            ],
            "waning_crescent": [
                "Записать мысли в блокнот 5 мин.",
                "Список идей «может быть потом» — без обязательств.",
            ],
        },
    },
    "en": {
        "practices": {
            "new_moon": [
                "5–10 min quiet and one clear thought for the cycle.",
                "Breath: inhale 4, pause 4, exhale 6.",
                "Write the intention down.",
            ],
            "waxing_crescent": [
                "Short morning pause — same practice as yesterday.",
                "Box breathing 4×4.",
                "Even 7 minutes a day count.",
            ],
            "first_quarter": [
                "15 min focused practice.",
                "Slightly active breath — no overload.",
                "Ask yourself why before you start.",
            ],
            "waxing_gibbous": [
                "Deepen what works — slower and more attentive.",
                "Longer exhales help you focus.",
                "Don’t swap methods — strengthen what responds.",
            ],
            "full_moon": [
                "Quiet gratitude — 3 things this cycle.",
                "Slow belly breathing 5–7 min.",
                "Finish without rush or overload.",
            ],
            "waning_gibbous": [
                "Gentle practice, no forcing.",
                "Shoulders down on each exhale.",
                "Share what helped with someone close.",
            ],
            "last_quarter": [
                "Brief “let go” pause 5–7 min.",
                "Keep 1–2 techniques for the cycle.",
            ],
            "waning_crescent": [
                "Silence or relaxation before sleep.",
                "Body scan from head to feet.",
                "A new long course — after the new Moon.",
            ],
        },
        "health": {
            "new_moon": [
                "Light food: soup, vegetables, nothing heavy at night.",
                "Sleep at your usual time.",
                "Postpone cuts and treatments for 1–2 days.",
            ],
            "waxing_crescent": [
                "Hydrate — a glass in the morning and between meals.",
                "A 20–30 min walk already helps.",
                "Waxing Moon — cut for hair growth.",
            ],
            "first_quarter": [
                "Moderate movement — no pushing through pain.",
                "Protein and vegetables each meal.",
                "Mask or oil on ends — growth care.",
            ],
            "waxing_gibbous": [
                "Tune meals and sleep — small steps.",
                "Less sugar and caffeine to push through.",
                "Waxing cut for volume.",
            ],
            "full_moon": [
                "Eat simply and slowly — smaller portions.",
                "Alcohol and spicy food hit harder today.",
                "No drastic image changes.",
            ],
            "waning_gibbous": [
                "Unloading day: porridge, soup, salad.",
                "A walk and warm bath without overheating.",
            ],
            "last_quarter": [
                "Gentle cleanse: water, greens, less sugar.",
                "Waning Moon — cut strengthens hair.",
            ],
            "waning_crescent": [
                "8+ hours sleep beats any detox.",
                "Simple food, minimal harsh treatments.",
            ],
        },
        "creativity": {
            "new_moon": [
                "Write 3 ideas — no judging.",
                "Short intention: “Where do I start this cycle?”",
                "“I start small.”",
            ],
            "waxing_crescent": [
                "20 min draft — starting matters most.",
                "One format, not five at once.",
            ],
            "first_quarter": [
                "One main project.",
                "What can you do in 1–2 hours today?",
            ],
            "waxing_gibbous": [
                "Look at your work with fresh eyes.",
                "One edit that helps most.",
            ],
            "full_moon": [
                "Show or mark progress — capture it.",
                "Don’t decide sharply on emotion.",
            ],
            "waning_gibbous": [
                "Ask 1–2 people you trust.",
                "Feedback is a hint, not a verdict.",
            ],
            "last_quarter": [
                "Trim plans — keep what’s strong.",
                "Rewrite the plan shorter.",
            ],
            "waning_crescent": [
                "Journal thoughts for 5 min.",
                "A “maybe later” idea list — no obligations.",
            ],
        },
    },
}
