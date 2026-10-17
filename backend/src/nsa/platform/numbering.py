"""Document numbering: one atomic counter per resolved prefix (D24.06).

Pattern fields come from the caller, e.g. "SIT-{contract}-{year}-{n:03d}" with contract="C14",
year=2026 gives SIT-C14-2026-001, SIT-C14-2026-002, ... The counter scope is the pattern with every
field except {n} resolved, so each contract and year counts independently.
"""

from __future__ import annotations

import re

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from nsa.platform.models import Counter

_N_FIELD = re.compile(r"\{n(:[^}]*)?\}")


class NumberingError(ValueError):
    pass


def next_value(session: Session, scope: str) -> int:
    stmt = (insert(Counter).values(scope=scope, value=1)
            .on_conflict_do_update(index_elements=[Counter.scope], set_={"value": Counter.value + 1})
            .returning(Counter.value))
    return session.execute(stmt).scalar_one()


def next_number(session: Session, pattern: str, **fields) -> str:
    if len(_N_FIELD.findall(pattern)) != 1:
        raise NumberingError("Pattern must contain exactly one {n} field")
    try:
        scope = _N_FIELD.sub("#", pattern).format(**fields)
    except KeyError as exc:
        raise NumberingError(f"Missing numbering field {exc}") from exc
    n = next_value(session, scope)
    return pattern.format(n=n, **fields)
