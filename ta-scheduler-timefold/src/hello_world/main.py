from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory

import argparse
import logging
import sys, os

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import constraints_provider_dict
from hello_world.demo_data   import generate_demo_data, _generate_demo_data_dict
from hello_world.utils       import print_timetable, initialize_logger, DataConstructor

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

def create_solver_config(constraint_version: str) -> SolverConfig:
    """ Create the solver configuration based on the constraint version """
    if constraint_version not in constraints_provider_dict:
        raise ValueError(f"Invalid constraint version: {constraint_version}. "
                         f"Available versions: {list(constraints_provider_dict.keys())}")
    # Get the appropriate constraints provider function
    constraints_provider_function = constraints_provider_dict[constraint_version]
    # Create the solver configuration
    solver_config = SolverConfig(
        solution_class=Timetable,
        entity_class_list=[ShiftAssignment],
        score_director_factory_config=ScoreDirectorFactoryConfig(
            constraint_provider_function= constraints_provider_function
        ),
        termination_config=TerminationConfig(
            # The solver runs only for 5 seconds on this small dataset.
            # It's recommended to run for at least 5 minutes ("5m") otherwise.
            spent_limit = Duration(seconds=40),
            unimproved_spent_limit= Duration(seconds=5)
        )
        )
    return solver_config

def create_timetable_demo(solver_factory: SolverFactory, logger: logging.Logger, demo_data_select: str = "demo_data_weekly_scheduling-random", print_initial_timetable: bool = False) -> Timetable:

    # Load the problem
    logger.info(f"=== Loading the demo data {demo_data_select} ===")
    problem = generate_demo_data(name="my_demo", select=demo_data_select)
    # Visualize the problem
    if print_initial_timetable:
        logger.info("************************** Initial Timetable **************************")
        print_timetable(time_table=problem, logger=logger)

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    logger.info("************************** Final Timetable **************************")
    print_timetable(time_table=solution, logger=logger)

    return solution

def create_timetable_from_data_folder(solver_factory: SolverFactory,  logger: logging.Logger,
                         ta_csv_path: str, shift_csv_path: str, availability_folder: str):

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

    # # Initialize the logger
    # logger = initialize_logger()

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    logger.info("************************** Final Timetable **************************")
    print_timetable(time_table=solution, logger=logger)

    return solution

def run_app():

    # Parse command line arguments
    args = get_args()

    # Create the solver configuration
    solver_config  = create_solver_config(args.constraint_version)
    # Create the solver factory
    solver_factory = SolverFactory.create(solver_config)

    # initialize the logger
    logger = initialize_logger(args.constraint_version)
    
    if args.overwrite:
        logger.info("=== Rostering the TAs from a custom location ===")
        solution = create_timetable_from_data_folder(solver_factory= solver_factory, 
                                        logger=logger, 
                                        ta_csv_path=args.ta_csv_path, 
                                        shift_csv_path=args.shift_csv_path, 
                                        availability_folder=args.availability_folder)
        logger.info("=== Done Solving ===")

    else:
        logger.info("=== Rostering the TAs from the demo data ===")
        solution = create_timetable_demo(solver_factory=solver_factory, 
                            logger=logger,
                            demo_data_select=args.demo_data_select,
                            print_initial_timetable=True if args.demo_data_select == "demo_data_weekly_scheduling-random" else False)
        logger.info("=== Done Solving ===")

if __name__ == '__main__':
    try:
        run_app()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        print("Exiting the program. Goodbye!")
        sys.exit(0)