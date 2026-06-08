from dataclasses import dataclass
from datetime import date

from app.compatibility import calculate_compatibility, compatibility_text
from app.zodiac import zodiac_sign


@dataclass
class SynastryResult:
    score: int
    relation_mode: str
    partner_sign: str
    details: str


def synastry_score(user_sign: str, partner_sign: str, relation_mode: str) -> int:
    base = calculate_compatibility(user_sign, partner_sign)
    mode_bonus = {"love": 3, "friendship": 1, "work": 2}.get(relation_mode, 0)
    return max(35, min(98, base + mode_bonus))


def build_synastry(locale: str, user_sign: str, partner_birth_date: date, relation_mode: str) -> SynastryResult:
    partner_sign = zodiac_sign(partner_birth_date)
    score = synastry_score(user_sign, partner_sign, relation_mode)
    details = compatibility_text(locale, score)
    return SynastryResult(
        score=score,
        relation_mode=relation_mode,
        partner_sign=partner_sign,
        details=details,
    )
