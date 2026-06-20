"""Print sample natal Q&A answers for manual review (plain Russian)."""
from __future__ import annotations

import re
import sys
from datetime import date, time

from app.jyotish_engine import build_jyotish_chart
from app.natal_sphere_qa import (
    build_family_answer,
    build_finance_answer,
    build_health_answer,
    build_karma_answer,
    build_popular_answer,
    build_traits_answer,
    family_questions,
    finance_questions,
    health_questions,
    karma_questions,
    traits_questions,
)

_WEEKLY_ROUTES: dict[tuple[str, str], tuple[str, int]] = {
    ("health_madness", "madness"): ("traits", 1),
    ("health_madness", "mental"): ("traits", 2),
    ("health_madness", "body"): ("health", 0),
}

_WEEKLY_POST_RU = """Здоровье: Твой тип безумия по натальной карте 👽

Помню, когда я училась медитировать, мой учитель говорил: «Если взрослый человек не может просидеть 30 минут на коврике в тишине — он безумен… 🧘‍♀️»

Ну что ж. Кажется, у каждого из нас есть свои скелеты в шкафу! А что самое интересное — они прописаны в натальной карте 🫡

Да уж… Вопросы ниже не из простых, но ты держись!

◽️ Давай посмотрим, что карта говорит о тебе…"""


def build_weekly_block_answer(theme_id: str, block_id: str, chart, locale: str, *, style: str) -> str | None:
    route = _WEEKLY_ROUTES.get((theme_id, block_id))
    if route is None:
        return None
    builder_name, question_index = route
    builders = {
        "traits": build_traits_answer,
        "health": build_health_answer,
        "family": build_family_answer,
        "finance": build_finance_answer,
        "karma": build_karma_answer,
    }
    builder = builders.get(builder_name)
    if builder is None:
        return None
    return builder(chart, locale, question_index, style=style)


def strip_html(text: str) -> str:
    text = re.sub(r"</?(?:b|i|u|code|pre)>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()


def main() -> None:
    chart = build_jyotish_chart(
        birth_date=date(1995, 4, 15),
        birth_time=time(14, 30),
        city="Moscow",
        timezone_name="Europe/Moscow",
        locale="ru",
    )
    if chart is None:
        print("Chart build failed", file=sys.stderr)
        sys.exit(1)

    sections: list[tuple[str, str]] = []

    sections.append(("ЕЖЕНЕДЕЛЬНЫЙ ПОСТ (понедельник 11:00)", _WEEKLY_POST_RU))
    for bid, label in (
        ("madness", "МОЙ ТИП БЕЗУМИЯ 👻"),
        ("mental", "ПСИХИЧЕСКОЕ ЗДОРОВЬЕ В КАРТЕ"),
        ("body", "ОБЩЕЕ ЗДОРОВЬЕ 🌿"),
    ):
        ans = build_weekly_block_answer("health_madness", bid, chart, "ru", style="plain")
        if ans:
            sections.append((f"Кнопка: {label}", strip_html(ans)))

    for i, q in enumerate(health_questions("ru")):
        sections.append(
            (f"💪 Здоровье · вопрос {i + 1}: {q}", strip_html(build_health_answer(chart, "ru", i, style="plain")))
        )

    for i, q in enumerate(family_questions("ru")):
        sections.append(
            (f"💍 Семья · вопрос {i + 1}: {q}", strip_html(build_family_answer(chart, "ru", i, style="plain")))
        )

    for i, q in enumerate(finance_questions("ru")):
        sections.append(
            (f"💸 Финансы · вопрос {i + 1}: {q}", strip_html(build_finance_answer(chart, "ru", i, style="plain")))
        )

    for i, q in enumerate(karma_questions("ru")):
        sections.append(
            (f"🪷 Карма · вопрос {i + 1}: {q}", strip_html(build_karma_answer(chart, "ru", i, style="plain")))
        )

    for i, q in enumerate(traits_questions("ru")):
        sections.append(
            (f"✨ Характер · вопрос {i + 1}: {q}", strip_html(build_traits_answer(chart, "ru", i, style="plain")))
        )

    sections.append(
        (
            "🔥 Популярное · тема карты",
            strip_html(build_popular_answer(chart, "ru", "theme", style="plain")),
        )
    )

    lines: list[str] = [
        "Пример карты: 15.04.1995 14:30 Москва · Лагна Лев",
        "",
    ]
    for title, body in sections:
        lines.extend(["=" * 64, title, "-" * 64, body, ""])

    text = "\n".join(lines)
    out_path = __import__("pathlib").Path(__file__).resolve().parent.parent / "marketing" / "weekly" / "sample-answers-preview.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"\n[Saved: {out_path}]", file=sys.stderr)


if __name__ == "__main__":
    main()
