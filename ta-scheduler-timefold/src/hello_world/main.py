import argparse
import logging
import sys, os

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.demo_data   import generate_demo_data, _generate_demo_data_dict
from hello_world.utils       import print_ta_availability, initialize_logger, DataConstructor
from hello_world.solver      import solve_problem

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the TA Rostering Program in Terminal')

    parser.add_argument('--ta_csv_path', 
                        type=str, 
                        help='Path to the TA csv file',
                        default='ta_list.csv')
    
    parser.add_argument('--shift_csv_path', 
                        type=str, 
                        help='Path to the shift csv file',
                        default='shift_list.csv')
    
    parser.add_argument('--availability_folder', 
                        type=str, 
                        help='Path to the availability folder',
                        default='availability')
    
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='Run the roster with data from a custom location',
                        default=False)
    
    parser.add_argument('--constraint_version',
                        type=str,
                        choices=['default', 'tabriz'],
                        help='Choose the constraint version to use',
                        default='default')
    
    # add an argument to select the demo data
    parser.add_argument('--demo_data_select',
                        type=str,
                        choices=list(_generate_demo_data_dict.keys()),
                        help='Select the demo data to use',
                        default='demo_data_weekly_scheduling-random')

    
    args = parser.parse_args()

    return args

def create_timetable_demo(logger: logging.Logger, demo_data_select: str = "demo_data_weekly_scheduling-random", print_initial_timetable: bool = False) -> Timetable:

    # Load the problem
    logger.info(f"=== Loading the demo data {demo_data_select} ===")
    problem = generate_demo_data(name="my_demo", select=demo_data_select, logger=logger)
    # Visualize the problem
    if print_initial_timetable:
        logger.info("************************** Initial Timetable **************************")
        print_ta_availability(time_table=problem, logger=logger)

    return problem

def create_timetable_from_data_folder(logger: logging.Logger,
                         ta_csv_path: str, shift_csv_path: str, availability_folder: str) -> Timetable:

    try:
        data_constructor = DataConstructor(
                                    ta_csv_path= ta_csv_path,
                                    shift_csv_path= shift_csv_path,
                                    availability_folder= availability_folder,
                                    load= True
                                    )
    except FileNotFoundError:
        logger.error("!!!!!!!!! Data not found. Please check the file paths !!!!!!!!!")
        logger.error("Path to TA csv file: %s", ta_csv_path)
        logger.error("Path to Shift csv file: %s", shift_csv_path)
        logger.error("Path to Availability folder: %s", availability_folder)
        logger.error("current working directory: %s", os.getcwd())
        logger.error("!!!!!!!!! Exiting the program !!!!!!!!!")
        sys.exit(1)

    # Load the problem
    problem = data_constructor.timetable

    return problem

def run_app():
    # Parse command line arguments
    args = get_args()
    # Initialize the logger
    logger = initialize_logger(args.constraint_version)
    # Create the planning problem
    if args.overwrite:
        logger.info("=== Rostering the TAs from a custom location ===")
        problem = create_timetable_from_data_folder(logger=logger, 
                                        ta_csv_path=args.ta_csv_path, 
                                        shift_csv_path=args.shift_csv_path, 
                                        availability_folder=args.availability_folder)
    else:
        logger.info("=== Rostering the TAs from the demo data ===")
        problem = create_timetable_demo(logger=logger,
                            demo_data_select=args.demo_data_select,
                            print_initial_timetable=True if args.demo_data_select == "demo_data_weekly_scheduling-random" else False)
    # Solve the problem
    solution = solve_problem(problem=problem, constraint_version=args.constraint_version, logger=logger)
    # Explain the solution (analysis) TODO
    

if __name__ == '__main__':
    try:
        run_app()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        print("Exiting the program. Goodbye!")
        sys.exit(0)