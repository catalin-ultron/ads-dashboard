"""Run the CPM engine for a stored schedule and write dates and float back (D06)."""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from nsa.schedule.engine import mpxj_adapter
from nsa.schedule.model import types as t
from nsa.schedule.models import Activity, ActivityRelationship, Calendar, Schedule, ScheduleRun


def _calendar(row: Calendar) -> t.Calendar:
    week = {int(day): [t.WorkShift(time.fromisoformat(a), time.fromisoformat(b)) for a, b in shifts]
            for day, shifts in row.week.items()}
    return t.Calendar(row.code, week, {date.fromisoformat(d) for d in row.holidays}, row.hours_per_day)


def run_schedule(session: Session, schedule_id: int) -> ScheduleRun:
    sched = session.get(Schedule, schedule_id)
    if sched is None:
        raise mpxj_adapter.ScheduleError(f"Schedule {schedule_id} not found")
    calendars = {c.id: c for c in session.scalars(select(Calendar).where(Calendar.schedule_id == schedule_id))}
    activities = list(session.scalars(select(Activity).where(Activity.schedule_id == schedule_id)))
    by_id = {a.id: a for a in activities}
    rels = session.scalars(select(ActivityRelationship).where(
        ActivityRelationship.predecessor_id.in_(by_id), ActivityRelationship.successor_id.in_(by_id)))

    default = calendars.get(sched.default_calendar_id)
    if default is None:
        raise mpxj_adapter.ScheduleError("Schedule has no default calendar")

    inp = t.ScheduleInput(
        project_start=sched.project_start,
        data_date=sched.data_date,
        must_finish_by=sched.must_finish_by,
        calendars=[_calendar(c) for c in calendars.values()],
        default_calendar=default.code,
        activities=[t.Activity(
            code=a.code, name=a.name, duration_hours=a.duration_hours, remaining_hours=a.remaining_hours,
            activity_type=t.ActivityType(a.activity_type),
            calendar=calendars[a.calendar_id].code if a.calendar_id else None,
            actual_start=a.actual_start, actual_finish=a.actual_finish,
            constraint=t.ConstraintType(a.constraint_type) if a.constraint_type else None,
            constraint_date=a.constraint_date) for a in activities],
        relationships=[t.Relationship(by_id[r.predecessor_id].code, by_id[r.successor_id].code,
                                      t.LinkType(r.link), r.lag_hours) for r in rels],
    )

    run = ScheduleRun(schedule_id=schedule_id, run_at=datetime.now(timezone.utc))
    try:
        result = mpxj_adapter.schedule(inp)
    except mpxj_adapter.ScheduleError as exc:
        run.status, run.log = "failed", {"error": str(exc)}
        session.add(run)
        session.flush()
        raise

    for a in activities:
        r = result.activities[a.code]
        a.early_start, a.early_finish = r.early_start, r.early_finish
        a.late_start, a.late_finish = r.late_start, r.late_finish
        a.total_float_hours, a.free_float_hours, a.critical = r.total_float_hours, r.free_float_hours, r.critical
    run.status, run.project_finish = "ok", result.project_finish
    run.log = {"critical_path": result.critical_path, "activities": len(activities)}
    session.add(run)
    session.flush()
    return run
