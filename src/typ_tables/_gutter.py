"""Module for handling the table gutters."""

from dataclasses import dataclass, field

from typ_tables import ttypes


@dataclass
class GutterContainer:
    """Class representing the table gutters."""

    value: ttypes.Gutter | None = None

    def __str__(self) -> str:
        """Typst string representation of the gutter."""
        if self.value is None:
            return "()"
        return self.value

    def __bool__(self) -> bool:
        return bool(self.value)


@dataclass
class Gutters:
    """Class managing all potential gutter parameters."""

    gutter: GutterContainer = field(default_factory=GutterContainer)
    row_gutter: GutterContainer = field(default_factory=GutterContainer)
    column_gutter: GutterContainer = field(default_factory=GutterContainer)

    @property
    def row(self) -> GutterContainer:
        if self.row_gutter:
            return self.row_gutter
        return self.gutter

    @property
    def column(self) -> GutterContainer:
        if self.column_gutter:
            return self.column_gutter
        return self.gutter
