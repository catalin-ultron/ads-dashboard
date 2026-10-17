from decimal import Decimal as D

import pytest

from nsa.contracts import workflows  # noqa: F401  (registers the addendum workflow)
from nsa.contracts.models import Addendum, Contract
from nsa.masterdata.models import Partner
from nsa.platform.identity.permissions import load_grants
from nsa.platform.models import Company, Membership, Role, User
from nsa.platform.workflow.engine import WorkflowError, apply


@pytest.fixture
def ctx(session):
    co = Company(code="AGA", name="AG", cui="902")
    auth = Partner(name="Apa Canal Sibiu", kind="authority")
    role = Role(code="cm", name="Contract manager", permissions=["addendum:*"])
    user = User(email="cm@x", full_name="CM")
    session.add_all([co, auth, role, user])
    session.flush()
    c = Contract(company_id=co.id, number="CL12", title="Rețele apă", authority_id=auth.id, funding_source="eu",
                 price_excl_vat=D("10000000"))
    session.add(c)
    session.add(Membership(user_id=user.id, company_id=co.id, role_id=role.id))
    session.flush()
    return dict(c=c, uid=user.id, g=load_grants(session, user.id))


def _add(session, c, number, kind, delta, **kw):
    a = Addendum(contract_id=c.id, number=number, kind=kind, value_delta=D(delta), **kw)
    session.add(a)
    session.flush()
    return a


def test_signing_updates_price_and_limits_block_excess(session, ctx):
    c, uid, g = ctx["c"], ctx["uid"], ctx["g"]
    a1 = _add(session, c, "AA1", "extra_works", "4000000")
    apply(session, "addendum", a1, "approve", uid, g)
    apply(session, "addendum", a1, "sign", uid, g)
    assert c.price_excl_vat == D("14000000") and c.initial_price_excl_vat == D("10000000")

    a2 = _add(session, c, "AA2", "price_adjustment", "1500000")  # EU-funded: shares the 50% cap
    with pytest.raises(WorkflowError, match="50%"):
        apply(session, "addendum", a2, "approve", uid, g)

    a3 = _add(session, c, "AA3", "price_adjustment", "1000000")
    apply(session, "addendum", a3, "approve", uid, g)
    assert a3.status == "approved"


def test_non_substantial_needs_assessment(session, ctx):
    c, uid, g = ctx["c"], ctx["uid"], ctx["g"]
    a = _add(session, c, "AA4", "duration", "0")
    with pytest.raises(WorkflowError, match="221"):
        apply(session, "addendum", a, "approve", uid, g)
    a.substantiality = {"shifts_economic_balance": False}
    apply(session, "addendum", a, "approve", uid, g)
    assert a.status == "approved"
