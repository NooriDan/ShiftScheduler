import random
import argparse
import logging
import sys, os

from copy import deepcopy

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.demo_data   import generate_demo_data_with_default_params, _generate_demo_data_dict
from hello_world.utils       import print_ta_availability, initialize_logger
from hello_world.solver      import TimetableSolverBlocking, TimetableSolverWithSolverManager
# Constants for random shift generation
SEED = random.randint(0, 1000000)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the TA Rostering Program in Terminal')
    
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

    parser.add_argument('--solving_method', 
                        type=str, 
                        choices=["solver_manager", "blocking", "tqdm"],
                        help='the solver instantiation method',
                        default='solver_manager')
    
    parser.add_argument('--use_config_xml',
                        action='store_true',
                        help='uses the solver_config.xml file to configure the solver',
                        default=False)
    
    parser.add_argument('--path_to_config_xml',
                        type=str, 
                        help='the relative path to the solver_config.xml file to configure the solver',
                        default=None)
    
    args = parser.parse_args()

    return args


def run_benchmark():
    # standard library
    random.seed(SEED)
    # Parse command line arguments
    args = get_args()
    # Initialize the logger
    logger = initialize_logger(args)
    logger.info(f"Running the TA Rostering Program with seed: {SEED}")

    # Create the planning problem
    problem = create_the_problem(logger=logger, args=args)
    
    # Solve the problem
    solver = TimetableSolverWithSolverManager(constraint_version=args.constraint_version,
                                                random_seed=SEED,
                                                use_config_xml=args.use_config_xml,
                                                path_to_config_xml=args.path_to_config_xml,
                                                logger=logger)
    
    solution = solver.solve_problem(problem=problem)

    # Explain the solution (analysis) TODO