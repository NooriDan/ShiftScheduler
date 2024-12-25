from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory

import argparse
import logging
import sys, os

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import define_constraints
from hello_world.demo_data   import generate_demo_data
from hello_world.utils       import print_timetable, initialize_logger, DataConstructor


def run_demo(solver_factory: SolverFactory, logger: logging.Logger):

    # Load the problem
    problem = generate_demo_data()

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    logger.info("************************** Final Timetable **************************")
    print_timetable(time_table=solution, logger=logger)

    return solution


def run_from_data_folder(solver_factory: SolverFactory,  logger: logging.Logger,
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

    # Initialize the logger
    logger = initialize_logger()

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    logger.info("************************** Final Timetable **************************")
    print_timetable(time_table=solution, logger=logger)

    return solution

def run_app():
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
    
    args = parser.parse_args()

    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=Timetable,
            entity_class_list=[ShiftAssignment],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            ),
            termination_config=TerminationConfig(
                # The solver runs only for 5 seconds on this small dataset.
                # It's recommended to run for at least 5 minutes ("5m") otherwise.
                spent_limit=Duration(seconds=5)
            )
            )
        )
    
    # initialize the logger
    logger = initialize_logger()
    
    if args.overwrite:
        logger.info("=== Rostering the TAs from a custom location ===")
        solution = run_from_data_folder(solver_factory= solver_factory, 
                                        logger=logger, 
                                        ta_csv_path=args.ta_csv_path, 
                                        shift_csv_path=args.shift_csv_path, 
                                        availability_folder=args.availability_folder)
        logger.info("=== Done Solving ===")
        

    else:
        logger.info("=== Rostering the TAs from the demo data ===")
        solution = run_demo(solver_factory=solver_factory, 
                            logger=logger)
        logger.info("=== Done Solving ===")

if __name__ == '__main__':
    run_app()
