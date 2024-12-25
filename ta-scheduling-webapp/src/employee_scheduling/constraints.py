from timefold.solver.score import (constraint_provider, HardSoftScore,
                                   ConstraintFactory, Constraint, ConstraintCollectors, Joiners)
from .domain import Shift, TA, ShiftAssignment
    
@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return [
        shift_must_have_required_tas_exactly(constraint_factory),
        ta_duplicate_shift_assignment(constraint_factory),
        ta_meets_shift_requirement(constraint_factory),
        penalize_over_assignment(constraint_factory),
        ta_unavailable_shift(constraint_factory),
        ta_undesired_shift(constraint_factory),
        ta_desired_shift(constraint_factory)
        # at_least_one_grad_undergrad_ta(constraint_factory),
        # favourite_partners(constraint_factory),
    ]


def shift_must_have_required_tas_exactly(constraint_factory: ConstraintFactory) -> Constraint:
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

def ta_meets_shift_requirement(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should be assigned to at least their required number of shifts """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            .filter(lambda ta, count: count < ta.required_shifts)
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA must have required shifts"))
    
# System penalizes if a TA is doing more than their required number of shifts
def penalize_over_assignment(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should assigned to more than their required number of shifts should be penalized (Soft) """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.count())
            .filter(lambda ta, count: count > ta.required_shifts)
            .penalize(HardSoftScore.ONE_SOFT, lambda ta, count: count - ta.required_shifts)
            .as_constraint("TA should not to more than the required shifts"))
    
# TA doesnt work on unavailable days
def ta_unavailable_shift(constraint_factory: ConstraintFactory) -> Constraint:
    """ Each TA should not be assigned to a shift that they are unavailable for """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.to_list(lambda assignment: assignment.shift))
            .filter(lambda ta, shifts: any(shift in ta.unavailable for shift in shifts))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("TA unavailable"))

# TA preferably doesn't work on undesired days
def ta_undesired_shift (constraint_factory: ConstraintFactory) -> Constraint:
    """ Penalize if a TA is assigned to a shift that they don't want to work on """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.to_list(lambda assignment: assignment.shift))
            .filter(lambda ta, shifts: any(shift in ta.undesired for shift in shifts))
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("TA undesired"))

# TA preferably works on undesired days
def ta_desired_shift (constraint_factory: ConstraintFactory) -> Constraint:
    """ Reward if a TA is assigned to a shift that they want to work on """
    return (constraint_factory
            .for_each(ShiftAssignment)
            .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.to_list(lambda assignment: assignment.shift))
            .filter(lambda ta, shifts: any(shift in ta.desired for shift in shifts))
            .reward(HardSoftScore.ONE_SOFT)
            .as_constraint("TA desired"))



# # TA's favourite partners should be assigned to the same shift
# def favourite_partners(constraint_factory: ConstraintFactory) -> Constraint:
#     return (constraint_factory
#             .for_each(ShiftAssignment)
#             .join(ConstraintParameters)
#             .filter(lambda shift_assignment, constraint_parameters: constraint_parameters.allow_favourite_partners)
#             # group by shift and collect the TAs assigned to that shift
#             .group_by(lambda shift_assignment: shift_assignment, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
#             # filter out shifts where no TA has a favourite partner assigned to the same shift
#             .filter(lambda shift_assignment, tas: any(set(ta.favourite_partners).isdisjoint(tas) for ta in tas))
#             .penalize(HardSoftScore.ONE_SOFT)
#             .as_constraint("Favourite partners"))
    
# # Grad and undergrad TAs should be assigned to the same shift
# def at_least_one_grad_undergrad_ta(constraint_factory: ConstraintFactory) -> Constraint:
#     return (constraint_factory
#             .for_each(ShiftAssignment)
#             .join(ConstraintParameters)
#             .filter(lambda shift_assignment, constraint_parameters: constraint_parameters.mandate_grad_undergrad)
#             # group by shift and collect TAs assigned to that shift
#             .group_by(lambda shift_assignment: shift_assignment, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
#             # filter out shifts where there is no grad and undergrad TA assigned to the same shift
#             .filter(lambda shift_assignment, tas: not (any(ta.is_grad_student for ta in tas) and any(not ta.is_grad_student for ta in tas)))
#             .penalize(HardSoftScore.ONE_HARD)
#             .as_constraint("At least one grad and undergrad TA"))


# from timefold.solver.score import (constraint_provider, HardSoftScore,
#                                    ConstraintFactory, Constraint, ConstraintCollectors, Joiners)
# from .domain import Shift, ConstraintParameters, TA


    
# @constraint_provider
# def define_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
#     return [
#         required_tas(constraint_factory),
#         ta_must_have_required_shifts(constraint_factory),
#         ta_should_not_have_more_than_required_shifts(constraint_factory),
#         ta_availability(constraint_factory),
#         at_least_one_grad_undergrad_ta(constraint_factory),
#         favourite_partners(constraint_factory),
#     ]

# # TA's availability must match the shift they are assigned to
# def ta_availability(constraint_factory: ConstraintFactory) -> Constraint:
#     return (constraint_factory
#             .for_each(TA)
#             # filter out shifts that the TA is not available for
#             .join(constraint_factory.for_each(Shift), Joiners.filtering(lambda ta, shift: ta in shift.assigned_tas))
#             .filter(lambda ta, shift: ta..contains(shift))
#             .penalize(HardSoftScore.ONE_HARD)
#             .as_constraint("TA availability"))

# # TA's favourite partners should be assigned to the same shift
# def favourite_partners(constraint_factory: ConstraintFactory) -> Constraint:
#     return (constraint_factory
#             .for_each(TA)
#             .join(ConstraintParameters)
#             .filter(lambda shift_assignment, constraint_parameters: constraint_parameters.allow_favourite_partners)
#             # group by shift and collect the TAs assigned to that shift
#             .group_by(lambda shift_assignment: shift_assignment, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
#             # filter out shifts where no TA has a favourite partner assigned to the same shift
#             .filter(lambda shift_assignment, tas: any(set(ta.favourite_partners).isdisjoint(tas) for ta in tas))
#             .penalize(HardSoftScore.ONE_SOFT)
#             .as_constraint("Favourite partners"))
    
# # Grad and undergrad TAs should be assigned to the same shift
# def at_least_one_grad_undergrad_ta(constraint_factory: ConstraintFactory) -> Constraint:
#     return (constraint_factory
#             .for_each(TA)
#             .join(ConstraintParameters)
#             .filter(lambda shift_assignment, constraint_parameters: constraint_parameters.mandate_grad_undergrad)
#             # group by shift and collect TAs assigned to that shift
#             .group_by(lambda shift_assignment: shift_assignment, ConstraintCollectors.to_list(lambda assignment: assignment.assigned_ta))
#             # filter out shifts where there is no grad and undergrad TA assigned to the same shift
#             .filter(lambda shift_assignment, tas: not (any(ta.is_grad_student for ta in tas) and any(not ta.is_grad_student for ta in tas)))
#             .penalize(HardSoftScore.ONE_HARD)
#             .as_constraint("At least one grad and undergrad TA"))