"""Module dealing with localisation details."""

import typing as t
from csv import DictReader
from functools import cache
from pathlib import Path

DATA_MOD = Path(__file__).parent / "data"


def read_csv(filepath: Path) -> list[dict[str, t.Any]]:
    with filepath.open(encoding="utf8") as f:
        return list(DictReader(f))


class CurrenciesDataDict(t.TypedDict):
    curr_code: str
    curr_number: int
    exponent: int
    curr_name: str
    symbol: str


def _get_currencies_data() -> list[CurrenciesDataDict]:
    filepath = DATA_MOD / "x_currencies.csv"

    return t.cast("list[CurrenciesDataDict]", read_csv(filepath))


@cache
def get_currency_str(currency: str) -> str:
    data = _get_currencies_data()

    for d in data:
        if d["curr_code"] == currency:
            return d["symbol"]

    msg = f"'{currency}' is not a recognised currency code."
    raise ValueError(msg)
