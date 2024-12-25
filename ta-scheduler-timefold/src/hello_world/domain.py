from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore
from dataclasses import dataclass, field
from datetime import time, date
from typing import Annotated
from pydantic import Field


@dataclass
class ShiftGroup:
    id:     Annotated[str, PlanningId]
    group_name: str
    day_of_week: str
    start_time: time
    end_time: time
    required_tas: int

    def __str__(self):
        return f'{self.group_name} {self.day_of_week} {self.start_time.strftime("%H:%M")}'
    
@dataclass
class TA:
    id:     Annotated[str, PlanningId]
    name: str
    required_shifts: int
    # Extra properties
    favourite_partners: Annotated[list['TA'], Field(default=None)]
    is_grad_student: bool
    # Availability Information
    unavailable_dates: Annotated[set[date], Field(default_factory=set)]
    undesired_dates: Annotated[set[date], Field(default_factory=set)]
    desired_dates: Annotated[set[date], Field(default_factory=set)]

    def __str__(self):
        return f'{self.name}'


@planning_entity
@dataclass
class Shift:
    id: Annotated[str, PlanningId]
    subject: str
    teacher: str
    student_group: str
    timeslot: Annotated[ShiftGroup | None, PlanningVariable] = field(default=None)
    room: Annotated[TA | None, PlanningVariable] = field(default=None)


@planning_solution
@dataclass
class Timetable:
    id: str
    shift_groups: Annotated[list[ShiftGroup],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    tas: Annotated[list[TA],
                     ProblemFactCollectionProperty,
                     ValueRangeProvider]
    shifts: Annotated[list[Shift],
                       PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)


if __name__ == '__main__':
    # shift_group_1 = ShiftGroup("1", "L01", "Mon", time(14, 30), time(17, 30), 2)
    print("Running domain.py")