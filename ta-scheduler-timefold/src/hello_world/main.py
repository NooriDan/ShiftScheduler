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
    parser = argparse.ArgumentParser(description='Solve a school timetable.')
    parser.add_argument('--demo_data', dest='demo_data', action='store',
                        choices=['SMALL', 'LARGE', 'CUSTOM'],
                        default='SMALL',
                        help='Demo dataset to use')
    args = parser.parse_args()

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
    demo_data = getattr(DemoData, args.demo_data)
    problem = generate_demo_data(demo_data)

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
           unavailable_shifts= [shifts[1]], 
           desired_shifts    = [shifts[0]],
           undesired_shifts  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "D. Noori", 
           required_shifts= 3, 
           unavailable_shifts= [shifts[1]], 
           desired_shifts    = [shifts[0]],
           undesired_shifts  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "A. Gholami", 
           required_shifts= 2, 
           unavailable_shifts= [shifts[1]], 
           desired_shifts    = [shifts[0]],
           undesired_shifts  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "M. Jafari", 
           required_shifts= 3, 
           unavailable_shifts= [shifts[1]], 
           desired_shifts    = [shifts[0]],
           undesired_shifts  = [shifts[2]]
        ),
        TA(id = next(ids), 
           name = "A. Athar", 
           required_shifts= 2, 
           unavailable_shifts= [shifts[1]], 
           desired_shifts    = [shifts[0]],
           undesired_shifts  = [shifts[2]]
        ),
    ]

    ids = id_generator()
    shift_assignments: List[ShiftAssignment] = []
    # Shifts for Monday (L07) need 2 TAs
    shift_index = 0
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))

    # Shifts for Monday (L08) need 3 TAs
    shift_index = 1
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))

    # Shifts for Tuesday (L09) need 2 TAs
    shift_index = 2
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))

    # Shifts for Tuesday (L10) need 3 TAs
    shift_index = 3
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))
    shift_assignments.append(ShiftAssignment(id= next(ids), shift_group= shifts[shift_index], assigned_ta= None))

    return Timetable(
                    id= name, 
                    shift_groups=shifts, 
                    tas=course_tas, 
                    shift_assignments= shift_assignments
            )


def print_timetable(time_table: Timetable) -> None:
    LOGGER.info("")

    column_width = 18
    rooms = time_table.tas
    timeslots = time_table.shift_groups
    lessons = time_table.shift_assignments
    lesson_map = {
        (lesson.room.name, lesson.timeslot.day_of_week, lesson.timeslot.start_time): lesson
        for lesson in lessons
        if lesson.room is not None and lesson.timeslot is not None
    }
    row_format = ("|{:<" + str(column_width) + "}") * (len(rooms) + 1) + "|"
    sep_format = "+" + ((("-" * column_width) + "+") * (len(rooms) + 1))

    LOGGER.info(sep_format)
    LOGGER.info(row_format.format('', *[room.name for room in rooms]))
    LOGGER.info(sep_format)

    for timeslot in timeslots:
        def get_row_lessons():
            for room in rooms:
                yield lesson_map.get((room.name, timeslot.day_of_week, timeslot.start_time),
                                     ShiftAssignment('', '', '', ''))

        row_lessons = [*get_row_lessons()]
        LOGGER.info(row_format.format(str(timeslot), *[lesson.subject for lesson in row_lessons]))
        LOGGER.info(row_format.format('', *[lesson.teacher for lesson in row_lessons]))
        LOGGER.info(row_format.format('', *[lesson.student_group for lesson in row_lessons]))
        LOGGER.info(sep_format)

    unassigned_lessons = [lesson for lesson in lessons if lesson.room is None or lesson.timeslot is None]
    if len(unassigned_lessons) > 0:
        LOGGER.info("")
        LOGGER.info("Unassigned lessons")
        for lesson in unassigned_lessons:
            LOGGER.info(f'    {lesson.subject} - {lesson.teacher} - {lesson.student_group}')


if __name__ == '__main__':
    # main()
    generate_demo_data()
