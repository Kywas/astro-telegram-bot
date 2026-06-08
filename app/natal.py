from __future__ import annotations

from datetime import date, time
import random


ELEMENT_BY_SIGN = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}


ELEMENT_TEXT = {
    "ru": {
        "fire": "Огонь: высокая энергия, инициативность, стремление действовать быстро.",
        "earth": "Земля: практичность, устойчивость, фокус на результате и надежности.",
        "air": "Воздух: интеллект, общительность, гибкость мышления и интерес к идеям.",
        "water": "Вода: эмпатия, интуиция, глубокая эмоциональность и чувствительность.",
    },
    "en": {
        "fire": "Fire: high energy, initiative, and a drive to act quickly.",
        "earth": "Earth: practicality, stability, and focus on reliable results.",
        "air": "Air: intellect, sociability, mental flexibility, and idea-driven style.",
        "water": "Water: empathy, intuition, deep emotions, and sensitivity.",
    },
}


WEEKDAY_FOCUS = {
    "ru": {
        0: "Лучше всего раскрывается через системность и планирование.",
        1: "Сильная сторона - самостоятельность и решительность.",
        2: "Талант к коммуникации и обучению через обмен опытом.",
        3: "Хорошо работает стратегия роста через дисциплину.",
        4: "Умение объединять людей и создавать атмосферу доверия.",
        5: "Сильна адаптация и скорость реакции на изменения.",
        6: "Глубокая интуиция и ориентация на внутренние ценности.",
    },
    "en": {
        0: "Best expressed through structure and planning.",
        1: "Strong side: independence and decisiveness.",
        2: "Natural talent for communication and learning through exchange.",
        3: "Growth strategy works best through discipline.",
        4: "Ability to unite people and build trust.",
        5: "Strong adaptability and quick reaction to change.",
        6: "Deep intuition and focus on inner values.",
    },
}


TIME_STYLE = {
    "ru": {
        "morning": "Утренний ритм: легче начинать новые задачи и задавать темп дню.",
        "day": "Дневной ритм: эффективен баланс логики, общения и продуктивности.",
        "evening": "Вечерний ритм: сильнее проявляется анализ, рефлексия и креатив.",
        "unknown": "Без времени рождения: интерпретация сделана по базовым параметрам.",
    },
    "en": {
        "morning": "Morning rhythm: easier to start new tasks and set the day's pace.",
        "day": "Day rhythm: strong balance of logic, communication, and productivity.",
        "evening": "Evening rhythm: analysis, reflection, and creativity are more pronounced.",
        "unknown": "Without birth time: interpretation is based on core parameters only.",
    },
}


def _time_bucket(value: time | None) -> str:
    if value is None:
        return "unknown"
    if value.hour < 12:
        return "morning"
    if value.hour < 18:
        return "day"
    return "evening"


def _seed_from_profile(
    sign_key: str | None,
    birth_date: date,
    relationship_status: str | None,
    goal: str | None,
    mood_score: int | None,
) -> int:
    raw = (
        f"{sign_key or 'unknown'}|{birth_date.isoformat()}|"
        f"{relationship_status or '-'}|{goal or '-'}|{mood_score if mood_score is not None else '-'}"
    )
    return sum(ord(ch) for ch in raw)


def _bounded(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))


def _score_bar(score: int) -> str:
    filled = max(0, min(10, round(score / 10)))
    return ("🟩" * filled) + ("⬜" * (10 - filled))


def build_natal_summary(
    *,
    locale: str,
    sign_name: str,
    sign_key: str | None,
    birth_date: date,
    birth_time: time | None,
    city: str,
    relationship_status: str | None = None,
    goal: str | None = None,
    mood_score: int | None = None,
    mode: str = "full",
) -> str:
    lang = "ru" if locale == "ru" else "en"
    element = ELEMENT_BY_SIGN.get(sign_key or "", "air")
    weekday = birth_date.weekday()
    time_bucket = _time_bucket(birth_time)
    rng = random.Random(
        _seed_from_profile(sign_key, birth_date, relationship_status, goal, mood_score)
    )
    base = 62 + rng.randint(0, 18)
    mood_shift = 0 if mood_score is None else (mood_score - 5)
    rel_score = _bounded(base + rng.randint(-6, 8) + mood_shift)
    career_score = _bounded(base + rng.randint(-4, 10) + (2 if goal == "career" else 0))
    money_score = _bounded(base + rng.randint(-7, 9) + (2 if goal == "money" else 0))
    energy_score = _bounded(base + rng.randint(-5, 7) + (3 if element == "fire" else 0) + mood_shift)

    compact_mode = mode == "short"

    if lang == "ru":
        relation_text = {
            "single": "Сейчас акцент на личных границах и самодостаточности.",
            "relationship": "Сейчас акцент на партнерстве и эмоциональном обмене.",
        }.get(relationship_status or "", "Сейчас важен баланс между личными целями и общением.")
        goal_text = {
            "love": "Фокус недели: отношения. Вкладывайся в качество диалога и честность.",
            "career": "Фокус недели: карьера. Держи приоритет на 1-2 ключевых задачах.",
            "money": "Фокус недели: финансы. Избегай импульсивных трат и фиксируй бюджет.",
            "balance": "Фокус недели: баланс. Распредели нагрузку и оставь время на восстановление.",
        }.get(goal or "", "Фокус недели: стабильный ритм и небольшие, но регулярные шаги.")
        mood_text = (
            f"Текущее настроение: {mood_score}/10. "
            "Чем ниже энергия, тем полезнее короткие задачи и щадящий режим."
            if mood_score is not None
            else "Настроение не зафиксировано. Добавь /mood 1..10 для более точной персонализации."
        )
        weekly_actions = {
            "love": [
                "Запланируй 1 честный разговор без отвлечений.",
                "Сделай маленький, но конкретный жест заботы.",
                "Сформулируй ожидания от отношений на неделю.",
            ],
            "career": [
                "Выдели главный приоритет недели и разбей его на 3 шага.",
                "Закрой одну задачу, которую долго откладывал(а).",
                "Зафиксируй результат недели в заметках.",
            ],
            "money": [
                "Составь лимит расходов на ближайшие 7 дней.",
                "Отложи импульсные покупки на 24 часа.",
                "Проверь 1 способ увеличить доход или снизить расход.",
            ],
            "balance": [
                "Запланируй 2 слота отдыха в календаре заранее.",
                "Каждый день оставляй 20 минут без телефона.",
                "Подведи короткий итог дня по энергии и настроению.",
            ],
        }.get(
            goal or "",
            [
                "Определи 1 главную цель недели.",
                "Раздели ее на небольшие ежедневные шаги.",
                "Проверь прогресс в конце недели и скорректируй план.",
            ],
        )
        top_name, top_score = max(
            [
                ("отношения", rel_score),
                ("карьера", career_score),
                ("финансы", money_score),
                ("энергия", energy_score),
            ],
            key=lambda item: item[1],
        )
        low_name, low_score = min(
            [
                ("отношения", rel_score),
                ("карьера", career_score),
                ("финансы", money_score),
                ("энергия", energy_score),
            ],
            key=lambda item: item[1],
        )
        header = "Натальная карта"
        basics = (
            f"Знак: {sign_name}\n"
            f"Дата рождения: {birth_date.strftime('%d.%m.%Y')}\n"
            f"Время: {birth_time.isoformat(timespec='minutes') if birth_time else 'неизвестно'}\n"
            f"Город: {city}"
        )
        if compact_mode:
            sections = (
                "Краткий формат:\n"
                "Оценки по сферам (0-100)\n"
                f"Отношения: {rel_score} {_score_bar(rel_score)}\n"
                f"Карьера: {career_score} {_score_bar(career_score)}\n"
                f"Финансы: {money_score} {_score_bar(money_score)}\n"
                f"Энергия: {energy_score} {_score_bar(energy_score)}\n\n"
                "План недели (3 шага)\n"
                f"1. {weekly_actions[0]}\n"
                f"2. {weekly_actions[1]}\n"
                f"3. {weekly_actions[2]}\n\n"
                "Итог:\n"
                f"• Точка роста недели: {top_name} ({top_score}).\n"
                f"• Зона внимания: {low_name} ({low_score})."
            )
        else:
            sections = (
                f"1) Базовая энергия\n{ELEMENT_TEXT[lang][element]}\n\n"
                f"2) Личный вектор\n{WEEKDAY_FOCUS[lang][weekday]}\n\n"
                f"3) Суточный ритм\n{TIME_STYLE[lang][time_bucket]}\n\n"
                f"4) Отношения\n{relation_text}\n\n"
                f"5) Карьера и финансы\n{goal_text}\n\n"
                f"6) Рекомендации на неделю\n{mood_text}\n"
                "Опирайся на сильные стороны знака, фиксируй цели на неделю и проверяй прогресс каждый вечер.\n\n"
                "7) Оценки по сферам (0-100)\n"
                f"Отношения: {rel_score} {_score_bar(rel_score)}\n"
                f"Карьера: {career_score} {_score_bar(career_score)}\n"
                f"Финансы: {money_score} {_score_bar(money_score)}\n"
                f"Энергия: {energy_score} {_score_bar(energy_score)}\n\n"
                "8) План недели (3 шага)\n"
                f"1. {weekly_actions[0]}\n"
                f"2. {weekly_actions[1]}\n"
                f"3. {weekly_actions[2]}\n\n"
                "Итог:\n"
                f"• Точка роста недели: {top_name} ({top_score}). Усиливай это направление.\n"
                f"• Зона внимания: {low_name} ({low_score}). Действуй мягко и поэтапно."
            )
    else:
        relation_text = {
            "single": "Current emphasis is personal boundaries and self-reliance.",
            "relationship": "Current emphasis is partnership and emotional exchange.",
        }.get(relationship_status or "", "Current emphasis is balancing personal goals and communication.")
        goal_text = {
            "love": "Weekly focus: relationships. Invest in dialogue quality and honesty.",
            "career": "Weekly focus: career. Keep priority on 1-2 key tasks.",
            "money": "Weekly focus: finances. Avoid impulsive spending and track your budget.",
            "balance": "Weekly focus: balance. Distribute workload and reserve recovery time.",
        }.get(goal or "", "Weekly focus: stable rhythm and small but consistent steps.")
        mood_text = (
            f"Current mood: {mood_score}/10. "
            "When energy is lower, short tasks and gentle pacing work better."
            if mood_score is not None
            else "Mood is not set. Add /mood 1..10 for deeper personalization."
        )
        weekly_actions = {
            "love": [
                "Schedule one honest conversation without distractions.",
                "Make one small but concrete act of care.",
                "Define relationship expectations for this week.",
            ],
            "career": [
                "Pick one top weekly priority and split it into 3 steps.",
                "Close one task you have been postponing.",
                "Write down this week's outcomes in notes.",
            ],
            "money": [
                "Set a 7-day spending limit.",
                "Delay impulsive purchases for 24 hours.",
                "Review one way to increase income or cut costs.",
            ],
            "balance": [
                "Pre-book two recovery slots in your calendar.",
                "Keep 20 minutes phone-free each day.",
                "Do a short evening check-in on mood and energy.",
            ],
        }.get(
            goal or "",
            [
                "Choose one main goal for the week.",
                "Break it into small daily steps.",
                "Review progress at week end and adjust.",
            ],
        )
        top_name, top_score = max(
            [
                ("relationships", rel_score),
                ("career", career_score),
                ("money", money_score),
                ("energy", energy_score),
            ],
            key=lambda item: item[1],
        )
        low_name, low_score = min(
            [
                ("relationships", rel_score),
                ("career", career_score),
                ("money", money_score),
                ("energy", energy_score),
            ],
            key=lambda item: item[1],
        )
        header = "Natal chart"
        basics = (
            f"Sign: {sign_name}\n"
            f"Birth date: {birth_date.isoformat()}\n"
            f"Time: {birth_time.isoformat(timespec='minutes') if birth_time else 'unknown'}\n"
            f"City: {city}"
        )
        if compact_mode:
            sections = (
                "Compact format:\n"
                "Area scores (0-100)\n"
                f"Relationships: {rel_score} {_score_bar(rel_score)}\n"
                f"Career: {career_score} {_score_bar(career_score)}\n"
                f"Money: {money_score} {_score_bar(money_score)}\n"
                f"Energy: {energy_score} {_score_bar(energy_score)}\n\n"
                "Weekly plan (3 steps)\n"
                f"1. {weekly_actions[0]}\n"
                f"2. {weekly_actions[1]}\n"
                f"3. {weekly_actions[2]}\n\n"
                "Summary:\n"
                f"• Strongest area this week: {top_name} ({top_score}).\n"
                f"• Watch zone: {low_name} ({low_score})."
            )
        else:
            sections = (
                f"1) Core energy\n{ELEMENT_TEXT[lang][element]}\n\n"
                f"2) Personal vector\n{WEEKDAY_FOCUS[lang][weekday]}\n\n"
                f"3) Daily rhythm\n{TIME_STYLE[lang][time_bucket]}\n\n"
                f"4) Relationships\n{relation_text}\n\n"
                f"5) Career and money\n{goal_text}\n\n"
                f"6) Weekly guidance\n{mood_text}\n"
                "Lean on your sign strengths, set weekly goals, and review progress every evening.\n\n"
                "7) Area scores (0-100)\n"
                f"Relationships: {rel_score} {_score_bar(rel_score)}\n"
                f"Career: {career_score} {_score_bar(career_score)}\n"
                f"Money: {money_score} {_score_bar(money_score)}\n"
                f"Energy: {energy_score} {_score_bar(energy_score)}\n\n"
                "8) Weekly plan (3 steps)\n"
                f"1. {weekly_actions[0]}\n"
                f"2. {weekly_actions[1]}\n"
                f"3. {weekly_actions[2]}\n\n"
                "Summary:\n"
                f"• Strongest area this week: {top_name} ({top_score}). Leverage it.\n"
                f"• Watch zone: {low_name} ({low_score}). Move gently and consistently."
            )

    return f"{header}\n\n{basics}\n\n{sections}"
