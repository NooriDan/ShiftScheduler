import logging
import os
import datetime

from .domain import ShiftAssignment, Timetable

# Configure the logging
LOG_FILE = f"logs/timefold_assignment_matrix_{datetime.datetime.now().strftime('%y_%m_%d_%s')}.log"

# Create the logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),  # Save logs to a file, overwrite each run
        logging.StreamHandler()  # Also display logs in the console
    ]
)
LOGGER = logging.getLogger('app')

def id_generator():
    current = 0
    while True:
        yield str(current)
        current += 1

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
    LOGGER.info(row_format.format('', *[f"{ta.name} (ID: {ta.id})" for ta in tas]))
    LOGGER.info(row_format.format('', *[f"(requires: {ta.required_shifts})" for ta in tas]))

    LOGGER.info(sep_format)

    ids = id_generator()
    for shift_group in shift_groups:
        def get_row_shifts():
            for ta in tas:
                yield assignment_map.get((ta.name, shift_group.series, shift_group.start_time),
                                     ShiftAssignment(next(ids), shift=None, assigned_ta=None))

        # Logging the shift group
        row_shifts = [*get_row_shifts()]
        LOGGER.info(row_format.format(
            str(shift_group), 
            *[assignment.assigned_ta.name if assignment.assigned_ta is not None else " " 
              for assignment in row_shifts]
        ))

        LOGGER.info(row_format.format( 
            f"requires {shift_group.required_tas}",
            *[assignment.assigned_ta.get_status_for_shift(shift_group) if assignment.assigned_ta is not None else " " 
              for assignment in row_shifts]
        ))

        LOGGER.info(sep_format)

    unassigned_shifts = [assignment for assignment in shift_assignments if assignment.shift is None or assignment.assigned_ta is None]
    if len(unassigned_shifts) > 0:
        LOGGER.info("")
        LOGGER.info("Unassigned shifts")
        for shift in unassigned_shifts:
            LOGGER.info(f'{shift.shift} - {shift.assigned_ta}')

    LOGGER.info("=== Finished printing the assignment matrix ===")

