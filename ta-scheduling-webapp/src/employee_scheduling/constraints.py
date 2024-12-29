from timefold.solver.score import (constraint_provider, HardSoftScore,
                                   ConstraintFactory, Constraint, ConstraintCollectors, Joiners)
from datetime import time

# Custom Imports
from .domain import Shift, TA, ShiftAssignment


    
@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        # Hard constraints
        shift_meet_ta_required_exactly(constraint_factory),
        ta_duplicate_shift_assignment(constraint_factory),
        ta_meets_shift_requirement(constraint_factory),
        ta_unavailable_shift(constraint_factory),

        # Soft constraints
        penalize_over_assignment(constraint_factory),  
        ta_undesired_shift(constraint_factory),
        ta_desired_shift(constraint_factory), 
    ]


def shift_meet_ta_required_exactly(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each shift should have exactly the required number of TAs """
    return (constraint_factory
            .for_each(ShiftAssignment)
            # filter out shifts that don't have the required amount of TAs
            .group_by(lambda shift_assignment: shift_assignment.shift, ConstraintCollectors.count())
            .filter(lambda shift, count: count != shift.required_tas)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Required TAs per shift violated"))

def ta_duplicate_shift_assignment(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should be assigned to a shift only once """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.to_list(lambda assignment: assignment.shift.id))
            .filter(lambda ta, shift_ids: len(shift_ids) > len(set(shift_ids)))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA duplicate shift assignment"))

# def ta_meets_shift_requirement(constraint_factory: ConstraintFactory) -> Constraint:
#     """ Each TA should be assigned to at least their required number of shifts """
#     return (constraint_factory
#             .for_each(ShiftAssignment)
#             .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
#             .filter(lambda ta, count: count != ta.required_shifts)
#             .penalize(HardSoftScore.ONE_HARD)
#             .as_constraint("TA must have required shifts"))

def ta_meets_shift_requirement(factory: ConstraintFactory) -> Constraint:
    """ Each TA should be assigned to at least their required number of shifts """
    return (factory.for_each(TA)
                .join(ShiftAssignment, Joiners.equal(lambda ta: ta, lambda shift: shift.assigned_ta))
                .concat(
                        factory.for_each(TA)
                                .if_not_exists(ShiftAssignment, Joiners.equal(lambda ta: ta, lambda shift: shift.assigned_ta))
                )
                .group_by(lambda ta, shift: ta,
                        ConstraintCollectors.conditionally(lambda ta, shift: shift is not None,
                                                            ConstraintCollectors.count_bi())
                )
                .filter(lambda ta, shift_count:  shift_count < ta.required_shifts)
                .penalize(HardSoftScore.ONE_HARD, lambda employee, shift_count: (employee.required_shifts - shift_count))
                .as_constraint("TA must have required shifts")
            )

def penalize_over_assignment(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should assigned to more than their required number of shifts should be penalized (Soft) """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            .filter(lambda ta, count: count > ta.required_shifts)
            .penalize(HardSoftScore.ONE_HARD, lambda ta, count: 10*(count - ta.required_shifts))
            .as_constraint("TA should not to more than the required shifts"))
    
def ta_unavailable_shift(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should not be assigned to a shift that they are unavailable for """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: [shift.id for shift in shift_assignment.assigned_ta.unavailable], ConstraintCollectors.to_list(lambda assignment: assignment.shift.id))
            .filter(lambda unavailable, shift_ids: any(id in unavailable for id in shift_ids))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA unavailable"))

# Soft  Constraints
def ta_undesired_shift (constraint_factory: ConstraintFactory) -> Constraint:
    """ Penalize if a TA is assigned to a shift that they don't want to work on """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: [shift.id for shift in shift_assignment.assigned_ta.undesired], ConstraintCollectors.to_list(lambda assignment: assignment.shift.id))
            .filter(lambda unavailable, shift_ids: any(id in unavailable for id in shift_ids))
            .penalize(HardSoftScore.ONE_SOFT, lambda ta, shifts: 10)
            .as_constraint("TA undesired"))

def ta_desired_shift (constraint_factory: ConstraintFactory) -> Constraint:
    """ Reward if a TA is assigned to a shift that they want to work on """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: [shift.id for shift in shift_assignment.assigned_ta.desired], ConstraintCollectors.to_list(lambda assignment: assignment.shift.id))
            .filter(lambda unavailable, shift_ids: any(id in unavailable for id in shift_ids))
            .reward(HardSoftScore.ONE_SOFT, lambda ta, shifts: 1)
            .as_constraint("TA desired"))
