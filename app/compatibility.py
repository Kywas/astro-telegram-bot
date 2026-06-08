from random import Random


SIGN_GROUPS = {
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

GROUP_MATCH_SCORE = {
    ("fire", "air"): 88,
    ("air", "fire"): 88,
    ("earth", "water"): 86,
    ("water", "earth"): 86,
    ("fire", "fire"): 78,
    ("earth", "earth"): 77,
    ("air", "air"): 79,
    ("water", "water"): 80,
    ("fire", "water"): 58,
    ("water", "fire"): 58,
    ("fire", "earth"): 62,
    ("earth", "fire"): 62,
    ("air", "water"): 64,
    ("water", "air"): 64,
    ("air", "earth"): 66,
    ("earth", "air"): 66,
}


def calculate_compatibility(sign_a: str, sign_b: str) -> int:
    group_a = SIGN_GROUPS.get(sign_a)
    group_b = SIGN_GROUPS.get(sign_b)
    base = GROUP_MATCH_SCORE.get((group_a, group_b), 70)

    # Small deterministic variation, so results are stable for same sign pair.
    seed = "-".join(sorted([sign_a, sign_b]))
    rnd = Random(seed)
    return max(35, min(97, base + rnd.randint(-6, 6)))


def compatibility_text(locale: str, score: int) -> str:
    if locale == "ru":
        if score >= 85:
            return "Очень высокая совместимость. Между вами много общего по темпу и ценностям."
        if score >= 70:
            return "Хорошая совместимость. При взаимной поддержке отношения могут быть очень гармоничными."
        if score >= 55:
            return "Средняя совместимость. Важно чаще обсуждать ожидания и границы."
        return "Непростая совместимость. Понадобятся терпение, уважение и работа над коммуникацией."

    if score >= 85:
        return "Very high compatibility. You share a similar rhythm and core values."
    if score >= 70:
        return "Good compatibility. With mutual support, this can become a very harmonious match."
    if score >= 55:
        return "Average compatibility. It helps to discuss expectations and boundaries more often."
    return "Challenging compatibility. Patience, respect, and communication will be key."
