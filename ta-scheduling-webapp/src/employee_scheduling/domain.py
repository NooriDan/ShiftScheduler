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
    id:     Annotated[str, PlanningId]
    name:   str
    required_shifts: int
    is_grad_student: bool
    favourite_partners: Annotated[list['TA'], Field(default=None)]
    # availability: Annotated[list[Shift], Field(default_factory=list)]
    desired:        Annotated[list[str], Field(default_factory=list)]
    undesired:      Annotated[list[str], Field(default_factory=list)]
    unavailable:    Annotated[list[str], Field(default_factory=list)]

@dataclass
class ShiftGroup(JsonDomainBase):
    id: Annotated[str, PlanningId]
    group_name: str
    day_of_week: str
    start_time: time
    end_time: time
    required_tas: int

@planning_entity
@dataclass
class Shift(JsonDomainBase):
    id: Annotated[str, PlanningId]
    shift_group: ShiftGroup
    assigned_ta: Annotated[TA | None,
                        PlanningVariable,
                        Field(default=None)]

@planning_solution
class Timetable(JsonDomainBase):
    # problem facts
    tas:            Annotated[list[TA], ProblemFactCollectionProperty,  ValueRangeProvider]
    shift_groups:   Annotated[list[ShiftGroup], ProblemFactCollectionProperty,  ValueRangeProvider]

    # planning entities
    shift_assignments: Annotated[list[Shift], PlanningEntityCollectionProperty]

    # score and solver status
    score:          Annotated[HardSoftScore | None,
                                        PlanningScore, ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]
    
    
    