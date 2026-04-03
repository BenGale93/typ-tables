"""Module containing utility functions."""

from dataclasses import dataclass

from typ_tables.locators import CellPos
from typ_tables.style import StyleHolder


@dataclass
class StylePosition:
    """List of tables cells and the style to apply to them."""

    style: list[StyleHolder]
    positions: list[CellPos]


def find_styles(column: str, row: int, styles: list[StylePosition]) -> StyleHolder:
    """Find all styles applicable to the column and row."""
    current_pos = CellPos(column=column, row=row)
    final_style = StyleHolder()

    for style in styles:
        for pos in style.positions:
            if current_pos == pos:
                final_style = final_style | style.style[row]

    return final_style
