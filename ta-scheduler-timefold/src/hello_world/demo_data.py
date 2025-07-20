import random
from datetime import time
from typing import List

# Custom Imports
from hello_world.domain import Shift, TA, ShiftAssignment, Timetable
from hello_world.utils import id_generator

DAY_START_TIME = time(14, 30)
DAY_END_TIME   = time(17, 30)

AFTERNOON_START_TIME =  time(18, 30)
AFTERNOON_END_TIME   =  time(21, 30)

def demo_data_weekly_scheduling(name: str) -> Timetable:
    
   ids = id_generator()
   shifts: List[Shift] = [
      Shift(id=next(ids),series="L07", day_of_week="Mon", start_time=DAY_START_TIME, end_time=DAY_END_TIME, required_tas=2, week_id= 1),
      Shift(id=next(ids),series="L08", day_of_week="Mon", start_time=AFTERNOON_START_TIME, end_time=AFTERNOON_END_TIME, required_tas=3, week_id= 1),
      Shift(id=next(ids),series="L09", day_of_week="Tue", start_time=DAY_START_TIME, end_time=DAY_END_TIME, required_tas=2, week_id= 1),
      Shift(id=next(ids),series="L10", day_of_week="Tue", start_time=AFTERNOON_START_TIME, end_time=AFTERNOON_END_TIME, required_tas=1, week_id= 1),
      Shift(id=next(ids),series="L11", day_of_week="Thu", start_time=AFTERNOON_START_TIME, end_time=AFTERNOON_END_TIME, required_tas=2, week_id= 1),
      ]
   
   
   ids = id_generator()
   course_tas: List[TA] = [
      TA(id = next(ids), 
         name = "M. Roghani", 
         min_shifts_per_week= 3, 
         max_shifts_per_week= 3,
         required_shifts_per_semester= 10,
         skill_level= 3,
         unavailable= [shifts[4]], 
         desired    = [shifts[0], shifts[1], shifts[2]],
         undesired  = [shifts[3]]
      ),
      TA(id = next(ids), 
         name = "D. Noori", 
         min_shifts_per_week= 2, 
         max_shifts_per_week= 2,
         required_shifts_per_semester= 8,
         skill_level= 2,
         unavailable= [shifts[0]], 
         desired    = [],
         undesired  = [shifts[2]]
      ),
      TA(id = next(ids), 
         name = "A. Gholami", 
         min_shifts_per_week= 1, 
         max_shifts_per_week= 1,
         required_shifts_per_semester= 5,
         skill_level= 1,
         unavailable= [shifts[1]], 
         desired    = [shifts[0]],
         undesired  = [shifts[2]]
      ),
      TA(id = next(ids), 
         name = "M. Jafari", 
         min_shifts_per_week= 2,
         max_shifts_per_week= 2,
         required_shifts_per_semester= 6,
         skill_level= 2,
         unavailable= [shifts[3]], 
         desired    = [shifts[1]],
         undesired  = [shifts[2]]
      ),
      TA(id = next(ids), 
         name = "A. Athar", 
         min_shifts_per_week= 2,
         max_shifts_per_week= 2,
         required_shifts_per_semester= 6,
         skill_level= 2,
         unavailable= [], 
         desired    = [shifts[0]],
         undesired  = [shifts[2], shifts[1], shifts[3], shifts[4]]
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

   # Shifts for Tuesday (L10) need 1 TAs
   shift_index = 3
   shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))

   # Shifts for Thursday (L11) need 2 TAs
   shift_index = 4
   shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))
   shift_assignments.append(ShiftAssignment(id= next(ids), shift= shifts[shift_index], assigned_ta= None))

   return Timetable(
                  id= name, 
                  shifts=shifts, 
                  tas=course_tas, 
                  shift_assignments= shift_assignments
         )

def demo_data_weekly_scheduling_random(name: str) -> Timetable:
    ids = id_generator()
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    shift_series_prefix = "L"
    num_shifts = random.randint(5, 8)  # number of shifts
    
    # Generate random shifts
    shifts: List[Shift] = []
    for _ in range(num_shifts):
        shift_id = next(ids)
        day = random.choice(days)
        series = f"{shift_series_prefix}{random.randint(1,20):02d}"
        start_time = random.choice([DAY_START_TIME, AFTERNOON_START_TIME])
        end_time = DAY_END_TIME if start_time == DAY_START_TIME else AFTERNOON_END_TIME
        required_tas = random.randint(1, 4)
        shifts.append(Shift(
            id=shift_id,
            series=series,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            required_tas=required_tas,
            week_id=1
        ))
    
    # Generate random TAs
    ids = id_generator()
    names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"]
    num_tas = random.randint(5, 8)
    course_tas: List[TA] = []
    
    for _ in range(num_tas):
        ta_id = next(ids)
        name_ta = random.choice(names)
        min_shifts = random.randint(1, 2)
        max_shifts = min_shifts + random.randint(0, 1)
        required_shifts = random.randint(min_shifts * 3, max_shifts * 5)
        skill_level = random.randint(1, 3)
        
        # Pick unavailable, desired, and undesired *without replacement*
        unavailable = random.sample(shifts, k=min(len(shifts), random.randint(0, 2)))
        remaining = [s for s in shifts if s not in unavailable]
        
        desired = random.sample(remaining, k=min(len(remaining), random.randint(0, 3)))
        remaining2 = [s for s in remaining if s not in desired]
        
        undesired = random.sample(remaining2, k=min(len(remaining2), random.randint(0, 3)))
        
        course_tas.append(TA(
            id=ta_id,
            name=name_ta,
            min_shifts_per_week=min_shifts,
            max_shifts_per_week=max_shifts,
            required_shifts_per_semester=required_shifts,
            skill_level=skill_level,
            unavailable=unavailable,
            desired=desired,
            undesired=undesired,
        ))
    
    # Generate shift assignments
    ids = id_generator()
    shift_assignments: List[ShiftAssignment] = []
    for shift in shifts:
        for _ in range(shift.required_tas):
            shift_assignments.append(ShiftAssignment(
                id=next(ids),
                shift=shift,
                assigned_ta=None
            ))
    
    return Timetable(
        id=name,
        shifts=shifts,
        tas=course_tas,
        shift_assignments=shift_assignments
    )

def demo_data_semeseter_scheduling(name: str) -> Timetable:
   pass

def demo_data_semeseter_scheduling_random(name: str) -> Timetable:
   pass

generate_demo_data_dict = {
   "demo_data_weekly_scheduling"                   : demo_data_weekly_scheduling,
   "demo_data_weekly_scheduling-random"            : demo_data_weekly_scheduling_random,
   "demo_data_semeseter_scheduling"                : demo_data_semeseter_scheduling,
   "demo_data_semeseter_scheduling-random"         : demo_data_semeseter_scheduling_random,
}


def generate_demo_data(name: str = "CUSTOM", select: str = "demo_data_weekly_scheduling") -> Timetable:
   if generate_demo_data_dict.get(select):
      return generate_demo_data_dict[select](name)
   else:
      # provide options for the user
      print("Available demo data options:")
      for key in generate_demo_data_dict.keys():
         print(f"- {key}")
      raise ValueError(f"Unknown demo data name: {select}")