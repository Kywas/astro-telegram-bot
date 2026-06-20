# Расписание на 7 дней (3 поста в день)

Посты **11–31** — контент на неделю после запуска первых 10.

| День | Утро (morning) | Обед (lunch) | Вечер (evening) |
|------|----------------|--------------|-----------------|
| 1 | `same-again` | `your-sign` | `evening-letgo` |
| 2 | `morning-hard` | `inner-voice` | `boundaries` |
| 3 | `tiny-ritual` | `name-feeling` | `trigger-soft` |
| 4 | `week-soft` | `stories-compare` | `phone-drain` |
| 5 | `small-win` | `fear-wrong` | `cant-sleep` |
| 6 | `ask-help` | `jealousy-ok` | `light-day` |
| 7 | `moon-day` | `burnout-signal` | `need-control` |

## Публикация на сервере (вся неделя)

```bash
cd /opt/astro-telegram-bot && git pull && . .venv/bin/activate

for slug in same-again your-sign evening-letgo morning-hard inner-voice boundaries tiny-ritual name-feeling trigger-soft week-soft stories-compare phone-drain small-win fear-wrong cant-sleep ask-help jealousy-ok light-day moon-day burnout-signal need-control; do
  echo "Publishing $slug..."
  python scripts/publish_channel_post.py "$slug"
  sleep 45
done
```

Или по одному: `/channelpublish same-again`
