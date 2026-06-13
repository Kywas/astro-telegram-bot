"""Telegram HTML formatting helpers for user-facing text."""
from __future__ import annotations

import re
from html import escape

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")

TELEGRAM_TEXT_LIMIT = 4096
TELEGRAM_SAFE_LIMIT = 4080

_EMOJI_OR_MARKER = re.compile(
    r"^([\U0001F300-\U0001FAFF\u2600-\u27BF]|ℹ️|✅|⚠️|💡|💞|🌙|⭐|🎯|📋|🔥|💫|❓|✨|🪷|💼|💍|🕉️|✈️|🪬|✍️|1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣|🔟|•)"
)


def h(text: str) -> str:
    return escape(text, quote=False)


def b(text: str) -> str:
    return f"<b>{h(text)}</b>"


def p(*blocks: str) -> str:
    return "\n\n".join(block.strip() for block in blocks if block and block.strip())


def sentence_paragraphs(text: str, *, sentences_per_para: int = 2) -> str:
    text = text.strip()
    if not text:
        return ""
    sentences = [part.strip() for part in _SENTENCE_SPLIT.split(text) if part.strip()]
    if not sentences:
        return h(text)
    chunks: list[str] = []
    buf: list[str] = []
    for sentence in sentences:
        buf.append(sentence)
        if len(buf) >= sentences_per_para:
            chunks.append(h(" ".join(buf)))
            buf = []
    if buf:
        chunks.append(h(" ".join(buf)))
    return p(*chunks)


def enrich_reading(text: str, *, sentences_per_para: int = 2) -> str:
    """Plain prose → paragraphs; first sentence in bold."""
    text = text.strip()
    if not text:
        return ""
    sentences = [part.strip() for part in _SENTENCE_SPLIT.split(text) if part.strip()]
    if not sentences:
        return h(text)
    lead = sentences[0]
    if not lead.endswith((".", "!", "?", "…")):
        lead = f"{lead}."
    blocks = [b(lead)]
    if len(sentences) > 1:
        rest = " ".join(sentences[1:])
        body = sentence_paragraphs(rest, sentences_per_para=sentences_per_para)
        if body:
            blocks.append(body)
    return p(*blocks)


def qa_response(header: str, question: str, body: str) -> str:
    return p(
        b(header),
        f"❓ {h(question)}",
        body.strip(),
    )


def section_block(title: str, body: str) -> str:
    body = body.strip()
    if not body:
        return b(title)
    return f"{b(title)}\n{sentence_paragraphs(body, sentences_per_para=2)}"


def labeled_block(label: str, body: str) -> str:
    body = body.strip()
    if not body:
        return b(label)
    return f"{b(label)}\n{sentence_paragraphs(body, sentences_per_para=2)}"


def breadcrumb_html(root: str, *parts: str) -> str:
    trail = " › ".join([h(root), *(h(part) for part in parts)])
    return f"<i>{trail}</i>"


def _is_header_line(line: str) -> bool:
    line = line.strip()
    if not line:
        return False
    if line.startswith(("•", "-", "·")):
        return False
    if _EMOJI_OR_MARKER.match(line):
        return True
    if line.endswith(":") and len(line) <= 120:
        return True
    return len(line) <= 80 and not line.endswith(".")


def _format_section(section: str) -> str:
    lines = [line.strip() for line in section.split("\n") if line.strip()]
    if not lines:
        return h(section)
    if len(lines) == 1:
        line = lines[0]
        if _is_header_line(line):
            return b(line)
        if "." in line:
            return enrich_reading(line)
        return b(line)

    blocks: list[str] = []
    body_lines: list[str] = []
    for line in lines:
        if not body_lines and _is_header_line(line):
            blocks.append(b(line))
            continue
        body_lines.append(line)
    if body_lines:
        body = "\n".join(body_lines)
        blocks.append(sentence_paragraphs(body) if "." in body else h(body))
    if len(blocks) == 1:
        return blocks[0]
    return p(*blocks)


def format_screen_body(text: str) -> str:
    """Plain panel copy → HTML paragraphs with bold section leads."""
    text = (text or "").strip()
    if not text:
        return ""
    if "<b>" in text:
        if "\n\n" in text:
            return p(*[part.strip() for part in text.split("\n\n") if part.strip()])
        return text
    sections = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not sections:
        return h(text)
    return p(*(_format_section(section) for section in sections))


def format_report(text: str) -> str:
    """Long multi-section readings (synastry, natal chart parts)."""
    return format_screen_body(text)


def screen_page(breadcrumb: str | None = None, *sections: str) -> str:
    blocks: list[str] = []
    if breadcrumb:
        blocks.append(breadcrumb)
    for section in sections:
        if section:
            blocks.append(format_screen_body(section))
    return p(*blocks)


def prepare_panel_text(text: str) -> str:
    """Format user-facing panel text unless it is already HTML-heavy."""
    text = (text or "").strip()
    if not text or "<b>" in text:
        return text
    if text.startswith("<i>") and "</i>" in text:
        breadcrumb_part, _, body = text.partition("\n\n")
        if body:
            return p(breadcrumb_part, format_screen_body(body))
        return breadcrumb_part
    return format_screen_body(text)


def _hard_split_text(text: str, limit: int) -> list[str]:
    parts: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            parts.append(remaining)
            break
        cut = remaining.rfind(" ", 0, limit)
        if cut <= limit // 4:
            cut = limit
        parts.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    return [part for part in parts if part]


def split_telegram_text(text: str, *, limit: int = TELEGRAM_SAFE_LIMIT) -> list[str]:
    """Split text into Telegram-safe chunks, preferring paragraph/line boundaries."""
    text = text or ""
    if len(text) <= limit:
        return [text]

    if "\n\n" in text:
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
        separator = "\n\n"
    else:
        blocks = [block.strip() for block in text.split("\n") if block.strip()]
        separator = "\n"

    if not blocks:
        return _hard_split_text(text, limit)

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append(separator.join(current))
            current = []
            current_len = 0

    for block in blocks:
        if len(block) > limit:
            flush()
            chunks.extend(_hard_split_text(block, limit))
            continue
        extra = len(separator) if current else 0
        if current_len + extra + len(block) > limit:
            flush()
        current.append(block)
        current_len += extra + len(block)

    flush()
    return chunks or _hard_split_text(text, limit)
