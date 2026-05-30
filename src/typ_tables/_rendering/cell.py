"""Cell rendering."""

from dataclasses import dataclass, field, fields

from typ_tables._escape import Typst, escape_value
from typ_tables._style import CellStyleForCell, TextStyleForCell


def _to_typst(v: object, *, wrap: bool = False) -> object:
    if wrap and isinstance(v, str):
        return f'"{_to_typst(v, wrap=False)}"'
    if isinstance(v, bool):
        return "true" if v else "false"
    return v


@dataclass
class Content:
    value: str | Typst | None
    text_style: TextStyleForCell = field(default_factory=TextStyleForCell)

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        args: list[str] = []
        for f in fields(self.text_style):
            name = f.name
            value = getattr(self.text_style, name)
            if value is None:
                continue

            wrap = "wrap" in f.metadata
            v = _to_typst(value, wrap=wrap)

            args.append(f"{name}: {v}")

        content = "None" if self.value is None else f"{escape_value(self.value)}"
        if args:
            joined_args = ", ".join(args)
            content = f"#text({joined_args})[{content}]"

        return content


@dataclass
class Cell:
    """A table cell."""

    content: Content
    rowspan: int = 1
    colspan: int = 1
    cell_style: CellStyleForCell = field(default_factory=CellStyleForCell)

    def render(self) -> str:
        args: list[str] = []
        if self.rowspan > 1:
            args.append(f"rowspan: {self.rowspan}")
        if self.colspan > 1:
            args.append(f"colspan: {self.colspan}")
        for f in fields(self.cell_style):
            name = f.name
            value = getattr(self.cell_style, name)
            if value is None:
                continue

            wrap = "wrap" in f.metadata
            v = _to_typst(value, wrap=wrap)

            args.append(f"{name}: {v}")

        cell = "[]" if not self.content else f"[{self.content}]"
        if args:
            joined_args = ", ".join(args)
            cell = f"[#table.cell({joined_args}){cell}]"

        return cell
