"""Addendum workflow: approval is blocked when the modification exceeds the legal limits (D40.05)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select

from nsa.contracts.modification import ContractFrame, Modification, SubstantialityTests, assess, basis_for
from nsa.contracts.models import Addendum, Contract
from nsa.platform.workflow.engine import Transition, Workflow, register


def frame_of(contract: Contract) -> ContractFrame:
    return ContractFrame(
        initial_value=contract.initial_price_excl_vat or contract.price_excl_vat,
        works=contract.works,
        funding_source=contract.funding_source,
        direct_award=contract.procedure_type == "direct",
        simplified_procedure=contract.procedure_type == "simplified",
    )


def assess_addendum(session, doc: Addendum, on: date | None = None):
    contract = session.get(Contract, doc.contract_id)
    signed = session.scalars(select(Addendum).where(Addendum.contract_id == doc.contract_id,
                                                    Addendum.status == "signed", Addendum.id != doc.id))
    history = [Modification(basis_for(a.kind, contract.funding_source), a.value_delta) for a in signed]
    tests = SubstantialityTests(**doc.substantiality) if doc.substantiality is not None else None
    return assess(frame_of(contract), history,
                  Modification(basis_for(doc.kind, contract.funding_source), doc.value_delta),
                  on or doc.signed_on or date.today(), tests)


def _within_limits(session, doc: Addendum) -> str | None:
    result = assess_addendum(session, doc)
    return None if result.admissible else "; ".join(result.reasons)


def _apply_to_contract(session, doc: Addendum, user_id: int) -> None:
    contract = session.get(Contract, doc.contract_id)
    if contract.initial_price_excl_vat is None:
        contract.initial_price_excl_vat = contract.price_excl_vat
    contract.price_excl_vat += doc.value_delta
    if doc.signed_on is None:
        doc.signed_on = date.today()


ADDENDUM = register(Workflow(
    doc_type="addendum",
    states=("draft", "approved", "signed", "cancelled"),
    initial="draft",
    locked_states=frozenset({"approved", "signed", "cancelled"}),
    company_of=lambda s, d: s.get(Contract, d.contract_id).company_id,
    contract_of=lambda s, d: d.contract_id,
    transitions=(
        Transition("approve", "draft", "approved", "addendum:approve", conditions=(_within_limits,)),
        Transition("sign", "approved", "signed", "addendum:sign", conditions=(_within_limits,),
                   effects=(_apply_to_contract,)),
        Transition("cancel", "draft", "cancelled", "addendum:approve"),
        Transition("withdraw", "approved", "draft", "addendum:approve"),
    ),
))
