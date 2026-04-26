"""Module for escaping Typst text."""

import re

ESCAPE_PATTERN = re.compile(r"([\\#*_`$<>@\[\]=+\-/~])")


class Typst(str):
    """Typst text."""

    __slots__ = ()


START = "<typst>"
END = "</typst>"


def formatted(string: str) -> str:
    """Tag a string as formatted with typst."""
    return f"{START}{string}{END}"


def escape_value(value: object) -> Typst | str:
    """Escape special characters."""
    if not isinstance(value, str):
        return str(value)
    if isinstance(value, Typst):
        return value
    if START in value:
        start_index = value.index(START)
        end_index = value.index(END) + len(END)
        before = value[:start_index]
        mid = value[start_index + len(START) : end_index - len(END)]
        after = value[end_index:]

        escaped_before = ESCAPE_PATTERN.sub(r"\\\1", before)
        escaped_after = ESCAPE_PATTERN.sub(r"\\\1", after)

        return f"{escaped_before}{mid}{escaped_after}"

    return ESCAPE_PATTERN.sub(r"\\\1", value)
