"""Utility classes and functions."""

import typing as t
from collections.abc import Iterable, Iterator

T = t.TypeVar("T")


class OrderedSet(set[T]):
    def __init__(self, d: Iterable[T] = ()) -> None:
        self._d = self._create(d)

    def _create(self, d: Iterable[T]) -> dict[T, bool]:
        return dict.fromkeys(d, True)

    def as_set(self) -> set[T]:
        return set(self._d)

    def as_list(self) -> list[T]:
        return list(self._d)

    def as_dict(self) -> dict[T, bool]:
        return dict(self._d)

    def __contains__(self, k: object) -> bool:
        return k in self._d

    def __iter__(self) -> Iterator[T]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __repr__(self) -> str:
        cls_name = type(self).__name__
        lst = self.as_list()
        return f"{cls_name}({lst!r})"
