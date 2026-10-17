"""Decimal money helpers. Amounts are RON unless a currency is carried alongside."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def D(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(repr(value))
    return Decimal(value)


def round_money(value: Decimal) -> Decimal:
    return D(value).quantize(CENT, rounding=ROUND_HALF_UP)
