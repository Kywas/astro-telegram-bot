"""Date parsing helpers for user input."""
from datetime import datetime


def target_date_from_day_month(day_month: str, today: datetime) -> datetime | None:
    try:
        day_str, month_str = day_month.split(".")
        day = int(day_str)
        month = int(month_str)
    except ValueError:
        return None

    for year in (today.year, today.year + 1):
        try:
            candidate = datetime(year, month, day)
        except ValueError:
            continue
        if 0 <= (candidate.date() - today.date()).days < 30:
            return candidate
    return None
