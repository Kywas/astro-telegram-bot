"""Plain-language compatibility narratives — simple, warm, a little humor, no astro jargon."""
from __future__ import annotations

from app.sun_sign_compat import SIGN_LABELS, SunSignCompat, SunSignKind
from app.synastry_elements import COMPATIBLE_ELEMENT_PAIRS, ElementBalance


def _lang(locale: str) -> str:
    return "ru" if locale == "ru" else "en"


def _mode_key(mode: str) -> str:
    return mode if mode in {"love", "friendship", "work"} else "love"


_SIGN_VIBE = {
    "ru": {
        "Aries": "действие и «давай уже»",
        "Taurus": "стабильность и «не торопи»",
        "Gemini": "разговоры и «ещё одна идея»",
        "Cancer": "забота и «обнимашки, когда тяжело»",
        "Leo": "яркость и «заметь меня»",
        "Virgo": "порядок и «давай по плану»",
        "Libra": "гармония и «давай без скандала»",
        "Scorpio": "глубина и «не поверхностно»",
        "Sagittarius": "свобода и «куда дальше»",
        "Capricorn": "цели и «сначала дело»",
        "Aquarius": "своё мнение и «не как у всех»",
        "Pisces": "чувствительность и «я всё чувствую»",
    },
    "en": {
        "Aries": "action and «let's go already»",
        "Taurus": "stability and «don't rush me»",
        "Gemini": "talk and «one more idea»",
        "Cancer": "care and «hug me when it's hard»",
        "Leo": "spotlight and «notice me»",
        "Virgo": "order and «let's follow the plan»",
        "Libra": "harmony and «no drama please»",
        "Scorpio": "depth and «nothing shallow»",
        "Sagittarius": "freedom and «where next»",
        "Capricorn": "goals and «work first»",
        "Aquarius": "own take and «not like everyone»",
        "Pisces": "sensitivity and «I feel everything»",
    },
}

_DOMINANT_VIBE = {
    "ru": {
        "fire": "драйв, спонтанность и «погнали»",
        "earth": "стабильность, быт и «давай надёжно»",
        "air": "болтовня, идеи и «а если по-другому»",
        "water": "чувства, глубина и «что между нами»",
    },
    "en": {
        "fire": "drive, spontaneity, and «let's go»",
        "earth": "stability, routine, and «let's do this solidly»",
        "air": "chat, ideas, and «what if we try another way»",
        "water": "feelings, depth, and «what's between us»",
    },
}


def _sign_vibe(locale: str, sign_key: str) -> str:
    return _SIGN_VIBE[_lang(locale)].get(sign_key, sign_key)


def _dominant_vibe(locale: str, element: str) -> str:
    return _DOMINANT_VIBE[_lang(locale)].get(element, element)


def plain_sun_sign_narrative(locale: str, compat: SunSignCompat, *, mode: str = "love") -> str:
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    user = SIGN_LABELS[lang][compat.user_sign]
    partner = SIGN_LABELS[lang][compat.partner_sign]
    user_v = _sign_vibe(locale, compat.user_sign)
    partner_v = _sign_vibe(locale, compat.partner_sign)

    if lang == "ru":
        titles = {
            "love": "☀️ Кто вы по знакам",
            "friendship": "☀️ Вы как друзья по знакам",
            "work": "☀️ Вы как команда по знакам",
        }
        title = titles[mode_key]
    else:
        titles = {
            "love": "☀️ Who you are by sign",
            "friendship": "☀️ You as friends by sign",
            "work": "☀️ You as a team by sign",
        }
        title = titles[mode_key]

    if compat.kind == SunSignKind.SAME_SIGN:
        openings = {
            "love": (
                f"{user} + {partner} — вы как два зеркала. "
                f"Быстро понимаете друг друга, иногда слишком быстро — и повторяете одни косяки вдвоём."
            ),
            "friendship": (
                f"{user} + {partner} — похожие люди, похожый юмор. "
                f"Дружба лёгкая, но иногда не хватает «свежего взгляда сбоку»."
            ),
            "work": (
                f"{user} + {partner} — один стиль работы. "
                f"Меньше объяснений «на пальцах», но легко застрять в одном подходе."
            ),
        }
        closers = {
            "love": "Следите, чтобы не превращаться в «мы всегда правы, потому что мы одинаковые».",
            "friendship": "Иногда полезно позвать третьего — не для драмы, а для другого угла.",
            "work": "Назначьте кого-то «адвокатом другой идеи» — хотя бы на совещании.",
        }
    elif compat.kind == SunSignKind.OPPOSITE:
        openings = {
            "love": (
                f"{user} и {partner} — противоположности. Магнит работает, "
                f"но без разговоров легко устроить мини-шторм из «ты опять не так понял»."
            ),
            "friendship": (
                f"{user} и {partner} — разные, но интересные. "
                f"Как специи: без контраста скучно, с контрастом — вкусно, если не переборщить."
            ),
            "work": (
                f"{user} и {partner} — разные стили. "
                f"Один тянет в одну сторону, другой — в другую. В задачах это сила, если есть правила."
            ),
        }
        closers = {
            "love": "Не пытайтесь переделать друг друга — лучше договориться, что каждый приносит в пару.",
            "friendship": "Уважайте разницу — дружба не про клонов, а про «ты другой, и это ок».",
            "work": "Распределите роли: кто генерирует, кто проверяет, кто доводит до конца.",
        }
    elif compat.kind == SunSignKind.SAME_ELEMENT:
        openings = {
            "love": (
                f"{user} + {partner} — похожий темп. "
                f"Часто понимаете друг друга с полуслова — удобно, когда не играете в молчанку."
            ),
            "friendship": (
                f"{user} + {partner} — «свои» по ритму. "
                f"Легко болтать и не объяснять, почему вы устали от людей."
            ),
            "work": (
                f"{user} + {partner} — один рабочий темп. "
                f"Меньше «ты опять торопишься / тянешь», больше общего языка в задачах."
            ),
        }
        closers = {
            "love": "Осторожно только с одной слепой зоной на двоих — её тоже можно не замечать.",
            "friendship": "Не забывайте иногда выходить из пузыря «мы такие же» — мир шире.",
            "work": "Если оба любите один подход — проверьте, не пропускаете ли очевидные риски.",
        }
    elif compat.kind == SunSignKind.COMPATIBLE_ELEMENTS:
        openings = {
            "love": (
                f"{user} ({user_v}) и {partner} ({partner_v}) — "
                f"хорошо дополняете друг друга. Обычно легче договориться, чем спорить до ночи."
            ),
            "friendship": (
                f"{user} и {partner} — разные, но стыкуются. "
                f"Один приносит одно, другой — другое, и из этого получается живой контакт."
            ),
            "work": (
                f"{user} и {partner} — разные сильные стороны, но они складываются. "
                f"Как «идеи + исполнение», если не мешать друг другу."
            ),
        }
        closers = {
            "love": "Главное — не воспринимать различия как «он/она неправильный».",
            "friendship": "Цените, что другой не копия — иначе зачем дружить.",
            "work": "Закрепите, кто за что отвечает — и не лезьте в чужую зону без спроса.",
        }
    else:
        openings = {
            "love": (
                f"{user} ({user_v}) и {partner} ({partner_v}) — "
                f"классика «плед vs уведомления». Один тянет к уюту и «ты со мной?», "
                f"другой — к движению и «давай ещё тему». Не баг — feature, если говорить."
            ),
            "friendship": (
                f"{user} и {partner} — разный темп. "
                f"Один пишет «давай созвонимся», другой «я тут, просто в потоке». "
                f"Нормально, если не требовать одинаковой скорости ответов."
            ),
            "work": (
                f"{user} и {partner} — разные рабочие стили. "
                f"Один про «давай надёжно», другой про «давай быстрее/иначе». "
                f"В проектах распределите: кто держит процесс, кто приносит варианты."
            ),
        }
        closers = {
            "love": "Намёки не работают — лучше один честный разговор, чем неделя додумываний.",
            "friendship": "Скажите вслух, как вам удобно общаться — это не неловко, это взрослость.",
            "work": "Письменно фиксируйте задачи — «я думал, ты сам» — любимая фраза хаоса.",
        }

    opening = openings[mode_key]
    closer = closers[mode_key]
    return f"{title}\n\n{opening}\n\n{closer}"


def plain_element_balance_narrative(locale: str, balance: ElementBalance, *, mode: str = "love") -> str:
    lang = _lang(locale)
    mode_key = _mode_key(mode)
    user_v = _dominant_vibe(locale, balance.user.dominant)
    partner_v = _dominant_vibe(locale, balance.partner.dominant)
    compatible = (balance.user.dominant, balance.partner.dominant) in COMPATIBLE_ELEMENT_PAIRS
    same = balance.user.dominant == balance.partner.dominant

    if lang == "ru":
        titles = {
            "love": "⚖️ Темп и ритм",
            "friendship": "⚖️ Темп дружбы",
            "work": "⚖️ Рабочий ритм",
        }
        title = titles[mode_key]
    else:
        titles = {
            "love": "⚖️ Pace and rhythm",
            "friendship": "⚖️ Friendship pace",
            "work": "⚖️ Work pace",
        }
        title = titles[mode_key]

    if same:
        cores = {
            "love": (
                f"У вас похожий внутренний темп — больше про {user_v}. "
                f"Понимаете друг друга быстрее, но можете застрять в одних и тех же привычках."
            ),
            "friendship": (
                f"Вы на одной волне — оба больше про {user_v}. "
                f"Легко дружить, но иногда не хватает «а давай по-другому»."
            ),
            "work": (
                f"Рабочий ритм похож — оба про {user_v}. "
                f"Меньше трения в темпе, но следите, чтобы не пропустить слепую зону команды."
            ),
        }
    elif compatible:
        cores = {
            "love": (
                f"Ты больше про {user_v}, партнёр — про {partner_v}. "
                f"Классика «один заземляет, другой оживляет» — если не мешать друг другу."
            ),
            "friendship": (
                f"Ты про {user_v}, друг — про {partner_v}. "
                f"Дополняете друг друга: одному легче там, где другому скучно."
            ),
            "work": (
                f"Ты про {user_v}, коллега — про {partner_v}. "
                f"Хорошая связка «план + идеи» — если роли не смешивать."
            ),
        }
    else:
        cores = {
            "love": (
                f"Темп разный: ты ближе к {user_v}, партнёр — к {partner_v}. "
                f"Это не «несовместимы», это «разный Wi‑Fi». Договоритесь, когда тормозить, а когда газовать."
            ),
            "friendship": (
                f"Ритмы разные: ты — {user_v}, друг — {partner_v}. "
                f"Не спорьте, кто прав — просто скажите, как вам удобно писать и видеться."
            ),
            "work": (
                f"Скорости разные: ты — {user_v}, коллега — {partner_v}. "
                f"Не ждите телепатии — проговорите дедлайны и «готово» значит готово."
            ),
        }

    gap = _gap_hint(locale, balance, mode_key)
    closer = {
        "ru": {
            "love": "Если чувствуете «не на одной волне» — скажите об этом. Карта не приговор, разговор — бесплатный.",
            "friendship": "Дружба не про одинаковость — про честность. Даже «мне нужно побыть одному» — норм.",
            "work": "Разный темп — не повод для войны, повод для нормального brief.",
        },
        "en": {
            "love": "If you feel out of sync — say so. The chart isn't a verdict; talking is free.",
            "friendship": "Friendship isn't sameness — it's honesty. Even «I need alone time» is fine.",
            "work": "Different pace isn't war — it's a reason for a clear brief.",
        },
    }[lang][mode_key]

    parts = [title, "", cores[mode_key]]
    if gap:
        parts.extend(["", gap])
    parts.extend(["", closer])
    return "\n".join(parts)


def _gap_hint(locale: str, balance: ElementBalance, mode_key: str) -> str:
    lang = _lang(locale)
    for element in ("fire", "earth", "air", "water"):
        u, p = balance.user.counts[element], balance.partner.counts[element]
        vibe = _dominant_vibe(locale, element)
        if u >= 2 and p == 0:
            hints = {
                "ru": {
                    "love": f"Тебе ближе {vibe}, партнёру — нет. Не обижайся, если он/она не считывает это с полуслова.",
                    "friendship": f"Тебе близко {vibe}, другу — меньше. Объясни один раз — не три года намёками.",
                    "work": f"Тебе важно {vibe}, коллеге — меньше. Проговори ожидания, не жди «сам поймёт».",
                },
                "en": {
                    "love": f"You lean on {vibe}, your partner less. Don't sulk if they don't read your mind.",
                    "friendship": f"{vibe.capitalize()} matters more to you. Explain once — not three years of hints.",
                    "work": f"You care about {vibe}; your colleague less. State expectations — no mind-reading.",
                },
            }
            return hints[lang][mode_key]
        if p >= 2 and u == 0:
            hints = {
                "ru": {
                    "love": f"Партнёру ближе {vibe}, тебе — меньше. Не обесценивай — просто спроси, что для него/неё важно.",
                    "friendship": f"Другу ближе {vibe}. Не «он странный» — просто другой язык заботы.",
                    "work": f"Коллеге ближе {vibe}. Уважай стиль — и попроси свой формат ответа.",
                },
                "en": {
                    "love": f"Your partner leans on {vibe}, you less. Don't dismiss — ask what matters to them.",
                    "friendship": f"Your friend leans on {vibe}. Not «weird» — just a different care language.",
                    "work": f"Your colleague leans on {vibe}. Respect it — and ask for your preferred format.",
                },
            }
            return hints[lang][mode_key]
    return ""
