"""Module for specifying Typst cell styling."""

import typing as t
from dataclasses import asdict, dataclass, field, fields
from textwrap import indent

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables._escape import Typst, escape_value
from typ_tables.ttypes import Alignment, Auto, Data, Relative

Fill = str
"""Typst fill value.

Use any Typst-compatible paint string, such as `"red"` or `"#f2f2f2"`.
"""
Length = str
"""Typst length value.

Use a Typst-compatible string such as `"10pt"`, `"1em"`, or `"0.2cm"`.
"""
Stroke = str
"""Typst stroke value.

Use any Typst-compatible stroke string, such as `"1pt + black"`.
"""
FontStyle = t.Literal["normal", "italic", "oblique"]
"""Typst font style keyword."""
FontWeight = (
    t.Literal[
        "thin", "extralight", "light", "regular", "medium", "semibold", "bold", "extrabold", "black"
    ]
    | int
)
"""Typst font weight keyword or numeric font weight."""

T = t.TypeVar("T")


@dataclass(slots=True)
class Sides(t.Generic[T]):
    """Describe per-side values for Typst cell properties.

    Use this helper for properties that can vary by side, such as `inset` and
    `stroke`. Only fields with non-`None` values are emitted to Typst.
    """

    rest: T | None = None
    """Fallback value for sides without a more specific value."""
    x: T | None = None
    """Horizontal value applied to the left and right sides."""
    y: T | None = None
    """Vertical value applied to the top and bottom sides."""
    top: T | None = None
    """Top-side value."""
    right: T | None = None
    """Right-side value."""
    left: T | None = None
    """Left-side value."""
    bottom: T | None = None
    """Bottom-side value."""

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

    def __or__(self, value: object) -> t.Self:
        """Merge two text styles, preferring values from `value` when set.

        Args:
            value: Another `Sides` instance.

        Returns:
            A merged `Sides` instance.
        """
        klass = type(self)
        if value is None:
            return self

        if not isinstance(value, klass):  # pragma: no cover
            return NotImplemented

        current = {k: v for k, v in asdict(self).items() if v is not None}
        new = {k: v for k, v in asdict(value).items() if v is not None}

        return klass(**(current | new))

    def __ror__(self, value: object) -> t.Self:
        """Merge two text styles, preferring values from `value` when set.

        Args:
            value: Another `Sides` instance.

        Returns:
            A merged `Sides` instance.
        """
        return self.__or__(value)


Inset = Relative | Sides[Relative] | dict[str, str]
"""Cell inset value.

Use a [`Relative`][typ_tables.ttypes.Relative] value for uniform inset,
[`Sides`][typ_tables.style.Sides] for per-side inset, or a dictionary accepted
by `Sides`.
"""
FullStroke = Stroke | Sides[Stroke] | dict[str, str]
"""Stroke value accepted by style fields.

Use a [`Stroke`][typ_tables.style.Stroke] value for a uniform stroke,
[`Sides`][typ_tables.style.Sides] for per-side stroke, or a dictionary accepted
by `Sides`.
"""


def _coerce_sides(attr: t.Any) -> t.Any:
    if isinstance(attr, dict):
        return Sides(**attr)
    if isinstance(attr, list):
        return [Sides(**i) if isinstance(i, dict) else i for i in attr]
    return attr


CELL_PROPERTY_INDENT = " " * 2


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
    fill: Fill | None = None
    stroke: Stroke | Sides[Stroke] | None = None
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
            if isinstance(new, Sides):
                new_text_style[name] = current | new
            else:
                new_text_style[name] = new if new is not None else current

        return type(self)(**new_text_style)


class _DataclassInstance(t.Protocol):
    __dataclass_fields__: t.ClassVar[dict[str, t.Any]]


def _resolve_style_to_list_of_styles(
    instance: _DataclassInstance, data: Data[IntoDataFrame]
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
    """Text-level style properties for selected table cells.

    These fields map to Typst `text(...)` arguments. Values are written as Typst
    strings, except for `fractions`, which is rendered as a boolean. Scalar
    values apply the same style everywhere the locator selects. Lists and
    Narwhals expressions resolve one value per data row for row-based locators.
    """

    font: str | list[str] | nw.Expr | None = None
    """Font family name."""
    style: FontStyle | list[FontStyle] | nw.Expr | None = None
    """Font [`FontStyle`][typ_tables.style.FontStyle]."""
    weight: FontWeight | list[FontWeight] | nw.Expr | None = None
    """Font [`FontWeight`][typ_tables.style.FontWeight]."""
    stretch: str | list[str] | nw.Expr | None = None
    """Font stretch value."""
    size: Length | list[Length] | nw.Expr | None = None
    """Text size as a [`Length`][typ_tables.style.Length] value."""
    fill: Fill | list[Fill] | nw.Expr | None = None
    """Text [`Fill`][typ_tables.style.Fill] color or paint."""
    stroke: FullStroke | list[FullStroke] | nw.Expr | None = None
    """Text [`FullStroke`][typ_tables.style.FullStroke]."""
    tracking: Length | list[Length] | nw.Expr | None = None
    """Additional spacing between glyphs as a [`Length`][typ_tables.style.Length] value."""
    spacing: Relative | list[Relative] | nw.Expr | None = None
    """Additional spacing between words as a [`Relative`][typ_tables.ttypes.Relative] value."""
    fractions: bool | list[bool] | nw.Expr | None = None
    """Whether Typst should render numeric fractions specially."""

    def __post_init__(self) -> None:
        """Coerces types."""
        self.stroke = _coerce_sides(self.stroke)

    def resolve(self, data: Data[IntoDataFrame]) -> list[TextStyleForCell]:
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

    inset: Relative | Sides[Relative] | None = None
    align: Auto | Alignment | None = None
    fill: Fill | None = None
    stroke: Stroke | Sides[Stroke] | None = None

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
            if isinstance(new, Sides):
                new_cell_style[name] = current | new
            else:
                new_cell_style[name] = new if new is not None else current

        return type(self)(**new_cell_style)


@dataclass
class CellStyle:
    """Cell-level style properties for selected table cells.

    These fields map to Typst `table.cell(...)` arguments. Scalar values apply
    the same style everywhere the locator selects. Lists and Narwhals
    expressions resolve one value per data row for row-based locators.
    """

    inset: Inset | list[Inset] | nw.Expr | None = None
    """Cell padding/inset as an [`Inset`][typ_tables.style.Inset] value."""
    align: Auto | Alignment | list[Auto | Alignment] | nw.Expr | None = None
    """Cell content [`Alignment`][typ_tables.ttypes.Alignment] or
    [`Auto`][typ_tables.ttypes.Auto].
    """
    fill: Fill | list[Fill] | nw.Expr | None = None
    """Cell background [`Fill`][typ_tables.style.Fill] color or paint."""
    stroke: FullStroke | list[FullStroke] | nw.Expr | None = None
    """Cell border [`FullStroke`][typ_tables.style.FullStroke]."""

    def __post_init__(self) -> None:
        """Coerces types."""
        self.inset = _coerce_sides(self.inset)
        self.stroke = _coerce_sides(self.stroke)

    def resolve(self, data: Data[IntoDataFrame]) -> list[CellStyleForCell]:
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
        if value is None:
            return self
        if not isinstance(value, StyleHolder):  # pragma: no cover
            return NotImplemented

        match (self.text, value.text):
            case (None, TextStyleForCell()):
                new_text = value.text
            case (TextStyleForCell(), None):
                new_text = self.text
            case (TextStyleForCell(), TextStyleForCell()):
                new_text = self.text | value.text
            case _:
                new_text = None

        match (self.cell, value.cell):
            case (None, CellStyleForCell()):
                new_cell = value.cell
            case (CellStyleForCell(), None):
                new_cell = self.cell
            case (CellStyleForCell(), CellStyleForCell()):
                new_cell = self.cell | value.cell
            case _:
                new_cell = None

        return type(self)(text=new_text, cell=new_cell)

    def __ror__(self, value: object) -> t.Self:  # pragma: no cover
        """Merge two style holders, preferring values from `value` when set.

        Args:
            value: Another `StyleHolder` instance.

        Returns:
            A merged `StyleHolder` instance.
        """
        return self.__or__(value)

    def clear(self) -> None:
        """Clears all the styles from the holder."""
        self.text = None
        self.cell = None


@dataclass
class DefaultStyles:
    """Container for all default styles."""

    header: StyleHolder = field(
        default_factory=lambda: StyleHolder(
            cell=CellStyleForCell(align="center", stroke=Sides(top="1.2pt", bottom="1.2pt"))
        )
    )
    header_cells: StyleHolder = field(
        default_factory=lambda: StyleHolder(cell=CellStyleForCell(stroke=Sides(bottom="1.2pt")))
    )
    spanner_cells: StyleHolder = field(
        default_factory=lambda: StyleHolder(cell=CellStyleForCell(align="center", stroke="1.2pt"))
    )
    stub_header_cell: StyleHolder = field(
        default_factory=lambda: StyleHolder(cell=CellStyleForCell(stroke=Sides(bottom="1.2pt")))
    )
    stub_cell: StyleHolder = field(
        default_factory=lambda: StyleHolder(
            cell=CellStyleForCell(stroke=Sides(bottom="0.6pt", right="1pt"))
        )
    )
    body_cell: StyleHolder = field(
        default_factory=lambda: StyleHolder(cell=CellStyleForCell(stroke=Sides(bottom="0.6pt")))
    )
    row_group: StyleHolder = field(
        default_factory=lambda: StyleHolder(cell=CellStyleForCell(stroke=Sides(bottom="1pt")))
    )

    def clear(self) -> None:
        """Sets text and cell styles to None for all style holders."""
        self.header.clear()
        self.header_cells.clear()
        self.spanner_cells.clear()
        self.stub_header_cell.clear()
        self.stub_cell.clear()
        self.body_cell.clear()
        self.row_group.clear()
