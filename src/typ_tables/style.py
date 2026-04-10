"""Module for specifying Typst cell styling."""

import typing as t
from dataclasses import asdict, dataclass, field, fields
from textwrap import indent

import narwhals as nw

from typ_tables.escape import Typst, escape_value
from typ_tables.ttypes import Alignment, Auto, Data

Relative = str


@dataclass(slots=True)
class Sides:
    """Represents per-side relative size values for Typst properties.

    Attributes:
        rest: Default value for unspecified sides.
        x: Horizontal value applied to left and right.
        y: Vertical value applied to top and bottom.
        top: Top-side value.
        right: Right-side value.
        left: Left-side value.
        bottom: Bottom-side value.
    """

    rest: Relative | None = None
    x: Relative | None = None
    y: Relative | None = None
    top: Relative | None = None
    right: Relative | None = None
    left: Relative | None = None
    bottom: Relative | None = None

    def __str__(self) -> str:
        """Render the sides object as a Typst-style named tuple string.

        Returns:
            A string like `"(top: 1pt, x: 2pt)"` containing only set fields.
        """
        set_sides = []
        for name, value in asdict(self).items():
            if value is None:
                continue
            set_sides.append(f"{name}: {value}")

        sides = ", ".join(set_sides)
        return f"({sides})"


CELL_PROPERTY_INDENT = " " * 2

Length = str
FontStyle = t.Literal["normal", "italic", "oblique"]
FontWeight = (
    t.Literal[
        "thin", "extralight", "light", "regular", "medium", "semibold", "bold", "extrabold", "black"
    ]
    | int
)


def _to_typst(v: object, *, wrap: bool = False) -> object:
    if wrap and isinstance(v, str):
        return f'"{_to_typst(v, wrap=False)}"'
    if isinstance(v, bool):
        return "true" if v else "false"
    return v


@dataclass
class TextStyleForCell:
    """Text style for an individual cell in a table."""

    font: str | None = field(default=None, metadata={"wrap": True})
    style: FontStyle | None = field(default=None, metadata={"wrap": True})
    weight: FontWeight | None = field(default=None, metadata={"wrap": True})
    stretch: str | None = None
    size: Length | None = None
    fill: str | None = None
    stroke: str | None = None
    tracking: Length | None = None
    spacing: Relative | None = None
    fractions: bool | None = None

    def to_typst(self, body: str) -> str:
        """Wrap a body string in a Typst `text(...)` call when configured.

        Args:
            body: Pre-rendered Typst cell body to style.

        Returns:
            The original body if no text properties are set, otherwise a
            `text(...)` block wrapping `body`.
        """
        text_snippets = ["text("]

        for f in fields(self):
            name = f.name
            value = getattr(self, name)
            if value is None:
                continue

            wrap = "wrap" in f.metadata
            v = _to_typst(value, wrap=wrap)

            text_snippets.append(indent(f"{name}: {v},", CELL_PROPERTY_INDENT))

        if len(text_snippets) == 1:
            return body

        text_snippets.append(f"){body}")
        return "\n".join(text_snippets)

    def __or__(self, value: object) -> t.Self:
        """Merge two text styles, preferring values from `value` when set.

        Args:
            value: Another `TextStyle` instance.

        Returns:
            A merged `TextStyle` instance.
        """
        if not isinstance(value, type(self)):  # pragma: no cover
            return NotImplemented

        new_text_style = {}
        for f in fields(self):
            name = f.name
            current = getattr(self, name)
            new = getattr(value, name)
            new_text_style[name] = new if new is not None else current

        return type(self)(**new_text_style)


class _DataclassInstance(t.Protocol):
    __dataclass_fields__: t.ClassVar[dict[str, t.Any]]


def _resolve_style_to_list_of_styles(
    instance: _DataclassInstance, data: Data
) -> dict[str, list[t.Any]]:
    n_rows = len(data)
    resolved_fields: dict[str, list[t.Any]] = {}
    for f in fields(instance):
        name = f.name
        value = getattr(instance, name)
        if isinstance(value, nw.Expr):
            result = data.select(value)
            values = result[result.columns[0]].to_list()
            resolved_fields[name] = values
        elif isinstance(value, list):
            resolved_fields[name] = value
        else:
            resolved_fields[name] = [value] * n_rows
    return resolved_fields


def _resolve_style_to_single_style(instance: _DataclassInstance) -> dict[str, t.Any]:
    resolved_fields: dict[str, t.Any] = {}
    for f in fields(instance):
        name = f.name
        value = getattr(instance, name)
        if isinstance(value, (list, nw.Expr)):
            msg = f"Expected only scalars in style field: `{name}` for this location."
            raise TypeError(msg)
        resolved_fields[name] = value
    return resolved_fields


@dataclass
class TextStyle:
    """Text-level style properties applied to table cell content."""

    font: str | list[str] | nw.Expr | None = None
    style: FontStyle | list[FontStyle] | nw.Expr | None = None
    weight: FontWeight | list[FontWeight] | nw.Expr | None = None
    stretch: str | list[str] | nw.Expr | None = None
    size: Length | list[Length] | nw.Expr | None = None
    fill: str | list[str] | nw.Expr | None = None
    stroke: str | list[str] | nw.Expr | None = None
    tracking: Length | list[Length] | nw.Expr | None = None
    spacing: Relative | list[Relative] | nw.Expr | None = None
    fractions: bool | list[bool] | nw.Expr | None = None

    def resolve(self, data: Data) -> list[TextStyleForCell]:
        """Resolve the text style into a list of text styles for each cell in a column."""
        resolved_fields = _resolve_style_to_list_of_styles(self, data)
        return [
            TextStyleForCell(**dict(zip(resolved_fields, t, strict=True)))
            for t in zip(*resolved_fields.values(), strict=True)
        ]

    def get_single(self) -> TextStyleForCell:
        """Return a text style for a single cell.

        Used for single cell locations like the header.
        """
        resolved_fields = _resolve_style_to_single_style(self)
        return TextStyleForCell(**resolved_fields)


@dataclass
class CellStyleForCell:
    """Cell style for an individual cell in a table."""

    inset: Relative | Sides | None = None
    align: Auto | Alignment | None = None

    def to_typst(self, body: str, colspan: int | None = None) -> str:
        """Wrap a body string in a Typst `table.cell(...)` call when configured.

        Args:
            body: Pre-rendered Typst body string.
            colspan: Optional number of columns spanned by the cell.

        Returns:
            The original body if no cell properties are set and `colspan` is
            not provided, otherwise a `table.cell(...)` block wrapping `body`.
        """
        cell_snippets = ["table.cell("]
        if colspan is not None:
            cell_snippets.append(indent(f"colspan: {colspan},", CELL_PROPERTY_INDENT))

        for f in fields(self):
            name = f.name
            value = getattr(self, name)
            if value:
                cell_snippets.append(indent(f"{name}: {value},", CELL_PROPERTY_INDENT))

        if len(cell_snippets) == 1:
            return body

        cell_snippets.append(indent(body, CELL_PROPERTY_INDENT))

        cell_snippets.append("),")
        return "\n".join(cell_snippets)

    def __or__(self, value: object) -> t.Self:
        """Merge two cell styles, preferring values from `value` when set.

        Args:
            value: Another `CellStyle` instance.

        Returns:
            A merged `CellStyle` instance.
        """
        if not isinstance(value, type(self)):  # pragma: no cover
            return NotImplemented

        new_cell_style = {}
        for f in fields(self):
            name = f.name
            current = getattr(self, name)
            new = getattr(value, name)
            new_cell_style[name] = new if new is not None else current

        return type(self)(**new_cell_style)


@dataclass
class CellStyle:
    """Text-level style properties applied to table cell content."""

    inset: Relative | Sides | list[Relative | Sides] | nw.Expr | None = None
    align: Auto | Alignment | list[Auto | Alignment] | nw.Expr | None = None

    def resolve(self, data: Data) -> list[CellStyleForCell]:
        """Resolve the cell style into a list of cell styles for each cell in a column."""
        resolved_fields = _resolve_style_to_list_of_styles(self, data)
        return [
            CellStyleForCell(**dict(zip(resolved_fields, t, strict=True)))
            for t in zip(*resolved_fields.values(), strict=True)
        ]

    def get_single(self) -> CellStyleForCell:
        """Return a cell style for a single cell.

        Used for single cell locations like the header.
        """
        resolved_fields = _resolve_style_to_single_style(self)
        return CellStyleForCell(**resolved_fields)


@dataclass
class StyleHolder:
    """Container for composing text and cell style layers.

    Attributes:
        text: Optional text-level style settings.
        cell: Optional cell-level style settings.
    """

    text: TextStyleForCell | None = None
    cell: CellStyleForCell | None = None

    def to_typst(self, body: str | Typst, colspan: int | None = None) -> str:
        """Render a value into a fully styled Typst cell snippet.

        Args:
            body: Raw value or pre-escaped Typst content.
            colspan: Optional number of columns the cell spans.

        Returns:
            A Typst snippet with value escaping plus text and cell wrappers
            applied when configured.
        """
        body = f"[{escape_value(body)}],"
        if self.text:
            body = self.text.to_typst(body)
        if self.cell or (colspan is not None and colspan > 1):
            cell = CellStyleForCell() if self.cell is None else self.cell
            body = cell.to_typst(body, colspan)
        return body

    def __or__(self, value: object) -> t.Self:
        """Merge two style holders, preferring values from `value` when set.

        Args:
            value: Another `StyleHolder` instance.

        Returns:
            A merged `StyleHolder` instance.
        """
        if not isinstance(value, StyleHolder):  # pragma: no cover
            return NotImplemented

        new_text = value.text if value.text is not None else self.text

        new_cell = value.cell if value.cell is not None else self.cell

        return type(self)(text=new_text, cell=new_cell)
