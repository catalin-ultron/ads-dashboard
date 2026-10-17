from datetime import date, datetime

import pytest

from nsa.integration.schedule_files import export_schedule, import_schedule
from nsa.schedule.engine.mpxj_adapter import schedule
from nsa.schedule.model.types import Activity, Calendar, LinkType, Relationship, ScheduleInput


def _sample():
    return ScheduleInput(
        project_start=datetime(2026, 11, 2, 8, 0),
        activities=[Activity("A1000", "Organizare șantier", 16), Activity("A1010", "Săpături", 24),
                    Activity("A1020", "Fundații", 40), Activity("A1030", "Comandă armătură", 8)],
        relationships=[Relationship("A1000", "A1010"), Relationship("A1010", "A1020", LinkType.SS, 8),
                       Relationship("A1000", "A1030")],
        calendars=[Calendar.standard(holidays={date(2026, 11, 30), date(2026, 12, 1)})],
        default_calendar="STD",
    )


@pytest.mark.parametrize("fmt,suffix", [("xer", ".xer"), ("mspdi", ".xml"), ("pmxml", ".xml")])
def test_roundtrip_preserves_network_and_dates(tmp_path, fmt, suffix):
    original = _sample()
    path = export_schedule(original, tmp_path / f"plan_{fmt}{suffix}", fmt)
    assert path.stat().st_size > 0
    back = import_schedule(path)
    assert {a.code for a in back.activities} == {a.code for a in original.activities}
    assert {(r.predecessor, r.successor, r.link) for r in back.relationships} == \
           {(r.predecessor, r.successor, r.link) for r in original.relationships}
    durations = {a.code: a.duration_hours for a in back.activities}
    assert durations["A1020"] == pytest.approx(40)
    assert schedule(back).project_finish == schedule(original).project_finish
