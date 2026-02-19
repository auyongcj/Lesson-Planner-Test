from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from typing import Literal
from typing import List, Literal



@dataclass
class LessonInfoRow:
    stage: str = "1"
    activity: str = ""
    time_minutes: str = ""   # e.g. "10 mins"


@dataclass
class LogisticsRow:
    logistics: str = ""
    remarks: str = ""
    quantity: str = ""


@dataclass
class RemarkItem:
    text: str = ""
    subitems: List[str] = field(default_factory=list)

ListStyle = Literal["bullet", "number", "roman"]

@dataclass
class RemarksBlock:
    lead: str = ""                         # optional lead line above the list
    style: ListStyle = "bullet"            # bullet | number | roman
    items: List[RemarkItem] = field(default_factory=list)



@dataclass
class MethodRow:
    stage: str = "1"
    activity: str = ""
    remarks: RemarksBlock = field(default_factory=RemarksBlock)


@dataclass
class PersonnelRow:
    role: str = ""
    names: str = ""
    remarks: str = ""


@dataclass
class LessonPlanDoc:
    lesson_title: str = "Administrative Matters."
    lesson_objectives: List[str] = field(default_factory=list)
    prior_knowledge: List[str] = field(default_factory=list)

    # 4. Lesson Information (table + metadata)
    lesson_info_rows: List[LessonInfoRow] = field(default_factory=lambda: [LessonInfoRow(stage="1")])
    attire: str = ""
    targeted_participants: str = ""
    location: str = ""

    # 5. Equipment & Logistics
    logistics_rows: List[LogisticsRow] = field(default_factory=list)

    # 6. Method of Instruction
    training_personnel_line: str = ""     # e.g. "2 CLs : 20 Cadets"
    method_rows: List[MethodRow] = field(default_factory=lambda: [MethodRow(stage="1")])

    # 7. Training Personnel
    personnel_rows: List[PersonnelRow] = field(default_factory=list)

    # 8–10
    safety_precautions: List[str] = field(default_factory=list)
    contingency_plans: List[str] = field(default_factory=list)

    prepared_by: str = ""
    vetted_by: str = ""
    date_text: str = ""  # you can use date picker later

