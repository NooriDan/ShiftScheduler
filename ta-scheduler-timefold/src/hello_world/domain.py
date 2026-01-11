from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ProblemFactProperty, ValueRangeProvider, ConstraintWeightOverrides,
                                    PlanningScore, PlanningPin)
from timefold.solver import SolverStatus
from timefold.solver.score import HardSoftScore, HardMediumSoftScore
from dataclasses import dataclass, field
from datetime import time, date, timedelta, datetime
from typing import Annotated, List
from pydantic import Field

import logging
from collections import defaultdict

from typing import Dict, Tuple

def id_generator():
    """Generates unique IDs for the shift assignments."""
    current = 0
    while True:
        yield str(current)
        current += 1

@dataclass
class ConstraintParameters:
    undesired_assignment_penalty:   int = 20    # Soft
    desired_assignment_reward:      int = 5     # Soft
    same_sereis_assignment_reward:  int = 1     # Soft

    unavailable_assignment_penalty:  int = 1     # Soft

    def __str__(self):
        return f"ConstraintParameters"

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
    
    def get_duration(self) -> timedelta:
        start_time_dt = datetime.combine(self.shift_date, self.start_time)
        end_time_dt = datetime.combine(self.shift_date, self.end_time)
        return end_time_dt - start_time_dt
    
    def overlaps_with_other_shift(self, other: 'Shift') -> bool:
        if self.day_of_week == other.day_of_week:
            if other.end_time <= self.end_time and other.end_time >= self.start_time:
                return True
            elif other.start_time <= self.end_time and other.start_time >= self.start_time:
                return True
        return False
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
    
    def get_week_id(self) -> str:
        return str(self.shift.week_id)
    
    def get_shift_series(self) -> str:
        return str(self.shift.series)
    
    def get_ta(self) -> TA | None:
        return self.assigned_ta
    
    def get_ta_id(self) -> str | None:
        return self.assigned_ta.id if self.assigned_ta is not None else None
    
    def get_shift(self) -> Shift:
        return self.shift
    
    def get_shift_id(self) -> str:
        return self.shift.id

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
    
    def overlaps_in_time_with(self, other: 'ShiftAssignment') -> bool:
        """"""
        if self.id == other.id:
            return False # a shift_assignment cannont overlap with itself!
        
        if self.has_the_same_ta(other=other):
            return self.shift.overlaps_with_other_shift(other=other.shift)
        
        return False
    


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
        return f"timetable_{self.id} - {len(self.shifts)} shifts - {len(self.tas)} TAs - [{len(self.shift_assignments)} planning variables]"


    def sanity_check(self, logger: logging.Logger) -> Tuple[bool, Dict[str, Dict[str, Dict[int, int]]]]:

        sanity          = True
        count_tas       = len(self.tas)
        count_shifts    = len(self.shifts)
        logger.info(f"\tProblem has {count_tas} TAs and {count_shifts} shifts.")

        # (1) Check if there are enough TAs for the shifts
        total_required_tas              = sum(shift.required_tas for shift in self.shifts)
        total_available_tas_per_week    = sum(ta.max_shifts_per_week for ta in self.tas)
        
        num_of_weeks = len(set(shift.week_id for shift in self.shifts))
        total_available_tas = total_available_tas_per_week * num_of_weeks

        if total_required_tas > total_available_tas:
            logger.warning(f"\t⚠️  SANITY CHECK WARNING [TMTBL.workforce.count]: Total required TAs ({total_required_tas}) over the planning problem exceeds anticipated TA duties ({total_available_tas}).")
            logger.warning(f"\t\tCount_TAs: {count_tas}, Num_of_weeks: {num_of_weeks}, Total_available_TAs_per_week: {total_available_tas_per_week}")
            logger.warning(f"\t\tConsider increasing the number of TAs or their maximum shifts per week, or reducing the required TAs per shift.")
            sanity = False

        # (2) Check if too many TAs are unavailable for any shift
        count_unavailable_by_series_week_id : Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        count_undesired_by_series_week_id : Dict[str, Dict[int, int]]   = defaultdict(lambda: defaultdict(int))
        count_desired_by_series_week_id : Dict[str, Dict[int, int]]     = defaultdict(lambda: defaultdict(int))

        # Populate the counts
        for ta in self.tas:
            for shift in ta.unavailable:
                count_unavailable_by_series_week_id[shift.series][shift.week_id] += 1
            for shift in ta.undesired:
                count_undesired_by_series_week_id[shift.series][shift.week_id] += 1
            for shift in ta.desired:
                count_desired_by_series_week_id[shift.series][shift.week_id] += 1
        
        # Analyze the counts for each shift
        for shifts in self.shifts:
            series  = shifts.series
            week_id = shifts.week_id
            count_unavailable = count_unavailable_by_series_week_id.get(series, {}).get(week_id, 0)
            count_undesired   = count_undesired_by_series_week_id.get(series, {}).get(week_id, 0)
            count_desired     = count_desired_by_series_week_id.get(series, {}).get(week_id, 0)
            # UNAVAILABLE CHECKS
            if count_unavailable == count_tas:
                logger.warning(f"\t⚠️  SANITY CHECK WARNING [TMTBL.shifts.unavailable]: All TAs are unavailable for shift series '{series}' in week '{week_id}'.")
                sanity = False
            elif shifts.required_tas > count_tas - count_unavailable:
                logger.warning(f"\t⚠️  SANITY CHECK WARNING [TMTBL.shifts.unavailable]: Only {count_tas - count_unavailable} TAs are available for shift series '{series}' in week '{week_id}', but {shifts.required_tas} are required.")
                sanity = False
            # UNDESIRED CHECKS
            if count_undesired == count_tas:
                logger.warning(f"\t⚠️  SANITY CHECK WARNING [TMTBL.shifts.undesired]: All TAs are undesired for shift series '{series}' in week '{week_id}'.")
                sanity = False
            elif shifts.required_tas > count_tas - count_undesired:
                logger.warning(f"\t⚠️  SANITY CHECK WARNING [TMTBL.shifts.undesired]: Only {count_tas - count_undesired} TAs find shift series '{series}' in week '{week_id}' desired/neutral, but {shifts.required_tas} are required.")
                sanity = False
            # DESIRED CHECKS
            if count_desired == 0:
                logger.warning(f"\t⚠️  SANITY CHECK WARNING [TMTBL.shifts.desired]: No TAs have shift series '{series}' in week '{week_id}' as desired.")
                # sanity = False
            
        return sanity, {
            "unavailable": count_unavailable_by_series_week_id,
            "undesired": count_undesired_by_series_week_id,
            "desired": count_desired_by_series_week_id
            }
    
    def re_generate_empty_shift_assignments(self, shifts: List[Shift]) -> List[ShiftAssignment]:
        shift_assignments = []
        id_gen = id_generator()
        for shift in shifts:
            for i in range(shift.required_tas):
                shift_assignment = ShiftAssignment(
                    id=next(id_gen),
                    shift=shift,
                    assigned_ta=None
                )
                shift_assignments.append(shift_assignment)

        self.shift_assignments = shift_assignments
        return shift_assignments

if __name__ == '__main__':
    # shift_group_1 = ShiftGroup("1", "L01", "Mon", time(14, 30), time(17, 30), 2)
    print("Running domain.py")