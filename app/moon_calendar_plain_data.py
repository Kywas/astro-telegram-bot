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
                "do": "5–10 минут тишины, одна понятная мысль и запись на бумаге",
                "avoid": "длинных занятий и перегруза в первый день",
            },
            "waxing_crescent": {
                "do": "короткая ежедневная привычка — та же практика, что вчера",
                "avoid": "откладывать «на потом» и менять метод каждый день",
            },
            "first_quarter": {
                "do": "сделать практику чуть длиннее и собраннее — 15 мин",
                "avoid": "делать на автомате без внимания к дыханию",
            },
            "waxing_gibbous": {
                "do": "углубить то, что уже идёт — медленнее и внимательнее",
                "avoid": "хвататься за новые методы и гнаться за результатом",
            },
            "full_moon": {
                "do": "спокойно завершить цикл и поблагодарить себя",
                "avoid": "ночных марафонов, перегруза и жёстких практик",
            },
            "waning_gibbous": {
                "do": "мягкая практика и обмен опытом без давления",
                "avoid": "давить на себя результатом и «надо успеть»",
            },
            "last_quarter": {
                "do": "упростить практику — оставить 1–2 главных техники",
                "avoid": "добавлять лишнее и новые обязательства",
            },
            "waning_crescent": {
                "do": "отдых, тишина, расслабление перед новым стартом",
                "avoid": "начинать длинные курсы и практики через силу",
            },
        },
        "health": {
            "new_moon": {
                "do": "лёгкая еда, сон в привычное время, мягкий режим",
                "avoid": "жёстких диет, резких экспериментов и процедур",
            },
            "waxing_crescent": {
                "do": "пить воду, двигаться понемногу, простые супы и овощи",
                "avoid": "резко менять всё сразу и «начать с понедельника»",
            },
            "first_quarter": {
                "do": "умеренная активность, простая еда, белок и овощи",
                "avoid": "недосыпа ради тренировок и перегруза",
            },
            "waxing_gibbous": {
                "do": "подстроить режим сна и питания — маленькие шаги",
                "avoid": "лишнего сахара, кофе «на силу» и недосыпа",
            },
            "full_moon": {
                "do": "есть проще и медленнее, отдыхать больше",
                "avoid": "переедания, алкоголя и резкой смены образа",
            },
            "waning_gibbous": {
                "do": "лёгкий день: простая еда, прогулка, тёплая ванна",
                "avoid": "голодания и жёстких ограничений",
            },
            "last_quarter": {
                "do": "убрать лишнее из рациона, больше воды и зелени",
                "avoid": "новых жёстких диет и стрессовых нагрузок",
            },
            "waning_crescent": {
                "do": "сон 8+ часов, отдых, мягкая простая еда",
                "avoid": "экстремальных разгрузок и агрессивных процедур",
            },
        },
        "creativity": {
            "new_moon": {
                "do": "записать 2–3 идеи и короткое намерение на цикл",
                "avoid": "запускать большой проект без плана и черновика",
            },
            "waxing_crescent": {
                "do": "первый черновик 20 мин — текст, эскиз или набросок",
                "avoid": "ждать идеального момента и критиковать себя",
            },
            "first_quarter": {
                "do": "работать над одной задачей и довести до формы",
                "avoid": "распыляться на много проектов сразу",
            },
            "waxing_gibbous": {
                "do": "допилить, посмотреть свежим взглядом, одна правка",
                "avoid": "бесконечно переделывать и гнаться за идеалом",
            },
            "full_moon": {
                "do": "показать работу или подвести итог — зафиксировать прогресс",
                "avoid": "резких решений на эмоциях и сравнения с другими",
            },
            "waning_gibbous": {
                "do": "спросить мнение у 1–2 близких и отметить прогресс",
                "avoid": "сравнивать себя с другими и обесценивать работу",
            },
            "last_quarter": {
                "do": "убрать лишнее из плана, оставить сильное",
                "avoid": "выбрасывать всё подряд из импульса",
            },
            "waning_crescent": {
                "do": "записать мысли и идеи «на потом» без обязательств",
                "avoid": "старта большого проекта без отдыха",
            },
        },
    },
    "en": {
        "practices": {
            "new_moon": {
                "do": "5–10 minutes of quiet, one clear thought, write it down",
                "avoid": "long sessions and overload on day one",
            },
            "waxing_crescent": {
                "do": "a small daily habit — same practice as yesterday",
                "avoid": "putting it off and swapping methods daily",
            },
            "first_quarter": {
                "do": "make your practice a bit longer and focused — 15 min",
                "avoid": "going through the motions without breath awareness",
            },
            "waxing_gibbous": {
                "do": "deepen what works — slower and more attentive",
                "avoid": "grabbing new methods and chasing results",
            },
            "full_moon": {
                "do": "gently close the cycle and thank yourself",
                "avoid": "late-night marathons, overload, and harsh practice",
            },
            "waning_gibbous": {
                "do": "gentle practice and sharing without pressure",
                "avoid": "pressuring yourself for results and “must finish”",
            },
            "last_quarter": {
                "do": "simplify — keep 1–2 main techniques",
                "avoid": "adding extra tasks and new obligations",
            },
            "waning_crescent": {
                "do": "rest, quiet, relaxation before a fresh start",
                "avoid": "starting long courses and forced practice",
            },
        },
        "health": {
            "new_moon": {
                "do": "light food, sleep at your usual time, a soft routine",
                "avoid": "strict diets, harsh experiments, and treatments",
            },
            "waxing_crescent": {
                "do": "hydrate, move a little, simple soups and vegetables",
                "avoid": "changing everything at once and “starting Monday”",
            },
            "first_quarter": {
                "do": "moderate activity, simple food, protein and vegetables",
                "avoid": "skipping sleep for workouts and overload",
            },
            "waxing_gibbous": {
                "do": "tune sleep and meals — small steps already help",
                "avoid": "extra sugar, caffeine to push through, and sleep debt",
            },
            "full_moon": {
                "do": "eat simply and slowly, rest more",
                "avoid": "overeating, alcohol, and drastic image changes",
            },
            "waning_gibbous": {
                "do": "a light day: simple food, a walk, a warm bath",
                "avoid": "fasting and harsh restrictions",
            },
            "last_quarter": {
                "do": "trim excess from meals, more water and greens",
                "avoid": "new strict diets and stressful loads",
            },
            "waning_crescent": {
                "do": "8+ hours sleep if you can, rest, gentle simple food",
                "avoid": "extreme cleanses and harsh treatments",
            },
        },
        "creativity": {
            "new_moon": {
                "do": "write 2–3 ideas and a short intention for the cycle",
                "avoid": "launching a big project without a plan or draft",
            },
            "waxing_crescent": {
                "do": "a 20 min first draft — text, sketch, or outline",
                "avoid": "waiting for the perfect moment and self-criticism",
            },
            "first_quarter": {
                "do": "work on one task and bring it into form",
                "avoid": "spreading across many projects at once",
            },
            "waxing_gibbous": {
                "do": "polish, look with fresh eyes, one strong edit",
                "avoid": "endless reworking and chasing perfection",
            },
            "full_moon": {
                "do": "show your work or review progress — capture it",
                "avoid": "sharp decisions on emotion and comparing to others",
            },
            "waning_gibbous": {
                "do": "ask 1–2 people you trust and note your progress",
                "avoid": "comparing yourself to others and dismissing your work",
            },
            "last_quarter": {
                "do": "trim the plan, keep what’s strong",
                "avoid": "throwing everything out impulsively",
            },
            "waning_crescent": {
                "do": "journal thoughts and “maybe later” ideas — no obligations",
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
