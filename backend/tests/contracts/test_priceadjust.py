from datetime import date
from decimal import Decimal as D

import pytest
from hypothesis import given, strategies as st

from nsa.contracts.priceadjust import (
    AdjustmentIndices,
    AdjustmentInput,
    PriceAdjustmentError,
    adjust,
    reference_month,
)


def _inp(icc_m=(D("120"), D("100")), icc=(D("110"), D("100")), **kw):
    base = dict(payment_value=D("1000"), materials_value=D("400"), advance_share=D("0.10"),
                materials_weight=D("0.40"),
                indices=AdjustmentIndices(icc_m[0], icc_m[1], icc[0], icc[1]))
    base.update(kw)
    return AdjustmentInput(**base)


def test_worked_example():
    # materials 400×(0.13+0.87×1.2)=469.60; other 600; (1−0.4)×(600×(0.13+0.87×1.1)−600)=31.32
    res = adjust(_inp())
    assert res.adjusted_value == D("1100.92")
    assert res.adjustment == D("100.92")


def test_explicit_profit_share_overrides_default():
    assert adjust(_inp(profit_share=D("0.05"))).adjusted_value < adjust(_inp()).adjusted_value


def test_falling_indices_reduce_payment():
    res = adjust(_inp(icc_m=(D("90"), D("100")), icc=(D("95"), D("100"))))
    assert res.adjustment < 0


@given(vpl=st.decimals(min_value=1, max_value=10**8, places=2),
       share=st.decimals(min_value=0, max_value=1, places=4))
def test_unchanged_indices_give_zero_adjustment(vpl, share):
    res = adjust(_inp(payment_value=vpl, materials_value=(vpl * share).quantize(D("0.01")),
                      icc_m=(D("100"), D("100")), icc=(D("100"), D("100"))))
    assert res.adjustment == 0


def test_invalid_inputs():
    with pytest.raises(PriceAdjustmentError):
        adjust(_inp(materials_value=D("1500")))
    with pytest.raises(PriceAdjustmentError):
        adjust(_inp(advance_share=D("0.99"), profit_share=D("0.05")))
    with pytest.raises(PriceAdjustmentError):
        adjust(_inp(icc=(D("110"), D("0"))))


def test_reference_month():
    assert reference_month(date(2025, 3, 15)) == date(2025, 2, 1)
    assert reference_month(date(2024, 1, 10)) == date(2023, 12, 1)
    assert reference_month(date(2020, 5, 4)) == date(2021, 1, 1)
    assert reference_month(None, signature=date(2025, 7, 15)) == date(2025, 6, 1)
    with pytest.raises(PriceAdjustmentError):
        reference_month(None)
