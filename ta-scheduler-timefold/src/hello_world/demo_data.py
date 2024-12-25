from datetime import time
from typing import List

# Custom Imports
from hello_world.domain import Shift, TA, ShiftAssignment, Timetable
from hello_world.utils import id_generator

DAY_START_TIME = time(14, 30)
DAY_END_TIME   = time(17, 30)

AFTERNOON_START_TIME =  time(18, 30)
AFTERNOON_END_TIME   =  time(21, 30)

def demo_data_A(name: str) -> Timetable:
    
   ids = id_generator()
   shifts: List[Shift] = [
      Shift(next(ids),"L07", "Mon", DAY_START_TIME, DAY_END_TIME, 2),
      Shift(next(ids),"L08", "Mon", AFTERNOON_START_TIME, AFTERNOON_END_TIME, 3),
      Shift(next(ids),"L09", "Tue", DAY_START_TIME, DAY_END_TIME, 2),
      Shift(next(ids),"L10", "Tue", AFTERNOON_START_TIME, AFTERNOON_END_TIME, 1),
      Shift(next(ids),"L11", "Thu", AFTERNOON_START_TIME, AFTERNOON_END_TIME, 2),
      ]
   
   ids = id_generator()
   course_tas: List[TA] = [
      TA(id = next(ids), 
         name = "M. Roghani", 
         required_shifts= 3, 
         unavailable= [shifts[4]], 
         desired    = [shifts[0], shifts[1], shifts[2]],
         undesired  = [shifts[3]]
      ),
      TA(id = next(ids), 
         name = "D. Noori", 
         required_shifts= 2, 
         unavailable= [shifts[0]], 
         desired    = [],
         undesired  = [shifts[2]]
      ),
      TA(id = next(ids), 
         name = "A. Gholami", 
         required_shifts= 1, 
         unavailable= [shifts[1]], 
         desired    = [shifts[0]],
         undesired  = [shifts[2]]
      ),
      TA(id = next(ids), 
         name = "M. Jafari", 
         required_shifts= 2, 
         unavailable= [shifts[3]], 
         desired    = [shifts[1]],
         undesired  = [shifts[2]]
      ),
      TA(id = next(ids), 
         name = "A. Athar", 
         required_shifts= 2, 
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

def demo_data_B(name: str) -> Timetable:
   pass


def generate_demo_data(name: str = "CUSTOM", select: str = "A") -> Timetable:
   if select == "A":
      return demo_data_A(name)
   if select == "B":
      return demo_data_B(name)
   
   else:
      raise ValueError(f"Unknown demo data name: {select}")