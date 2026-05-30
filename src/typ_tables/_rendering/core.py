"""Core rendering functionality."""

import typing as t
from dataclasses import dataclass
from textwrap import indent

from typ_tables import Typst
from typ_tables._escape import escape_value


class Renderable(t.Protocol):
    """Can be rendered to a Typst string."""

    def render(self) -> str:
        """Render to a Typst string."""


@dataclass
class Figure:
    body: Renderable

    caption: Typst | str | None = None

    def render(self) -> str:
        args: list[str] = []
        if self.caption:
            args.append(f"caption: [{escape_value(self.caption)}]")
        rendered_body = self.body.render()
        if not args:
            return rendered_body
        joined_args = ",\n  ".join(args)
        return f"#figure({joined_args})[\n{indent(rendered_body, '  ')}]\n"
