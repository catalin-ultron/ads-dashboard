from datetime import date, datetime
from decimal import Decimal as D

import pytest

from nsa.billing.service import BillingError, MeasuredInput, build_situatie
from nsa.contracts.models import BoqItem, Contract, ContractParty, Guarantee
from nsa.contracts.priceadjust import AdjustmentIndices
from nsa.masterdata.models import Partner, Unit
from nsa.platform.models import Company
from nsa.schedule.models import Activity, ActivityRelationship, Calendar, Schedule
from nsa.schedule.service import run_schedule


@pytest.fixture
def contract(session):
    co = Company(code="AGC", name="TOTAL NSA AG CONSTRUCT SRL", cui="36594214")
    authority = Partner(name="Municipiul Sibiu", cui="4270740", kind="authority", public_authority=True)
    own = Partner(name="TOTAL NSA AG CONSTRUCT SRL", cui="36594214", kind="company")
    partner = Partner(name="PRO HART GROUP SRL", cui="22170774", kind="company")
    session.add_all([co, authority, own, partner, Unit(code="m3", name="cubic metre"), Unit(code="m2", name="square metre")])
    session.flush()
    c = Contract(company_id=co.id, number="C-2026-014", title="Reabilitare școală", authority_id=authority.id,
                 funding_source="pnrr", price_excl_vat=D("1000000"), advance_share=D("0.10"),
                 materials_weight=D("0.40"))
    session.add(c)
    session.flush()
    session.add_all([
        ContractParty(contract_id=c.id, partner_id=own.id, role="leader", share=D("0.6")),
        ContractParty(contract_id=c.id, partner_id=partner.id, role="member", share=D("0.4")),
        BoqItem(contract_id=c.id, code="TS.01", description="Săpătură", unit="m3", unit_price=D("45.50"),
                materials_unit_price=D("0"), contract_quantity=D("1000")),
        BoqItem(contract_id=c.id, code="CB.02", description="Beton C25/30", unit="m3", unit_price=D("520"),
                materials_unit_price=D("300"), contract_quantity=D("200"), hidden_works=True),
        Guarantee(contract_id=c.id, kind="good_execution", instrument="retention", target_share=D("0.05"),
                  planned_retention_share=D("0.05")),
    ])
    session.flush()
    session.refresh(c)
    return c


def test_two_month_billing_cycle(session, contract):
    s1 = build_situatie(session, contract.id, date(2026, 9, 1), "SIT-01", [
        MeasuredInput("TS.01", D("600")), MeasuredInput("CB.02", D("150"), "PV-01")])
    assert s1.certified == D("27300.00") + D("78000.00")
    assert s1.retention == D("5265.00")
    assert s1.payable == s1.certified - s1.retention

    s2 = build_situatie(session, contract.id, date(2026, 10, 15), "SIT-02", [
        MeasuredInput("TS.01", D("500")),               # cumulative 1100 > 1000 -> rejected
        MeasuredInput("CB.02", D("40"), "PV-02")],
        adjustment_indices=AdjustmentIndices(D("120"), D("100"), D("110"), D("100")))
    by_item = {ln.boq_item_id: ln for ln in s2.lines}
    assert sum(1 for ln in s2.lines if not ln.certified) == 1
    assert s2.certified == D("20800.00")
    assert s2.price_adjustment > 0
    assert len(by_item) == 2


def test_adjustment_requires_eu_funding(session, contract):
    contract.funding_source = "local"
    session.flush()
    with pytest.raises(BillingError):
        build_situatie(session, contract.id, date(2026, 9, 1), "SIT-01", [MeasuredInput("TS.01", D("10"))],
                       adjustment_indices=AdjustmentIndices(D("1"), D("1"), D("1"), D("1")))


def test_schedule_run_persists_dates(session):
    co = Company(code="AGC2", name="X", cui="1")
    session.add(co)
    session.flush()
    sched = Schedule(company_id=co.id, code="S1", name="Școala", project_start=datetime(2026, 11, 2, 8))
    session.add(sched)
    session.flush()
    cal = Calendar(schedule_id=sched.id, code="STD", week={str(d): [["08:00", "12:00"], ["13:00", "17:00"]]
                                                           for d in range(1, 6)}, holidays=["2026-11-30"])
    session.add(cal)
    session.flush()
    sched.default_calendar_id = cal.id
    a = Activity(schedule_id=sched.id, code="A", name="Demolare", duration_hours=16)
    b = Activity(schedule_id=sched.id, code="B", name="Fundații", duration_hours=24)
    c = Activity(schedule_id=sched.id, code="C", name="Comandă", duration_hours=8)
    session.add_all([a, b, c])
    session.flush()
    session.add_all([ActivityRelationship(predecessor_id=a.id, successor_id=b.id),
                     ActivityRelationship(predecessor_id=a.id, successor_id=c.id)])
    session.flush()
    run = run_schedule(session, sched.id)
    assert run.status == "ok"
    assert run.project_finish == datetime(2026, 11, 6, 17)
    assert b.critical and not c.critical
    assert c.total_float_hours == 16.0
