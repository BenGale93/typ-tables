"""Module containing functionality related to the column spanners."""

import typing as t
from copy import deepcopy
from dataclasses import dataclass

from typ_tables._escape import Typst, escape_value
from typ_tables._style import CellStyleForCell, StyleHolder
from typ_tables._utils import OrderedSet


@dataclass
class Spanner:
    label: Typst | str
    spanning: list[str]
    id_: str

    @classmethod
    def from_data(
        cls,
        label: Typst | str,
        spanning: list[str],
        *,
        id_: str | None = None,
    ) -> t.Self:
        if id_ is None:
            id_ = str(label)

        return cls(label=label, spanning=spanning, id_=id_)

    def drop_spanning(self, cols: list[str]) -> None:
        self.spanning = [s for s in self.spanning if s not in cols]

    def overlap(self, other: t.Self) -> bool:
        return bool(set(self.spanning).intersection(set(other.spanning)))


@dataclass
class SpannerCell:
    label: Typst | str
    id_: str | None
    colspan: int

    def to_typst(self, styling: StyleHolder) -> str:
        styling_copy = deepcopy(styling)
        if styling_copy.cell is None:
            styling_copy.cell = CellStyleForCell()
        if not self.label:
            styling_copy.cell.stroke = None
            label = self.label
        else:
            label = _label_with_bottom_rule(
                self.label, _bottom_rule_stroke(styling_copy.cell.stroke)
            )
            styling_copy.cell.stroke = None

        return styling_copy.to_typst(label, colspan=self.colspan)


def _bottom_rule_stroke(stroke_style: object) -> str:
    if stroke_style is None:
        return "none"
    if isinstance(stroke_style, str):
        return stroke_style
    bottom_stroke = getattr(stroke_style, "bottom", None)
    return str(bottom_stroke) if bottom_stroke is not None else "none"


def _label_with_bottom_rule(label: Typst | str, stroke_text: str) -> Typst:
    return Typst(
        f"{escape_value(label)}\n#v(5pt)\n#place(bottom + center, "
        f"line(length: 100%, stroke: {stroke_text}))"
    )


class Spanners:
    def __init__(self) -> None:
        self._spanners: dict[int, list[Spanner]] = {}

    def add_spanner(self, spanner: Spanner, level: int | None = None) -> int:
        self._validate_new_spanner(spanner, level)
        if level is None:
            level = self._infer_level(spanner)
            self._spanners.setdefault(level, []).append(spanner)
            return level

        self._add_spanner_at_level(spanner, level)
        return level

    def _validate_new_spanner(self, spanner: Spanner, level: int | None) -> None:
        if level is not None and level < 0:
            msg = f"Level may not be negative. Got: '{level}'."
            raise ValueError(msg)

        current_ids = self.get_ids()
        if spanner.id_ in current_ids:
            msg = f"Spanner id '{spanner.id_}' already exists."
            raise ValueError(msg)

    def _infer_level(self, spanner: Spanner) -> int:
        level = 0
        for current_level, spanners in self._spanners.items():
            for existing_spanner in spanners:
                if existing_spanner.overlap(spanner) and current_level >= level:
                    level = current_level + 1
        return level

    def _add_spanner_at_level(self, spanner: Spanner, level: int) -> None:
        existing_spanners = self._spanners.setdefault(level, [])
        for existing_spanner in existing_spanners:
            existing_spanner.drop_spanning(spanner.spanning)
        existing_spanners.append(spanner)
        self.clear_blank_spanners()

    def get_spanner_by_id(self, id_: str) -> tuple[int, Spanner]:
        for level, spanners in self._spanners.items():
            for spanner in spanners:
                if id_ == spanner.id_:
                    return level, spanner

        msg = f"Spanner id: '{id_}' not found."
        raise ValueError(msg)

    def get_ids(self) -> set[str]:
        ids = set()
        for spanners in self._spanners.values():
            for spanner in spanners:
                ids.add(spanner.id_)
        return ids

    def clear_blank_spanners(self) -> None:
        for level, spanners in list(self._spanners.items()):
            remaining_spanners = [spanner for spanner in spanners if spanner.spanning]
            if remaining_spanners:
                self._spanners[level] = remaining_spanners
            else:
                del self._spanners[level]

    def get_columns(self, spanner_ids: list[str]) -> OrderedSet[str]:
        missing_spanner_ids = set(spanner_ids) - self.get_ids()
        if missing_spanner_ids:
            missing = sorted(missing_spanner_ids)
            msg = f"Spanner ids not found: {missing!r}."
            raise ValueError(msg)

        columns = []
        for spanners in self._spanners.values():
            for spanner in spanners:
                if spanner.id_ in spanner_ids:
                    columns.extend(spanner.spanning)

        return OrderedSet(columns)

    def build_spanners(self, columns: list[str]) -> list[list[SpannerCell]]:
        return [
            self._build_spanner_row(self._spanners[level], columns)
            for level in sorted(self._spanners)
        ]

    def _build_spanner_row(self, spanners: list[Spanner], columns: list[str]) -> list[SpannerCell]:
        cells: list[SpannerCell] = []
        last_spanner: Spanner | None = None

        for column in columns:
            spanner = self._spanner_for_column(spanners, column)
            if cells and spanner == last_spanner:
                cells[-1].colspan += 1
            else:
                cells.append(self._cell_for_spanner(spanner))
                last_spanner = spanner

        return cells

    def _spanner_for_column(self, spanners: list[Spanner], column: str) -> Spanner | None:
        for spanner in spanners:
            if column in spanner.spanning:
                return spanner
        return None

    def _cell_for_spanner(self, spanner: Spanner | None) -> SpannerCell:
        if spanner is None:
            return SpannerCell(label="", id_=None, colspan=1)
        return SpannerCell(label=spanner.label, id_=spanner.id_, colspan=1)
