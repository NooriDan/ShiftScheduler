from timefold.solver.test import ConstraintVerifier # Used for writing testcases for the constraints

from employee_scheduling.domain import *
from employee_scheduling.constraints import *

from datetime import date, datetime, time, timedelta

DAY_1 = date(2021, 2, 1)
DAY_3 = date(2021, 2, 3)
DAY_START_TIME = datetime.combine(DAY_1, time(9, 0))
DAY_END_TIME = datetime.combine(DAY_1, time(17, 0))
AFTERNOON_START_TIME = datetime.combine(DAY_1, time(13, 0))
AFTERNOON_END_TIME = datetime.combine(DAY_1, time(21, 0))

constraint_verifier = ConstraintVerifier.build(define_constraints, Timetable, ShiftAssignment)


def test_required_skill():
    employee = Employee(name="Amy")
    (constraint_verifier.verify_that(required_skill)
    .given(employee,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee))
    .penalizes(1))
    
    employee = Employee(name="Beth", skills={"Skill"})
    (constraint_verifier.verify_that(required_skill)
    .given(employee,
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee))
    .penalizes(0))


# Mock TAs
ta1 = TA(name="TA1", required_shifts=2, unavailable=["Shift1"], undesired=["Shift2"], desired=["Shift3"])
ta2 = TA(name="TA2", required_shifts=3, unavailable=["Shift2"], undesired=["Shift1"], desired=["Shift4"])

# Mock Shifts
shift1 = Shift(name="Shift1", required_tas=1)
shift2 = Shift(name="Shift2", required_tas=2)
shift3 = Shift(name="Shift3", required_tas=1)

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

