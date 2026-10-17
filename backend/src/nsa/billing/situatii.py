"""Monthly situație de lucrări and centralizator (D39.04, D39.05).

line value          = quantity this period × unit price
cumulative quantity ≤ contract quantity + approved NCS quantity
lines on hidden works need their PV (D43.03) before certification
payable             = certified − advance recovery − retention − penalties + price adjustment
JV split            = payable × member share
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from nsa.platform.core.money import D, round_money


@dataclass(frozen=True)
class BoqItem:
    code: str
    unit: str
    unit_price: Decimal
    contract_quantity: Decimal
    approved_extra_quantity: Decimal = Decimal("0")  # from NCS / addenda (D40.06)
    hidden_works: bool = False

    @property
    def quantity_limit(self) -> Decimal:
        return D(self.contract_quantity) + D(self.approved_extra_quantity)


@dataclass(frozen=True)
class MeasuredLine:
    item_code: str
    quantity: Decimal
    pv_reference: str | None = None  # PV de lucrări ascunse / fază determinantă


@dataclass(frozen=True)
class LineResult:
    item_code: str
    quantity: Decimal
    cumulative_quantity: Decimal
    value: Decimal
    certified: bool
    issue: str | None = None


@dataclass(frozen=True)
class Deductions:
    advance_recovery: Decimal = Decimal("0")
    retention: Decimal = Decimal("0")
    penalties: Decimal = Decimal("0")
    price_adjustment: Decimal = Decimal("0")


@dataclass
class SituatieResult:
    lines: list[LineResult]
    gross: Decimal
    certified: Decimal
    deductions: Deductions
    payable: Decimal
    member_split: dict[str, Decimal] = field(default_factory=dict)

    @property
    def rejected(self) -> list[LineResult]:
        return [line for line in self.lines if not line.certified]


class SituatieError(ValueError):
    pass


def measure(boq: dict[str, BoqItem], previous_cumulative: dict[str, Decimal],
            lines: list[MeasuredLine]) -> list[LineResult]:
    results = []
    seen = set()
    for line in lines:
        item = boq.get(line.item_code)
        if item is None:
            raise SituatieError(f"Measured line references unknown BoQ item {line.item_code}")
        if line.item_code in seen:
            raise SituatieError(f"BoQ item {line.item_code} measured twice in one period")
        seen.add(line.item_code)
        qty = D(line.quantity)
        cumulative = D(previous_cumulative.get(line.item_code, Decimal("0"))) + qty
        value = round_money(qty * D(item.unit_price))
        issue = None
        if cumulative > item.quantity_limit:
            issue = f"cumulative {cumulative} exceeds contract plus approved extra quantity {item.quantity_limit}"
        elif cumulative < 0:
            issue = "cumulative quantity below zero"
        elif item.hidden_works and qty > 0 and not line.pv_reference:
            issue = "hidden works without PV"
        results.append(LineResult(line.item_code, qty, cumulative, value, issue is None, issue))
    return results


def centralize(lines: list[LineResult], deductions: Deductions,
               member_shares: dict[str, Decimal] | None = None) -> SituatieResult:
    gross = sum((line.value for line in lines), Decimal("0"))
    certified = sum((line.value for line in lines if line.certified), Decimal("0"))
    payable = round_money(certified - D(deductions.advance_recovery) - D(deductions.retention)
                          - D(deductions.penalties) + D(deductions.price_adjustment))
    split: dict[str, Decimal] = {}
    if member_shares:
        total_share = sum((D(s) for s in member_shares.values()), Decimal("0"))
        if total_share != 1:
            raise SituatieError("JV member shares must sum to 1")
        members = list(member_shares.items())
        allocated = Decimal("0")
        for name, share in members[:-1]:
            amount = round_money(payable * D(share))
            split[name] = amount
            allocated += amount
        split[members[-1][0]] = payable - allocated  # rounding remainder to the last member
    return SituatieResult(lines, gross, certified, deductions, payable, split)
