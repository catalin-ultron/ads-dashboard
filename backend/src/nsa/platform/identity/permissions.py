"""Permission evaluation (D02).

A role carries permission patterns "<resource>:<action>" with "*" wildcards. A membership grants a
role to a user in one company, either company-wide or narrowed to one contract. Rights are the
union of all matching memberships; there are no deny rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase

from sqlalchemy import Select, false, or_, select
from sqlalchemy.orm import Session

from nsa.platform.models import Membership, Role, User


class AccessDenied(PermissionError):
    pass


def matches(pattern: str, permission: str) -> bool:
    if pattern == "*":
        return True
    p_res, _, p_act = pattern.partition(":")
    res, _, act = permission.partition(":")
    return fnmatchcase(res, p_res or "*") and fnmatchcase(act, p_act or "*")


@dataclass
class Grants:
    user_id: int
    # (company_id, contract_id or None) -> patterns
    scopes: dict[tuple[int, int | None], set[str]] = field(default_factory=dict)

    def allows(self, permission: str, company_id: int, contract_id: int | None = None) -> bool:
        for (company, contract), patterns in self.scopes.items():
            if company != company_id:
                continue
            if contract is not None and contract != contract_id:
                continue
            if any(matches(p, permission) for p in patterns):
                return True
        return False

    def companies(self, permission: str) -> set[int]:
        """Companies where the permission holds company-wide."""
        return {company for (company, contract), patterns in self.scopes.items()
                if contract is None and any(matches(p, permission) for p in patterns)}

    def contracts(self, permission: str) -> set[int]:
        """Contracts where the permission holds through a contract-scoped membership."""
        return {contract for (_, contract), patterns in self.scopes.items()
                if contract is not None and any(matches(p, permission) for p in patterns)}


def load_grants(session: Session, user_id: int) -> Grants:
    user = session.get(User, user_id)
    grants = Grants(user_id)
    if user is None or user.status != "active" or user.deleted_at is not None:
        return grants
    rows = session.execute(
        select(Membership.company_id, Membership.contract_id, Role.permissions)
        .join(Role, Role.id == Membership.role_id)
        .where(Membership.user_id == user_id, Membership.deleted_at.is_(None), Role.deleted_at.is_(None))
    ).all()
    for company_id, contract_id, perms in rows:
        grants.scopes.setdefault((company_id, contract_id), set()).update(perms or [])
    return grants


def require(grants: Grants, permission: str, company_id: int, contract_id: int | None = None) -> None:
    if not grants.allows(permission, company_id, contract_id):
        raise AccessDenied(f"User {grants.user_id} lacks {permission} in company {company_id}"
                           + (f", contract {contract_id}" if contract_id else ""))


def scope_query(stmt: Select, grants: Grants, permission: str, *, company_col, contract_col=None) -> Select:
    """Restrict a query to rows the user may see: company-wide grants, or contract-scoped grants."""
    conditions = []
    companies = grants.companies(permission)
    if companies:
        conditions.append(company_col.in_(companies))
    contracts = grants.contracts(permission)
    if contracts and contract_col is not None:
        conditions.append(contract_col.in_(contracts))
    return stmt.where(or_(*conditions) if conditions else false())
