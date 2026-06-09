from __future__ import annotations

import re
from urllib.parse import unquote

_START_SOURCE_RE = re.compile(r"^[a-z0-9_]{1,32}$", re.IGNORECASE)


def parse_ref_code_from_start(payload: str) -> str | None:
    raw = unquote(payload.strip())
    if not raw.lower().startswith("ref_"):
        return None
    code = raw[4:].strip()
    return code or None


def parse_start_source_from_start(payload: str) -> str | None:
    raw = unquote(payload.strip())
    if not raw.lower().startswith("src_"):
        return None
    source = raw[4:].strip().lower()
    if not source or not _START_SOURCE_RE.match(source):
        return None
    return source
