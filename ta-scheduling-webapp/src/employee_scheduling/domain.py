from .json_serialization import *

from dataclasses import dataclass
from datetime import time, date
from typing import Annotated
from timefold.solver.domain import *
from timefold.solver.score import HardMediumSoftScore
from timefold.solver import SolverStatus
from pydantic import Field

class Shift(JsonDomainBase):
    id: Annotated[str, PlanningId]
    series: str # must also be unique
    day_of_week: str # not critical
    start_time: time # not critical
    end_time: time   # not critical
    required_tas: int 
    # Optional
    alias: str = "DEFAULT"
    shift_date: date = date(1900, 1, 1) 

    def __str__(self):
        return f'{self.series} {self.day_of_week} {self.start_time.strftime("%H:%M")}'
    

class TA(JsonDomainBase):
    id: Annotated[str, PlanningId]
    name: str # not critical
    required_shifts: int
    desired: Annotated[list[Shift], Field(default_factory=list)]
    undesired: Annotated[list[Shift], Field(default_factory=list)]
    unavailable: Annotated[list[Shift], Field(default_factory=list)]

    # favourite_partners: list['TA'] = None
    is_grad_student: bool = True

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

# @dataclass
# class ConstraintParameters(JsonDomainBase):
#     allow_favourite_partners: Annotated[bool, ProblemFactCollectionProperty]
#     mandate_grad_undergrad: Annotated[bool, ProblemFactCollectionProperty]

@planning_entity
class ShiftAssignment(JsonDomainBase):
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
class Timetable(JsonDomainBase):
    id: Annotated[str, PlanningId]
    # problem facts
    shifts: Annotated[list[Shift],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    tas: Annotated[list[TA],
                     ProblemFactCollectionProperty,
                     ValueRangeProvider]
    # planning entities
    shift_assignments: Annotated[list[ShiftAssignment],
                       PlanningEntityCollectionProperty]
    # score and solver status
    score: Annotated[HardMediumSoftScore, PlanningScore, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]

    def __str__(self):
        return f"timetable_{self.id}"


if __name__ == '__main__':
    # shift_group_1 = ShiftGroup("1", "L01", "Mon", time(14, 30), time(17, 30), 2)
    print("Running domain.py")