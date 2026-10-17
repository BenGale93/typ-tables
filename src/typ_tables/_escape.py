"""Module for escaping Typst text."""

import re

ESCAPE_PATTERN = re.compile(r"([\\#*_`$<>@\[\]=+\-/~])")


class Typst(str):
    """Raw Typst markup that should not be escaped.

    Wrap strings in `Typst` when you intentionally want Typst syntax to be
    interpreted by the rendered document. Plain strings are escaped so special
    Typst characters are displayed as text; `Typst` values are passed through
    unchanged.
    """

    __slots__: tuple[()] = ()


START = "<typst>"
END = "</typst>"

# Formatters wrap already-rendered values in `<typst>...</typst>` sentinels so that
# `escape_value` can pass them through as raw Typst. Only well-formed pairs are
# treated as markup; anything else (including stray start/end markers) is escaped
# like ordinary text.
SENTINEL_PATTERN = re.compile(re.escape(START) + ".*?" + re.escape(END), re.DOTALL)


def formatted(string: str) -> str:
    """Tag a string as formatted with typst."""
    return f"{START}{string}{END}"


def escape_value(value: object) -> Typst | str:
    """Escape special characters.

    Well-formed `<typst>...</typst>` sentinels (produced by `formatted`) are
    preserved as raw Typst, while all surrounding text is escaped. Multiple
    sentinel pairs in a single string are all preserved, and unmatched or
    otherwise malformed sentinels are escaped as ordinary text instead of
    raising an error.
    """
    if not isinstance(value, str):
        return str(value)
    if isinstance(value, Typst):
        return value

    parts: list[str] = []
    last = 0
    for match in SENTINEL_PATTERN.finditer(value):
        parts.append(ESCAPE_PATTERN.sub(r"\\\1", value[last : match.start()]))
        parts.append(value[match.start() + len(START) : match.end() - len(END)])
        last = match.end()
    parts.append(ESCAPE_PATTERN.sub(r"\\\1", value[last:]))

    return "".join(parts)
