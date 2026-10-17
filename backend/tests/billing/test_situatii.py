from decimal import Decimal as D

import pytest

from nsa.billing.situatii import BoqItem, Deductions, MeasuredLine, SituatieError, centralize, measure

BOQ = {
    "TS.01": BoqItem("TS.01", "m3", D("45.50"), D("1000")),
    "CB.02": BoqItem("CB.02", "m3", D("520.00"), D("200"), approved_extra_quantity=D("20"), hidden_works=True),
    "IZ.03": BoqItem("IZ.03", "m2", D("38.00"), D("500")),
}


def test_period_with_rejections_and_split():
    lines = measure(BOQ, {"CB.02": D("150"), "IZ.03": D("480")}, [
        MeasuredLine("TS.01", D("300")),
        MeasuredLine("CB.02", D("60"), pv_reference="PV-12"),  # 210 ≤ 220 with NCS
        MeasuredLine("IZ.03", D("40")),                          # 520 > 500
    ])
    assert [line.certified for line in lines] == [True, True, False]
    res = centralize(lines, Deductions(advance_recovery=D("4000"), retention=D("2000"),
                                       price_adjustment=D("1500.55")),
                     {"AG Construct": D("0.6"), "Pro Hart": D("0.4")})
    assert res.gross == D("13650.00") + D("31200.00") + D("1520.00")
    assert res.certified == D("44850.00")
    assert res.payable == D("40350.55")
    assert sum(res.member_split.values()) == res.payable
    assert res.member_split["AG Construct"] == D("24210.33")
    assert len(res.rejected) == 1


def test_hidden_works_need_pv():
    lines = measure(BOQ, {}, [MeasuredLine("CB.02", D("10"))])
    assert not lines[0].certified and "PV" in lines[0].issue


def test_negative_correction_allowed_within_cumulative():
    lines = measure(BOQ, {"TS.01": D("100")}, [MeasuredLine("TS.01", D("-20"))])
    assert lines[0].certified and lines[0].value == D("-910.00")


def test_errors():
    with pytest.raises(SituatieError):
        measure(BOQ, {}, [MeasuredLine("XX", D("1"))])
    with pytest.raises(SituatieError):
        measure(BOQ, {}, [MeasuredLine("TS.01", D("1")), MeasuredLine("TS.01", D("1"))])
    with pytest.raises(SituatieError):
        centralize([], Deductions(), {"A": D("0.5"), "B": D("0.4")})
