from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ProblemFactProperty, ValueRangeProvider, ConstraintWeightOverrides,
                                    PlanningScore, PlanningPin)
from timefold.solver import SolverStatus
from timefold.solver.score import HardSoftScore, HardMediumSoftScore
from dataclasses import dataclass, field
from datetime import time, date
from typing import Annotated, List
from pydantic import Field

@dataclass
class ConstraintParameters:
    undesired_assignment_penalty:   int = 20
    desired_assignment_reward:      int = 1

    def __str__(self):
        return f"undesired_assignment_penalty={self.undesired_assignment_penalty}, desired_assignment_reward={self.desired_assignment_reward}"

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
        return f'{self.series} {self.day_of_week} {self.start_time.strftime("%H:%M")} - week {self.week_id}'
    
    def is_from_the_same_series_as(self, other: 'Shift') -> bool:
        """Check if this shift is from the same series as another shift."""
        return self.series == other.series
    
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
            return '** Desired **'
        if shift in self.undesired:
            return '>> Undesired <<'
        if shift in self.unavailable:
            return 'X Unavailable X'
        return 'Neutral'
    
    def is_available_for_shift(self, shift: Shift) -> bool:
        return shift not in self.unavailable



@planning_entity
@dataclass
class ShiftAssignment():
    id: Annotated[str, PlanningId]
    shift: Shift
    assigned_ta: Annotated[TA | None,
                        PlanningVariable, # allow unassigned: PlanningVariable(allows_unassigned=True) -> Constraint Streams filter out planning entities with a null planning variable by default. Use forEachIncludingUnassigned() to avoid such unwanted behaviour.
                        Field(default=None)]
    # pinned: Annotated[bool, PlanningPin] # Pin down planning entities with @PlanningPin
    
    def __str__(self):
        return f'assigning {self.shift.series} to {self.assigned_ta}'
    
    def is_assigned_a_ta(self) -> bool:
        """Check if the shift assignment is valid."""
        return self.assigned_ta is not None and self.shift is not None
    
    # Helper methods to be used in constraints
    def is_desired(self) -> bool:
        """Check if the shift assignment is desired by the TA."""
        if not self.is_assigned_a_ta():
            raise ValueError("Shift assignment is not valid. Ensure that both assigned_ta and shift are set.")   
         
        return self.shift in self.assigned_ta.desired
    
    def is_undesired(self) -> bool:
        """Check if the shift assignment is undesired by the TA."""
        if not self.is_assigned_a_ta():
            raise ValueError("Shift assignment is not valid. Ensure that both assigned_ta and shift are set.") 
        
        return self.shift in self.assigned_ta.undesired
    
    def is_unavailable(self) -> bool:
        """Check if the shift assignment is unavailable for the TA."""
        if not self.is_assigned_a_ta():
            raise ValueError("Shift assignment is not valid. Ensure that both assigned_ta and shift are set.") 
        
        return self.shift in self.assigned_ta.unavailable
    
    def has_the_same_ta(self, other: 'ShiftAssignment') -> bool:
        """Check if this assignment has the same TA as another assignment."""
        return self.assigned_ta is not None and other.assigned_ta is not None and self.assigned_ta.id == other.assigned_ta.id
    
    def has_the_same_shift(self, other: 'ShiftAssignment') -> bool:
        """Check if this assignment has the same shift as another assignment."""
        return self.shift is not None and other.shift is not None and self.shift.id == other.shift.id
    
    def is_from_the_same_series_as(self, other: 'ShiftAssignment') -> bool:
        """Check if this assignment is from the same series as another assignment."""
        return self.shift is not None and other.shift is not None and self.shift.is_from_the_same_series_as(other.shift)
    


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
    # weight_overrides: ConstraintWeightOverrides
    constraint_parameters: Annotated[ConstraintParameters, ProblemFactProperty]

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