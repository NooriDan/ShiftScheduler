from timefold.solver.score import (
    HardSoftScore, 
    HardMediumSoftScore,                               
    constraint_provider,
    ConstraintFactory, 
    Constraint, 
    ConstraintCollectors, 
    ConstraintJustification,
    Joiners)

from datetime import time
from typing import Dict, List, Callable

# Custom Imports
from .domain import Shift, TA, ShiftAssignment, ConstraintParameters

# TODO
#   - fix the name of each constraint... more readable and descriptive

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        # Hard constraints
        shift_meet_ta_required_exactly(constraint_factory),
        ta_duplicate_shift_assignment(constraint_factory),
        # ta_meets_shift_requirement_exactly(constraint_factory),
        ta_unavailable_shift(constraint_factory),

        # Medium Constraints
        legacy_ta_meets_shift_requirement_per_week(constraint_factory),
        penalize_over_assignment_in_a_week(constraint_factory),  

        # Soft constraints
        ta_undesired_shift(constraint_factory),
        ta_desired_shift(constraint_factory), 
    ]

@constraint_provider
def define_constraints_tabriz_edition(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        # Hard constraints
        shift_meet_ta_required_exactly(constraint_factory),
        ta_duplicate_shift_assignment(constraint_factory),
        ta_unavailable_shift(constraint_factory),

        # Medium (1) Constraints
        ta_meets_shift_requirement_over_the_semester(constraint_factory),
        # Medium (2) Constraints
        penalize_over_assignment_in_a_week(constraint_factory),  


        # Soft (1) constraints
        # TODO
        # reward_assignment_to_consecutive_shifts(constraint_factory),

        # Soft (2) constraints
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
            .penalize(HardMediumSoftScore.ONE_HARD, lambda shift, count: abs(shift.required_tas - count))
            .as_constraint("Shift does not meet required TAs exactly"))

def ta_duplicate_shift_assignment(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should be assigned to a shift only once """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.to_list(lambda assignment: assignment.shift.id))
            .filter(lambda ta, shift_ids: len(shift_ids) > len(set(shift_ids)))
            .penalize(HardMediumSoftScore.ONE_HARD, lambda ta, shift_id: 1 )
            .as_constraint("TA duplicate shift assignment"))

# def ta_meets_shift_requirement(constraint_factory: ConstraintFactory) -> Constraint:
#     """ Each TA should be assigned to at least their required number of shifts """
#     return (constraint_factory
#             .for_each(ShiftAssignment)
#             .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
#             .filter(lambda ta, count: count < ta.min_shifts_per_week or count > ta.max_shifts_per_week)
#             .penalize(HardMediumSoftScore.ONE_HARD)
#             .as_constraint("TA must have required shifts"))

def legacy_ta_meets_shift_requirement_exactly(factory: ConstraintFactory) -> Constraint:
    """ Each TA should be assigned to exactly their required number of shifts """
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
                .filter(lambda ta, shift_count:  shift_count > ta.max_shifts_per_week or shift_count < ta.min_shifts_per_week)
                .penalize(HardMediumSoftScore.ONE_HARD, lambda ta, count: 100)
                .as_constraint("TA must have required shifts")
            )

def legacy_ta_meets_shift_requirement_per_week(factory: ConstraintFactory) -> Constraint:
    """ [legacy - assumes weekly scheduling] Each TA should be assigned to at least their required number of shifts """
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
                .filter(lambda ta, shift_count:  shift_count > ta.max_shifts_per_week or shift_count < ta.min_shifts_per_week)
                .penalize(HardMediumSoftScore.ONE_MEDIUM, lambda employee, shift_count: abs(employee.max_shifts_per_week - shift_count))
                .as_constraint("[LEGACY] TA does not meet weekly shift count requirements")
            )

def ta_meets_shift_requirement_over_the_semester(factory: ConstraintFactory) -> Constraint:
    """ Each TA should be assigned to at least their required number of shifts over the whole semester """
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
                .filter(lambda ta, shift_count:  shift_count < ta.required_shifts_per_semester)
                .penalize(HardMediumSoftScore.ONE_MEDIUM, lambda ta, shift_count: (ta.required_shifts_per_semester - shift_count))
                .as_constraint("TA should work at least the required shifts over the semester")
            )

def penalize_over_assignment_in_a_week(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should assigned to more than their required number of shifts should be penalized (Soft) """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            .filter(lambda ta, count: count > ta.max_shifts_per_week)
            .penalize(HardMediumSoftScore.ONE_MEDIUM, lambda ta, count: (count - ta.max_shifts_per_week))
            .as_constraint("TA should not work more than the required shifts per week"))

#
# HARD: never assign a TA to a shift they marked unavailable
#  
def ta_unavailable_shift(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should not be assigned to a shift that they are unavailable for """
    return (constraint_factory.for_each(ShiftAssignment)
            .filter(lambda assignment:
                assignment.assigned_ta is not None and
                assignment.shift in assignment.assigned_ta.unavailable
            )
            .penalize(HardMediumSoftScore.ONE_HARD, lambda assignment: 1)
            .as_constraint("TA assigned to unavailable shift"))

# Soft  Constraints
def ta_undesired_shift (constraint_factory: ConstraintFactory) -> Constraint:
    """ Penalize if a TA is assigned to a shift that they don't want to work on """
    return (
        constraint_factory.for_each(ShiftAssignment)
               .filter(lambda assignment:
                   assignment.assigned_ta is not None
                   and assignment.shift in assignment.assigned_ta.undesired
               )
               .join(ConstraintParameters)
               .penalize(HardMediumSoftScore.ONE_SOFT, lambda assignment, params: params.undesired_assignment_penalty)
               .as_constraint("TA assigned to >>undesired<< shift")
    )

def ta_desired_shift(factory: ConstraintFactory) -> Constraint:
    """Reward if a TA is assigned to a shift that they want to work on."""
    return (
        factory.for_each(ShiftAssignment)
               .filter(lambda assignment:
                   assignment.assigned_ta is not None
                   and assignment.shift in assignment.assigned_ta.desired
               )
               .join(ConstraintParameters)
               .reward(HardMediumSoftScore.ONE_SOFT, lambda assignment, params: params.desired_assignment_penalty)
               .indict_with(lambda assignment, params: [assignment])
               .as_constraint("TA assigned to *desired* shift")
    )



# Constraint provider dictionary for dynamic selection
constraints_provider_dict: Dict[str, Callable[[ConstraintFactory], List[Constraint]]] = {
    'default'       : define_constraints,
    'tabriz'        : define_constraints_tabriz_edition
}
# TODO: Add constraints for Continuous planning (windowed planning) -> tabriz edition

# NEEDS MODIFICATION BUT THIS IS HOW THIS SHOULD WORK
# def penalize_unassigned_visits(factory: ConstraintFactory) -> Constraint:
#     return (factory.for_each_including_unassigned(Visit)
#                    .filter(lambda visit: visit.vehicle is None)
#                    .penalize(HardMediumSoftScore.ONE_MEDIUM)
#                    .as_constraint("Unassigned Visit")
#     )
