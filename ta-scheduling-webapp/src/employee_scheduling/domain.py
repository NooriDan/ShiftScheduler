from .json_serialization import *

from dataclasses import dataclass
from datetime import time
from typing import Annotated
from timefold.solver.domain import *
from timefold.solver.score import HardSoftScore
from timefold.solver import SolverStatus
from pydantic import Field

@dataclass
class TA(JsonDomainBase):
    id: Annotated[str, PlanningId]
    name: str
    required_shifts: int
    is_grad_student: bool
    favourite_partners: Annotated[list['TA'], Field(default=None)]
    # availability: Annotated[list[Shift], Field(default_factory=list)]
    desired: Annotated[list['Shift'], Field(default_factory=list)]
    undesired: Annotated[list['Shift'], Field(default_factory=list)]
    unavailable: Annotated[list['Shift'], Field(default_factory=list)]


# @dataclass
# class ConstraintParameters(JsonDomainBase):
#     allow_favourite_partners: Annotated[bool, ProblemFactCollectionProperty]
#     mandate_grad_undergrad: Annotated[bool, ProblemFactCollectionProperty]

# @planning_entity
@dataclass
class Shift(JsonDomainBase):
    id: Annotated[str, PlanningId]
    series: str
    day_of_week: str
    start_time: time
    end_time: time
    required_tas: int
    assigned_tas: Annotated[list[TA],
                        PlanningVariable,
                        Field(default=list)]

@planning_solution
class Timetable(JsonDomainBase):
    # problem facts
    # shifts: Annotated[list[Shift], ProblemFactCollectionProperty, Val]
    tas: Annotated[list[TA], ProblemFactCollectionProperty,  ValueRangeProvider]
    # constraint_parameters: Annotated[ConstraintParameters, ProblemFactProperty]
    # planning entities
    shift_assignments: Annotated[list[Shift], PlanningEntityCollectionProperty]
    # score and solver status
    score:          Annotated[HardSoftScore | None,
                                        PlanningScore, ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]
    
    
    