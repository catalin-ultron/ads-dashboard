"""Situație workflow: drafted by the contractor, certified by the site supervisor (diriginte)."""

from __future__ import annotations

from datetime import date

from nsa.billing.models import Situatie
from nsa.contracts.models import Contract
from nsa.platform.workflow.engine import Transition, Workflow, register


def _has_certified_value(doc: Situatie) -> str | None:
    return None if doc.certified and doc.certified > 0 else "no certified value"


def _all_lines_resolved(doc: Situatie) -> str | None:
    open_issues = [ln for ln in doc.lines if not ln.certified]
    return f"{len(open_issues)} line(s) with unresolved issues" if open_issues else None


def _stamp_certification(session, doc: Situatie, user_id: int) -> None:
    doc.certified_on = date.today()


SITUATIE = register(Workflow(
    doc_type="situatie",
    states=("draft", "submitted", "certified", "invoiced", "paid", "rejected"),
    initial="draft",
    locked_states=frozenset({"submitted", "certified", "invoiced", "paid"}),
    company_of=lambda s, d: s.get(Contract, d.contract_id).company_id,
    contract_of=lambda s, d: d.contract_id,
    transitions=(
        Transition("submit", "draft", "submitted", "situatie:submit",
                   conditions=(_has_certified_value, _all_lines_resolved)),
        Transition("certify", "submitted", "certified", "situatie:certify",
                   not_by_actor_of=("submit",), effects=(_stamp_certification,)),
        Transition("reject", "submitted", "rejected", "situatie:certify", not_by_actor_of=("submit",)),
        Transition("rework", "rejected", "draft", "situatie:submit"),
        Transition("invoice", "certified", "invoiced", "situatie:invoice"),
        Transition("mark_paid", "invoiced", "paid", "situatie:invoice"),
    ),
))
