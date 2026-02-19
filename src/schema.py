from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class ScheduleRow:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    time: str = ""
    activity: str = ""
    venue: str = ""
    ic: str = ""
    attire: str = ""
    remarks: str = ""


@dataclass
class ScheduleDoc:
    unit_title: str = "(S2 SQUAD)"
    programme_title: str = "Training Programme"
    programme_date_line: str = "for 20th February 2026, Friday"

    rows: List[ScheduleRow] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    authenticated_by: str = ""
    vetted_by: str = ""