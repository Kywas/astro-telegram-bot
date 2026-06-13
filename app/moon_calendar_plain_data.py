"""Plain-language copy for the moon calendar (no astrological jargon)."""

PLAIN_PHASE_NAMES = {
    "ru": {
        "new_moon": "Начало цикла",
        "waxing_crescent": "Рост",
        "first_quarter": "Разворот к действию",
        "waxing_gibbous": "Доработка",
        "full_moon": "Пик цикла",
        "waning_gibbous": "Делиться результатом",
        "last_quarter": "Отпускание",
        "waning_crescent": "Отдых перед стартом",
    },
    "en": {
        "new_moon": "Cycle start",
        "waxing_crescent": "Growth",
        "first_quarter": "Turn to action",
        "waxing_gibbous": "Refinement",
        "full_moon": "Peak of cycle",
        "waning_gibbous": "Share results",
        "last_quarter": "Release",
        "waning_crescent": "Rest before start",
    },
}

PLAIN_SHORT_PHASE = {
    "ru": {
        "new_moon": "старт",
        "waxing_crescent": "рост",
        "first_quarter": "действ.",
        "waxing_gibbous": "доводка",
        "full_moon": "пик",
        "waning_gibbous": "делиться",
        "last_quarter": "отпуск.",
        "waning_crescent": "отдых",
    },
    "en": {
        "new_moon": "start",
        "waxing_crescent": "grow",
        "first_quarter": "act",
        "waxing_gibbous": "refine",
        "full_moon": "peak",
        "waning_gibbous": "share",
        "last_quarter": "release",
        "waning_crescent": "rest",
    },
}

PLAIN_FOCUS_SECTION = {
    "ru": {
        "practices": "🧘 Практики на сегодня",
        "health": "💚 Здоровье на сегодня",
        "creativity": "✨ Идеи и саморазвитие",
    },
    "en": {
        "practices": "🧘 Practices for today",
        "health": "💚 Health for today",
        "creativity": "✨ Ideas and growth",
    },
}

PLAIN_MODE_PHASE_GUIDANCE = {
    "ru": {
        "practices": {
            "new_moon": {
                "do": "5–10 минут тишины и одно простое намерение",
                "avoid": "длинных занятий и перегруза",
            },
            "waxing_crescent": {
                "do": "короткая ежедневная привычка — начни с малого",
                "avoid": "откладывать «на потом»",
            },
            "first_quarter": {
                "do": "сделать практику чуть длиннее и собраннее",
                "avoid": "делать на автомате без внимания",
            },
            "waxing_gibbous": {
                "do": "углубить то, что уже идёт",
                "avoid": "хвататься за новые методы",
            },
            "full_moon": {
                "do": "спокойно завершить цикл и поблагодарить себя",
                "avoid": "ночных марафонов и перегруза",
            },
            "waning_gibbous": {
                "do": "мягкая практика и обмен опытом",
                "avoid": "давить на себя результатом",
            },
            "last_quarter": {
                "do": "упростить практику, оставить главное",
                "avoid": "добавлять лишнее",
            },
            "waning_crescent": {
                "do": "отдых, тишина, подготовка к новому старту",
                "avoid": "начинать длинные курсы",
            },
        },
        "health": {
            "new_moon": {
                "do": "лёгкая еда и нормальный сон",
                "avoid": "жёстких диет и резких экспериментов",
            },
            "waxing_crescent": {
                "do": "пить воду, двигаться понемногу",
                "avoid": "резко менять всё сразу",
            },
            "first_quarter": {
                "do": "умеренная активность и простая еда",
                "avoid": "недосыпа ради тренировок",
            },
            "waxing_gibbous": {
                "do": "подстроить режим сна и питания",
                "avoid": "лишнего сахара и кофе «на силу»",
            },
            "full_moon": {
                "do": "есть проще, отдыхать больше",
                "avoid": "переедания и алкоголя",
            },
            "waning_gibbous": {
                "do": "лёгкий день, прогулка, простая еда",
                "avoid": "голодания и жёстких ограничений",
            },
            "last_quarter": {
                "do": "убрать лишнее из рациона, больше воды",
                "avoid": "новых жёстких диет",
            },
            "waning_crescent": {
                "do": "сон, отдых, мягкая еда",
                "avoid": "экстремальных разгрузок",
            },
        },
        "creativity": {
            "new_moon": {
                "do": "записать 2–3 идеи в блокнот",
                "avoid": "запускать большой проект без плана",
            },
            "waxing_crescent": {
                "do": "первый черновик или пробный шаг",
                "avoid": "ждать идеального момента",
            },
            "first_quarter": {
                "do": "работать над одной задачей",
                "avoid": "распыляться",
            },
            "waxing_gibbous": {
                "do": "допилить и проверить результат",
                "avoid": "бесконечно переделывать",
            },
            "full_moon": {
                "do": "показать работу или подвести итог",
                "avoid": "резких решений на эмоциях",
            },
            "waning_gibbous": {
                "do": "спросить мнение и отметить прогресс",
                "avoid": "сравнивать себя с другими",
            },
            "last_quarter": {
                "do": "убрать лишнее, оставить сильное",
                "avoid": "выбрасывать всё подряд",
            },
            "waning_crescent": {
                "do": "записать мысли и инсайты",
                "avoid": "старта большого проекта без отдыха",
            },
        },
    },
    "en": {
        "practices": {
            "new_moon": {
                "do": "5–10 minutes of quiet and one simple intention",
                "avoid": "long sessions and overload",
            },
            "waxing_crescent": {
                "do": "a small daily habit — start tiny",
                "avoid": "putting it off",
            },
            "first_quarter": {
                "do": "make your practice a bit longer and focused",
                "avoid": "going through the motions",
            },
            "waxing_gibbous": {
                "do": "deepen what is already working",
                "avoid": "grabbing new methods",
            },
            "full_moon": {
                "do": "gently close the cycle and thank yourself",
                "avoid": "late-night marathons",
            },
            "waning_gibbous": {
                "do": "gentle practice and sharing experience",
                "avoid": "pressuring yourself for results",
            },
            "last_quarter": {
                "do": "simplify practice, keep what matters",
                "avoid": "adding extra tasks",
            },
            "waning_crescent": {
                "do": "rest, quiet, prepare a fresh start",
                "avoid": "starting long new courses",
            },
        },
        "health": {
            "new_moon": {
                "do": "light meals and regular sleep",
                "avoid": "strict diets and harsh experiments",
            },
            "waxing_crescent": {
                "do": "hydrate and move a little each day",
                "avoid": "changing everything at once",
            },
            "first_quarter": {
                "do": "moderate activity and simple food",
                "avoid": "skipping sleep for workouts",
            },
            "waxing_gibbous": {
                "do": "tune sleep and meal rhythm",
                "avoid": "extra sugar and caffeine to push through",
            },
            "full_moon": {
                "do": "eat simply and rest more",
                "avoid": "overeating and alcohol",
            },
            "waning_gibbous": {
                "do": "a light day, a walk, simple food",
                "avoid": "fasting and harsh restrictions",
            },
            "last_quarter": {
                "do": "trim excess from meals, drink water",
                "avoid": "new strict diets",
            },
            "waning_crescent": {
                "do": "sleep, rest, gentle food",
                "avoid": "extreme cleanses",
            },
        },
        "creativity": {
            "new_moon": {
                "do": "jot down 2–3 ideas",
                "avoid": "launching a big project without a plan",
            },
            "waxing_crescent": {
                "do": "a first draft or trial step",
                "avoid": "waiting for the perfect moment",
            },
            "first_quarter": {
                "do": "work on one main task",
                "avoid": "spreading too thin",
            },
            "waxing_gibbous": {
                "do": "polish and test what you made",
                "avoid": "endless reworking",
            },
            "full_moon": {
                "do": "show your work or review progress",
                "avoid": "sharp decisions on emotion",
            },
            "waning_gibbous": {
                "do": "ask for feedback and note progress",
                "avoid": "comparing yourself to others",
            },
            "last_quarter": {
                "do": "cut excess, keep what is strong",
                "avoid": "throwing everything away",
            },
            "waning_crescent": {
                "do": "journal thoughts and insights",
                "avoid": "starting a big project without rest",
            },
        },
    },
}

PLAIN_PHASE_GUIDANCE = {
    "ru": {
        "new_moon": {
            "do": "задумать одно намерение и начать с малого",
            "avoid": "спешки и перегруза",
        },
        "waxing_crescent": {
            "do": "делать первые шаги",
            "avoid": "откладывания",
        },
        "first_quarter": {
            "do": "действовать и уточнять план",
            "avoid": "конфликтов из нетерпения",
        },
        "waxing_gibbous": {
            "do": "доводить начатое",
            "avoid": "перфекционизма",
        },
        "full_moon": {
            "do": "подвести итог и завершить важное",
            "avoid": "эмоциональных крайностей",
        },
        "waning_gibbous": {
            "do": "делиться результатом",
            "avoid": "давления на себя",
        },
        "last_quarter": {
            "do": "упрощать и отпускать лишнее",
            "avoid": "упрямства",
        },
        "waning_crescent": {
            "do": "отдыхать и восстанавливаться",
            "avoid": "крупных новых стартов",
        },
    },
    "en": {
        "new_moon": {
            "do": "set one intention and start small",
            "avoid": "rush and overload",
        },
        "waxing_crescent": {
            "do": "take first steps",
            "avoid": "delaying",
        },
        "first_quarter": {
            "do": "act and clarify the plan",
            "avoid": "conflicts from impatience",
        },
        "waxing_gibbous": {
            "do": "finish what you started",
            "avoid": "perfectionism",
        },
        "full_moon": {
            "do": "review and wrap up what matters",
            "avoid": "emotional extremes",
        },
        "waning_gibbous": {
            "do": "share results",
            "avoid": "pressure on yourself",
        },
        "last_quarter": {
            "do": "simplify and let go of excess",
            "avoid": "stubbornness",
        },
        "waning_crescent": {
            "do": "rest and recover",
            "avoid": "major new launches",
        },
    },
}

TERMS_FOCUS_SECTION = {
    "ru": {
        "practices": "🧘 Планирование практик · фазы Луны",
        "health": "💚 Забота о здоровье · лунный ритм",
        "creativity": "✨ Творчество · цикл Луны",
    },
    "en": {
        "practices": "🧘 Practice planning · lunar phases",
        "health": "💚 Health care · lunar rhythm",
        "creativity": "✨ Creativity · Moon cycle",
    },
}
