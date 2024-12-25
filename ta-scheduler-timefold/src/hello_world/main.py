from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory

import logging
import argparse
from typing import List

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import define_constraints
from hello_world.demo_data   import generate_demo_data, id_generator

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
    problem = generate_demo_data()

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    print_timetable(solution)

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
