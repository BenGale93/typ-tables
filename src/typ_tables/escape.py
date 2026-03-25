"""Module for escaping Typst text."""

import re

ESCAPE_PATTERN = re.compile(r"([\\#*_`$<>@\[\]=+\-/~])")


def escape_value(value: object) -> str:
    """Escape special characters."""
    if not isinstance(value, str):
        return str(value)

    return ESCAPE_PATTERN.sub(r"\\\1", value)
