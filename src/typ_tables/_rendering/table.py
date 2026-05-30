"""Table rendering."""

from dataclasses import dataclass, field

from typ_tables._rendering.cell import Cell
from typ_tables._style import Sides
from typ_tables.ttypes import Gutter, Relative


@dataclass
class Header:
    content: list[Cell] = field(default_factory=list)
    repeat: bool = True
    level: int = 1

    def render(self) -> str:
        args: list[str] = []
        if not self.repeat:
            args.append("repeat: false,")
        if self.level > 1:
            args.append(f"level: {self.level},")

        row_content = "".join([c.render() for c in self.content])
        if args:
            joined_args = " ".join(args)
            prefix = f"table.header({joined_args})"
        else:
            prefix = "table.header"
        return f"{prefix}{row_content}"


@dataclass
class Footer:
    content: list[Cell] = field(default_factory=list)
    repeat: bool = True

    def render(self) -> str:
        args: list[str] = []
        if not self.repeat:
            args.append("repeat: false,")

        row_content = "".join([c.render() for c in self.content])
        if args:
            joined_args = " ".join(args)
            prefix = f"table.footer({joined_args})"
        else:
            prefix = "table.footer"
        return f"{prefix}{row_content}"


@dataclass
class Table:
    columns: str | None = None
    column_gutter: Gutter | None = None
    row_gutter: Gutter | None = None
    stroke: str | None = None
    alignment: str | None = None
    inset: str | Sides[Relative] | None = None

    headers: list[Header] = field(default_factory=list)
    body: list[list[Cell]] = field(default_factory=list)
    footer: Footer | None = None

    def render(self) -> str:
        args = [
            ("columns", self.columns),
            ("column-gutter", self.column_gutter),
            ("row-gutter", self.row_gutter),
            ("stroke", self.stroke),
            ("align", self.alignment),
            ("inset", self.inset),
        ]

        headers = ",\n  ".join(r.render() for r in self.headers)
        body = ",\n  ".join(", ".join([c.render() for c in r]) for r in self.body)

        inner = [f"{name}: {value}," for name, value in args if value is not None]
        if headers:
            inner.append(headers + ",")
        if body:
            inner.append(body + ",")
        if self.footer:
            inner.append(self.footer.render() + ",\n")
        if (inner and not body and not self.footer) or (body and not self.footer):
            inner[-1] += "\n"

        joined_inner = "\n  ".join(inner)
        if not joined_inner:
            return "#table()\n"
        return f"#table(\n  {joined_inner})\n"
