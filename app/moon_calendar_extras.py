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

# Personal recommendations per focus × phase (2 lines each)
FOCUS_PERSONAL_NOTES: dict[str, dict[str, dict[str, list[str]]]] = {
    "ru": {
        "practices": {
            "new_moon": [
                "🧘 Медитация 5–10 мин: одно намерение, без спешки",
                "🌬 Дыхание 4-4-6 — вдох, пауза, длинный выдох",
            ],
            "waxing_crescent": [
                "🧘 Утренняя практика 10 мин — закрепи привычку",
                "🌬 «Квадрат» 4×4: вдох–задержка–выдох–задержка",
            ],
            "first_quarter": [
                "🧘 Активная медитация или мантра 15 мин",
                "🌬 «Огонь» 2–3 мин: быстрый вдох через нос, выдох через рот",
            ],
            "waxing_gibbous": [
                "🧘 Углуби текущую практику, не меняй технику",
                "🌬 Замедли ритм: выдох в 1,5–2 раза длиннее вдоха",
            ],
            "full_moon": [
                "🧘 Медитация благодарности — что получилось за цикл",
                "🌬 Спокойное дыхание животом 5–7 мин",
            ],
            "waning_gibbous": [
                "🧘 Мягкая практика без цели «добиться»",
                "🌬 «Волна»: плечи вниз на каждом выдохе",
            ],
            "last_quarter": [
                "🧘 Короткая практика «отпускание» — 5–7 мин",
                "🌬 С каждым выдохом отпускай напряжение в теле",
            ],
            "waning_crescent": [
                "🧘 Тишина или body scan перед сном",
                "🌬 Самое мягкое дыхание, без контроля",
            ],
        },
        "health": {
            "new_moon": [
                "🥗 Разгрузка: простая еда, без тяжёлого вечером",
                "💇 Косметику и стрижку лучше отложить на 1–2 дня",
            ],
            "waxing_crescent": [
                "💧 Больше воды, лёгкие супы и овощи",
                "💇 Растущая Луна: стрижка стимулирует рост волос",
            ],
            "first_quarter": [
                "🏃 Умеренная активность, не через боль",
                "💇 Маски и питание кончиков — уход на рост",
            ],
            "waxing_gibbous": [
                "🥗 Подстрой рацион, меньше сахара и кофе «на силу»",
                "💇 Растущая Луна: стрижка/укладка — для объёма",
            ],
            "full_moon": [
                "🍵 Простая еда, без переедания и алкоголя",
                "💇 Не экспериментируй с резкой сменой образа",
            ],
            "waning_gibbous": [
                "🥗 Разгрузочный день: каша, овощи, травяной чай",
                "🧖 Лёгкая ванна или сауна — без перегрева",
            ],
            "last_quarter": [
                "💧 Мягкое очищение: вода, зелень, без сладкого",
                "💇 Убывающая Луна: стрижка укрепляет структуру волос",
            ],
            "waning_crescent": [
                "😴 Сон важнее жёсткого детокса",
                "💇 Укрепляющий уход, минимум агрессивных процедур",
            ],
        },
        "creativity": {
            "new_moon": [
                "📝 Запиши 3 идеи или набросок vision-board",
                "💬 «Я создаю с радостью и без спешки»",
            ],
            "waxing_crescent": [
                "✏️ Черновик без самокритики — главное начать",
                "💬 «Мой первый шаг уже ценен»",
            ],
            "first_quarter": [
                "🎯 Один главный проект, остальное — в список «потом»",
                "💬 «Я довожу начатое до формы»",
            ],
            "waxing_gibbous": [
                "🔍 Финальные правки и тест «как это выглядит со стороны»",
                "💬 «Детали делают работу живой»",
            ],
            "full_moon": [
                "🎉 Покажи работу или отметь прогресс — даже маленький",
                "💬 «Я вижу свой результат»",
            ],
            "waning_gibbous": [
                "💬 Собери отклик: 1–2 человека, которым доверяешь",
                "💬 «Обратная связь помогает расти»",
            ],
            "last_quarter": [
                "🗂️ Убери лишнее из проекта, оставь сильное",
                "💬 «Я оставляю только нужное»",
            ],
            "waning_crescent": [
                "📓 Дневник инсайтов — 5 мин перед сном",
                "💬 «Пауза питает воображение»",
            ],
        },
    },
    "en": {
        "practices": {
            "new_moon": [
                "🧘 5–10 min meditation: one intention, no rush",
                "🌬 4-4-6 breath — inhale, pause, long exhale",
            ],
            "waxing_crescent": [
                "🧘 10 min morning practice — anchor the habit",
                "🌬 Box breathing 4×4",
            ],
            "first_quarter": [
                "🧘 15 min active meditation or mantra",
                "🌬 “Fire breath” 2–3 min: quick inhale, strong exhale",
            ],
            "waxing_gibbous": [
                "🧘 Deepen your current practice, don’t swap techniques",
                "🌬 Slow down: exhale 1.5–2× longer than inhale",
            ],
            "full_moon": [
                "🧘 Gratitude meditation — what worked this cycle",
                "🌬 Calm belly breathing 5–7 min",
            ],
            "waning_gibbous": [
                "🧘 Gentle practice with no “must achieve”",
                "🌬 “Wave breath”: shoulders down on each exhale",
            ],
            "last_quarter": [
                "🧘 Short “release” practice — 5–7 min",
                "🌬 Let tension go with each exhale",
            ],
            "waning_crescent": [
                "🧘 Silence or body scan before sleep",
                "🌬 Very soft breathing, no forcing",
            ],
        },
        "health": {
            "new_moon": [
                "🥗 Light meals, nothing heavy in the evening",
                "💇 Postpone major beauty changes for 1–2 days",
            ],
            "waxing_crescent": [
                "💧 More water, light soups and vegetables",
                "💇 Waxing Moon: a cut may boost hair growth",
            ],
            "first_quarter": [
                "🏃 Moderate activity, not through pain",
                "💇 Masks and nourishing ends — growth care",
            ],
            "waxing_gibbous": [
                "🥗 Tune meals; less sugar and “push-through” caffeine",
                "💇 Waxing Moon: cut/style for volume",
            ],
            "full_moon": [
                "🍵 Simple food, no overeating or alcohol",
                "💇 Avoid drastic image experiments",
            ],
            "waning_gibbous": [
                "🥗 Unloading day: grains, vegetables, herbal tea",
                "🧖 Light bath or sauna — no overheating",
            ],
            "last_quarter": [
                "💧 Gentle cleanse: water, greens, less sugar",
                "💇 Waning Moon: a cut strengthens hair structure",
            ],
            "waning_crescent": [
                "😴 Sleep beats harsh detox",
                "💇 Strengthening care, minimal harsh treatments",
            ],
        },
        "creativity": {
            "new_moon": [
                "📝 Write 3 ideas or a tiny vision-board sketch",
                "💬 “I create with joy and without rush”",
            ],
            "waxing_crescent": [
                "✏️ Draft without self-criticism — start first",
                "💬 “My first step already counts”",
            ],
            "first_quarter": [
                "🎯 One main project; park the rest for later",
                "💬 “I bring work into form”",
            ],
            "waxing_gibbous": [
                "🔍 Final edits; test how it reads for others",
                "💬 “Details make the work alive”",
            ],
            "full_moon": [
                "🎉 Show your work or mark progress — even small",
                "💬 “I see my result”",
            ],
            "waning_gibbous": [
                "💬 Gather feedback from 1–2 people you trust",
                "💬 “Feedback helps me grow”",
            ],
            "last_quarter": [
                "🗂️ Cut excess from the project, keep the strong parts",
                "💬 “I keep only what I need”",
            ],
            "waning_crescent": [
                "📓 Insight journal — 5 min before sleep",
                "💬 “Pause feeds imagination”",
            ],
        },
    },
}

PLAIN_FOCUS_PERSONAL_NOTES: dict[str, dict[str, dict[str, list[str]]]] = {
    "ru": {
        "practices": {
            "new_moon": ["Помолчи 5 мин.", "Подыши: вдох 4, выдох 6."],
            "waxing_crescent": ["Короткая утренняя пауза.", "Ровное дыхание «квадрат»."],
            "first_quarter": ["15 мин сосредоточенной практики.", "Дыхание чуть активнее обычного."],
            "waxing_gibbous": ["Углуби то, что уже делаешь.", "Выдох длиннее вдоха."],
            "full_moon": ["Спокойная благодарность себе.", "Медленное дыхание."],
            "waning_gibbous": ["Мягкая практика без напора."],
            "last_quarter": ["Короткая пауза «отпустить лишнее»."],
            "waning_crescent": ["Тишина или расслабление перед сном."],
        },
        "health": {
            "new_moon": ["Лёгкая еда.", "Стрижку и процедуры лучше отложить."],
            "waxing_crescent": ["Пей больше воды.", "На растущей Луне стрижка — для роста."],
            "first_quarter": ["Движение в меру.", "Питательный уход за волосами."],
            "waxing_gibbous": ["Подстрой питание.", "Стрижка на растущей — для объёма."],
            "full_moon": ["Ешь проще.", "Не меняй образ резко."],
            "waning_gibbous": ["Разгрузочный день: простая еда, прогулка."],
            "last_quarter": ["Мягкое очищение без сахара.", "На убывающей стрижка укрепляет волосы."],
            "waning_crescent": ["Сон важнее детокса.", "Минимум процедур."],
        },
        "creativity": {
            "new_moon": ["Запиши 3 идеи.", "«Я начинаю с малого»."],
            "waxing_crescent": ["Черновик без критики."],
            "first_quarter": ["Один проект — главный."],
            "waxing_gibbous": ["Допилить и проверить."],
            "full_moon": ["Показать или отметить результат."],
            "waning_gibbous": ["Спросить мнение у близкого человека."],
            "last_quarter": ["Убрать лишнее из планов."],
            "waning_crescent": ["Записать мысли в блокнот."],
        },
    },
    "en": {
        "practices": {
            "new_moon": ["5 min quiet.", "Breath: inhale 4, exhale 6."],
            "waxing_crescent": ["Short morning pause.", "Box breathing."],
            "first_quarter": ["15 min focused practice.", "Slightly active breath."],
            "waxing_gibbous": ["Deepen what works.", "Longer exhales."],
            "full_moon": ["Quiet gratitude.", "Slow breathing."],
            "waning_gibbous": ["Gentle practice, no forcing."],
            "last_quarter": ["Brief “let go” pause."],
            "waning_crescent": ["Silence before sleep."],
        },
        "health": {
            "new_moon": ["Light food.", "Postpone cuts and heavy treatments."],
            "waxing_crescent": ["Hydrate well.", "Waxing Moon — cut for growth."],
            "first_quarter": ["Moderate movement.", "Nourishing hair care."],
            "waxing_gibbous": ["Tune meals.", "Waxing cut for volume."],
            "full_moon": ["Eat simply.", "No drastic image changes."],
            "waning_gibbous": ["Unloading day: simple food, walk."],
            "last_quarter": ["Gentle cleanse.", "Waning Moon — cut strengthens hair."],
            "waning_crescent": ["Sleep over detox.", "Minimal procedures."],
        },
        "creativity": {
            "new_moon": ["Write 3 ideas.", "“I start small.”"],
            "waxing_crescent": ["Draft without criticism."],
            "first_quarter": ["One main project."],
            "waxing_gibbous": ["Polish and test."],
            "full_moon": ["Show or celebrate progress."],
            "waning_gibbous": ["Ask someone you trust."],
            "last_quarter": ["Trim plans."],
            "waning_crescent": ["Journal your thoughts."],
        },
    },
}
