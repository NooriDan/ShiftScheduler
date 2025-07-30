import  random
import  logging
from dataclasses import dataclass, field
from    datetime   import time
from    typing     import List, Any, Dict, Tuple
from    tqdm       import tqdm

# Custom Imports
from hello_world.domain import Shift, TA, ShiftAssignment, Timetable, ConstraintParameters
from hello_world.utils  import id_generator


DAY_START_TIME = time(14, 30)
DAY_END_TIME   = time(17, 30)

AFTERNOON_START_TIME =  time(18, 30)
AFTERNOON_END_TIME   =  time(21, 30)

@dataclass
class ProblemRandomizationParameters:
    """A class to hold the randomization parameters for the Timetable."""

    MIN_NUM_SHIFTS_PER_WEEK: int = 6
    MAX_NUM_SHIFTS_PER_WEEK: int = 12

    MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT: int = 2
    MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT: int = 3

    MIN_NUM_OF_SHIFT_PER_TA_PER_WEEK: int = 0
    MAX_NUM_OF_SHIFT_PER_TA_PER_WEEK: int | None = field(default=None)  # To be set later dynamically

    MIN_TA_SKILL_LEVEL: int = 1
    MAX_TA_SKILL_LEVEL: int = 3

    MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV: int = 0
    MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV: int = 20

    MIN_NUM_OF_DESIRED_SHIFTS_DIV: int = 0
    MAX_NUM_OF_DESIRED_SHIFTS_DIV: int = 40

    MIN_NUM_OF_UNDESIRED_SHIFTS_DIV: int = 0
    MAX_NUM_OF_UNDESIRED_SHIFTS_DIV: int = 30

    def __post_init__(self):
        total_max_div = (
            self.MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV +
            self.MAX_NUM_OF_DESIRED_SHIFTS_DIV +
            self.MAX_NUM_OF_UNDESIRED_SHIFTS_DIV
        )
        if total_max_div > 100:
            raise ValueError("The sum of unavailable, desired, and undesired shift percentages exceeds 100%.")


class RandmizationUtil:
    def __init__(self, logger: logging.Logger):
        """Utility class for randomization functions."""
        self.logger = logger

    # Message Logger
    def log_program_constants(self, randomization_params: ProblemRandomizationParameters) -> None:
        """Log the constants used in the demo data generation."""
        logger = self.logger

        logger.info("📌 === Program Constants for Demo Data Generation ===")

        logger.info("📅 Shift Configuration:")
        logger.info(f"\t🔽 MIN_NUM_SHIFTS_PER_WEEK\t= {randomization_params.MIN_NUM_SHIFTS_PER_WEEK:02d}")
        logger.info(f"\t🔼 MAX_NUM_SHIFTS_PER_WEEK\t= {randomization_params.MAX_NUM_SHIFTS_PER_WEEK:02d}")

        logger.info("👥 TA Shift Requirements:")
        logger.info(f"\t🔽 MIN_TAS_REQUIRED_PER_SHIFT\t= {randomization_params.MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT:02d}")
        logger.info(f"\t🔼 MAX_TAS_REQUIRED_PER_SHIFT\t= {randomization_params.MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT:02d}")

        logger.info("🎯 TA Skill Levels:")
        logger.info(f"\t🧠 MIN_TA_SKILL_LEVEL\t\t= {randomization_params.MIN_TA_SKILL_LEVEL:02d}")
        logger.info(f"\t🚀 MAX_TA_SKILL_LEVEL\t\t= {randomization_params.MAX_TA_SKILL_LEVEL:02d}")

        logger.info("⛔ Unavailability (% of shifts/week):")
        logger.info(f"\t🔽 MIN_UNAVAILABLE_SHIFTS_DIV\t= {randomization_params.MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV:02d} %\t# Minimum pecentage of unavailable shifts in a week for TAs")
        logger.info(f"\t🔼 MAX_UNAVAILABLE_SHIFTS_DIV\t= {randomization_params.MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV:02d} %\t# Maximum pecentage of unavailable shifts in a week for TAs")

        logger.info("❤️ Desired Availability (% of shifts/week):")
        logger.info(f"\t🔽 MIN_DESIRED_SHIFTS_DIV\t= {randomization_params.MIN_NUM_OF_DESIRED_SHIFTS_DIV:02d} %\t# Minimum pecentage of desired shifts in a week for TAs")
        logger.info(f"\t🔼 MAX_DESIRED_SHIFTS_DIV\t= {randomization_params.MAX_NUM_OF_DESIRED_SHIFTS_DIV:02d} %\t# Maximum pecentage of desired shifts in a week for TAs")

        logger.info("⚠️  Undesired Availability (% of shifts/week):")
        logger.info(f"\t🔽 MIN_UNDESIRED_SHIFTS_DIV\t= {randomization_params.MIN_NUM_OF_UNDESIRED_SHIFTS_DIV:02d} %\t# Minimum pecentage of undesired shifts in a week for TAs")
        logger.info(f"\t🔼 MAX_UNDESIRED_SHIFTS_DIV\t= {randomization_params.MAX_NUM_OF_UNDESIRED_SHIFTS_DIV:02d} %\t# Maximum pecentage of undesired shifts in a week for TAs")

        logger.info("✅ === End of Constants ===\n")

    def log_ta_creation(self, ta: TA, logger: logging.Logger) -> None:
        """Log the creation of a TA."""
        logger.info(f"👤 TA Created: (ID: {int(ta.id):02d}) {ta.name}")
        logger.info(f"\t🔧 Skill Level:\t\t{ta.skill_level:02d}")
        logger.info(f"\t📆 Required Shifts:\t{ta.required_shifts_per_semester:02d}")
        logger.info(f"\t🗓️  Weekly Shift Bounds:\t{ta.min_shifts_per_week:02d} ⟶ {ta.max_shifts_per_week:02d}")

        logger.info(f"\t\t❌ Unavailable:\t{len(ta.unavailable):02d}")
        logger.info(f"\t\t✅ Desired:\t{len(ta.desired):02d}")
        logger.info(f"\t\t⚠️  Undesired:\t{len(ta.undesired):02d}\n")

    # List manipulation functions
    def remove_items_from_list(self, selected: List[Any], lst: List[Any]) -> List[Any]:
        """Remove items from a list based on another list."""
        return [item for item in lst if item not in selected]
    
    def draw_without_replacement(self,
            population: List[Any],
            k: int
        ) -> Tuple[List[Any], List[Any]]:
        """Draw k unique items from a population without replacement."""
        selected = random.sample(
                                population=population, 
                                k=min(len(population), k)
                            )
        population_after_selection = self.remove_items_from_list(selected=selected, lst=population)
        return selected, population_after_selection
    
    def draw_num_of_shifts_for_ta_per_semester_given_ta_demand(self, ta_demand: int, num_of_tas: int, upper_deviation: int = 2, lower_deviation: int = -2) -> List[int]:
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

class RandomTimetableGenerator:
    """A class to generate random demo data for the Timetable."""
    
    def __init__(self,
                name: str, 
                logger: logging.Logger,
                constraint_params: ConstraintParameters | None = None,
                days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
                shift_series_prefix: str = "L",
                ta_names : List[str] = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
                num_of_weeks: int = 1,
                allow_different_weekly_availability: bool = False,
                randomization_params: ProblemRandomizationParameters | None = None
                ):
        self.name = name
        self.logger = logger
        self.constraint_params = constraint_params if constraint_params else ConstraintParameters()
        self.days = days
        self.shift_series_prefix = shift_series_prefix
        self.ta_names = ta_names
        self.num_of_weeks = num_of_weeks
        self.allow_different_weekly_availability = allow_different_weekly_availability
        self.randomization_params = randomization_params if randomization_params else ProblemRandomizationParameters()

        self.helper = RandmizationUtil(logger=logger)

        # Random Variables
        self.num_shifts_per_week: int = 0
        self.shifts: List[Shift]     = []
        self.series_list: List[str]  = []
        self.ta_demands: int         = 0         # Total TA demand across all shifts to help plan TA loads and describe the problem
        self.ta_demands_weekly: int  = 0         # Total TA demand for each week (constant for all weeks)
        self.shift_assignments:  List[ShiftAssignment] = []
        self.course_tas:    List[TA] = []
        self.generated_problem: Timetable | None = None
        # Initialization log
        self.print_generator_config()

    def print_generator_config(self):
        # ======================
        # Pre-processing
        # ======================
        logger = self.logger
        shift_series_prefix = self.shift_series_prefix.upper()   # Ensure the prefix is uppercase
        logger.info(f"============================")
        logger.info(f"[Pre-processing] Generating demo data with timetable name '{self.name}'")
        logger.info(f"============================")
        # Log the constants used in the demo data generation
        self.helper.log_program_constants(randomization_params=self.randomization_params)
        # Log the input parameters
        logger.info(f"===========================")
        logger.info(f"Generating random shifts for {self.num_of_weeks} weeks with prefix '{shift_series_prefix}'")
        logger.info(f"============================")
        logger.info(f"\tAvailable days:\t\t{', '.join(self.days)}")
        logger.info(f"\t------------------------")
        logger.info(f"\tAvailable TA names:\t{', '.join(self.ta_names)}")
        logger.info(f"\t------------------------\n")

    def gen_demo_data(self) -> Tuple[Timetable, Dict[str, Dict[str, Any]]]:
        logger = self.logger
        # ======================
        # Generate random shifts
        # ======================
        # Generate shifts
        shifts, shift_metadata = self.generate_shifts()
        self.shifts = shifts

        # ======================
        # Generate random TAs
        # ======================
        # Generate TAs with random availability
        course_tas, ta_metadata = self.generate_course_tas(
            ta_names=self.ta_names,
            shifts=shifts,
            allow_different_weekly_availability=self.allow_different_weekly_availability,
            logger=logger
        )
        self.course_tas = course_tas

        # Generate "dummy" shift assignments - needed for how we set up the planning problem
        # Each shift assignment will require ONE TA, so we will expand the list of shifts by the number of TAs required for each shift
        shift_assignments: List[ShiftAssignment] = self.generate_dummy_shift_assignments()
        self.shift_assignments                   = shift_assignments

        # ======================
        self.generated_problem = Timetable(
            id=self.name,
            shifts=self.shifts,
            tas=self.course_tas,
            shift_assignments=self.shift_assignments,
            constraint_parameters=self.constraint_params,
        )

        metadata: Dict[str, Dict[str, Any]] = {
            "shift_metadata": shift_metadata,
            "ta_metadata": ta_metadata,
            "problem_metadata": {
                "name": self.name,
                "num_of_weeks": self.num_of_weeks,
                "num_of_shifts": len(self.shifts),
                "num_of_tas": len(self.course_tas),
                "allow_different_weekly_availability": self.allow_different_weekly_availability,
            }
        }


        return self.generated_problem, metadata

    def set_seed(self, seed: int) -> None:
        """Set the random seed for reproducibility."""
        random.seed(seed)
        self.logger.info(f"Random seed set to: {seed}")

    # ---------------
    # Helper methods for the random data generation
    # --------------- 
        
    def draw_shifts_for_ta(self,
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

            unavailable, shifts = self.helper.draw_without_replacement(population=shifts, 
                                                            k=random.randint(
                                                                a=draw_size*self.randomization_params.MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100, 
                                                                b=draw_size*self.randomization_params.MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100
                                                            )
                                                        )
            desired, shifts = self.helper.draw_without_replacement(population=shifts, 
                                                            k=random.randint(
                                                                a=draw_size*self.randomization_params.MIN_NUM_OF_DESIRED_SHIFTS_DIV//100, 
                                                                b=draw_size*self.randomization_params.MAX_NUM_OF_DESIRED_SHIFTS_DIV//100
                                                            )
                                                        )
            undesired, shifts = self.helper.draw_without_replacement(population=shifts, 
                                                            k=random.randint(
                                                                a=draw_size*self.randomization_params.MIN_NUM_OF_UNDESIRED_SHIFTS_DIV//100, 
                                                                b=draw_size*self.randomization_params.MAX_NUM_OF_UNDESIRED_SHIFTS_DIV//100
                                                            )
                                                        ) 
        else:
            # will pick the availablity from the series_list which containts the unique series of the shifts (e.g., L01, L02, ...)
            draw_size   = len(series_list)
            unavailable_series, series_list = self.helper.draw_without_replacement(population=series_list, 
                                                            k=random.randint(
                                                                a=draw_size*self.randomization_params.MIN_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100, 
                                                                b=draw_size*self.randomization_params.MAX_NUM_OF_UNAVAILABLE_SHIFTS_DIV//100
                                                            )
                                                        )
            desired_series, series_list = self.helper.draw_without_replacement(population=series_list, 
                                                            k=random.randint(
                                                                a=draw_size*self.randomization_params.MIN_NUM_OF_DESIRED_SHIFTS_DIV//100, 
                                                                b=draw_size*self.randomization_params.MAX_NUM_OF_DESIRED_SHIFTS_DIV//100
                                                            )
                                                        )
            undesired_series, series_list = self.helper.draw_without_replacement(population=series_list, 
                                                            k=random.randint(
                                                                a=draw_size*self.randomization_params.MIN_NUM_OF_UNDESIRED_SHIFTS_DIV//100, 
                                                                b=draw_size*self.randomization_params.MAX_NUM_OF_UNDESIRED_SHIFTS_DIV//100
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

    def compute_ta_demand_from_shifts(self, shifts: List[Shift]) -> Tuple[int, int, Dict[int, int]]:
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

    def generate_course_tas(self,
            ta_names: List[str],
            shifts: List[Shift],
            allow_different_weekly_availability: bool,
            logger: logging.Logger,
            ) -> Tuple[List[TA], Dict[str, Any]]:
        """Generate TAs with random availability and log their creation."""
        ids = id_generator()
        course_tas: List[TA] = []

        # Infer some constants based on the inputs
        num_of_weeks: int                       = max(1, len({shift.week_id for shift in shifts}))          # Default to 1 week if no shifts are provided          
        num_tas: int                            = len(ta_names)
        series_list: List[str]                  = list({shift.series for shift in shifts})                  # convert to a set to remove duplicates and then convert back to a list
        total_ta_demands, ta_demands_weekly, _  = self.compute_ta_demand_from_shifts(shifts=shifts)              # returns "total_sum, largest_weekly_demand, ta_demand_per_week_id_dict"... discarding the ta_demand_per_week_id_dict

        max_num_of_shift_per_ta_per_week: int = ta_demands_weekly // num_tas + 1 if ta_demands_weekly % num_tas > 0 else ta_demands_weekly // num_tas
        min_shifts_per_week: int            = self.randomization_params.MIN_NUM_OF_SHIFT_PER_TA_PER_WEEK if self.randomization_params.MIN_NUM_OF_SHIFT_PER_TA_PER_WEEK < max_num_of_shift_per_ta_per_week else max_num_of_shift_per_ta_per_week
        max_shifts_per_week: int            = max_num_of_shift_per_ta_per_week

        # randomize the number of shifts per TA per semester
        tas_shift_count: List[int]          = self.helper.draw_num_of_shifts_for_ta_per_semester_given_ta_demand(
                                                                                            ta_demand=total_ta_demands, 
                                                                                            num_of_tas=num_tas, 
                                                                                            upper_deviation=2, 
                                                                                            lower_deviation=-2
                                                                                            )
        total_desired_shifts: int = 0
        total_undesired_shifts: int = 0
        total_unavailable_shifts: int = 0

        logger.info("✨ Generating Course TAs ✨")
        logger.info("🔍 Drawing weekly shift availability and preferences...")

        for index in range(num_tas):
            # Generate random TA details
            ta_id                           = next(ids)
            skill_level                     = random.randint(self.randomization_params.MIN_TA_SKILL_LEVEL, self.randomization_params.MAX_TA_SKILL_LEVEL)
            name_ta                         = random.choice(ta_names)
            # Remove the selected name to avoid duplicates
            ta_names                        = self.helper.remove_items_from_list(selected=[name_ta], lst=ta_names)

            required_shifts_per_semester    = tas_shift_count[index]  # Get the number of shifts for this TA
            
            # draw shifts for the TA
            drawn_shifts = self.draw_shifts_for_ta(
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
            # Update the total counts
            total_desired_shifts    += len(ta_to_append.desired)
            total_undesired_shifts  += len(ta_to_append.undesired)
            total_unavailable_shifts += len(ta_to_append.unavailable)
            # Log the creation of the TA
            self.helper.log_ta_creation(ta=ta_to_append, logger=logger)

        logger.info("📋 ===========================")
        logger.info(f"👩‍🏫 Generated TAs:\t\t{len(course_tas)}")
        logger.info(f"📊 Total TA Demand:\t\t{total_ta_demands} shifts across {num_of_weeks} weeks")
        # show the breakdown between the desired, undesired, and unavailable shifts
        logger.info(f"🟢 Desired Shifts:\t\t{total_desired_shifts:03d} ({total_desired_shifts / len(course_tas):.2f} per TA)\t\t🌟 Unique:\t{len(set(shift.series for ta in course_tas for shift in ta.desired))}")
        logger.info(f"🟡 Undesired Shifts:\t\t{total_undesired_shifts:03d} ({total_undesired_shifts / len(course_tas):.2f} per TA)\t\t⚠️ Unique:\t{len(set(shift.series for ta in course_tas for shift in ta.undesired))}")
        logger.info(f"🔴 Unavailable Shifts:\t\t{total_unavailable_shifts:03d} ({total_unavailable_shifts / len(course_tas):.2f} per TA)\t\t🚫 Unique:\t{len(set(shift.series for ta in course_tas for shift in ta.unavailable))}")
        logger.info(f"⏳ Weekly Shift Limits:\t\tMin: {min_shifts_per_week}, Max: {max_shifts_per_week}")
        logger.info(f"🔄 Allow Different Weekly Availability:\t\t{'✅ Yes' if allow_different_weekly_availability else '❌ No'}")
        logger.info("📋 ===========================\n")

        metadata: Dict[str, Any] = {
            "name": self.name,
            "num_of_weeks": num_of_weeks,
            "num_of_tas": len(course_tas),
            "total_ta_demand": total_ta_demands,
            "ta_demand_weekly": ta_demands_weekly,

            "total_desired_shifts": total_desired_shifts,
            "total_undesired_shifts": total_undesired_shifts,
            "total_unavailable_shifts": total_unavailable_shifts,

            "total_desired_shifts_unique": len(set(shift.series for ta in course_tas for shift in ta.desired)),
            "total_undesired_shifts_unique": len(set(shift.series for ta in course_tas for shift in ta.undesired)),
            "total_unavailable_shifts_unique": len(set(shift.series for ta in course_tas for shift in ta.unavailable)),

            "allow_different_weekly_availability": allow_different_weekly_availability,
            "tas_shift_count": tas_shift_count,
            "ta_names": [ta.name for ta in course_tas],
        }

        return course_tas, metadata

    def generate_shifts(self) -> Tuple[List[Shift], Dict[str, Any]]:
        """Generate random shifts for the given days and number of weeks."""
        logger = self.logger
        # ======================
        # 🔄 Resetting Member Variables
        # ======================
        self.shifts                 = []
        self.series_list            = []
        self.ta_demands             = 0
        self.ta_demands_weekly      = 0
        self.num_shifts_per_week    = random.randint(self.randomization_params.MIN_NUM_SHIFTS_PER_WEEK, self.randomization_params.MAX_NUM_SHIFTS_PER_WEEK)  # number of shifts (constant for all weeks)
        
        logger.info("🛠️ Generating Shifts...")
        logger.info(f"\t📅 Shifts per Week: {self.num_shifts_per_week:02d}")

        # ======================
        # Generate shifts
        # =====================
        ids                 = id_generator()                # Unique ID generator for shifts
        
        for i in range(self.num_shifts_per_week):
            # Generate random shift details
            required_tas   = random.randint(self.randomization_params.MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT, self.randomization_params.MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT)
            day            = random.choice(self.days)
            series         = f"{self.shift_series_prefix}{i + 1:02d}"  # e.g., L01, L02, ...
            start_time     = random.choice([DAY_START_TIME, AFTERNOON_START_TIME])
            end_time       = DAY_END_TIME if start_time == DAY_START_TIME else AFTERNOON_END_TIME
            
            self.ta_demands_weekly  += required_tas 
            self.ta_demands         += required_tas * self.num_of_weeks
            self.series_list.append(series)

            for week_id in range(self.num_of_weeks):
                shift_id       = next(ids)
                # Add the shift to the list
                self.shifts.append(Shift(
                    id=shift_id,
                    series=series,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    required_tas=required_tas,
                    week_id=week_id
                ))
                logger.info(
                    f"\t📦 [ID: {int(shift_id):02d}] [Week: {int(week_id):02d}] \t"
                    f"{series} on {day} \t{start_time}–{end_time} ⏰ \t"
                    f"Requires: {required_tas} TA(s)"
                )

        # ======================
        # 📊 Summary
        # ======================
        logger.info("==============================================")
        logger.info(f"📋 Shift Series: \t\t{', '.join(self.series_list)}")
        logger.info(f"🧪 Total Shifts Generated: \t{len(self.shifts):03d}")
        logger.info(f"🧮 TA Demand per Week: \t\t{self.ta_demands_weekly:03d}")
        logger.info(f"📈 Total TA Demand: \t\t{self.ta_demands:03d} across {self.num_of_weeks} week(s)")
        logger.info(f"🎯 Shift TA Requirement Range: \t{self.randomization_params.MIN_NUM_OF_TAS_REQUIRED_PER_SHIFT}–{self.randomization_params.MAX_NUM_OF_TAS_REQUIRED_PER_SHIFT}")
        logger.info("==============================================\n")

        metdata: Dict[str, Any] = {
            "name": self.name,
            "num_of_weeks": self.num_of_weeks,
            "num_of_shifts_per_week": self.num_shifts_per_week,
            "ta_demand_weekly": self.ta_demands_weekly,
            "ta_demand_total": self.ta_demands,
            "series_list": self.series_list,
            "shifts_count": len(self.shifts),
            "shift_series_prefix": self.shift_series_prefix,
        }
        return self.shifts, metdata

    def generate_dummy_shift_assignments(self) -> List[ShiftAssignment]:
        """Expands the list of shifts into a list of shift assignments, each requiring ONE TA. this is needed for how we set up the planning problem."""
        
        shift_assignments: List[ShiftAssignment] = []
        ids = id_generator()
        for shift in self.shifts:
            for _ in range(shift.required_tas):
                shift_assignments.append(ShiftAssignment(
                    id=next(ids),
                    shift=shift,
                    assigned_ta=None
                ))
        self.shift_assignments = shift_assignments
        self.logger.info(f"Generated {len(shift_assignments)} shift assignments for {len(self.shifts)} shifts...")
        return shift_assignments
    
    # ---------------
    # End of methods functions for the random data generation
    # ---------------

# ---------------
# Public API functions
# ---------------
def demo_data_semeseter_scheduling_random(
      name: str,
      logger: logging.Logger,
      constraint_params: ConstraintParameters = ConstraintParameters(),
      days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
      shift_series_prefix: str = "L",
      ta_names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
      num_of_weeks: int = 12,
      randomization_params: ProblemRandomizationParameters = ProblemRandomizationParameters()
      ) -> Timetable:
   
   return demo_data_random(
      name=name,
      logger=logger,
      constraint_params=constraint_params,
      days=days,
      shift_series_prefix=shift_series_prefix,
      ta_names=ta_names,
      num_of_weeks=num_of_weeks,
      randomization_params = randomization_params
   )

def demo_data_random(
        name: str,
        logger: logging.Logger,
        constraint_params: ConstraintParameters = ConstraintParameters(),
        days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"],
        shift_series_prefix: str = "L",
        ta_names = ["M. Roghani", "D. Noori", "A. Gholami", "M. Jafari", "A. Athar", "S. Smith", "J. Doe"],
        num_of_weeks: int = 1,
        allow_different_weekly_availability: bool = False,
        randomization_params: ProblemRandomizationParameters = ProblemRandomizationParameters()
      ) -> Timetable:
    """Generate random demo data for the Timetable."""
    generator = RandomTimetableGenerator(name=name, logger=logger)
    problem, _ = generator.gen_demo_data() # discarding the metadata via _
    return problem

def demo_data_weekly_scheduling(name: str, logger: logging.Logger, constraint_params: ConstraintParameters = ConstraintParameters()) -> Timetable:
    
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
                  shift_assignments= shift_assignments,
                  constraint_parameters=constraint_params
         )

def demo_data_semeseter_scheduling(name: str, logger: logging.Logger) -> Timetable:
   # TODO
   pass

# -------------------
# Random demo data generation
# -------------------
_generate_demo_data_dict = {
   "demo_data_weekly_scheduling"                   : demo_data_weekly_scheduling,
   "demo_data_weekly_scheduling-random"            : demo_data_random,
   "demo_data_semeseter_scheduling"                : demo_data_semeseter_scheduling,
   "demo_data_semeseter_scheduling-random"         : demo_data_semeseter_scheduling_random,
}

def generate_demo_data_with_default_params(logger: logging.Logger, name: str = "CUSTOM", select: str = "demo_data_weekly_scheduling") -> Timetable:
    """   Generate demo data based on the provided name and selection.
       If the selection is not found, it will print available options.
       Args:
           name (str): Name of the demo Timetable data.
           select (str): Selection key for the demo data."""
    if _generate_demo_data_dict.get(select):
        return _generate_demo_data_dict[select](name=name, logger=logger)
    else:
        # provide options for the user
        logger.info("Available demo data options:")
        for key in _generate_demo_data_dict.keys():
            logger.info(f"- {key}")
        raise ValueError(f"Unknown demo data name: {select}")
