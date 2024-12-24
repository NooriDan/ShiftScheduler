from timefold.solver.test import ConstraintVerifier # Used for writing testcases for the constraints

from employee_scheduling.domain import *
from employee_scheduling.constraints import *

from datetime import date, datetime, time, timedelta

DAY_1 = date(2021, 2, 1)
DAY_2 = date(2021, 2, 2)
DAY_3 = date(2021, 2, 3)
DAY_4 = date(2021, 2, 4)
DAY_5 = date(2021, 2, 5)

DAY_START_TIME = datetime.combine(DAY_1, time(9, 0))
DAY_END_TIME = datetime.combine(DAY_1, time(17, 0))

AFTERNOON_START_TIME = datetime.combine(DAY_1, time(13, 0))
AFTERNOON_END_TIME = datetime.combine(DAY_1, time(21, 0))

constraint_verifier = ConstraintVerifier.build(define_constraints, Timetable, ShiftAssignment)

# Mock Shifts
shift1 = Shift(name="L01", required_tas=1)
shift2 = Shift(name="L02", required_tas=2)
shift3 = Shift(name="L03", required_tas=1)
shift4 = Shift(id="4", series="L04", day_of_week="Wed", start_time=)

# Mock TAs
ta1 = TA(name="TA1", required_shifts=2, unavailable=[shift1], undesired=[shift2], desired=[shift3])
ta2 = TA(name="TA2", required_shifts=3, unavailable=[shift2], undesired=[shift1], desired=[shift4])

# Mock Shift Assignments
assignments = [
    ShiftAssignment(shift=shift1, assigned_tas=[ta1]),  # Missing required TAs
    ShiftAssignment(shift=shift2, assigned_tas=[ta2]),  # Matches required TAs
    ShiftAssignment(shift=shift3, assigned_tas=[ta1, ta2])  # Extra TA assigned
]


def test_required_skill():
      ta1 = TA(name="TA1", required_shifts=2, unavailable=["Shift1"], undesired=["Shift2"], desired=["Shift3"])
      pass

def test_shift_meets_ta_requirement():
     pass

def test_ta_meets_shift_requirment():
     pass

def test_respect_ta_unavailability():
     pass

