from timefold.solver.score import (constraint_provider, HardSoftScore, Joiners,
                                   ConstraintFactory, Constraint, ConstraintCollectors)
from datetime import time
from .domain import ShiftAssignment, TA, Timetable, Shift

@constraint_provider
def basic_ta_scheduling_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        required_tas(constraint_factory),
        ta_must_have_required_shifts(constraint_factory),
        ta_should_not_have_more_than_required_shifts(constraint_factory),
        ta_availability(constraint_factory),
    ]
    
@constraint_provider
def grad_undergrad_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        required_tas(constraint_factory),
        ta_must_have_required_shifts(constraint_factory),
        ta_should_not_have_more_than_required_shifts(constraint_factory),
        ta_availability(constraint_factory),
        at_least_one_grad_undergrad_ta(constraint_factory),
    ]
    
@constraint_provider
def favourite_partners_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        required_tas(constraint_factory),
        ta_must_have_required_shifts(constraint_factory),
        ta_should_not_have_more_than_required_shifts(constraint_factory),
        ta_availability(constraint_factory),
        favourite_partners(constraint_factory),
    ]
    
@constraint_provider
def all_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        required_tas(constraint_factory),
        ta_must_have_required_shifts(constraint_factory),
        ta_should_not_have_more_than_required_shifts(constraint_factory),
        ta_availability(constraint_factory),
        at_least_one_grad_undergrad_ta(constraint_factory),
        favourite_partners(constraint_factory),
    ]


# Each shift gets exactly their required number of TAs
def required_tas(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            # filter out shifts that don't have the required amount of TAs
            .filter(lambda shift_assignment: len(shift_assignment.assigned_tas) != shift_assignment.shift.required_tas)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Required TAs"))
    
# Each TA teaches at least their minimum number of shifts
def ta_must_have_required_shifts(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            # group by TA and count the number of shifts that they are assigned to
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            # filter out TAs that don't have the required amount of shifts
            .filter(lambda ta, count: count < ta.required_shifts)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA must have required shifts"))
    
# System penalizes if a TA is doing more than their required number of shifts
def ta_should_not_have_more_than_required_shifts(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            # group by TA and count the number of shifts that they are assigned to
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            # filter out TAs that are doing more than the required amount of shifts
            .filter(lambda ta, count: count > ta.required_shifts)
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("TA should not to more than the required shifts"))
    
# TA's availability must match the shift they are assigned to
def ta_availability(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            # filter out shifts that the TA is not available for
            .filter(lambda shift_assignment: shift_assignment.assigned_ta.availability.contains(shift_assignment.shift))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA availability"))

# TA's favourite partners should be assigned to the same shift
def favourite_partners(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            # group by shift and collect the TAs assigned to that shift
            .group_by(lambda shift_assignment: shift_assignment, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
            # filter out shifts where no TA has a favourite partner assigned to the same shift
            .filter(lambda shift_assignment, tas: any(set(ta.favourite_partners).isdisjoint(tas) for ta in tas))
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("Favourite partners"))
    
# Grad and undergrad TAs should be assigned to the same shift
def at_least_one_grad_undergrad_ta(constraint_factory: ConstraintFactory) -> Constraint:
    return (constraint_factory
            .for_each(ShiftAssignment)
            # group by shift and collect TAs assigned to that shift
            .group_by(lambda shift_assignment: shift_assignment, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
            # filter out shifts where there is no grad and undergrad TA assigned to the same shift
            .filter(lambda shift_assignment, tas: not (any(ta.is_grad_student for ta in tas) and any(not ta.is_grad_student for ta in tas)))
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("At least one grad and undergrad TA"))