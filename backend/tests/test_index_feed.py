import json
from datetime import date
from decimal import Decimal as D
from pathlib import Path

import pytest

from nsa.billing.models import PriceAdjustmentRun, Situatie
from nsa.contracts.models import Contract
from nsa.masterdata import indices
from nsa.masterdata.models import Partner
from nsa.platform.models import Company

SAMPLES = Path(__file__).resolve().parents[2] / "construction-map/lead/research/ins-samples"


@pytest.fixture(scope="module")
def observations():
    return indices.parse_dataset(json.loads((SAMPLES / "CNS107D_dataset_2024-07_to_2026-07.json").read_text()))


def test_parse_sample(observations):
    by = {(o.series, o.period): o for o in observations}
    jul = by[("ICC_TOTAL", date(2026, 7, 1))]
    assert jul.value == D("166.7") and jul.status == "provisional"
    assert by[("ICC_MATERIALS", date(2026, 6, 1))].value == D("150.1")
    assert by[("ICC_MATERIALS", date(2026, 6, 1))].status == "revised"
    assert len({o.series for o in observations}) == 9
    assert min(o.period for o in observations) == date(2024, 7, 1)


def test_cells_and_months():
    assert indices.parse_cell("164,3") == (D("164.3"), "final")
    assert indices.parse_cell("<u>166,7</u>") == (D("166.7"), "provisional")
    assert indices.parse_month("Luna februarie 2025") == date(2025, 2, 1)
    with pytest.raises(indices.IndexFeedError):
        indices.parse_month("Trim. I 2025")


def test_current_index_month():
    assert indices.current_index_month(date(2026, 10, 1)) == date(2026, 9, 1)
    assert indices.current_index_month(date(2026, 3, 1)) == date(2026, 1, 1)


def test_dataset_request_from_metadata():
    meta = json.loads((SAMPLES / "CNS107D_matrix_metadata_truncated.json").read_text())
    body = indices.dataset_request(meta, ["ICC_TOTAL", "ICC_MATERIALS"], months=3)
    assert [o["nomItemId"] for o in body["arr"][0]] == [23295, 23303]
    assert body["arr"][1][-1]["label"] == "Luna iulie 2026" and len(body["arr"][1]) == 3


def test_upsert_lookup_and_recalculation(session, observations):
    first = indices.upsert(session, observations)
    assert len(first) == len(observations)
    assert indices.upsert(session, observations) == []

    co = Company(code="AGI", name="AG", cui="903")
    auth = Partner(name="Universitatea Lucian Blaga", kind="authority")
    session.add_all([co, auth])
    session.flush()
    c = Contract(company_id=co.id, number="CI", title="Cămin", authority_id=auth.id, funding_source="eu",
                 price_excl_vat=D("100"))
    session.add(c)
    session.flush()
    sit = Situatie(contract_id=c.id, number="S1", period=date(2026, 9, 1))
    session.add(sit)
    session.flush()

    idx, meta = indices.adjustment_indices(session, filing_month=date(2026, 10, 1), reference_month=date(2024, 8, 1))
    assert meta["current_period"] == date(2026, 9, 1) and not meta["indices_final"]
    assert idx.icc_current == D("166.7")  # September not published yet: falls back to July
    run = PriceAdjustmentRun(situatie_id=sit.id, method="oug64_2022", payment_value=D("1"), materials_value=D("0"),
                             advance_share=D("0"), profit_share=D("0.03"), materials_weight=D("0.4"),
                             icc_materials_current=idx.icc_materials_current,
                             icc_materials_reference=idx.icc_materials_reference, icc_current=idx.icc_current,
                             icc_reference=idx.icc_reference, adjusted_value=D("1"), adjustment=D("0"),
                             **{**meta, "current_period": date(2026, 7, 1)})
    session.add(run)
    session.flush()

    revised = [indices.Observation("ICC_TOTAL", date(2026, 7, 1), D("166.9"), "revised")]
    changes = indices.upsert(session, revised)
    assert changes[0].old_value == D("166.7")
    assert indices.runs_to_recalculate(session, changes) == [run]

    with pytest.raises(indices.IndexFeedError):
        indices.adjustment_indices(session, date(2026, 10, 1), reference_month=date(2020, 1, 1))
