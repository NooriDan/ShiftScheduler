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
class Shift:
    id: Annotated[str, PlanningId]
    series: str
    day_of_week: str
    start_time: time
    end_time: time
    required_tas: int

    def __str__(self):
        return f'{self.series} {self.day_of_week} {self.start_time.strftime("%H:%M")}'
    
@dataclass
class TA:
    id: Annotated[str, PlanningId]
    name: str
    required_shifts: int
    # is_grad_student: bool
    # favourite_partners: Annotated[list['TA'], Field(default=None)]
    desired: Annotated[list[Shift], Field(default_factory=list)]
    undesired: Annotated[list[Shift], Field(default_factory=list)]
    unavailable: Annotated[list[Shift], Field(default_factory=list)]

    def __str__(self):
        return f'{self.name}'


@planning_entity
@dataclass
class ShiftAssignment:
    id: Annotated[str, PlanningId]
    shift: Shift
    assigned_ta: Annotated[TA | None,
                        PlanningVariable,
                        Field(default=None)]
    
    # def __str__(self):
    #     return f'{self.shift} {self.assigned_ta}'
    
    # def __repr__(self):
    #     return f'{self.shift.id}-{self.shift.sereis}_{self.assigned_ta.id}-{self.assigned_ta.name}'

@planning_solution
@dataclass
class Timetable:
    id: Annotated[str, PlanningId]
    # problem facts
    shift_groups: Annotated[list[Shift],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    tas: Annotated[list[TA],
                     ProblemFactCollectionProperty,
                     ValueRangeProvider]
    # planning entities
    shift_assignments: Annotated[list[ShiftAssignment],
                       PlanningEntityCollectionProperty]
    # score and solver status
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)


if __name__ == '__main__':
    # shift_group_1 = ShiftGroup("1", "L01", "Mon", time(14, 30), time(17, 30), 2)
    print("Running domain.py")