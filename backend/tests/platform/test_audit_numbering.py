import time
from datetime import datetime, timezone
from decimal import Decimal as D

import pytest
from sqlalchemy import update
from sqlalchemy.orm.exc import StaleDataError

from nsa.contracts.models import Contract
from nsa.masterdata.models import Partner
from nsa.platform import audit
from nsa.platform.models import Company
from nsa.platform.numbering import NumberingError, next_number


@pytest.fixture(autouse=True)
def _journal():
    audit.install()


@pytest.fixture
def contract(session):
    co = Company(code="AGJ", name="AG", cui="900")
    auth = Partner(name="CJ Sibiu", kind="authority")
    session.add_all([co, auth])
    session.flush()
    c = Contract(company_id=co.id, number="C-77", title="Spital", authority_id=auth.id,
                 funding_source="eu", price_excl_vat=D("1000000"))
    session.add(c)
    session.flush()
    return c


def test_versions_and_as_of(session, contract):
    session.info["user_id"] = None
    t0 = datetime.now(timezone.utc)
    time.sleep(0.01)
    contract.price_excl_vat = D("1150000")
    session.flush()
    time.sleep(0.01)
    t1 = datetime.now(timezone.utc)
    contract.status = "signed"
    session.flush()

    hist = audit.history(session, Contract, contract.id)
    assert [h.version for h in hist] == [1, 2, 3]
    assert [h.data["_op"] for h in hist] == ["insert", "update", "update"]
    assert hist[0].valid_to == hist[1].valid_from and hist[2].valid_to is None
    assert audit.as_of(session, Contract, contract.id, t0)["price_excl_vat"] == "1000000.00"
    assert audit.as_of(session, Contract, contract.id, t1)["price_excl_vat"] == "1150000.00"
    assert audit.as_of(session, Contract, contract.id, t1)["status"] == "draft"


def test_delete_closes_history(session, contract):
    cid = contract.id
    session.delete(contract)
    session.flush()
    assert audit.history(session, Contract, cid)[-1].data["_op"] == "delete"
    assert audit.as_of(session, Contract, cid, datetime.now(timezone.utc)) is None


def test_stale_update_is_rejected(session, contract):
    assert contract.lock_version == 1
    session.execute(update(Contract).where(Contract.id == contract.id).values(lock_version=5)
                    .execution_options(synchronize_session=False))
    contract.title = "changed elsewhere meanwhile"
    with pytest.raises(StaleDataError):
        session.flush()


def test_numbering_per_scope(session):
    pat = "SIT-{contract}-{year}-{n:03d}"
    assert next_number(session, pat, contract="C14", year=2026) == "SIT-C14-2026-001"
    assert next_number(session, pat, contract="C14", year=2026) == "SIT-C14-2026-002"
    assert next_number(session, pat, contract="C15", year=2026) == "SIT-C15-2026-001"
    assert next_number(session, pat, contract="C14", year=2027) == "SIT-C14-2027-001"
    with pytest.raises(NumberingError):
        next_number(session, "SIT-{contract}", contract="C1")
    with pytest.raises(NumberingError):
        next_number(session, "SIT-{contract}-{n}")
