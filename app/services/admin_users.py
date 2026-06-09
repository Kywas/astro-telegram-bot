"""Admin user list with pagination."""
from __future__ import annotations

from app.bot_context import db
from app.i18n import sign_display, t
from app.premium import is_premium_active

USERS_PAGE_SIZE = 12


def _format_created_at(raw: str | None) -> str:
    if not raw:
        return "—"
    if "T" in raw:
        return raw.split("T", 1)[0]
    return raw[:10]


def _format_user_line(locale: str, index: int, row) -> str:
    name = row.first_name or "—"
    username = f"@{row.username}" if row.username else "—"
    sign = sign_display(locale, row.sign) if row.sign else "—"
    premium = "⭐" if is_premium_active(row.premium_until) else "—"
    source = row.start_source or t(locale, "stats_source_direct")
    created = _format_created_at(row.created_at)
    return t(
        locale,
        "admin_users_line",
        index=str(index),
        user_id=str(row.user_id),
        username=username,
        name=name,
        sign=sign,
        language=row.language,
        premium=premium,
        source=source,
        created=created,
    )


async def build_admin_users_page(locale: str, page: int) -> tuple[str, int, int]:
    total = await db.count_users()
    total_pages = max(1, (total + USERS_PAGE_SIZE - 1) // USERS_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    rows = await db.list_users_page(offset=page * USERS_PAGE_SIZE, limit=USERS_PAGE_SIZE)

    if total == 0:
        body = t(locale, "admin_users_empty")
    else:
        start_index = page * USERS_PAGE_SIZE + 1
        lines = [
            _format_user_line(locale, start_index + offset, row)
            for offset, row in enumerate(rows)
        ]
        body = "\n".join(lines)

    header = t(
        locale,
        "admin_users_header",
        total=str(total),
        page=str(page + 1),
        pages=str(total_pages),
    )
    return f"{header}\n\n{body}", page, total_pages
