"""Telegram HTML formatting helpers for user-facing text."""
from __future__ import annotations

import re
from html import escape

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")

TELEGRAM_TEXT_LIMIT = 4096
TELEGRAM_SAFE_LIMIT = 4080


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
