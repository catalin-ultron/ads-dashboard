"""Source-neutral schedule types consumed and produced by the CPM engine (D03-D06)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class LinkType(str, Enum):
    FS = "FS"
    SS = "SS"
    FF = "FF"
    SF = "SF"


class ActivityType(str, Enum):
    TASK_DEPENDENT = "task_dependent"
    RESOURCE_DEPENDENT = "resource_dependent"
    LEVEL_OF_EFFORT = "level_of_effort"
    START_MILESTONE = "start_milestone"
    FINISH_MILESTONE = "finish_milestone"
    WBS_SUMMARY = "wbs_summary"


class ConstraintType(str, Enum):
    START_ON = "start_on"
    START_ON_OR_AFTER = "start_on_or_after"
    START_ON_OR_BEFORE = "start_on_or_before"
    FINISH_ON = "finish_on"
    FINISH_ON_OR_AFTER = "finish_on_or_after"
    FINISH_ON_OR_BEFORE = "finish_on_or_before"
    MANDATORY_START = "mandatory_start"
    MANDATORY_FINISH = "mandatory_finish"
    AS_LATE_AS_POSSIBLE = "as_late_as_possible"


@dataclass(frozen=True)
class WorkShift:
    start: time
    end: time


@dataclass
class Calendar:
    code: str
    # ISO weekday (1=Monday .. 7=Sunday) -> working shifts; missing day = non-working
    week: dict[int, list[WorkShift]]
    holidays: set[date] = field(default_factory=set)
    hours_per_day: float = 8.0

    @classmethod
    def standard(cls, code: str = "STD", holidays: set[date] | None = None) -> "Calendar":
        shifts = [WorkShift(time(8), time(12)), WorkShift(time(13), time(17))]
        return cls(code=code, week={d: shifts for d in range(1, 6)}, holidays=holidays or set())


@dataclass
class Activity:
    code: str
    name: str
    duration_hours: float
    remaining_hours: float | None = None
    activity_type: ActivityType = ActivityType.TASK_DEPENDENT
    calendar: str | None = None
    actual_start: datetime | None = None
    actual_finish: datetime | None = None
    constraint: ConstraintType | None = None
    constraint_date: datetime | None = None


@dataclass
class Relationship:
    predecessor: str
    successor: str
    link: LinkType = LinkType.FS
    lag_hours: float = 0.0


@dataclass
class ScheduleInput:
    project_start: datetime
    activities: list[Activity]
    relationships: list[Relationship]
    calendars: list[Calendar]
    default_calendar: str
    data_date: datetime | None = None
    must_finish_by: datetime | None = None


@dataclass
class ActivityResult:
    code: str
    early_start: datetime
    early_finish: datetime
    late_start: datetime
    late_finish: datetime
    total_float_hours: float
    free_float_hours: float
    critical: bool


@dataclass
class ScheduleResult:
    project_finish: datetime
    activities: dict[str, ActivityResult]

    @property
    def critical_path(self) -> list[str]:
        crit = [a for a in self.activities.values() if a.critical]
        return [a.code for a in sorted(crit, key=lambda a: (a.early_start, a.early_finish))]
