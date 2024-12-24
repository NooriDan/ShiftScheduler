from timefold.solver.score import (constraint_provider, HardSoftScore, Joiners,
                                   ConstraintFactory, Constraint, ConstraintCollectors)
from datetime import time
from .domain import ShiftAssignment, TA, Timetable, Shift

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
    ]

# Each shift gets exactly their required number of TAs
def required_tas(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            .filter(lambda shift_assignment: len(shift_assignment.assigned_tas) != shift_assignment.shift.required_tas)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Required TAs"))
    
# Each TA teaches at least their minimum number of shifts
def ta_must_have_required_shifts(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            .filter(lambda ta, count: count < ta.required_shifts)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA must have required shifts"))
    
# System penalizes if a TA is doing more than their required number of shifts
def ta_must_have_required_shifts(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            .filter(lambda ta, count: count > ta.required_shifts)
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("TA should not to more than the required shifts"))
    
# TA's availability must match the shift they are assigned to
def ta_availability(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            .filter(lambda shift_assignment: shift_assignment.assigned_ta.availability.contains(shift_assignment.shift))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA availability"))

# TA's favourite partners should be assigned to the same shift
def favourite_partners(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.shift, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
            .filter(lambda shift_assignment: any(ta for ta in shift_assignment.assigned_tas if shift_assignment.shift not in ta.availability))
            .filter(lambda shift, tas: )
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("Favourite partners"))