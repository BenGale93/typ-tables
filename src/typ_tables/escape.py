"""Module for escaping Typst text."""

import re
from dataclasses import dataclass

ESCAPE_PATTERN = re.compile(r"([\\#*_`$<>@\[\]=+\-/~])")


def escape_value(value: object) -> str:
    """Escape special characters."""
    if not isinstance(value, str):
        return str(value)

    return ESCAPE_PATTERN.sub(r"\\\1", value)


@dataclass
class Typst:
    """Typst text."""

    text: str

    def __str__(self) -> str:
        """String representation."""
        return self.text

    def __bool__(self) -> bool:
        """Return the truthiness of the underlying text."""
        return bool(self.text)
