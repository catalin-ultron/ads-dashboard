from decimal import Decimal as D

import pytest
from sqlalchemy import select

from nsa.contracts.models import Contract
from nsa.masterdata.models import Partner
from nsa.platform.identity.permissions import AccessDenied, load_grants, matches, require, scope_query
from nsa.platform.models import Company, Membership, Role, User


def test_pattern_matching():
    assert matches("*", "situatie:certify")
    assert matches("situatie:*", "situatie:certify")
    assert matches("*:read", "contract:read")
    assert not matches("situatie:read", "situatie:certify")
    assert not matches("contract:*", "situatie:read")


@pytest.fixture
def world(session):
    ag, ph = Company(code="AG", name="AG", cui="36594214"), Company(code="PH", name="PH", cui="22170774")
    auth = Partner(name="Municipiul Sibiu", kind="authority")
    session.add_all([ag, ph, auth])
    session.flush()
    c1 = Contract(company_id=ag.id, number="C1", title="t", authority_id=auth.id, funding_source="local",
                  price_excl_vat=D("1"))
    c2 = Contract(company_id=ag.id, number="C2", title="t", authority_id=auth.id, funding_source="local",
                  price_excl_vat=D("1"))
    c3 = Contract(company_id=ph.id, number="C3", title="t", authority_id=auth.id, funding_source="local",
                  price_excl_vat=D("1"))
    pm = Role(code="pm", name="Project manager", permissions=["contract:read", "situatie:*"])
    viewer = Role(code="viewer", name="Viewer", permissions=["*:read"])
    alice = User(email="a@x.ro", full_name="Alice")
    bob = User(email="b@x.ro", full_name="Bob", status="locked")
    session.add_all([c1, c2, c3, pm, viewer, alice, bob])
    session.flush()
    session.add_all([
        Membership(user_id=alice.id, company_id=ag.id, role_id=pm.id, contract_id=c1.id),
        Membership(user_id=alice.id, company_id=ph.id, role_id=viewer.id),
        Membership(user_id=bob.id, company_id=ag.id, role_id=viewer.id),
    ])
    session.flush()
    return dict(ag=ag, ph=ph, c1=c1, c2=c2, c3=c3, alice=alice, bob=bob)


def test_contract_scoped_and_company_wide(session, world):
    g = load_grants(session, world["alice"].id)
    assert g.allows("situatie:certify", world["ag"].id, world["c1"].id)
    assert not g.allows("situatie:certify", world["ag"].id, world["c2"].id)
    assert not g.allows("situatie:certify", world["ag"].id)
    assert g.allows("contract:read", world["ph"].id, world["c3"].id)
    assert not g.allows("contract:update", world["ph"].id)
    with pytest.raises(AccessDenied):
        require(g, "situatie:certify", world["ag"].id, world["c2"].id)


def test_scope_query_returns_visible_contracts_only(session, world):
    g = load_grants(session, world["alice"].id)
    stmt = scope_query(select(Contract.number), g, "contract:read",
                       company_col=Contract.company_id, contract_col=Contract.id)
    assert sorted(session.scalars(stmt)) == ["C1", "C3"]


def test_inactive_user_has_no_rights(session, world):
    g = load_grants(session, world["bob"].id)
    assert not g.scopes
    stmt = scope_query(select(Contract.number), g, "contract:read", company_col=Contract.company_id)
    assert list(session.scalars(stmt)) == []
