"""Schedules, WBS, activities, relationships, calendars and CPM runs (D03-D06, D10)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (BigInteger, CheckConstraint, DateTime, Float, ForeignKey, String, UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from nsa.platform.core.db import Audited, Base, CompanyScoped, Keyed


class Schedule(Keyed, Audited, CompanyScoped, Base):
    __tablename__ = "schedule"

    contract_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("contract.id"), index=True)
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    project_start: Mapped[datetime] = mapped_column(DateTime)
    data_date: Mapped[datetime | None] = mapped_column(DateTime)
    must_finish_by: Mapped[datetime | None] = mapped_column(DateTime)
    default_calendar_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("calendar.id"))
    baseline_of_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("schedule.id"))
    source_format: Mapped[str | None] = mapped_column(String(16))  # xer, pmxml, mspdi, native

    __table_args__ = (UniqueConstraint("company_id", "code"),)


class Calendar(Keyed, Audited, Base):
    __tablename__ = "calendar"

    schedule_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("schedule.id", use_alter=True))
    code: Mapped[str] = mapped_column(String(64))
    hours_per_day: Mapped[float] = mapped_column(Float, default=8.0)
    week: Mapped[dict] = mapped_column(JSONB)       # {"1": [["08:00","12:00"],["13:00","17:00"]], ...}
    holidays: Mapped[list] = mapped_column(JSONB, default=list)

    __table_args__ = (UniqueConstraint("schedule_id", "code"),)


class WbsNode(Keyed, Audited, Base):
    __tablename__ = "wbs_node"

    schedule_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("schedule.id"), index=True)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("wbs_node.id"))
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    boq_object_code: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (UniqueConstraint("schedule_id", "code"),)


class Activity(Keyed, Audited, Base):
    __tablename__ = "activity"

    schedule_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("schedule.id"), index=True)
    wbs_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("wbs_node.id"))
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    activity_type: Mapped[str] = mapped_column(String(24), default="task_dependent")
    calendar_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("calendar.id"))
    duration_hours: Mapped[float] = mapped_column(Float)
    remaining_hours: Mapped[float | None] = mapped_column(Float)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime)
    actual_finish: Mapped[datetime | None] = mapped_column(DateTime)
    constraint_type: Mapped[str | None] = mapped_column(String(24))
    constraint_date: Mapped[datetime | None] = mapped_column(DateTime)
    early_start: Mapped[datetime | None] = mapped_column(DateTime)
    early_finish: Mapped[datetime | None] = mapped_column(DateTime)
    late_start: Mapped[datetime | None] = mapped_column(DateTime)
    late_finish: Mapped[datetime | None] = mapped_column(DateTime)
    total_float_hours: Mapped[float | None] = mapped_column(Float)
    free_float_hours: Mapped[float | None] = mapped_column(Float)
    critical: Mapped[bool | None]
    budget_cost: Mapped[Decimal | None]

    __table_args__ = (
        UniqueConstraint("schedule_id", "code"),
        CheckConstraint("activity_type in ('task_dependent','resource_dependent','level_of_effort',"
                        "'start_milestone','finish_milestone','wbs_summary')", name="activity_type"),
        CheckConstraint("duration_hours >= 0", name="duration"),
    )


class ActivityRelationship(Keyed, Base):
    __tablename__ = "activity_relationship"

    predecessor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("activity.id"), index=True)
    successor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("activity.id"), index=True)
    link: Mapped[str] = mapped_column(String(2), default="FS")
    lag_hours: Mapped[float] = mapped_column(Float, default=0.0)

    __table_args__ = (
        UniqueConstraint("predecessor_id", "successor_id"),
        CheckConstraint("link in ('FS','SS','FF','SF')", name="link"),
        CheckConstraint("predecessor_id <> successor_id", name="no_self_link"),
    )


class ScheduleRun(Keyed, Base):
    __tablename__ = "schedule_run"

    schedule_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("schedule.id"), index=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    engine: Mapped[str] = mapped_column(String(32), default="mpxj-primavera")
    project_finish: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(12))
    log: Mapped[dict] = mapped_column(JSONB, default=dict)
