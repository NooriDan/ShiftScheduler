import random
from datetime import time
from typing import List, Any

# Custom Imports
from hello_world.domain import Shift, TA, ShiftAssignment, Timetable
from hello_world.utils import id_generator

# Constants for random shift generation
DAY_START_TIME = time(14, 30)
DAY_END_TIME   = time(17, 30)

AFTERNOON_START_TIME =  time(18, 30)
AFTERNOON_END_TIME   =  time(21, 30)

MIN_NUM_SHIFTS_PER_WEEK = 6
MAX_NUM_SHIFTS_PER_WEEK = 12

MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT = 2
MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT = 4

# Constants for random TA generation
MIN_TA_SKILL_LEVEL = 1
MAX_TA_SKILL_LEVEL = 3

MIN_NUM_OF_UNAVAILABLE_SHIFTS   = 0
MAX_NUM_OF_UNAVAILABLE_SHIFTS   = MAX_NUM_SHIFTS_PER_WEEK // 3

MIN_NUM_OF_DESIRED_SHIFTS       = 0
MAX_NUM_OF_DESIRED_SHIFTS       = MAX_NUM_SHIFTS_PER_WEEK // 2

MIN_NUM_OF_UNDESIRED_SHIFTS     = 0
MAX_NUM_OF_UNDESIRED_SHIFTS     = MAX_NUM_SHIFTS_PER_WEEK // 3

MIN_NUM_OF_TAS = MIN_NUM_SHIFTS_PER_WEEK * MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT
# MAX_NUM_OF_TAS = TBD by the number of shifts and their requirements

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

def demo_data_random(
      name: str, 
      days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
      shift_series_prefix: str = "L",
      ta_names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
      num_of_weeks: int = 1
      ) -> Timetable:
    
    # ======================
    # Pre-processing
    # ======================
    shift_series_prefix = shift_series_prefix.upper()   # Ensure the prefix is uppercase
    
    # ======================
    # Generate random shifts
    # ======================
    shifts: List[Shift] = []
    ta_demands: int     = 0     # Total TA demand across all shifts to help plan TA loads and describe the problem

    ids                 = id_generator()                # Unique ID generator for shifts
    num_shifts          = random.randint(MIN_NUM_SHIFTS_PER_WEEK, MAX_NUM_SHIFTS_PER_WEEK)  # number of shifts (constant for all weeks)
    
    for week_id in range(num_of_weeks):
        for i in range(num_shifts):
            # Generate random shift details
            shift_id       = next(ids)
            day            = random.choice(days)
            required_tas   = random.randint(MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT, MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT)
            series         = f"{shift_series_prefix}{i + 1:02d}"  # e.g., L01, L02, ...
            start_time     = random.choice([DAY_START_TIME, AFTERNOON_START_TIME])
            end_time       = DAY_END_TIME if start_time == DAY_START_TIME else AFTERNOON_END_TIME
            # Add the shift to the list
            shifts.append(Shift(
                id=shift_id,
                series=series,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                required_tas=required_tas,
                week_id=week_id
            ))
            # Increment the total TA demand
            ta_demands += required_tas
    
    # ======================
    # Generate random TAs
    # ======================
    ids                     = id_generator()
    num_tas: int            = len(ta_names) if len(ta_names) > 0 else 1  # Ensure at least one TA
    course_tas: List[TA]    = []
    tas_shift_count: int    = ta_demands // num_tas if num_tas > 0 else 1  # Average shifts per TA, ensuring at least 1 shift per TA
    
    for _ in range(num_tas):
        ta_id                           = next(ids)
        skill_level                     = random.randint(MIN_TA_SKILL_LEVEL, MAX_TA_SKILL_LEVEL)
        name_ta                         = random.choice(ta_names)
        # Remove the selected name to avoid duplicates
        ta_names                        = remove_items_from_list(selected=[name_ta], lst=ta_names)

        min_shifts_per_week             = random.randint(1, 2)
        max_shifts_per_week             = min_shifts_per_week + random.randint(0, 1)

        required_shifts_per_semester    = num_of_weeks * (min_shifts_per_week + max_shifts_per_week) // 2  # Average shifts per semester
        
        # Pick unavailable, desired, and undesired *without replacement*
        unavailable = random.sample(
                                population=shifts, 
                                k=min(len(shifts), random.randint(MIN_NUM_OF_UNAVAILABLE_SHIFTS, MAX_NUM_OF_UNAVAILABLE_SHIFTS))
                                )
        remaining   = remove_items_from_list(selected=unavailable, lst=shifts)
        
        desired     = random.sample(
                                population=remaining, 
                                k=min(len(remaining), random.randint(MIN_NUM_OF_DESIRED_SHIFTS, MAX_NUM_OF_DESIRED_SHIFTS))
                                )
        remaining   = remove_items_from_list(selected=desired, lst=remaining)
        
        undesired   = random.sample(
                                remaining, 
                                k=min(len(remaining), random.randint(MIN_NUM_OF_UNDESIRED_SHIFTS, MAX_NUM_OF_UNDESIRED_SHIFTS))
                                )
        
        course_tas.append(TA(
            id=ta_id,
            name=name_ta,
            min_shifts_per_week=min_shifts_per_week,
            max_shifts_per_week=max_shifts_per_week,
            required_shifts_per_semester=required_shifts_per_semester,
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

def demo_data_semeseter_scheduling_random(
      name: str, 
      days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
      shift_series_prefix: str = "L",
      ta_names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
      num_of_weeks: int = 12
      ) -> Timetable:
   
   return demo_data_random(
      name=name,
      days=days,
      shift_series_prefix=shift_series_prefix,
      ta_names=ta_names,
      num_of_weeks=num_of_weeks
   )

_generate_demo_data_dict = {
   "demo_data_weekly_scheduling"                   : demo_data_weekly_scheduling,
   "demo_data_weekly_scheduling-random"            : demo_data_random,
   "demo_data_semeseter_scheduling"                : demo_data_semeseter_scheduling,
   "demo_data_semeseter_scheduling-random"         : demo_data_semeseter_scheduling_random,
}


def generate_demo_data(name: str = "CUSTOM", select: str = "demo_data_weekly_scheduling") -> Timetable:
   """   Generate demo data based on the provided name and selection.
       If the selection is not found, it will print available options.
       Args:
           name (str): Name of the demo Timetable data.
           select (str): Selection key for the demo data."""
   if _generate_demo_data_dict.get(select):
      return _generate_demo_data_dict[select](name)
   else:
      # provide options for the user
      print("Available demo data options:")
      for key in _generate_demo_data_dict.keys():
         print(f"- {key}")
      raise ValueError(f"Unknown demo data name: {select}")
   
def remove_items_from_list(selected: List[Any], lst: List[Any]) -> List[Any]:
    """Remove items from a list based on another list."""
    return [item for item in lst if item not in selected]