"""Shared bot runtime: routers, settings, database."""
from pathlib import Path

from aiogram import Router

from app.config import load_settings
from app.database import Database

router = Router()
admin_router = Router()
settings = load_settings()
db = Database(settings.database_path)

FREE_PARTNER_LIMIT = 2
PREMIUM_PARTNER_LIMIT = 10
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOT_ICON_PATH = PROJECT_ROOT / "assets" / "bot_icon.jpg"

SIGN_RU = {
    "Aries": "Овен",
    "Taurus": "Телец",
    "Gemini": "Близнецы",
    "Cancer": "Рак",
    "Leo": "Лев",
    "Virgo": "Дева",
    "Libra": "Весы",
    "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn": "Козерог",
    "Aquarius": "Водолей",
    "Pisces": "Рыбы",
}

SIGN_EN = {
    "Aries": "Aries",
    "Taurus": "Taurus",
    "Gemini": "Gemini",
    "Cancer": "Cancer",
    "Leo": "Leo",
    "Virgo": "Virgo",
    "Libra": "Libra",
    "Scorpio": "Scorpio",
    "Sagittarius": "Sagittarius",
    "Capricorn": "Capricorn",
    "Aquarius": "Aquarius",
    "Pisces": "Pisces",
}

SIGN_EMOJI = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

DAILY_PRESET_TIMES = ("07:00", "08:00", "09:00", "10:00", "12:00", "18:00", "21:00")
EVENING_PRESET_TIMES = ("19:00", "20:00", "21:00", "22:00")


GOAL_TEXT_KEYS = {
    "love": "goal_love",
    "career": "goal_career",
    "money": "goal_money",
    "balance": "goal_balance",
}

