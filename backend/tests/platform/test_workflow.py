from datetime import date
from decimal import Decimal as D

import pytest

from nsa.billing import workflows  # noqa: F401  (registers the situație workflow)
from nsa.billing.models import Situatie, SituatieLine
from nsa.contracts.models import BoqItem, Contract
from nsa.masterdata.models import Partner, Unit
from nsa.platform.identity.permissions import load_grants
from nsa.platform.models import Company, Membership, Role, User
from nsa.platform.workflow.engine import (Transition, Workflow, WorkflowError, apply, assert_editable,
                                          available_actions)


@pytest.fixture
def setup(session):
    co = Company(code="AGW", name="AG", cui="901")
    auth = Partner(name="Primăria Săliște", kind="authority")
    session.add_all([co, auth, Unit(code="mc", name="m3")])
    session.flush()
    c = Contract(company_id=co.id, number="C-9", title="Drum", authority_id=auth.id, funding_source="local",
                 price_excl_vat=D("500000"))
    session.add(c)
    session.flush()
    item = BoqItem(contract_id=c.id, code="X1", description="d", unit="mc", unit_price=D("10"),
                   contract_quantity=D("100"))
    eng = Role(code="eng", name="Site engineer", permissions=["situatie:submit", "situatie:invoice"])
    sup = Role(code="sup", name="Supervisor", permissions=["situatie:certify"])
    both = Role(code="both", name="Both", permissions=["situatie:*"])
    u_eng, u_sup, u_both = User(email="e@x", full_name="E"), User(email="s@x", full_name="S"), User(
        email="b@x", full_name="B")
    session.add_all([item, eng, sup, both, u_eng, u_sup, u_both])
    session.flush()
    session.add_all([Membership(user_id=u_eng.id, company_id=co.id, role_id=eng.id),
                     Membership(user_id=u_sup.id, company_id=co.id, role_id=sup.id, contract_id=c.id),
                     Membership(user_id=u_both.id, company_id=co.id, role_id=both.id)])
    sit = Situatie(contract_id=c.id, number="SIT-1", period=date(2026, 9, 1),
                   status="draft", certified=D("1000"))
    sit.lines.append(SituatieLine(boq_item_id=item.id, quantity=D("100"), cumulative_quantity=D("100"),
                                  value=D("1000"), certified=True))
    session.add(sit)
    session.flush()
    g = {u.id: load_grants(session, u.id) for u in (u_eng, u_sup, u_both)}
    return dict(sit=sit, eng=u_eng.id, sup=u_sup.id, both=u_both.id, g=g)


def test_full_cycle_with_four_eyes(session, setup):
    sit, g = setup["sit"], setup["g"]
    apply(session, "situatie", sit, "submit", setup["both"], g[setup["both"]])
    assert sit.status == "submitted"
    with pytest.raises(WorkflowError):
        assert_editable("situatie", sit)
    acts = available_actions(session, "situatie", sit, setup["both"], g[setup["both"]])
    assert "same user" in acts["certify"]
    with pytest.raises(WorkflowError, match="missing permission"):
        apply(session, "situatie", sit, "certify", setup["eng"], g[setup["eng"]])
    apply(session, "situatie", sit, "certify", setup["sup"], g[setup["sup"]], comment="OK")
    assert sit.status == "certified" and sit.certified_on is not None
    apply(session, "situatie", sit, "invoice", setup["eng"], g[setup["eng"]])
    apply(session, "situatie", sit, "mark_paid", setup["eng"], g[setup["eng"]])
    assert sit.status == "paid"


def test_conditions_block_submit(session, setup):
    sit, g = setup["sit"], setup["g"]
    sit.lines[0].certified = False
    with pytest.raises(WorkflowError, match="unresolved"):
        apply(session, "situatie", sit, "submit", setup["eng"], g[setup["eng"]])


def test_reject_and_rework(session, setup):
    sit, g = setup["sit"], setup["g"]
    apply(session, "situatie", sit, "submit", setup["eng"], g[setup["eng"]])
    apply(session, "situatie", sit, "reject", setup["sup"], g[setup["sup"]], comment="cantități greșite")
    apply(session, "situatie", sit, "rework", setup["eng"], g[setup["eng"]])
    assert sit.status == "draft"
    with pytest.raises(WorkflowError, match="not available"):
        apply(session, "situatie", sit, "certify", setup["sup"], g[setup["sup"]])


def test_definition_validation():
    with pytest.raises(WorkflowError):
        Workflow("x", ("a",), "a", (Transition("go", "a", "b", "x:go"),))
    with pytest.raises(WorkflowError):
        Workflow("x", ("a", "b"), "c", ())
