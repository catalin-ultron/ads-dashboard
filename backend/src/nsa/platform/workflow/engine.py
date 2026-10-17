"""Declarative document workflows (D24).

A workflow lists states and transitions. A transition needs a permission (checked in the
document's company and contract), may need a condition on the document, and may forbid the actor
who performed an earlier transition (four-eyes rule, e.g. submitter cannot certify). The current
state lives in the document's status column; every applied transition is logged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from nsa.platform.identity.permissions import Grants
from nsa.platform.workflow.models import WorkflowLog

Condition = Callable[[object], str | None]  # returns a reason when the transition is blocked
Effect = Callable[[Session, object, int], None]


class WorkflowError(Exception):
    pass


@dataclass(frozen=True)
class Transition:
    action: str
    source: str
    target: str
    permission: str
    conditions: tuple[Condition, ...] = ()
    not_by_actor_of: tuple[str, ...] = ()  # actions whose actor may not perform this one
    effects: tuple[Effect, ...] = ()


@dataclass
class Workflow:
    doc_type: str
    states: tuple[str, ...]
    initial: str
    transitions: tuple[Transition, ...]
    locked_states: frozenset[str] = field(default_factory=frozenset)  # no field edits allowed
    status_attr: str = "status"
    company_of: Callable[[Session, object], int] = lambda s, d: d.company_id
    contract_of: Callable[[Session, object], int | None] = lambda s, d: getattr(d, "contract_id", None)

    def __post_init__(self):
        if self.initial not in self.states:
            raise WorkflowError(f"{self.doc_type}: initial state {self.initial} is not a state")
        seen = set()
        for t in self.transitions:
            if t.source not in self.states or t.target not in self.states:
                raise WorkflowError(f"{self.doc_type}: transition {t.action} uses an unknown state")
            if (t.source, t.action) in seen:
                raise WorkflowError(f"{self.doc_type}: duplicate action {t.action} from {t.source}")
            seen.add((t.source, t.action))

    def state(self, doc) -> str:
        return getattr(doc, self.status_attr)


_REGISTRY: dict[str, Workflow] = {}


def register(workflow: Workflow) -> Workflow:
    _REGISTRY[workflow.doc_type] = workflow
    return workflow


def get(doc_type: str) -> Workflow:
    try:
        return _REGISTRY[doc_type]
    except KeyError:
        raise WorkflowError(f"No workflow registered for {doc_type}") from None


def _actors(session: Session, doc_type: str, doc_id: int, actions: tuple[str, ...]) -> set[int]:
    if not actions:
        return set()
    return set(session.scalars(select(WorkflowLog.user_id).where(
        WorkflowLog.doc_type == doc_type, WorkflowLog.doc_id == doc_id, WorkflowLog.action.in_(actions))))


def _blocked(session: Session, wf: Workflow, t: Transition, doc, user_id: int, grants: Grants) -> str | None:
    company = wf.company_of(session, doc)
    contract = wf.contract_of(session, doc)
    if not grants.allows(t.permission, company, contract):
        return f"missing permission {t.permission}"
    if user_id in _actors(session, wf.doc_type, doc.id, t.not_by_actor_of):
        return f"same user performed {', '.join(t.not_by_actor_of)}"
    for cond in t.conditions:
        reason = cond(doc)
        if reason:
            return reason
    return None


def available_actions(session: Session, doc_type: str, doc, user_id: int, grants: Grants) -> dict[str, str | None]:
    """Actions from the current state, mapped to None when allowed or to the blocking reason."""
    wf = get(doc_type)
    return {t.action: _blocked(session, wf, t, doc, user_id, grants)
            for t in wf.transitions if t.source == wf.state(doc)}


def apply(session: Session, doc_type: str, doc, action: str, user_id: int, grants: Grants,
          comment: str | None = None) -> WorkflowLog:
    wf = get(doc_type)
    current = wf.state(doc)
    t = next((t for t in wf.transitions if t.source == current and t.action == action), None)
    if t is None:
        raise WorkflowError(f"{doc_type} {doc.id}: action {action} not available in state {current}")
    reason = _blocked(session, wf, t, doc, user_id, grants)
    if reason:
        raise WorkflowError(f"{doc_type} {doc.id}: {action} blocked: {reason}")
    setattr(doc, wf.status_attr, t.target)
    log = WorkflowLog(doc_type=doc_type, doc_id=doc.id, action=action, from_state=current, to_state=t.target,
                      user_id=user_id, at=datetime.now(timezone.utc), comment=comment)
    session.add(log)
    for effect in t.effects:
        effect(session, doc, user_id)
    session.flush()
    return log


def assert_editable(doc_type: str, doc) -> None:
    wf = get(doc_type)
    if wf.state(doc) in wf.locked_states:
        raise WorkflowError(f"{doc_type} {doc.id} is {wf.state(doc)} and cannot be edited")
