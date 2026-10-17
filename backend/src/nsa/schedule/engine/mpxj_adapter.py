"""CPM engine adapter over MPXJ's P6-compatible scheduler (D06).

MPXJ (LGPL-2.1-or-later) is used unchanged as a library through JPype; no MPXJ
code is copied into this package.
"""

from __future__ import annotations

import threading
from datetime import datetime

from nsa.schedule.model.types import (
    ActivityResult,
    ActivityType,
    Calendar,
    ConstraintType,
    LinkType,
    ScheduleInput,
    ScheduleResult,
)

_jvm_lock = threading.Lock()
_J = None


def _java():
    """Start the JVM once and return a namespace of the Java classes used here."""
    global _J
    with _jvm_lock:
        if _J is None:
            import jpype
            import mpxj  # noqa: F401  (adds the bundled MPXJ jars to the class path)

            if not jpype.isJVMStarted():
                jpype.startJVM(convertStrings=True)
            from java.lang import Integer
            from java.time import DayOfWeek, LocalDate, LocalDateTime, LocalTime
            from org.mpxj import (
                ActivityType as JActivityType,
                ConstraintType as JConstraintType,
                Duration,
                LocalTimeRange,
                ProjectFile,
                Relation,
                RelationType,
                TimeUnit,
            )
            from org.mpxj.cpm import PrimaveraScheduler

            class NS:
                pass

            ns = NS()
            for name, val in dict(
                Integer=Integer, DayOfWeek=DayOfWeek, LocalDate=LocalDate, LocalDateTime=LocalDateTime,
                LocalTime=LocalTime, JActivityType=JActivityType, JConstraintType=JConstraintType,
                Duration=Duration, LocalTimeRange=LocalTimeRange, ProjectFile=ProjectFile,
                Relation=Relation, RelationType=RelationType, TimeUnit=TimeUnit,
                PrimaveraScheduler=PrimaveraScheduler,
            ).items():
                setattr(ns, name, val)
            _J = ns
    return _J


_LINK = {
    LinkType.FS: "FINISH_START",
    LinkType.SS: "START_START",
    LinkType.FF: "FINISH_FINISH",
    LinkType.SF: "START_FINISH",
}

_ACTIVITY = {
    ActivityType.TASK_DEPENDENT: "TASK_DEPENDENT",
    ActivityType.RESOURCE_DEPENDENT: "RESOURCE_DEPENDENT",
    ActivityType.LEVEL_OF_EFFORT: "LEVEL_OF_EFFORT",
    ActivityType.START_MILESTONE: "START_MILESTONE",
    ActivityType.FINISH_MILESTONE: "FINISH_MILESTONE",
    ActivityType.WBS_SUMMARY: "WBS_SUMMARY",
}

# P6 constraint semantics, mapped as in MPXJ's ConstraintTypeHelper (CS_* codes).
_CONSTRAINT = {
    ConstraintType.START_ON: "START_ON",
    ConstraintType.START_ON_OR_AFTER: "START_NO_EARLIER_THAN",
    ConstraintType.START_ON_OR_BEFORE: "START_NO_LATER_THAN",
    ConstraintType.FINISH_ON: "FINISH_ON",
    ConstraintType.FINISH_ON_OR_AFTER: "FINISH_NO_EARLIER_THAN",
    ConstraintType.FINISH_ON_OR_BEFORE: "FINISH_NO_LATER_THAN",
    ConstraintType.MANDATORY_START: "MUST_START_ON",
    ConstraintType.MANDATORY_FINISH: "MUST_FINISH_ON",
    ConstraintType.AS_LATE_AS_POSSIBLE: "AS_LATE_AS_POSSIBLE",
}


class ScheduleError(Exception):
    pass


def _ldt(j, value: datetime):
    return j.LocalDateTime.of(value.year, value.month, value.day, value.hour, value.minute, value.second)


def _py(value) -> datetime | None:
    if value is None:
        return None
    return datetime(value.getYear(), value.getMonthValue(), value.getDayOfMonth(),
                    value.getHour(), value.getMinute(), value.getSecond())


def _hours(j, duration) -> float:
    if duration is None:
        return 0.0
    if duration.getUnits() == j.TimeUnit.HOURS:
        return float(duration.getDuration())
    raise ScheduleError(f"Unexpected duration unit {duration.getUnits()}")


def _build_calendar(j, file, cal: Calendar):
    jc = file.addCalendar()
    jc.setName(cal.code)
    jc.setCalendarMinutesPerDay(j.Integer(int(cal.hours_per_day * 60)))
    for iso in range(1, 8):
        day = j.DayOfWeek.of(iso)
        shifts = cal.week.get(iso, [])
        jc.setWorkingDay(day, bool(shifts))
        hours = jc.addCalendarHours(day)
        for s in shifts:
            hours.add(j.LocalTimeRange(j.LocalTime.of(s.start.hour, s.start.minute),
                                       j.LocalTime.of(s.end.hour, s.end.minute)))
    for d in sorted(cal.holidays):
        jc.addCalendarException(j.LocalDate.of(d.year, d.month, d.day))
    return jc


def build_project_file(inp: ScheduleInput):
    """Translate a ScheduleInput into an MPXJ ProjectFile; returns (file, tasks by activity code)."""
    j = _java()
    file = j.ProjectFile()
    props = file.getProjectProperties()
    props.setStartDate(_ldt(j, inp.project_start))
    if inp.data_date:
        props.setStatusDate(_ldt(j, inp.data_date))
    if inp.must_finish_by:
        props.setMustFinishBy(_ldt(j, inp.must_finish_by))

    calendars = {c.code: _build_calendar(j, file, c) for c in inp.calendars}
    if inp.default_calendar not in calendars:
        raise ScheduleError(f"Unknown default calendar {inp.default_calendar}")
    file.setDefaultCalendar(calendars[inp.default_calendar])

    tasks = {}
    for a in inp.activities:
        if a.code in tasks:
            raise ScheduleError(f"Duplicate activity code {a.code}")
        t = file.addTask()
        t.setActivityID(a.code)
        t.setText(1, a.code)  # keeps the code in formats without an activity id (MSPDI)
        t.setName(a.name)
        t.setActivityType(getattr(j.JActivityType, _ACTIVITY[a.activity_type]))
        t.setDuration(j.Duration.getInstance(float(a.duration_hours), j.TimeUnit.HOURS))
        remaining = a.duration_hours if a.remaining_hours is None else a.remaining_hours
        t.setRemainingDuration(j.Duration.getInstance(float(remaining), j.TimeUnit.HOURS))
        if a.calendar:
            if a.calendar not in calendars:
                raise ScheduleError(f"Activity {a.code}: unknown calendar {a.calendar}")
            t.setCalendar(calendars[a.calendar])
        if a.actual_start:
            t.setActualStart(_ldt(j, a.actual_start))
        if a.actual_finish:
            t.setActualFinish(_ldt(j, a.actual_finish))
        if a.constraint:
            t.setConstraintType(getattr(j.JConstraintType, _CONSTRAINT[a.constraint]))
            if a.constraint_date:
                t.setConstraintDate(_ldt(j, a.constraint_date))
        tasks[a.code] = t

    for r in inp.relationships:
        for code in (r.predecessor, r.successor):
            if code not in tasks:
                raise ScheduleError(f"Relationship references unknown activity {code}")
        builder = (j.Relation.Builder()
                   .predecessorTask(tasks[r.predecessor])
                   .type(getattr(j.RelationType, _LINK[r.link]))
                   .lag(j.Duration.getInstance(float(r.lag_hours), j.TimeUnit.HOURS)))
        tasks[r.successor].addPredecessor(builder)
    return file, tasks


def schedule(inp: ScheduleInput) -> ScheduleResult:
    """Run a P6-style CPM pass and return early/late dates, float and criticality per activity."""
    j = _java()
    file, tasks = build_project_file(inp)
    props = file.getProjectProperties()
    try:
        j.PrimaveraScheduler().schedule(file, _ldt(j, inp.project_start))
    except Exception as exc:  # CpmException / CycleException surface as Java exceptions
        raise ScheduleError(str(exc)) from exc

    results = {}
    for code, t in tasks.items():
        total = _hours(j, t.getTotalSlack())
        results[code] = ActivityResult(
            code=code,
            early_start=_py(t.getEarlyStart()),
            early_finish=_py(t.getEarlyFinish()),
            late_start=_py(t.getLateStart()),
            late_finish=_py(t.getLateFinish()),
            total_float_hours=total,
            free_float_hours=_hours(j, t.getFreeSlack()),
            critical=bool(t.getCritical()),
        )
    return ScheduleResult(project_finish=_py(props.getFinishDate()), activities=results)
