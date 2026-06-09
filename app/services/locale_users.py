"""User locale detection."""
from app.bot_context import db
from app.i18n import get_locale

async def get_user_locale(user_id: int) -> str:
    profile = await db.get_user(user_id)
    return get_locale(profile.language if profile else None)


async def detect_locale_for_user(user_id: int, telegram_language_code: str | None) -> str:
    profile = await db.get_user(user_id)
    if profile and profile.language in TEXTS:
        return profile.language
    if telegram_language_code in TEXTS:
        return telegram_language_code
    return "en"


def _target_date_from_day_month(day_month: str, today: datetime) -> datetime | None:
    try:
        day_str, month_str = day_month.split(".")
        day = int(day_str)
        month = int(month_str)
    except ValueError:
        return None

    for year in [today.year, today.year + 1]:
        try:
            candidate = datetime(year, month, day)
        except ValueError:
            continue
        if 0 <= (candidate.date() - today.date()).days < 30:
            return candidate
    return None


