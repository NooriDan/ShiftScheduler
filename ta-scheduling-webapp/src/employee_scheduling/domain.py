from .json_serialization import *

from dataclasses import dataclass
from datetime import time
from typing import Annotated
from timefold.solver.domain import *
from timefold.solver.score import HardSoftScore
from timefold.solver import SolverStatus
from pydantic import Field


@dataclass
class Shift(JsonDomainBase):
    id: Annotated[str, PlanningId]
    day_of_week: str
    start_time: time
    end_time: time
    required_tas: int


@dataclass
class TA(JsonDomainBase):
    id: Annotated[str, PlanningId]
    name: str
    required_shifts: int
    availability: Annotated[list[Shift], Field(default_factory=list)]
    is_grad_student: bool
    favourite_partners: Annotated[list['TA'], Field(default=None)]

@dataclass
class ConstraintParameters(JsonDomainBase):
    allow_favourite_partners: Annotated[bool, ProblemFactCollectionProperty]
    mandate_grad_undergrad: Annotated[bool, ProblemFactCollectionProperty]

@planning_entity
@dataclass
class ShiftAssignment(JsonDomainBase):
    id: Annotated[str, PlanningId]
    series: str
    # shift: Shift
    assigned_ta: Annotated[TA | None,
                        PlanningVariable,
                        Field(default=None)]

@planning_solution
class Timetable(JsonDomainBase):
    # problem facts
    # shifts: Annotated[list[Shift], ProblemFactCollectionProperty]
    tas: Annotated[list[TA], ProblemFactCollectionProperty,  ValueRangeProvider]
    constraint_parameters: Annotated[ConstraintParameters, ProblemFactProperty]
    # planning entities
    shift_assignments: Annotated[list[ShiftAssignment], PlanningEntityCollectionProperty]
    # score and solver status
    score:          Annotated[HardSoftScore | None,
                                        PlanningScore, ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]
    
    
    