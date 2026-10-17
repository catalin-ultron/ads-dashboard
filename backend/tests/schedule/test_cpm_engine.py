from datetime import date, datetime

import pytest

from nsa.schedule.engine.mpxj_adapter import ScheduleError, schedule
from nsa.schedule.model.types import (
    Activity,
    ActivityType,
    Calendar,
    ConstraintType,
    LinkType,
    Relationship,
    ScheduleInput,
)

MON = datetime(2026, 11, 2, 8, 0)  # Monday


def _inp(activities, relationships, holidays=None, **kw):
    return ScheduleInput(
        project_start=MON,
        activities=activities,
        relationships=relationships,
        calendars=[Calendar.standard(holidays=holidays)],
        default_calendar="STD",
        **kw,
    )


def test_fs_chain_and_parallel_branch_float():
    # A(2d) -> B(3d) -> D(1d); A -> C(1d) -> D
    acts = [
        Activity("A", "Excavation", 16),
        Activity("B", "Foundations", 24),
        Activity("C", "Formwork order", 8),
        Activity("D", "Backfill", 8),
    ]
    rels = [Relationship("A", "B"), Relationship("B", "D"), Relationship("A", "C"), Relationship("C", "D")]
    res = schedule(_inp(acts, rels))
    a, b, c, d = (res.activities[k] for k in "ABCD")
    assert a.early_start == MON
    assert b.early_start == datetime(2026, 11, 4, 8, 0)
    assert d.early_finish == datetime(2026, 11, 9, 17, 0)
    assert res.project_finish == d.early_finish
    assert c.total_float_hours == pytest.approx(16.0)
    assert res.critical_path == ["A", "B", "D"]


def test_ss_with_lag_and_ff():
    acts = [Activity("A", "Pour slab", 40), Activity("B", "Cure monitoring", 40), Activity("C", "Strip", 8)]
    rels = [Relationship("A", "B", LinkType.SS, 8), Relationship("B", "C", LinkType.FF, 0)]
    res = schedule(_inp(acts, rels))
    assert res.activities["B"].early_start == datetime(2026, 11, 3, 8, 0)
    assert res.activities["C"].early_finish == res.activities["B"].early_finish


def test_holiday_shifts_work():
    acts = [Activity("A", "Work", 16)]
    res = schedule(_inp(acts, [], holidays={date(2026, 11, 3)}))
    assert res.activities["A"].early_finish == datetime(2026, 11, 4, 17, 0)


def test_start_on_or_after_constraint():
    acts = [Activity("A", "Mobilise", 8), Activity("B", "Asphalt", 8,
            constraint=ConstraintType.START_ON_OR_AFTER, constraint_date=datetime(2026, 11, 9, 8, 0))]
    res = schedule(_inp(acts, [Relationship("A", "B")]))
    assert res.activities["B"].early_start == datetime(2026, 11, 9, 8, 0)


def test_finish_milestone():
    acts = [Activity("A", "Works", 16), Activity("M", "Reception", 0, activity_type=ActivityType.FINISH_MILESTONE)]
    res = schedule(_inp(acts, [Relationship("A", "M")]))
    assert res.activities["M"].early_finish == res.activities["A"].early_finish


def test_cycle_is_rejected():
    acts = [Activity("A", "x", 8), Activity("B", "y", 8)]
    with pytest.raises(ScheduleError):
        schedule(_inp(acts, [Relationship("A", "B"), Relationship("B", "A")]))


def test_unknown_activity_in_relationship():
    with pytest.raises(ScheduleError):
        schedule(_inp([Activity("A", "x", 8)], [Relationship("A", "Z")]))
