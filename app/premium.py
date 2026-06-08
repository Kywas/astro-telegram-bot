from datetime import datetime, timezone


def is_premium_active(premium_until: str | None) -> bool:
    if not premium_until:
        return False
    try:
        until = datetime.fromisoformat(premium_until)
    except ValueError:
        return False
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    return until > datetime.now(timezone.utc)
