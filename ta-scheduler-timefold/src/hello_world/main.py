from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory
from enum import Enum
from datetime import time, datetime, date
import logging
import argparse
from typing import List

from hello_world.domain import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import define_constraints


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('app')


def main():
    # parser = argparse.ArgumentParser(description='Solve a school timetable.')
    # parser.add_argument('--demo_data', dest='demo_data', action='store',
    #                     choices=['SMALL', 'LARGE', 'CUSTOM'],
    #                     default='SMALL',
    #                     help='Demo dataset to use')
    # args = parser.parse_args()

    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=Timetable,
            entity_class_list=[ShiftAssignment],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            ),
            termination_config=TerminationConfig(
                # The solver runs only for 5 seconds on this small dataset.
                # It's recommended to run for at least 5 minutes ("5m") otherwise.
                spent_limit=Duration(seconds=5)
            )
        ))

    # Load the problem
    # demo_data = getattr(DemoData, args.demo_data)
    problem = generate_demo_data()

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    print_timetable(solution)

def id_generator():
    current = 0
    while True:
        yield str(current)
        current += 1

def generate_demo_data(name: str = "CUSTOM") -> Timetable:

    DAY_START_TIME = time(14, 30)
    DAY_END_TIME   = time(17, 30)

    AFTERNOON_START_TIME =  time(18, 30)
    AFTERNOON_END_TIME   =  time(21, 30)

    ids = id_generator()
    shifts: List[Shift] = [
        Shift(next(ids),"L07", "Mon", DAY_START_TIME, DAY_END_TIME, 2),
        Shift(next(ids),"L08", "Mon", AFTERNOON_START_TIME, AFTERNOON_END_TIME, 3),
        Shift(next(ids),"L09", "Tue", DAY_START_TIME, DAY_END_TIME, 2),
        Shift(next(ids),"L10", "Tue", AFTERNOON_START_TIME, AFTERNOON_END_TIME, 3),
        ]
    
    ids = id_generator()
    course_tas: List[TA] = [
        TA(id = next(ids), 
           name = "M. Roghani", 
           required_shifts= 2, 
           unavailable= [shifts[1]], 
           desired    = [shifts[0]],
           undesired  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "D. Noori", 
           required_shifts= 3, 
           unavailable= [shifts[1]], 
           desired    = [shifts[0]],
           undesired  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "A. Gholami", 
           required_shifts= 2, 
           unavailable= [shifts[1]], 
           desired    = [shifts[0]],
           undesired  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "M. Jafari", 
           required_shifts= 3, 
           unavailable= [shifts[1]], 
           desired    = [shifts[0]],
           undesired  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "A. Athar", 
           required_shifts= 2, 
           unavailable= [shifts[1]], 
           desired    = [shifts[0]],
           undesired  = [shifts[2]]
        ),
    ]

    ids = id_generator()
    shift_assignments: List[ShiftAssignment] = []
    # Shifts for Monday (L07) need 2 TAs
    shift_index = 0
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))

    # Shifts for Monday (L08) need 3 TAs
    shift_index = 1
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))

    # Shifts for Tuesday (L09) need 2 TAs
    shift_index = 2
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))

    # Shifts for Tuesday (L10) need 3 TAs
    shift_index = 3
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))

    return Timetable(
                    id= name, 
                    shift_groups=shifts, 
                    tas=course_tas, 
                    shift_assignments= shift_assignments
            )


def print_timetable(time_table: Timetable) -> None:
    LOGGER.info("=== Starting to print the assignment matrix ===")

    column_width = 18
    tas = time_table.tas
    shift_groups = time_table.shift_groups
    shift_assignments = time_table.shift_assignments
    
    assignment_map = {
        (assignment.assigned_ta.name, assignment.shift.series, assignment.shift.start_time): assignment
        for assignment in shift_assignments
        if assignment.shift is not None and assignment.assigned_ta is not None
    }

    row_format = ("|{:<" + str(column_width) + "}") * (len(tas) + 1) + "|"
    sep_format = "+" + ((("-" * column_width) + "+") * (len(tas) + 1))

    LOGGER.info(sep_format)
    LOGGER.info(row_format.format('', *[ta.name for ta in tas]))
    LOGGER.info(sep_format)

    ids = id_generator()
    for shift_group in shift_groups:
        def get_row_shifts():
            for ta in tas:
                yield assignment_map.get((ta.name, shift_group.series, shift_group.start_time),
                                     ShiftAssignment(next(ids), shift=None, assigned_ta=None))

        row_shifts = [*get_row_shifts()]
        LOGGER.info(row_format.format(
            str(shift_group), 
            *[assignment.assigned_ta.name if assignment.assigned_ta is not None else " " 
              for assignment in row_shifts]
        ))
        # LOGGER.info(row_format.format('', *[lesson.teacher for lesson in row_shifts]))
        # LOGGER.info(row_format.format('', *[lesson.student_group for lesson in row_shifts]))
        LOGGER.info(sep_format)

    unassigned_shifts = [assignment for assignment in shift_assignments if assignment.shift is None or assignment.assigned_ta is None]
    if len(unassigned_shifts) > 0:
        LOGGER.info("")
        LOGGER.info("Unassigned shifts")
        for shift in unassigned_shifts:
            LOGGER.info(f'    {shift.shift} - {shift.assigned_ta}')

    LOGGER.info("=== Finished printing the assignment matrix ===")


if __name__ == '__main__':
    main()
    # generate_demo_data()
