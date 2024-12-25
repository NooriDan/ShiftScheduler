from timefold.solver.test import ConstraintVerifier # Used for writing testcases for the constraints

from employee_scheduling.domain import Shift, ShiftAssignment, TA, Timetable
import employee_scheduling.constraints as constraints 

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

constraint_verifier = ConstraintVerifier.build(constraints.define_constraints, Timetable, ShiftAssignment)

def get_time(datetime: datetime) -> time:
     return datetime.time()

def get_day_of_week(datetime: datetime) -> str:
     return datetime.strftime("%a")

# Mock Shifts
SHIFT1 = Shift(id="1", series="L01", 
               day_of_week="Wed", required_tas=1, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

SHIFT2 = Shift(id="2", series="L02", 
               day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

SHIFT3 = Shift(id="3", series="L03", 
               day_of_week="Wed", required_tas=1, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

SHIFT4 = Shift(id="4", series="L04", 
               day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

# Mock TAs
TA1 = TA(id="1", name="TA1", required_shifts=2, 
     unavailable =[SHIFT1, SHIFT4], 
     undesired   =[SHIFT2], 
     desired     =[SHIFT3],
     is_grad_student=True,
     favourite_partners=[])

TA2 = TA(id="2", name="TA2", required_shifts=2, 
     unavailable =[SHIFT1, SHIFT2], 
     undesired   =[SHIFT2], 
     desired     =[SHIFT3],
     is_grad_student=True,
     favourite_partners=[])

TA3 = TA(id="3", name="TA3", required_shifts=1, 
     unavailable =[SHIFT2, SHIFT4], 
     undesired   =[SHIFT2], 
     desired     =[SHIFT3],
     is_grad_student=True,
     favourite_partners=[])

TA4 = TA(id="4", name="TA4", required_shifts=1, 
     unavailable =[SHIFT3], 
     undesired   =[SHIFT1, SHIFT2], 
     desired     =[],
     is_grad_student=True,
     favourite_partners=[])

def test_required_tas():

     # Mock Shifts
     shift1 = Shift(id="1", series="L01", 
                    day_of_week="Wed", required_tas=1, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift2 = Shift(id="2", series="L02", 
                    day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift3 = Shift(id="3", series="L03", 
                    day_of_week="Wed", required_tas=1, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     shift4 = Shift(id="4", series="L04", 
                    day_of_week="Wed", required_tas=2, start_time=DAY_START_TIME.time(), end_time=DAY_END_TIME.time())

     # Mock TAs
     ta1 = TA(id="1", name="TA1", required_shifts=2, 
          unavailable =[shift1, shift4], 
          undesired   =[shift2], 
          desired     =[shift3],
          is_grad_student=True,
          favourite_partners=[])

     ta2 = TA(id="2", name="TA2", required_shifts=2, 
          unavailable =[shift1, shift2], 
          undesired   =[shift4], 
          desired     =[shift3],
          is_grad_student=True,
          favourite_partners=[])

     ta3 = TA(id="3", name="TA3", required_shifts=1, 
          unavailable =[shift2, shift4], 
          undesired   =[shift1], 
          desired     =[shift3],
          is_grad_student=True,
          favourite_partners=[])

     ta4 = TA(id="4", name="TA4", required_shifts=1, 
          unavailable =[shift3], 
          undesired   =[shift1, shift4], 
          desired     =[],
          is_grad_student=True,
          favourite_partners=[])
     # As
     #SHIFT1.assigned_tas = [ta1]
     assignment1 = ShiftAssignment(id="1", shift=shift1, assigned_ta=ta1)
     (constraint_verifier
      .verify_that(constraints.shift_must_have_required_tas_exactly).given(assignment1, ta1, shift1)
      .penalizes(0))
     
     assignment2 = ShiftAssignment(id="2", shift=shift2, assigned_ta=ta1)
     (constraint_verifier
      .verify_that(constraints.shift_must_have_required_tas_exactly).given(assignment2, ta1, shift2)
      .penalizes(1))
     
     assignment3 = ShiftAssignment(id="3", shift=shift2, assigned_ta=ta2)
     (constraint_verifier
      .verify_that(constraints.shift_must_have_required_tas_exactly).given(assignment3, ta2, shift2)
      .penalizes(0))
     
def test_shift_meets_ta_requirement():
     pass

def test_ta_meets_shift_requirment():
     pass

def test_respect_ta_unavailability():
     pass



if __name__ == "__main__":
     print("Running tests for constraints.py")
     test_required_tas()
