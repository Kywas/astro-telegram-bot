# AstroPulse Telegram Bot

Astrology Telegram bot on Python + aiogram: horoscopes, compatibility, moon calendar, natal chart, Premium subscriptions, referrals, and admin tools.

## Features

### Core
- Onboarding (`/start`) with birth date, time, city, and zodiac sign
- Daily / weekly horoscope (`/today`) with personalization by goal and relationship status
- Compatibility / synastry (`/compat`) with saved partners (up to 2 free, 10 with Premium)
- Moon calendar (`/moon`) — today free, 7 and 30 days in Premium
- Natal chart (`/natal`) — short free, full in Premium
- Mood tracker (`/mood`) and evening check-in with streak counter
- Daily auto-delivery, evening check-in, and lunar notifications (`/daily`)
- Preferences wizard (`/prefssetup`, `/setprefs`, `/prefs`)
- RU / EN localization (`/language`)
- Feedback via `/feedback` and `FEEDBACK_USERNAME` in bot profile

### Premium
- **100 Stars · 199 ₽ · $3.00** per 30 days (Stars work out of the box; fiat needs BotFather provider)
- One-time **7-day trial** after profile completion (`PREMIUM_TRIAL_DAYS`)
- Expiry reminders at 11:00 user local time (3 days, 1 day, today)
- Admin notification on every successful purchase

### Growth
- Referral program: invite a friend → **+7 days Premium** (reward after full profile)
- UTM in `/start`: `?start=src_vk` — source tracked in `/stats`
- Share horoscope button with referral link

### Admin (`ADMIN_IDS`)
- `/stats` — users, subscribers, Premium, events, errors, **traffic sources**
- `/stars` — Telegram Stars balance and recent transactions
- `/grantpremium`, `/broadcast`, `/ping`, `/admin` panel
- Alerts: bot start/crash, error spike (≥10/hour)

## Project layout

```
app/
  bot.py              # entrypoint (run_bot)
  bot_context.py      # routers, settings, db singleton
  i18n.py             # localized strings
  keyboards.py        # inline keyboard builders
  ui.py               # panel edit/send helpers
  profile_public.py   # BotFather profile sync
  handlers/
    admin.py          # admin commands
    user.py           # user commands and callbacks
  services/           # shared business logic (home, compat, premium, …)
```

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set `BOT_TOKEN` from [@BotFather](https://t.me/BotFather).
4. Run:

```bash
python main.py
```

Windows helpers: `start_bot.ps1` or `start_bot.bat`.

## Environment (`.env`)

```env
BOT_TOKEN=
ADMIN_IDS=123456789
FEEDBACK_USERNAME=your_username

ENABLE_PAYMENTS=true
PREMIUM_PRICE_STARS=100
PREMIUM_PRICE_RUB=199
PREMIUM_PRICE_USD=300
PREMIUM_TRIAL_DAYS=7
PAYMENT_PROVIDER_TOKEN=       # YooKassa etc. after BotFather approval
PAYMENT_PROVIDER_TOKEN_USD=   # Stripe etc.

# Optional proxy if Telegram API is blocked
BOT_PROXY=http://127.0.0.1:7890
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot, fill profile |
| `/profile` | Show profile |
| `/today` | Horoscope (day / week / month) |
| `/compat` | Compatibility |
| `/moon` | Moon calendar |
| `/natal` | Natal chart |
| `/mood 1..10` | Save mood |
| `/daily` | Daily / evening / lunar notifications |
| `/prefs`, `/prefssetup` | Personal settings |
| `/premium`, `/buypremium` | Premium status and payment |
| `/ref` | Referral link |
| `/feedback` | Contact support |
| `/language`, `/menu`, `/help`, `/about` | UI helpers |
| `/stats`, `/stars`, `/grantpremium`, `/broadcast`, `/ping` | Admin only |

## Marketing links

- Referral: `https://t.me/YourBot?start=ref_CODE`
- Traffic source: `https://t.me/YourBot?start=src_vk`

## Deploy

Push to `main` triggers GitHub Actions deploy to VPS (`/opt/astro-telegram-bot`, systemd `astrobot`).

Offline checks:

```bash
python scripts/test_core.py
python -m compileall app main.py scripts
```

## Notes

- Entertainment content only — not professional advice.
- Data stored in SQLite (`astro_bot.db` on server).
