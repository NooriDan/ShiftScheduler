from abc        import ABC, abstractmethod

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

# ============================
# Constraint provider functions
# ============================
@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return TimetableConstraintGenBasic(constraint_factory).create_constraints()

@constraint_provider
def define_constraints_tabriz_edition(constraint_factory: ConstraintFactory) -> list[Constraint]:
    return TimetableConstraintGenTabrizEdition(constraint_factory=constraint_factory).create_constraints()

# ============================
# Constraint provider dictionary for dynamic selection
# ============================
constraints_provider_dict: Dict[str, Callable[[ConstraintFactory], List[Constraint]]] = {
    'default'       : define_constraints,
    'tabriz'        : define_constraints_tabriz_edition
}

# ============================
# Classs Definition
# ============================
class TimetableConstraintGenBase(ABC):
    """[Abstract class] Timetable constraint generator class base. Extend the create_constraints to modify behaviour"""
    def __init__(self, constraint_factory: ConstraintFactory):
        self.constraint_factory = constraint_factory

    @abstractmethod
    def create_constraints(self) -> List[Constraint]:
        """Create a list of constraints using the provided ConstraintFactory."""
        pass

    # Optional: You can add more methods or overwrite the existing ones to customize the constraint creation process
    # Hard Constraints
    def penalize_shift_not_meeting_ta_required_exactly(self) -> Constraint:
        """ Each shift should have exactly the required number of TAs """
        return (self.constraint_factory
                .for_each(ShiftAssignment)
                # filter out shifts that don't have the required amount of TAs
                .group_by(lambda shift_assignment: shift_assignment.shift, ConstraintCollectors.count())
                .filter(lambda shift, count: count != shift.required_tas)
                .penalize(HardMediumSoftScore.ONE_HARD, lambda shift, count: abs(shift.required_tas - count))
                .as_constraint("Shift does not meet required TAs exactly"))

    def penalize_ta_not_meeting_shift_requirement_over_the_semester(self) -> Constraint:
        """ Each TA MUST be assigned to exactly their required number of shifts over the whole semester (schedulign window)"""
        factory = self.constraint_factory
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
                    .filter(lambda ta, shift_count:  shift_count != ta.required_shifts_per_semester)
                    .penalize(HardMediumSoftScore.ONE_HARD, lambda ta, shift_count: abs(shift_count - ta.required_shifts_per_semester))
                    .as_constraint("TA MUST work EXACTLY their required shifts over the SEMESTER")
                )

    def penalize_duplicate_shift_assignment(self) -> Constraint:
        """ Each TA should be assigned to a shift only once """
        return (self.constraint_factory
                .for_each(ShiftAssignment)
                .group_by(lambda shift_assignment: shift_assignment.assigned_ta, ConstraintCollectors.to_list(lambda assignment: assignment.shift.id))
                .filter(lambda ta, shift_ids: len(shift_ids) > len(set(shift_ids)))
                .penalize(HardMediumSoftScore.ONE_HARD, lambda ta, shift_id: 1 )
                .as_constraint("TA duplicate shift assignment"))
    
    # Medium Constraints
    def penalize_ta_not_meeting_shift_requirement_per_week(self) -> Constraint:
        """ [legacy - assumes weekly scheduling] Each TA should be assigned to at least their required number of shifts """
        factory = self.constraint_factory
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
    
    def penalize_ta_over_assignment_per_week(self) -> Constraint:
        """
        Medium‐soft penalty if a TA works more than max_shifts_per_week in any given week.
        """
        cf = self.constraint_factory
        return (
            cf.for_each(ShiftAssignment)
            # ignore unassigned slots entirely
            .filter(lambda asg: asg.assigned_ta is not None)
            # group by the pair (TA, week_id) and count assignments
            .group_by(
                lambda asg: (asg.assigned_ta, asg.shift.week_id),
                ConstraintCollectors.count()
            )
            # now we have ( (ta, week), count )
            .filter(lambda ta_week, count: count > ta_week[0].max_shifts_per_week)
            # penalize by the shortfall (always >= 1 because of the filter)
            .penalize(
                HardMediumSoftScore.ONE_MEDIUM,
                lambda ta_week, count: count - ta_week[0].max_shifts_per_week
            )
            .as_constraint("TA works MORE than the required shifts per week")
        )
    
    def penalize_ta_under_assignment_per_week(self) -> Constraint:
        """
        Medium‐soft penalty if a TA works less than max_shifts_per_week in any given week.
        """
        cf = self.constraint_factory
        return (
            cf.for_each(ShiftAssignment)
            # ignore unassigned slots entirely
            .filter(lambda asg: asg.assigned_ta is not None)
            # group by the pair (TA, week_id) and count assignments
            .group_by(
                lambda asg: (asg.assigned_ta, asg.shift.week_id),
                ConstraintCollectors.count()
            )
            # now we have ( (ta, week), count )
            .filter(lambda ta_week, count: count < ta_week[0].min_shifts_per_week)
            # penalize by the shortfall (always >= 1 because of the filter)
            .penalize(
                HardMediumSoftScore.ONE_MEDIUM,
                lambda ta_week, count: ta_week[0].min_shifts_per_week - count
            )
            .as_constraint("TA works LESS than the required shifts per week")
        )
    
    # HARD: never assign a TA to a shift they marked unavailable
    def penalize_ta_assignment_to_unavailable_shift(self) -> Constraint:
        """ Each TA should not be assigned to a shift that they are unavailable for """
        constraint_factory = self.constraint_factory
        
        return (constraint_factory.for_each(ShiftAssignment)
                .filter(lambda assignment:
                    assignment.is_assigned_a_ta() and
                    assignment.is_unavailable()
                )
                .penalize(HardMediumSoftScore.ONE_HARD, lambda assignment: 1)
                .as_constraint("TA assigned to unavailable shift"))

    # Soft  Constraints
    def penalize_ta_assignment_to_undesired_shift (self) -> Constraint:
        """ Penalize if a TA is assigned to a shift that they don't want to work on """
        constraint_factory = self.constraint_factory
        return (
            constraint_factory.for_each(ShiftAssignment)
                .filter(lambda assignment:
                    assignment.is_assigned_a_ta()
                    and assignment.is_undesired()
                )
                .join(ConstraintParameters)
                .penalize(HardMediumSoftScore.ONE_SOFT, lambda assignment, params: params.undesired_assignment_penalty)
                .as_constraint("TA assigned to >>undesired<< shift")
        )

    def reward_ta_assignment_to_desired_shift(self) -> Constraint:
        """Reward if a TA is assigned to a shift that they want to work on."""
        factory = self.constraint_factory
        return (
            factory.for_each(ShiftAssignment)
                .filter(lambda assignment:
                    assignment.assigned_ta is not None
                    and assignment.is_desired()
                )
                .join(ConstraintParameters)
                .reward(HardMediumSoftScore.ONE_SOFT, lambda assignment, params: params.desired_assignment_reward)
                .indict_with(lambda assignment, params: [assignment])
                .as_constraint("TA assigned to *desired* shift")
        )

class TimetableConstraintGenBasic(TimetableConstraintGenBase):
    # Overwriting the mandatory parent class
    def create_constraints(self) -> List[Constraint]:
        """Create a list of constraints using the provided ConstraintFactory."""
        return [
        # Hard constraints
        self.penalize_shift_not_meeting_ta_required_exactly(),
        self.penalize_duplicate_shift_assignment(),
        self.penalize_ta_assignment_to_unavailable_shift(),
        self.penalize_ta_not_meeting_shift_requirement_over_the_semester(),

        # Medium Constraints
        # self.penalize_ta_not_meeting_shift_requirement_per_week(),
        self.penalize_ta_over_assignment_per_week(),  
        self.penalize_ta_under_assignment_per_week(),  

        # Soft constraints
        self.penalize_ta_assignment_to_undesired_shift(),
        self.reward_ta_assignment_to_desired_shift(), 
        ]

    # Optional: You can add more methods to customize the constraint creation process

class TimetableConstraintGenTabrizEdition(TimetableConstraintGenBasic):
    # Overwriting the mandatory parent class
    def create_constraints(self) -> List[Constraint]:
        """Create a list of constraints using the provided ConstraintFactory."""
        constraints = super().create_constraints()

        addition: List[Constraint] = [
        # Add the following
         # Soft (1) constraints
            # TODO
            # self.reward_assignment_to_consecutive_shifts(),
        ]
        
        constraints = constraints + addition

        return constraints
    
    # Optional: You can add more methods to customize the constraint creation process
    

# TODO: Add constraints for Continuous planning (windowed planning) -> tabriz edition

# NEEDS MODIFICATION BUT THIS IS HOW THIS SHOULD WORK
# def penalize_unassigned_visits(factory: ConstraintFactory) -> Constraint:
#     return (factory.for_each_including_unassigned(Visit)
#                    .filter(lambda visit: visit.vehicle is None)
#                    .penalize(HardMediumSoftScore.ONE_MEDIUM)
#                    .as_constraint("Unassigned Visit")
#     )
