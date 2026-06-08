# Astro Telegram Bot (MVP)

Simple astrology Telegram bot on Python + aiogram.

## Features

- User onboarding (`/start`)
- Profile collection: birth date, time, city
- Zodiac sign calculation
- Daily horoscope (`/today`)
- Compatibility check (`/compat`)
- Moon calendar (`/moon`)
- Moon table for 7/30 days with daily tips
- Mood tracking (`/mood 1..10`)
- Daily auto-delivery (`/daily on HH:MM`, `/daily off`)
- User preferences (`/prefs`, `/setprefs`)
- Basic analytics and premium status (`/stats`, `/premium`)
- Preferences wizard with buttons (`/prefssetup`)
- Premium payment skeleton (`/buypremium`)
- Admin utilities (`/grantpremium`, `/broadcast`, `/ping`)
- Error logging (`error_log` table)
- RU/EN localization with language switch
- Data stored in SQLite

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set your bot token from BotFather.
4. Run the bot:

```bash
python main.py
```

Or run helper script on Windows (creates `.venv` if needed, installs deps, starts bot):

```powershell
.\start_bot.ps1
```

If PowerShell execution policy blocks scripts, use batch file:

```bat
start_bot.bat
```

## Proxy setup (optional)

If Telegram API is blocked in your network, set proxy in `.env`:

```env
BOT_PROXY=http://127.0.0.1:7890
```

You can also use authenticated proxy:

```env
BOT_PROXY=http://username:password@host:port
```

If `BOT_PROXY` is empty, the bot will also try `HTTPS_PROXY` and `HTTP_PROXY`.

Admin and premium config in `.env`:

```env
ADMIN_IDS=123456789,987654321
PREMIUM_PRICE_STARS=100
ENABLE_PAYMENTS=false
```

## Commands

- `/start` - start and fill profile
- `/profile` - show current profile
- `/today` - get horoscope for today
- `/compat` - check compatibility with another person
- `/moon` - show moon calendar for today
- `/mood 1..10` - save current mood
- `/daily on HH:MM` - enable daily auto-send in UTC
- `/daily off` - disable daily auto-send
- `/prefs` - view personal preferences
- `/setprefs m single career` - update profile preferences
- `/prefssetup` - open step-by-step preferences wizard
- `/premium` - show premium status
- `/buypremium` - open premium payment skeleton
- `/stats` - show bot stats
- `/grantpremium <user_id> <days>` - admin grant premium
- `/broadcast <text>` - admin broadcast message to all users
- `/ping` - admin health check
- `/language` - switch RU/EN
- `/help` - command list

Notes:
- `/stats` is admin-only (IDs from `ADMIN_IDS`)
- `/buypremium` works only when `ENABLE_PAYMENTS=true`

## Notes

- This bot provides entertainment content.
- Do not share real personal data in testing.
