"""Price adjustment for EU-funded works contracts under OUG 64/2022 art. 17(8) (D40.02).

Formula as recorded in construction-map/lead/02-coverage.md D40.02 (OUG 64/2022 as amended
by OUG 109/2022). Legal text must be re-checked against the consolidated act before use on a
live contract.

    Vapl = Vm × [(%av + %p) + (1 − %av − %p) × ICCmr / ICCmlr]
         + (Vpl − Vm)
         + (1 − %cpm) × {(Vpl − Vm) × [(%av + %p) + (1 − %av − %p) × ICCr / ICCplr] − (Vpl − Vm)}

    SR = Vapl − Vpl
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from nsa.platform.core.money import D, round_money

DEFAULT_PROFIT_SHARE = Decimal("0.03")
REFERENCE_MONTH_FLOOR = date(2021, 1, 1)


@dataclass(frozen=True)
class AdjustmentIndices:
    icc_materials_current: Decimal    # ICCmr
    icc_materials_reference: Decimal  # ICCmlr
    icc_current: Decimal              # ICCr
    icc_reference: Decimal            # ICCplr (forecast) or ICCRlr (realised, transport/water)


@dataclass(frozen=True)
class AdjustmentInput:
    payment_value: Decimal            # Vpl: value of the payment at offer prices
    materials_value: Decimal          # Vm: materials share of Vpl
    advance_share: Decimal            # %av: advance paid, as a fraction of contract price
    materials_weight: Decimal         # %cpm: statutory materials weight for the construction type
    indices: AdjustmentIndices
    profit_share: Decimal | None = None  # %p; None -> 3% default


@dataclass(frozen=True)
class AdjustmentResult:
    adjusted_value: Decimal  # Vapl
    adjustment: Decimal      # SR


class PriceAdjustmentError(ValueError):
    pass


def reference_month(bid_deadline: date | None, signature: date | None = None) -> date:
    """Month before the bid deadline (or 30 days before signature), floored at January 2021."""
    if bid_deadline is not None:
        base = date(bid_deadline.year - (bid_deadline.month == 1), (bid_deadline.month - 2) % 12 + 1, 1)
    elif signature is not None:
        from datetime import timedelta

        d = signature - timedelta(days=30)
        base = date(d.year, d.month, 1)
    else:
        raise PriceAdjustmentError("Reference month needs a bid deadline or a signature date")
    return max(base, REFERENCE_MONTH_FLOOR)


def adjust(inp: AdjustmentInput) -> AdjustmentResult:
    vpl = D(inp.payment_value)
    vm = D(inp.materials_value)
    av = D(inp.advance_share)
    p = DEFAULT_PROFIT_SHARE if inp.profit_share is None else D(inp.profit_share)
    cpm = D(inp.materials_weight)
    idx = inp.indices

    if vm < 0 or vm > vpl:
        raise PriceAdjustmentError("Materials value must be between 0 and the payment value")
    for name, value in (("advance", av), ("profit", p), ("materials weight", cpm)):
        if not Decimal(0) <= value <= Decimal(1):
            raise PriceAdjustmentError(f"{name} share must be a fraction between 0 and 1")
    if av + p > 1:
        raise PriceAdjustmentError("Advance and profit shares exceed 100%")
    if D(idx.icc_materials_reference) <= 0 or D(idx.icc_reference) <= 0:
        raise PriceAdjustmentError("Reference indices must be positive")

    fixed = av + p
    variable = 1 - fixed
    other = vpl - vm

    materials_part = vm * (fixed + variable * D(idx.icc_materials_current) / D(idx.icc_materials_reference))
    other_part = other * (fixed + variable * D(idx.icc_current) / D(idx.icc_reference))
    vapl = materials_part + other + (1 - cpm) * (other_part - other)

    vapl = round_money(vapl)
    return AdjustmentResult(adjusted_value=vapl, adjustment=vapl - round_money(vpl))
