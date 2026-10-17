"""Procurement thresholds by validity period (Legea 98/2016 art. 7, ANAP notices).

Source: construction-map/lead/research/amendments-and-indices.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Thresholds:
    valid_from: date
    valid_to: date
    eu_works: Decimal
    eu_supplies_central: Decimal
    eu_supplies_local: Decimal
    direct_award_works: Decimal          # art. 7(5): strictly below
    direct_award_supplies: Decimal


PERIODS = (
    Thresholds(date(2024, 1, 1), date(2025, 12, 31), Decimal("27334460"), Decimal("0"), Decimal("0"),
               Decimal("900400"), Decimal("270120")),
    Thresholds(date(2026, 1, 1), date(2027, 12, 31), Decimal("26960556"), Decimal("698460"), Decimal("1077624"),
               Decimal("900400"), Decimal("270120")),
)


def thresholds_on(day: date) -> Thresholds:
    for t in PERIODS:
        if t.valid_from <= day <= t.valid_to:
            return t
    raise LookupError(f"No procurement thresholds recorded for {day}")
