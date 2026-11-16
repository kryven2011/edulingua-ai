"""EduLingua AI — General Helper Utilities.

Small, stateless utility functions used across the codebase.
"""

from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime
from typing import Any


def generate_progress_bar(
    current: int,
    total: int,
    *,
    length: int = 10,
    filled: str = "🟩",
    empty: str = "⬜",
) -> str:
    """Render an emoji-based progress bar.

    >>> generate_progress_bar(3, 10)
    '🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜'
    """
    if total <= 0:
        return empty * length
    ratio = min(current / total, 1.0)
    filled_len = round(ratio * length)
    return filled * filled_len + empty * (length - filled_len)


def truncate_text(text: str, max_length: int, *, suffix: str = "…") -> str:
    """Truncate *text* to *max_length* characters, appending *suffix* if cut.

    >>> truncate_text("Hello, World!", 5)
    'Hello…'
    """
    if len(text) <= max_length:
        return text
    return text[: max_length].rstrip() + suffix


def format_datetime(
    dt: datetime,
    lang: str = "en",
    *,
    include_time: bool = False,
) -> str:
    """Format a datetime for display, adapting to *lang*.

    Returns a locale-friendly string; falls back to ISO for unknown
    languages.
    """
    if include_time:
        fmt_map: dict[str, str] = {
            "ru": "%d.%m.%Y %H:%M",
            "uz": "%d.%m.%Y %H:%M",
            "en": "%Y-%m-%d %H:%M",
        }
    else:
        fmt_map = {
            "ru": "%d.%m.%Y",
            "uz": "%d.%m.%Y",
            "en": "%Y-%m-%d",
        }
    fmt = fmt_map.get(lang, "%Y-%m-%d")
    return dt.strftime(fmt)


_TAG_RE = re.compile(r"<[^>]+>")
_ALLOWED_TAGS = {"b", "i", "u", "s", "code", "pre", "a", "em", "strong"}


def sanitize_html(text: str) -> str:
    """Strip dangerous HTML tags, keeping only Telegram-safe formatting.

    Allowed tags: ``<b>``, ``<i>``, ``<u>``, ``<s>``, ``<code>``,
    ``<pre>``, ``<a>``, ``<em>``, ``<strong>``.
    """

    def _replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        # Extract the tag name (handle closing and self-closing tags)
        inner = tag.strip("<>/ ")
        tag_name = inner.split()[0].lower() if inner else ""
        if tag_name in _ALLOWED_TAGS:
            return tag
        return html.escape(tag)

    return _TAG_RE.sub(_replace, text)


def generate_idempotency_key(user_id: int, action: str, *args: Any) -> str:
    """Produce a deterministic idempotency key.

    The key is a SHA-256 hex digest derived from the user ID, action
    name, and any additional discriminators.

    >>> generate_idempotency_key(42, "xp_award", "lesson_1")
    '...'  # 64-char hex string
    """
    parts = [str(user_id), action] + [str(a) for a in args]
    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()
