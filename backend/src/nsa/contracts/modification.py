"""Contract modification limits (D40.05).

Legea 98/2016 art. 221 (lettering as in the consolidated text):
  (1)(a) review clauses             no value cap
  (1)(b) additional works           ┐ cumulative (b)+(c) ≤ 50% of the initial value (221(4));
  (1)(c) unforeseeable circumstances┘ EU Official Journal notice (221(6))
  (1)(d) contractor replacement     no value test here
  (1)(e) non-substantial            must pass the 221(7) substantiality tests
  (1)(f) de minimis                 net cumulative increase < EU works threshold and < 15% works / 10% other
  (10)   initial value is the indexed price when an indexation clause exists
OUG 64/2022 (EU-funded): art. 8 adjustment shares the 50% cap with (b)+(c); art. 9 reserve ≤ 23% of the
remaining value, top-ups ≤ 10% of it once ≥ 75% of the reserve is paid; art. 18 direct-award ceiling.
OUG 47/2022 (national budget): adjustment is a non-substantial modification, no 50% cap.
Every modification is published in SEAP (art. 222^1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

from nsa.contracts.thresholds import thresholds_on
from nsa.platform.core.money import D

HALF = Decimal("0.50")
DE_MINIMIS_WORKS = Decimal("0.15")
DE_MINIMIS_OTHER = Decimal("0.10")
RESERVE_MAX = Decimal("0.23")
RESERVE_TOPUP_MAX = Decimal("0.10")
RESERVE_TOPUP_AFTER = Decimal("0.75")


class Basis(str, Enum):
    REVIEW_CLAUSE = "221_1_a"
    ADDITIONAL_WORKS = "221_1_b"
    UNFORESEEABLE = "221_1_c"
    CONTRACTOR_REPLACEMENT = "221_1_d"
    NON_SUBSTANTIAL = "221_1_e"
    DE_MINIMIS = "221_1_f"
    ADJUSTMENT_OUG64 = "oug64_art8"
    ADJUSTMENT_OUG47 = "oug47_art8"


KIND_TO_BASIS = {
    "extra_works": Basis.ADDITIONAL_WORKS,
    "unforeseen": Basis.UNFORESEEABLE,
    "de_minimis": Basis.DE_MINIMIS,
    "review_clause": Basis.REVIEW_CLAUSE,
    "contractor_replacement": Basis.CONTRACTOR_REPLACEMENT,
    "non_substantial": Basis.NON_SUBSTANTIAL,
    "subcontractor": Basis.NON_SUBSTANTIAL,
    "duration": Basis.NON_SUBSTANTIAL,
}


def basis_for(kind: str, funding_source: str) -> Basis:
    if kind == "price_adjustment":
        return Basis.ADJUSTMENT_OUG64 if funding_source in ("eu", "pnrr") else Basis.ADJUSTMENT_OUG47
    try:
        return KIND_TO_BASIS[kind]
    except KeyError:
        raise ValueError(f"Addendum kind {kind} has no legal basis mapping") from None


@dataclass(frozen=True)
class Modification:
    basis: Basis
    value_delta: Decimal


@dataclass(frozen=True)
class SubstantialityTests:
    """Art. 221(7): any True makes the change substantial (not admissible under (1)(e))."""
    changes_award_conditions: bool = False
    shifts_economic_balance: bool = False
    extends_scope_considerably: bool = False
    replaces_contractor_outside_d: bool = False

    def failed(self) -> list[str]:
        return [name for name, value in vars(self).items() if value]


@dataclass
class Assessment:
    admissible: bool
    reasons: list[str] = field(default_factory=list)
    obligations: list[str] = field(default_factory=list)
    headroom_50pct: Decimal = Decimal("0")
    headroom_de_minimis: Decimal = Decimal("0")


@dataclass(frozen=True)
class ContractFrame:
    initial_value: Decimal          # indexed value where an indexation clause exists (221(10))
    works: bool = True
    funding_source: str = "local"
    direct_award: bool = False
    simplified_procedure: bool = False


def assess(frame: ContractFrame, signed: list[Modification], proposed: Modification, on: date,
           substantiality: SubstantialityTests | None = None) -> Assessment:
    initial = D(frame.initial_value)
    if initial <= 0:
        raise ValueError("Initial contract value must be positive")
    limits = thresholds_on(on)

    capped = {Basis.ADDITIONAL_WORKS, Basis.UNFORESEEABLE, Basis.ADJUSTMENT_OUG64}
    used_50 = sum((D(m.value_delta) for m in signed if m.basis in capped and m.value_delta > 0), Decimal("0"))
    used_dm = sum((D(m.value_delta) for m in signed if m.basis == Basis.DE_MINIMIS), Decimal("0"))
    used_dm = max(used_dm, Decimal("0"))  # changes that lower the price do not count (221(9))
    dm_share = DE_MINIMIS_WORKS if frame.works else DE_MINIMIS_OTHER
    dm_value_cap = limits.eu_works if frame.works else limits.eu_supplies_local
    dm_cap = min(initial * dm_share, dm_value_cap)

    res = Assessment(admissible=True,
                     headroom_50pct=initial * HALF - used_50,
                     headroom_de_minimis=dm_cap - used_dm)
    delta = D(proposed.value_delta)
    b = proposed.basis

    if b in capped and delta > 0:
        if used_50 + delta > initial * HALF:
            res.admissible = False
            res.reasons.append(f"cumulative additional/unforeseeable/OUG 64 changes {used_50 + delta} exceed 50% "
                               f"of the initial value {initial * HALF}")
        if b in (Basis.ADDITIONAL_WORKS, Basis.UNFORESEEABLE):
            res.obligations.append("Publish a modification notice in the EU Official Journal (art. 221(6))")
    if b == Basis.DE_MINIMIS and delta > 0:
        if used_dm + delta >= dm_cap:
            res.admissible = False
            res.reasons.append(f"net de minimis increases {used_dm + delta} reach the cap {dm_cap} "
                               f"(min of {dm_share:.0%} of initial value and {dm_value_cap})")
    if b == Basis.NON_SUBSTANTIAL:
        failed = (substantiality or SubstantialityTests()).failed()
        if substantiality is None:
            res.admissible = False
            res.reasons.append("non-substantial basis requires the art. 221(7) assessment")
        elif failed:
            res.admissible = False
            res.reasons.append(f"substantial change: {', '.join(failed)}")
    if b in (Basis.ADJUSTMENT_OUG64, Basis.ADJUSTMENT_OUG47) and frame.direct_award:
        total = initial + sum((D(m.value_delta) for m in signed), Decimal("0")) + delta
        ceiling = limits.direct_award_works if frame.works else limits.direct_award_supplies
        if total >= ceiling:
            res.admissible = False
            res.reasons.append(f"adjusted value {total} not below the direct-award ceiling {ceiling} (OUG 64 art. 18)")
    if b == Basis.ADJUSTMENT_OUG64 and frame.simplified_procedure:
        total = initial + sum((D(m.value_delta) for m in signed), Decimal("0")) + delta
        if total >= limits.eu_works:
            res.admissible = False
            res.reasons.append(f"adjusted value {total} not below the simplified-procedure ceiling {limits.eu_works}")
    res.obligations.append("Publish the modification in SEAP (art. 222^1)")
    return res


@dataclass
class AdjustmentReserve:
    """OUG 64/2022 art. 9 reserve for price adjustment on the remaining value."""
    remaining_value: Decimal
    reserve: Decimal = Decimal("0")
    paid: Decimal = Decimal("0")

    def constitute(self, amount: Decimal) -> None:
        if self.reserve > 0:
            raise ValueError("Reserve already constituted; use top_up")
        if D(amount) > D(self.remaining_value) * RESERVE_MAX:
            raise ValueError(f"Reserve exceeds 23% of the remaining value ({D(self.remaining_value) * RESERVE_MAX})")
        self.reserve = D(amount)

    def top_up(self, amount: Decimal) -> None:
        if self.reserve <= 0 or self.paid < self.reserve * RESERVE_TOPUP_AFTER:
            raise ValueError("Top-up allowed only after at least 75% of the reserve is paid")
        if D(amount) > D(self.remaining_value) * RESERVE_TOPUP_MAX:
            raise ValueError(f"Top-up exceeds 10% of the remaining value ({D(self.remaining_value) * RESERVE_TOPUP_MAX})")
        self.reserve += D(amount)

    def pay(self, amount: Decimal) -> None:
        if self.paid + D(amount) > self.reserve:
            raise ValueError("Adjustment payment exceeds the reserve")
        self.paid += D(amount)
