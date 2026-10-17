"""Schedule file import/export through MPXJ readers and writers (D35).

Reads anything MPXJ's UniversalProjectReader detects (XER, PMXML, MSPDI, MPP, MPX, Asta,
Phoenix, ...); writes XER, PMXML, MSPDI, MPX, Planner, SDEF, JSON.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path

from nsa.schedule.engine import mpxj_adapter
from nsa.schedule.engine.mpxj_adapter import ScheduleError, _java, _ldt, _py
from nsa.schedule.model import types as t

WRITE_FORMATS = {"xer": "XER", "pmxml": "PMXML", "mspdi": "MSPDI", "mpx": "MPX", "planner": "PLANNER",
                 "sdef": "SDEF", "json": "JSON"}

_LINK_BACK = {"FINISH_START": t.LinkType.FS, "START_START": t.LinkType.SS,
              "FINISH_FINISH": t.LinkType.FF, "START_FINISH": t.LinkType.SF}
_ACTIVITY_BACK = {v: k for k, v in mpxj_adapter._ACTIVITY.items()}
_CONSTRAINT_BACK = {v: k for k, v in mpxj_adapter._CONSTRAINT.items()}


def export_schedule(inp: t.ScheduleInput, path: str | Path, fmt: str) -> Path:
    j = _java()
    from org.mpxj.writer import FileFormat, UniversalProjectWriter

    if fmt not in WRITE_FORMATS:
        raise ScheduleError(f"Unsupported export format {fmt}")
    from org.mpxj.cpm import PrimaveraScheduler

    file, _ = mpxj_adapter.build_project_file(inp)
    PrimaveraScheduler().schedule(file, _ldt(j, inp.project_start))  # writers need computed dates
    file.getProjectProperties().setName(Path(path).stem)
    path = Path(path)
    UniversalProjectWriter(getattr(FileFormat, WRITE_FORMATS[fmt])).write(file, str(path))
    return path


def _hours(j, duration, props) -> float:
    if duration is None:
        return 0.0
    return float(duration.convertUnits(j.TimeUnit.HOURS, props).getDuration())


def _calendar(cal) -> t.Calendar:
    from java.time import DayOfWeek

    week = {}
    for iso in range(1, 8):
        hours = cal.getCalendarHours(DayOfWeek.of(iso))
        shifts = []
        if hours is not None and cal.isWorkingDay(DayOfWeek.of(iso)):
            for r in hours:
                start, end = r.getStart(), r.getEnd()
                end_t = time(23, 59) if end.getHour() == 0 and end.getMinute() == 0 else time(end.getHour(), end.getMinute())
                shifts.append(t.WorkShift(time(start.getHour(), start.getMinute()), end_t))
        if shifts:
            week[iso] = shifts
    holidays: set[date] = set()
    for exc in cal.getCalendarExceptions():
        if exc.getWorking():
            continue
        d = date(exc.getFromDate().getYear(), exc.getFromDate().getMonthValue(), exc.getFromDate().getDayOfMonth())
        last = date(exc.getToDate().getYear(), exc.getToDate().getMonthValue(), exc.getToDate().getDayOfMonth())
        while d <= last:
            holidays.add(d)
            d += timedelta(days=1)
    minutes = cal.getCalendarMinutesPerDay()
    return t.Calendar(code=str(cal.getName() or f"CAL{cal.getUniqueID()}"), week=week, holidays=holidays,
                      hours_per_day=(minutes / 60.0) if minutes else 8.0)


def import_schedule(path: str | Path) -> t.ScheduleInput:
    j = _java()
    from org.mpxj.reader import UniversalProjectReader

    file = UniversalProjectReader().read(str(path))
    if file is None:
        raise ScheduleError(f"Unrecognised schedule file {path}")
    props = file.getProjectProperties()

    calendars: dict[str, t.Calendar] = {}
    for cal in file.getCalendars():
        c = _calendar(cal)
        calendars.setdefault(c.code, c)
    default = file.getDefaultCalendar()
    default_code = _calendar(default).code if default is not None else next(iter(calendars), None)
    if default_code is None:
        raise ScheduleError("Schedule has no calendar")

    activities, codes = [], {}
    for task in file.getTasks():
        if task.hasChildTasks() or task.getUniqueID() is None or (task.getID() is not None and task.getID() == 0
                                                                  and task.getActivityID() is None):
            continue
        code = str(task.getActivityID() or task.getText(1) or task.getUniqueID())
        codes[task.getUniqueID()] = code
        at = task.getActivityType()
        if at is None:
            at_name = "FINISH_MILESTONE" if task.getMilestone() else "TASK_DEPENDENT"
        else:
            at_name = str(at.name())
        con = task.getConstraintType()
        con_type = _CONSTRAINT_BACK.get(str(con.name())) if con is not None else None
        cal = task.getCalendar()
        activities.append(t.Activity(
            code=code, name=str(task.getName() or code),
            duration_hours=_hours(j, task.getDuration(), props),
            remaining_hours=_hours(j, task.getRemainingDuration(), props) if task.getRemainingDuration() else None,
            activity_type=_ACTIVITY_BACK.get(at_name, t.ActivityType.TASK_DEPENDENT),
            calendar=_calendar(cal).code if cal is not None else None,
            actual_start=_py(task.getActualStart()), actual_finish=_py(task.getActualFinish()),
            constraint=con_type,
            constraint_date=_py(task.getConstraintDate()) if con_type else None,
        ))

    relationships = []
    for task in file.getTasks():
        succ = codes.get(task.getUniqueID())
        if succ is None:
            continue
        for rel in task.getPredecessors():
            pred = codes.get(rel.getPredecessorTask().getUniqueID())
            if pred is None:
                continue
            relationships.append(t.Relationship(pred, succ, _LINK_BACK[str(rel.getType().name())],
                                                _hours(j, rel.getLag(), props)))

    start = _py(props.getStartDate()) or _py(file.getEarliestStartDate()) or datetime.combine(date.today(), time(8))
    return t.ScheduleInput(project_start=start, activities=activities, relationships=relationships,
                           calendars=list(calendars.values()), default_calendar=default_code,
                           data_date=_py(props.getStatusDate()), must_finish_by=_py(props.getMustFinishBy()))


__all__ = ["export_schedule", "import_schedule", "WRITE_FORMATS"]
