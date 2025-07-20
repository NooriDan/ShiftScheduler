from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver import SolverStatus
from timefold.solver.score import HardSoftScore, HardMediumSoftScore
from dataclasses import dataclass, field
from datetime import time, date
from typing import Annotated, List
from pydantic import Field


@dataclass
class Shift():
    id: Annotated[str, PlanningId]
    series: str
    day_of_week: str
    week_id: int
    start_time: time
    end_time: time
    required_tas: int
    # Optional
    alias: str = "DEFAULT"
    shift_date: date = date(1900, 1, 1)

    def __str__(self):
        return f'{self.series} {self.day_of_week} {self.start_time.strftime("%H:%M")}'
    
@dataclass    
class TA():
    id: Annotated[str, PlanningId]
    name: str
    required_shifts_per_semester: int
    skill_level: int
    desired: Annotated[list[Shift], Field(default_factory=list)]
    undesired: Annotated[list[Shift], Field(default_factory=list)]
    unavailable: Annotated[list[Shift], Field(default_factory=list)]

    # favourite_partners: list['TA'] = None
    is_grad_student: bool = True
    min_shifts_per_week: int = 0
    max_shifts_per_week: int = 2

    
    def __str__(self):
        return f'{self.name}'
    
    def get_status_for_shift(self, shift: Shift) -> str:
        if shift in self.desired:
            return 'Desired'
        if shift in self.undesired:
            return 'Undesired'
        if shift in self.unavailable:
            return 'Unavailable'
        return 'Neutral'
    
    def is_available_for_shift(self, shift: Shift) -> bool:
        return shift not in self.unavailable



@planning_entity
@dataclass
class ShiftAssignment():
    id: Annotated[str, PlanningId]
    shift: Shift
    assigned_ta: Annotated[TA | None,
                        PlanningVariable,
                        Field(default=None)]
    
    def __str__(self):
        return f'{self.shift} {self.assigned_ta}'

@planning_solution
@dataclass
class Timetable():
    id: Annotated[str, PlanningId]
    # problem facts
    shifts: Annotated[list[Shift],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    tas: Annotated[list[TA],
                     ProblemFactCollectionProperty,
                     ValueRangeProvider]
    # planning entities
    shift_assignments: Annotated[List[ShiftAssignment],
                       PlanningEntityCollectionProperty]
    # score and solver status
    solver_status: Annotated[SolverStatus | None, Field(default=None)]  = Field(default=None)
    score: Annotated[HardMediumSoftScore, PlanningScore] = field(default=None)
    # score: Annotated[BendableScore, PlanningScore(bendable_hard_levels_size=2, bendable_soft_levels_size=3)] # custom score levels
    def __str__(self):
        return f"timetable_{self.id}"


if __name__ == '__main__':
    # shift_group_1 = ShiftGroup("1", "L01", "Mon", time(14, 30), time(17, 30), 2)
    print("Running domain.py")