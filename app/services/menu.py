"""Reply keyboard text → action mapping."""
import re

def _normalize_menu_text(text: str) -> str:
    # Remove emoji/punctuation noise so buttons work in different visual variants.
    cleaned = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().casefold()
    return cleaned


def _menu_action_from_text(text: str) -> str | None:
    normalized = _normalize_menu_text(text)

    aliases: dict[str, set[str]] = {
        "today": {
            "гороскоп",
            "horoscope",
        },
        "profile": {
            "профиль",
            "profile",
        },
        "language": {
            "язык",
            "language",
        },
        "help": {
            "помощь",
            "help",
        },
        "back": {
            "назад",
            "back",
        },
        "about": {
            "о боте",
            "about",
        },
        "prefs": {
            "preferences",
            "preferences",
            "настройки",
        },
        "compat": {
            "совместимость",
            "compatibility",
        },
        "moon": {
            "лунный календарь",
            "moon calendar",
        },
        "natal": {
            "натальная карта",
            "natal",
            "natal chart",
        },
        "premium": {
            "premium",
            "премиум",
        },
        "restart": {
            "заполнить профиль заново",
            "refill profile",
            "restart",
        },
    }

    for action, words in aliases.items():
        if normalized in words:
            return action
    return None


