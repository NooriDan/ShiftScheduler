import  random
import  logging
from    datetime   import time
from    typing     import List, Any, Dict, Tuple
from    tqdm       import tqdm

# Custom Imports
from hello_world.domain import Shift, TA, ShiftAssignment, Timetable
from hello_world.utils  import id_generator

# Constants for random shift generation
SEED = 42
# standard library
random.seed(SEED)

DAY_START_TIME = time(14, 30)
DAY_END_TIME   = time(17, 30)

AFTERNOON_START_TIME =  time(18, 30)
AFTERNOON_END_TIME   =  time(21, 30)

MIN_NUM_SHIFTS_PER_WEEK = 6
MAX_NUM_SHIFTS_PER_WEEK = 12

MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT = 2
MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT = 3

# Constants for random TA generation
MIN_NUM_OF_SHIFT_PER_TA_PER_WEEK = 0
# MAX_NUM_OF_SHIFT_PER_TA_PER_WEEK = ... # This value will be set dynamically based on the total TA demand and number of TAs (as to not over-constrain the problem)

MIN_TA_SKILL_LEVEL = 1
MAX_TA_SKILL_LEVEL = 3

MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV   = 0     # in pecentage of the total weekly shifts
MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV   = 0    # in pecentage of the total weekly shifts

MIN_NUM_OF_DESIRED_SHIFTS_DIV       = 0     # in pecentage of the total weekly shifts
MAX_NUM_OF_DESIRED_SHIFTS_DIV       = 40    # in pecentage of the total weekly shifts

MIN_NUM_OF_UNDESIRED_SHIFTS_DIV     = 0     # in pecentage of the total weekly shifts
MAX_NUM_OF_UNDESIRED_SHIFTS_DIV     = 0    # in pecentage of the total weekly shifts



def demo_data_weekly_scheduling(name: str, logger: logging.Logger) -> Timetable:
    
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
      logger: logging.Logger,
      days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
      shift_series_prefix: str = "L",
      ta_names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
      num_of_weeks: int = 1,
      allow_different_weekly_availability: bool = False
      ) -> Timetable:
    
    # ======================
    # Pre-processing
    # ======================
    shift_series_prefix = shift_series_prefix.upper()   # Ensure the prefix is uppercase
    logger.info(f"============================")
    logger.info(f"[Pre-processing] Generating demo data with timetable name '{name}'")
    logger.info(f"============================")
    # Log the constants used in the demo data generation
    log_program_constants(logger=logger)
    # Log the input parameters
    logger.info(f"===========================")
    logger.info(f"Generating random shifts for {num_of_weeks} weeks with prefix '{shift_series_prefix}'")
    logger.info(f"============================")
    logger.info(f"\tAvailable days:\t\t{', '.join(days)}")
    logger.info(f"\t------------------------")
    logger.info(f"\tAvailable TA names:\t{', '.join(ta_names)}")
    logger.info(f"\t------------------------\n")

    # ======================
    # Generate random shifts
    # ======================
    # Generate shifts
    shifts: List[Shift] = generate_shifts(
        days=days,
        shift_series_prefix=shift_series_prefix,
        num_of_weeks=num_of_weeks,
        logger=logger
    )

    # ======================
    # Generate random TAs
    # ======================
    # Generate TAs with random availability
    course_tas: List[TA] = generate_course_tas(
        ta_names=ta_names,
        shifts=shifts,
        allow_different_weekly_availability=allow_different_weekly_availability,
        logger=logger
    )

    # Generate "dummy" shift assignments - needed for how we set up the planning problem
    # Each shift assignment will require ONE TA, so we will expand the list of shifts by the number of TAs required for each shift
    shift_assignments: List[ShiftAssignment] = generate_dummy_shift_assignments(shifts=shifts, logger=logger)
    
    return Timetable(
        id=name,
        shifts=shifts,
        tas=course_tas,
        shift_assignments=shift_assignments
    )

def demo_data_semeseter_scheduling(name: str, logger: logging.Logger) -> Timetable:
   pass

def demo_data_semeseter_scheduling_random(
      name: str,
      logger: logging.Logger,
      days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
      shift_series_prefix: str = "L",
      ta_names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
      num_of_weeks: int = 12
      ) -> Timetable:
   
   return demo_data_random(
      name=name,
      logger=logger,
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


def generate_demo_data(logger: logging.Logger, name: str = "CUSTOM", select: str = "demo_data_weekly_scheduling") -> Timetable:
   """   Generate demo data based on the provided name and selection.
       If the selection is not found, it will print available options.
       Args:
           name (str): Name of the demo Timetable data.
           select (str): Selection key for the demo data."""
   if _generate_demo_data_dict.get(select):
      return _generate_demo_data_dict[select](name=name, logger=logger)
   else:
      # provide options for the user
      print("Available demo data options:")
      for key in _generate_demo_data_dict.keys():
         print(f"- {key}")
      raise ValueError(f"Unknown demo data name: {select}")

# ---------------
# Helper functions for the random data generation
# --------------- 
def remove_items_from_list(selected: List[Any], lst: List[Any]) -> List[Any]:
    """Remove items from a list based on another list."""
    return [item for item in lst if item not in selected]

def draw_num_of_shifts_for_ta_per_semester_given_ta_demand(ta_demand: int, num_of_tas: int, upper_deviation: int = 2, lower_deviation: int = -2) -> List[int]:
      """Draw a list of integers representing the number of shifts per semester for each TA.
      The sum of the list should equal the total TA demand."""
      # Sanity checks
      if ta_demand <= 0:
         raise ValueError("TA demand must be greater than zero.")
      if num_of_tas <= 0:
         raise ValueError("Number of TAs must be greater than zero.")
      if upper_deviation < 0 or lower_deviation > 0:
         raise ValueError("Deviations must be non-negative and non-positive respectively.")
      if upper_deviation < lower_deviation:
         raise ValueError("Upper deviation must be greater than or equal to lower deviation.")
      
      # Initialize the list to hold shifts per semester for each TA
      tas_shift_per_semester: List[int] = []
      avg_shifts_per_ta: int            = ta_demand // num_of_tas

      # Calculate average shifts per TA
      for _ in range(num_of_tas):
          tas_shift_per_semester.append(avg_shifts_per_ta + random.randint(lower_deviation, upper_deviation))

      diff: int = ta_demand - sum(tas_shift_per_semester)
      for i in range(abs(diff)):
         found_ta = False
         counter  = 0
         while not found_ta:
            if counter > num_of_tas * 10:  # Prevent infinite loop
               raise ValueError("Unable to adjust shifts to match TA demand. Please check the input parameters")
            index = random.randint(0, num_of_tas - 1)
            if diff > 0: # If we need to increase the total shifts (under-assigned)
               tas_shift_per_semester[index] += 1
            else:       # If we need to decrease the total shifts (over-assigned)
               if tas_shift_per_semester[index] < 1:
                  counter += 1
                  continue
               tas_shift_per_semester[index] -= 1
            found_ta = True

      # Ensure the total shifts match the TA demand
      if sum(tas_shift_per_semester) != ta_demand:
         raise ValueError("The total shifts per semester do not match the TA demand after adjustment. something went wrong...")
      
      return tas_shift_per_semester

def draw_without_replacement(
        population: List[Any],
        k: int
      ) -> Tuple[List[Any], List[Any]]:
    """Draw k unique items from a population without replacement."""
    selected = random.sample(
                            population=population, 
                            k=min(len(population), k)
                        )
    population_after_selection = remove_items_from_list(selected=selected, lst=population)
    return selected, population_after_selection
    
def draw_shifts_for_ta(
        shifts: List[Shift],
        series_list: List[str],
        num_shifts_per_week: int,
        num_of_weeks: int = 1,
        allow_different_weekly_availability: bool = False
      ) -> Dict[str, List[Shift]]:
    
    # Local variables
    draw_size: int  = 0
    unavailable:    List[Shift]     = []
    desired:        List[Shift]     = []
    undesired:      List[Shift]     = []

    # below is only for the case of fixed weekly availability
    unavailable_series:    List[str]     = []
    desired_series:        List[str]     = []
    undesired_series:      List[str]     = []

    # Pick unavailable, desired, and undesired *without replacement*
    if allow_different_weekly_availability:
        draw_size   = num_shifts_per_week*num_of_weeks

        unavailable, shifts = draw_without_replacement(population=shifts, 
                                                        k=random.randint(
                                                            a=draw_size*MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100, 
                                                            b=draw_size*MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100
                                                        )
                                                    )
        desired, shifts = draw_without_replacement(population=shifts, 
                                                        k=random.randint(
                                                            a=draw_size*MIN_NUM_OF_DESIRED_SHIFTS_DIV//100, 
                                                            b=draw_size*MAX_NUM_OF_DESIRED_SHIFTS_DIV//100
                                                        )
                                                    )
        undesired, shifts = draw_without_replacement(population=shifts, 
                                                        k=random.randint(
                                                            a=draw_size*MIN_NUM_OF_UNDESIRED_SHIFTS_DIV//100, 
                                                            b=draw_size*MAX_NUM_OF_UNDESIRED_SHIFTS_DIV//100
                                                        )
                                                    ) 
    else:
        # will pick the availablity from the series_list which containts the unique series of the shifts (e.g., L01, L02, ...)
        draw_size   = len(series_list)
        unavailable_series, series_list = draw_without_replacement(population=series_list, 
                                                        k=random.randint(
                                                            a=draw_size*MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100, 
                                                            b=draw_size*MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100
                                                        )
                                                    )
        desired_series, series_list = draw_without_replacement(population=series_list, 
                                                        k=random.randint(
                                                            a=draw_size*MIN_NUM_OF_DESIRED_SHIFTS_DIV//100, 
                                                            b=draw_size*MAX_NUM_OF_DESIRED_SHIFTS_DIV//100
                                                        )
                                                    )
        undesired_series, series_list = draw_without_replacement(population=series_list, 
                                                        k=random.randint(
                                                            a=draw_size*MIN_NUM_OF_UNDESIRED_SHIFTS_DIV//100, 
                                                            b=draw_size*MAX_NUM_OF_UNDESIRED_SHIFTS_DIV//100
                                                        )
                                                    )
        
        # Now filter the shifts based on the series
        unavailable = [shift for shift in shifts if shift.series in unavailable_series]
        desired     = [shift for shift in shifts if shift.series in desired_series]
        undesired   = [shift for shift in shifts if shift.series in undesired_series]
    # return a dictionary of the availability
    return {
        "unavailable": unavailable,
        "undesired": undesired,
        "desired": desired, 
        }

def compute_ta_demand_from_shifts(shifts: List[Shift]) -> Tuple[int, int, Dict[int, int]]:
    """Compute the total TA demand per week from the list of shifts. returns the following 
    - total TA demand across all shifts
    - total TA demand per week
    - a dictionary with week_id as key and the total TA demand for that week as value."""
    
    ta_demand_per_week_id_dict: Dict[int, int] = {}
    total_sum: int = 0
    largest_weekly_demand: int = 0
    for shift in shifts:
        ta_demand_per_week_id_dict[shift.week_id] = ta_demand_per_week_id_dict.get(shift.week_id, 0) + shift.required_tas
        total_sum += shift.required_tas

    largest_weekly_demand = max(ta_demand_per_week_id_dict.values(), default=0)

    return total_sum, largest_weekly_demand, ta_demand_per_week_id_dict

def generate_course_tas(
        ta_names: List[str],
        shifts: List[Shift],
        allow_different_weekly_availability: bool,
        logger: logging.Logger,
        ) -> List[TA]:
    """Generate TAs with random availability and log their creation."""
    ids = id_generator()
    course_tas: List[TA] = []

    # Infer some constants based on the inputs
    num_of_weeks: int                       = max(1, len({shift.week_id for shift in shifts}))          # Default to 1 week if no shifts are provided          
    num_tas: int                            = len(ta_names)
    series_list: List[str]                  = list({shift.series for shift in shifts})                  # convert to a set to remove duplicates and then convert back to a list
    total_ta_demands, ta_demands_weekly, _  = compute_ta_demand_from_shifts(shifts=shifts)              # returns "total_sum, largest_weekly_demand, ta_demand_per_week_id_dict"... discarding the ta_demand_per_week_id_dict

    max_num_of_shift_per_ta_per_week: int = ta_demands_weekly // num_tas + 1 if ta_demands_weekly % num_tas > 0 else ta_demands_weekly // num_tas
    min_shifts_per_week: int            = MIN_NUM_OF_SHIFT_PER_TA_PER_WEEK if MIN_NUM_OF_SHIFT_PER_TA_PER_WEEK < max_num_of_shift_per_ta_per_week else max_num_of_shift_per_ta_per_week
    max_shifts_per_week: int            = max_num_of_shift_per_ta_per_week

    # randomize the number of shifts per TA per semester
    tas_shift_count: List[int]          = draw_num_of_shifts_for_ta_per_semester_given_ta_demand(
                                                                                        ta_demand=total_ta_demands, 
                                                                                        num_of_tas=num_tas, 
                                                                                        upper_deviation=2, 
                                                                                        lower_deviation=-2
                                                                                        )
    # tas_shift_count_weekly: List[int]   = draw_num_of_shifts_for_ta_per_semester_given_ta_demand(
    #                                                                                     ta_demand=ta_demands_weekly, 
    #                                                                                     num_of_tas=num_tas, 
    #                                                                                     upper_deviation=1, 
    #                                                                                     lower_deviation=-1
    #                                                                                     )

    for index in range(num_tas):
        # Generate random TA details
        ta_id                           = next(ids)
        skill_level                     = random.randint(MIN_TA_SKILL_LEVEL, MAX_TA_SKILL_LEVEL)
        name_ta                         = random.choice(ta_names)
        # Remove the selected name to avoid duplicates
        ta_names                        = remove_items_from_list(selected=[name_ta], lst=ta_names)

        required_shifts_per_semester    = tas_shift_count[index]  # Get the number of shifts for this TA
        
        # draw shifts for the TA
        drawn_shifts = draw_shifts_for_ta(
                                        shifts=shifts,
                                        series_list=series_list,
                                        num_shifts_per_week=max_num_of_shift_per_ta_per_week,
                                        num_of_weeks=num_of_weeks,
                                        allow_different_weekly_availability=allow_different_weekly_availability
                                    )
        
        unavailable:    List[Shift] = drawn_shifts["unavailable"]
        desired:        List[Shift] = drawn_shifts["desired"]
        undesired:      List[Shift] = drawn_shifts["undesired"]

        ta_to_append: TA = TA(
            id=ta_id,
            name=name_ta,
            min_shifts_per_week=min_shifts_per_week,
            max_shifts_per_week=max_shifts_per_week,
            required_shifts_per_semester=required_shifts_per_semester,
            skill_level=skill_level,
            unavailable=unavailable,
            desired=desired,
            undesired=undesired,
        )
        
        course_tas.append(ta_to_append)
        log_ta_creation(ta=ta_to_append, logger=logger)

    logger.info(f"===========================")
    logger.info(f"Generated {len(course_tas)} TAs with a total TA demand of {total_ta_demands} across {num_of_weeks} weeks...")
    logger.info(f"Each TA has a minimum of {min_shifts_per_week} and a maximum of {max_shifts_per_week} shifts per week.")
    logger.info(f"Allow different weekly availability? {"yes" if allow_different_weekly_availability else "no"}")
    logger.info(f"===========================\n")

    return course_tas

def generate_shifts(
        days: List[str],
        shift_series_prefix: str,
        num_of_weeks: int,
        logger: logging.Logger
    ) -> List[Shift]:
    """Generate random shifts for the given days and number of weeks."""
        

    shifts: List[Shift]     = []
    series_list: List[str]  = []
    ta_demands: int         = 0         # Total TA demand across all shifts to help plan TA loads and describe the problem
    ta_demands_weekly: int  = 0         # Total TA demand for each week (constant for all weeks)

    ids                 = id_generator()                # Unique ID generator for shifts
    num_shifts_per_week = random.randint(MIN_NUM_SHIFTS_PER_WEEK, MAX_NUM_SHIFTS_PER_WEEK)  # number of shifts (constant for all weeks)
    
    for i in range(num_shifts_per_week):
        # Generate random shift details
        required_tas   = random.randint(MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT, MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT)
        day            = random.choice(days)
        series         = f"{shift_series_prefix}{i + 1:02d}"  # e.g., L01, L02, ...
        start_time     = random.choice([DAY_START_TIME, AFTERNOON_START_TIME])
        end_time       = DAY_END_TIME if start_time == DAY_START_TIME else AFTERNOON_END_TIME
        
        ta_demands_weekly  += required_tas 
        ta_demands         += required_tas * num_of_weeks
        series_list.append(series)

        for week_id in range(num_of_weeks):
            shift_id       = next(ids)
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
            # Log the generated shift
            logger.info(f"[ID: {int(shift_id):02d}] [weedk_id: {int(week_id):02d}] Generated Shift: {series} on {day} from {start_time} to {end_time} requiring {required_tas} TAs")
    
    # Log a summary of generated shifts
    logger.info(f"============================")
    logger.info(f"The shift series are:\t\t{', '.join(series_list)}")
    logger.info(f"Generated {len(shifts)} shifts with a total TA demand of {ta_demands} across {num_of_weeks} weeks ({num_shifts_per_week} shifts per week)...")
    logger.info(f"Each week has a total TA demand of {ta_demands_weekly} TAs.")
    logger.info(f"Each shift requires between {MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT} and {MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT} TAs.")
    logger.info(f"===========================\n")

    return shifts

def generate_dummy_shift_assignments(
        shifts: List[Shift], 
        logger: logging.Logger
        ) -> List[ShiftAssignment]:
    """Expands the list of shifts into a list of shift assignments, each requiring ONE TA. this is needed for how we set up the planning problem."""
    
    shift_assignments: List[ShiftAssignment] = []
    ids = id_generator()
    for shift in shifts:
        for _ in range(shift.required_tas):
            shift_assignments.append(ShiftAssignment(
                id=next(ids),
                shift=shift,
                assigned_ta=None
            ))
    logger.info(f"Generated {len(shift_assignments)} shift assignments for {len(shifts)} shifts...")
    return shift_assignments

# Message Logger
def log_program_constants(logger: logging.Logger) -> None:
    """Log the constants used in the demo data generation."""
    logger.info(f"Constants to be used:")
    logger.info(f"\tMIN_NUM_SHIFTS_PER_WEEK                 = {MIN_NUM_SHIFTS_PER_WEEK}\t# Minimum number of shifts per week")
    logger.info(f"\tMAX_NUM_SHIFTS_PER_WEEK                 = {MAX_NUM_SHIFTS_PER_WEEK}\t# Maximum number of shifts per week")
    logger.info(f"\tMIN_NUM_OF_TAS_REQUIRED_PER_SHIFT       = {MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT}\t# Minimum number of TAs required per shift")
    logger.info(f"\tMAX_NUM_OF_TAS_REQUIRED_PER_SHIFT       = {MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT}\t# Maximum number of TAs required per shift")
    logger.info(f"\t------------------------")
    logger.info(f"\tMIN_TA_SKILL_LEVEL                      = {MIN_TA_SKILL_LEVEL}\t# Minimum skill level for TAs")
    logger.info(f"\tMAX_TA_SKILL_LEVEL                      = {MAX_TA_SKILL_LEVEL}\t# Maximum skill level for TAs")
    logger.info(f"\t------------------------")
    logger.info(f"\tMIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV       = % {MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV}\t# Minimum pecentage of unavailable shifts in a week for TAs")
    logger.info(f"\tMAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV       = % {MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV}\t# Maximum pecentage of unavailable shifts in a week for TAs")
    logger.info(f"\t------------------------")
    logger.info(f"\tMIN_NUM_OF_DESIRED_SHIFTS_DIV           = % {MIN_NUM_OF_DESIRED_SHIFTS_DIV}\t# Minimum pecentage of desired shifts in a week for TAs")
    logger.info(f"\tMAX_NUM_OF_DESIRED_SHIFTS_DIV           = % {MAX_NUM_OF_DESIRED_SHIFTS_DIV}\t# Maximum pecentage of desired shifts in a week for TAs")
    logger.info(f"\t------------------------")
    logger.info(f"\tMIN_NUM_OF_UNDESIRED_SHIFTS_DIV         = % {MIN_NUM_OF_UNDESIRED_SHIFTS_DIV}\t# Minimum pecentage of undesired shifts in a week for TAs")
    logger.info(f"\tMAX_NUM_OF_UNDESIRED_SHIFTS_DIV         = % {MAX_NUM_OF_UNDESIRED_SHIFTS_DIV}\t# Maximum pecentage of undesired shifts in a week for TAs")
    logger.info(f"\t------------------------\n")

def log_ta_creation(ta: TA, logger: logging.Logger) -> None:
    """Log the creation of a TA."""
    logger.info(f"(ID: {int(ta.id):02d}) {ta.name}")
    logger.info(f"\t- Skill Level:              {ta.skill_level}")
    logger.info(f"\t- Required Shifts:          {ta.required_shifts_per_semester}")
    logger.info(f"\t- Min/Max Shifts per Week:  {ta.min_shifts_per_week} / {ta.max_shifts_per_week}")
    logger.info(f"\t\t- Unavailable:    {len(ta.unavailable)}")
    logger.info(f"\t\t- Desired:        {len(ta.desired)}")
    logger.info(f"\t\t- Undesired:      {len(ta.undesired)}")

# ---------------
# End of helper functions for the random data generation
# ---------------