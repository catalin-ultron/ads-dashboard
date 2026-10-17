"""Row journal with validity periods (D02 audit, D33 as-of reads).

Models opt in with `__journaled__ = True`. On every flush each inserted, updated or deleted row gets
a new journal version; the previous version's validity is closed at the same instant. The acting
user is read from `session.info["user_id"]`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Numeric, and_, event, inspect, insert, or_, select, update
from sqlalchemy.orm import Session

from nsa.platform.models import Journal

_installed = False


def _value(v):
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


def snapshot(obj) -> dict:
    data = {}
    for attr in inspect(obj).mapper.column_attrs:
        value = getattr(obj, attr.key)
        column_type = attr.columns[0].type
        if isinstance(value, Decimal) and isinstance(column_type, Numeric) and column_type.scale is not None:
            value = value.quantize(Decimal(1).scaleb(-column_type.scale))
        data[attr.key] = _value(value)
    return data


def _record(session: Session, flush_context, instances) -> None:
    changes = ([(o, "insert") for o in session.new] + [(o, "update") for o in session.dirty
                                                       if session.is_modified(o, include_collections=False)]
               + [(o, "delete") for o in session.deleted])
    rows = [(o, op) for o, op in changes if getattr(type(o), "__journaled__", False)]
    if not rows:
        return
    pending = session.info.setdefault("_journal_pending", [])
    for obj, op in rows:
        pending.append((obj, op, snapshot(obj) if op == "delete" else None))


def _write(session: Session, flush_context) -> None:
    pending = session.info.pop("_journal_pending", [])
    if not pending:
        return
    now = datetime.now(timezone.utc)
    user_id = session.info.get("user_id")
    conn = session.connection()
    for obj, op, deleted_data in pending:
        table = type(obj).__tablename__
        data = deleted_data if op == "delete" else snapshot(obj)
        data["_op"] = op
        last = conn.execute(select(Journal.version).where(Journal.table_name == table, Journal.row_id == obj.id)
                            .order_by(Journal.version.desc()).limit(1)).scalar()
        conn.execute(update(Journal).where(Journal.table_name == table, Journal.row_id == obj.id,
                                           Journal.valid_to.is_(None)).values(valid_to=now))
        conn.execute(insert(Journal).values(table_name=table, row_id=obj.id, version=(last or 0) + 1,
                                            valid_from=now, valid_to=now if op == "delete" else None,
                                            user_id=user_id, data=data))


def install() -> None:
    global _installed
    if _installed:
        return
    event.listen(Session, "before_flush", _record)
    event.listen(Session, "after_flush", _write)
    _installed = True


def as_of(session: Session, model, row_id: int, at: datetime) -> dict | None:
    """Row state valid at `at`, or None if the row did not exist then."""
    return session.execute(
        select(Journal.data).where(
            Journal.table_name == model.__tablename__, Journal.row_id == row_id,
            Journal.valid_from <= at, or_(Journal.valid_to.is_(None), Journal.valid_to > at),
            Journal.data["_op"].astext != "delete")
        .order_by(Journal.version.desc()).limit(1)
    ).scalar()


def history(session: Session, model, row_id: int) -> list[Journal]:
    return list(session.scalars(select(Journal).where(and_(Journal.table_name == model.__tablename__,
                                                           Journal.row_id == row_id))
                                .order_by(Journal.version)))
