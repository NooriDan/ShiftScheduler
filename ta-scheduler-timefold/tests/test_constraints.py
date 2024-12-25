from timefold.solver.test import ConstraintVerifier # Used for writing testcases for the constraints
from timefold.solver.score import HardSoftScore

from hello_world.domain import Shift, ShiftAssignment, TA, Timetable
import hello_world.constraints as constraints 


from datetime import date, datetime, time, timedelta
from dataclasses import dataclass

import pytest

DAY_1 = date(2021, 2, 1)
DAY_2 = date(2021, 2, 2)
DAY_3 = date(2021, 2, 3)
DAY_4 = date(2021, 2, 4)
DAY_5 = date(2021, 2, 5)

DAY_START_TIME = datetime.combine(DAY_1, time(9, 0))
DAY_END_TIME = datetime.combine(DAY_1, time(17, 0))

AFTERNOON_START_TIME = datetime.combine(DAY_1, time(13, 0))
AFTERNOON_END_TIME = datetime.combine(DAY_1, time(21, 0))

def get_time(datetime: datetime) -> time:
     return datetime.time()

def get_day_of_week(datetime: datetime) -> str:
     return datetime.strftime("%a")

@dataclass
class TestData:

     # Mock Shifts
     SHIFT1 = Shift(id="1", series="L01", 
                    day_of_week="Mon", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     SHIFT2 = Shift(id="2", series="L02", 
                    day_of_week="Tue", required_tas=3, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     SHIFT3 = Shift(id="3", series="L03", 
                    day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     SHIFT4 = Shift(id="4", series="L04", 
                    day_of_week="Thu", required_tas=3, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     # Mock TAs
     TA1 = TA(id="1", name="TA1", required_shifts=2, 
          unavailable =[SHIFT1, SHIFT4], 
          undesired   =[SHIFT2], 
          desired     =[SHIFT3],
          is_grad_student=True)

     TA2 = TA(id="2", name="TA2", required_shifts=2, 
          unavailable =[SHIFT1, SHIFT2], 
          undesired   =[SHIFT2], 
          desired     =[SHIFT3],
          is_grad_student=True)

     TA3 = TA(id="3", name="TA3", required_shifts=1, 
          unavailable =[SHIFT2, SHIFT4], 
          undesired   =[SHIFT2], 
          desired     =[SHIFT3],
          is_grad_student=True)

     TA4 = TA(id="4", name="TA4", required_shifts=1, 
          unavailable =[SHIFT3], 
          undesired   =[SHIFT1, SHIFT2], 
          desired     =[],
          is_grad_student=True)

constraint_verifier = ConstraintVerifier.build(constraints.define_constraints, Timetable, ShiftAssignment)

def test_shift_meets_ta_requirement():

     # Mock Shifts
     shift1 = Shift(id="1", series="L01", 
                    day_of_week="Wed", required_tas=1, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift2 = Shift(id="2", series="L02", 
                    day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift3 = Shift(id="3", series="L03", 
                    day_of_week="Wed", required_tas=3, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift4 = Shift(id="4", series="L04", 
                    day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     # Mock TAs
     ta1 = TA(id="1", name="TA1", required_shifts=2, 
          unavailable =[shift1, shift4], 
          undesired   =[shift2], 
          desired     =[shift3],
          is_grad_student=True)

     ta2 = TA(id="2", name="TA2", required_shifts=2, 
          unavailable =[shift1, shift2], 
          undesired   =[shift4], 
          desired     =[shift3],
          is_grad_student=True)

     ta3 = TA(id="3", name="TA3", required_shifts=1, 
          unavailable =[shift2, shift4], 
          undesired   =[shift1], 
          desired     =[shift3],
          is_grad_student=True)

     ta4 = TA(id="4", name="TA4", required_shifts=1, 
          unavailable =[shift3], 
          undesired   =[shift1, shift4], 
          desired     =[],
          is_grad_student=True)
     
     timetable = Timetable(id="DUMMY", shifts=[shift1, shift2, shift3, shift4], tas=[ta1, ta2, ta3, ta4], shift_assignments=[])

     # Shift 1 (required_tas = 1)
     timetable.shift_assignments.append(ShiftAssignment(id="1", shift=shift1, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes(0))
     
     # Shift 2 (required_tas = 2)
     timetable.shift_assignments.append(ShiftAssignment(id="2", shift=shift2, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="3", shift=shift2, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes(0))
     
     # Shift 3 (required_tas = 3)
     timetable.shift_assignments.append(ShiftAssignment(id="4", shift=shift3, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="5", shift=shift3, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="6", shift=shift3, assigned_ta=ta3))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes(0))
     
     # Shift 4 (required_tas = 2)
     timetable.shift_assignments.append(ShiftAssignment(id="7", shift=shift4, assigned_ta=ta3))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="8", shift=shift4, assigned_ta=ta4))
     (constraint_verifier
      .verify_that(constraints.shift_meet_ta_required_exactly)
      .given_solution(timetable)
      .penalizes(0))

def test_ta_duplicate_shift_assignment():

     # Mock Shifts
     shift1 = Shift(id="1", series="L01", 
                    day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift2 = Shift(id="2", series="L02", 
                    day_of_week="Wed", required_tas=3, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())
     
     ta1 = TA(id="1", name="TA1", required_shifts=2, 
          unavailable =[], 
          undesired   =[shift1], 
          desired     =[shift2],
          is_grad_student=True)
     
     ta2 = TA(id="2", name="TA2", required_shifts=2,
          unavailable =[], 
          undesired   =[shift2], 
          desired     =[shift1],
          is_grad_student=True)
     
     # (1) Duplicate shift assignments for the same TA
     timetable = Timetable(id="DUMMY",  shifts=[shift1, shift2], tas=[ta1, ta2], shift_assignments=[])
     timetable.shift_assignments.append(ShiftAssignment(id="1", shift=shift1, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.ta_duplicate_shift_assignment)
      .given_solution(timetable)
      .penalizes(0))
     
     timetable.shift_assignments.append(ShiftAssignment(id="2", shift=shift1, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.ta_duplicate_shift_assignment)
      .given_solution(timetable)
      .penalizes(1))
     
     # timetable.shift_assignments = [] # Reset shift assignments
     timetable.shift_assignments.append(ShiftAssignment(id="3", shift=shift2, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.ta_duplicate_shift_assignment)
      .given_solution(timetable)
      .penalizes(1))
     
     timetable.shift_assignments.append(ShiftAssignment(id="4", shift=shift2, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.ta_duplicate_shift_assignment)
      .given_solution(timetable)
      .penalizes(1))
     
     timetable.shift_assignments.append(ShiftAssignment(id="5", shift=shift2, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.ta_duplicate_shift_assignment)
      .given_solution(timetable)
      .penalizes(2))

def test_ta_meets_shift_requirment():
     ta1 = TestData.TA1 # TA1 has required_shifts = 2
     ta2 = TestData.TA2 # TA2 has required_shifts = 2
     ta3 = TestData.TA3 # TA3 has required_shifts = 1

     shift1 = TestData.SHIFT1 # SHIFT1 has required_tas = 2
     shift2 = TestData.SHIFT2 # SHIFT2 has required_tas = 3
     shift3 = TestData.SHIFT3 # SHIFT3 has required_tas = 2

     timetable = Timetable(id="DUMMY", shifts=[shift1, shift2, shift3], tas=[ta1, ta2, ta3], shift_assignments=[])

     
     timetable.shift_assignments.append(ShiftAssignment(id="1", shift=shift1, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.ta_meets_shift_requirement)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="2", shift=shift1, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.ta_meets_shift_requirement)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="3", shift=shift2, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.ta_meets_shift_requirement)
      .given_solution(timetable)
      .penalizes())
     
     timetable.shift_assignments.append(ShiftAssignment(id="4", shift=shift2, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.ta_meets_shift_requirement)
      .given_solution(timetable)
      .penalizes(0))
     
     # TA3 has required_shifts = 1 (TA3 has only 1 shift assignment)
     timetable.shift_assignments.append(ShiftAssignment(id="5", shift=shift2, assigned_ta=ta3))
     (constraint_verifier
      .verify_that(constraints.ta_meets_shift_requirement)
      .given_solution(timetable)
      .penalizes(0))
     
     # Does not penalize if TA is assigned to more than their required number of shifts
     timetable.shift_assignments.append(ShiftAssignment(id="6", shift=shift3, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.ta_meets_shift_requirement)
      .given_solution(timetable)
      .penalizes(0))

def test_penalize_over_assignment():
     ta1 = TestData.TA1 # TA1 has required_shifts = 2
     ta2 = TestData.TA2 # TA2 has required_shifts = 2
     ta3 = TestData.TA3 # TA3 has required_shifts = 1

     shift1 = TestData.SHIFT1 # SHIFT1 has required_tas = 2
     shift2 = TestData.SHIFT2 # SHIFT2 has required_tas = 3
     shift3 = TestData.SHIFT3 # SHIFT3 has required_tas = 2

     timetable = Timetable(id="DUMMY", shifts=[shift1, shift2, shift3], tas=[ta1, ta2, ta3], shift_assignments=[])

     # TA1 has 2 shift assignments
     timetable.shift_assignments.append(ShiftAssignment(id="1", shift=shift1, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.penalize_over_assignment)
      .given_solution(timetable)
      .penalizes(0))
     
     timetable.shift_assignments.append(ShiftAssignment(id="2", shift=shift2, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.penalize_over_assignment)
      .given_solution(timetable)
      .penalizes(0))
     
     # TA2 has 2 shift assignments (no penalty)
     timetable.shift_assignments.append(ShiftAssignment(id="3", shift=shift1, assigned_ta=ta2))
     (constraint_verifier
      .verify_that(constraints.penalize_over_assignment)
      .given_solution(timetable)
      .penalizes(0))
     
     
     # TA1 has 3 shift assignment
     timetable.shift_assignments.append(ShiftAssignment(id="4", shift=shift3, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.penalize_over_assignment)
      .given_solution(timetable)
      .penalizes())
     
     # TA1 has 4 shift assignment
     timetable.shift_assignments.append(ShiftAssignment(id="5", shift=shift3, assigned_ta=ta1))
     (constraint_verifier
      .verify_that(constraints.penalize_over_assignment)
      .given_solution(timetable)
      .penalizes())
     
def test_ta_unavailable_shift():
     pytest.skip("Incomplete: Skipping this test!")

def test_ta_undesired_shift():
     pytest.skip("Incomplete: Skipping this test!")

def test_ta_desired_shift():
     pytest.skip("Incomplete: Skipping this test!")


if __name__ == "__main__":
     print("Running tests for constraints.py")
     test_shift_meets_ta_requirement()
     test_ta_duplicate_shift_assignment()
     test_ta_meets_shift_requirment()
     test_penalize_over_assignment()
     test_ta_unavailable_shift()
     test_ta_undesired_shift()
     test_ta_desired_shift()
     print("All tests ran!")
