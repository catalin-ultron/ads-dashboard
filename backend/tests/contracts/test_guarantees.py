from decimal import Decimal as D

import pytest

from nsa.contracts.guarantees import GuaranteeError, RetentionAccount


def _acct():
    return RetentionAccount(contract_price=D("1000000"), target_share=D("0.05"),
                            planned_retention_share=D("0.05"))


def test_full_lifecycle():
    a = _acct()
    assert a.target == D("50000.00")
    a.deposit_initial(D("5000"))
    assert a.retain(D("200000"), "S1") == D("10000.00")
    assert a.retain(D("1000000"), "S2") == D("35000.00")  # capped at the remaining target
    assert a.retain(D("100000"), "S3") == 0
    assert a.balance == a.target
    assert a.release_on_completion(claims_pending=False) == D("35000.00")
    with pytest.raises(GuaranteeError):
        a.retain(D("1000"))
    assert a.release_final(claims_pending=False) == D("15000.00")
    assert a.balance == 0


def test_limits_and_guards():
    with pytest.raises(GuaranteeError):
        RetentionAccount(D("100"), D("0.11"), D("0.05"))
    a = _acct()
    with pytest.raises(GuaranteeError):
        a.deposit_initial(D("4999.99"))
    with pytest.raises(GuaranteeError):
        a.release_final(claims_pending=False)
    a.retain(D("200000"))
    with pytest.raises(GuaranteeError):
        a.release_on_completion(claims_pending=True)


def test_rebase_call_and_restore():
    a = _acct()
    a.retain(D("1000000"))
    a.rebase(D("1200000"))
    assert a.outstanding == D("10000.00")
    a.call(D("20000"), "penalty claim")
    assert a.outstanding == D("30000.00")
    a.restore(D("50000"))
    assert a.balance == a.target
    with pytest.raises(GuaranteeError):
        a.call(D("999999"))
