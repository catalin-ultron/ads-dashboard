from datetime import date
from decimal import Decimal as D

import pytest

from nsa.contracts.modification import (AdjustmentReserve, Basis, ContractFrame, Modification,
                                        SubstantialityTests, assess, basis_for)

ON = date(2026, 10, 1)
FRAME = ContractFrame(initial_value=D("10000000"), funding_source="eu")


def test_fifty_percent_is_cumulative_across_b_c_and_oug64():
    signed = [Modification(Basis.ADDITIONAL_WORKS, D("3000000")), Modification(Basis.ADJUSTMENT_OUG64, D("1500000"))]
    ok = assess(FRAME, signed, Modification(Basis.UNFORESEEABLE, D("500000")), ON)
    assert ok.admissible and ok.headroom_50pct == D("500000")
    assert any("Official Journal" in o for o in ok.obligations)
    over = assess(FRAME, signed, Modification(Basis.UNFORESEEABLE, D("500001")), ON)
    assert not over.admissible


def test_de_minimis_net_cumulative_and_both_caps():
    # 15% of 10M = 1.5M is below the 26.96M works threshold -> cap 1.5M
    signed = [Modification(Basis.DE_MINIMIS, D("1000000")), Modification(Basis.DE_MINIMIS, D("-200000"))]
    assert assess(FRAME, signed, Modification(Basis.DE_MINIMIS, D("699999")), ON).admissible
    assert not assess(FRAME, signed, Modification(Basis.DE_MINIMIS, D("700000")), ON).admissible
    big = ContractFrame(initial_value=D("400000000"))
    res = assess(big, [], Modification(Basis.DE_MINIMIS, D("26960556")), ON)
    assert not res.admissible and "26960556" in res.reasons[0]


def test_non_substantial_requires_assessment():
    assert not assess(FRAME, [], Modification(Basis.NON_SUBSTANTIAL, D("0")), ON).admissible
    assert assess(FRAME, [], Modification(Basis.NON_SUBSTANTIAL, D("0")), ON, SubstantialityTests()).admissible
    res = assess(FRAME, [], Modification(Basis.NON_SUBSTANTIAL, D("0")), ON,
                 SubstantialityTests(shifts_economic_balance=True))
    assert not res.admissible and "shifts_economic_balance" in res.reasons[0]


def test_review_clause_has_no_cap_and_oug47_no_fifty_percent():
    assert assess(FRAME, [], Modification(Basis.REVIEW_CLAUSE, D("9000000")), ON).admissible
    national = ContractFrame(initial_value=D("1000000"), funding_source="local")
    assert assess(national, [], Modification(Basis.ADJUSTMENT_OUG47, D("900000")), ON).admissible


def test_direct_award_ceiling():
    da = ContractFrame(initial_value=D("850000"), funding_source="eu", direct_award=True)
    assert assess(da, [], Modification(Basis.ADJUSTMENT_OUG64, D("50399")), ON).admissible
    assert not assess(da, [], Modification(Basis.ADJUSTMENT_OUG64, D("50400")), ON).admissible


def test_basis_mapping():
    assert basis_for("price_adjustment", "pnrr") == Basis.ADJUSTMENT_OUG64
    assert basis_for("price_adjustment", "local") == Basis.ADJUSTMENT_OUG47
    assert basis_for("extra_works", "eu") == Basis.ADDITIONAL_WORKS
    with pytest.raises(ValueError):
        basis_for("other", "eu")


def test_adjustment_reserve():
    r = AdjustmentReserve(remaining_value=D("1000000"))
    with pytest.raises(ValueError):
        r.constitute(D("230001"))
    r.constitute(D("200000"))
    r.pay(D("140000"))
    with pytest.raises(ValueError):
        r.top_up(D("50000"))  # only 70% paid
    r.pay(D("10000"))
    with pytest.raises(ValueError):
        r.top_up(D("100001"))
    r.top_up(D("100000"))
    assert r.reserve == D("300000")
    with pytest.raises(ValueError):
        r.pay(D("150001"))
