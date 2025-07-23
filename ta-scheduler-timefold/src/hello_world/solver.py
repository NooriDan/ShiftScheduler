import argparse
import logging
import sys, os

from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory, SolutionManager, Solver, SolverStatus

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import constraints_provider_dict
from hello_world.utils       import print_timetable

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
            spent_limit = Duration(minutes=0, seconds=30),
            # unimproved_spent_limit= Duration(seconds=30)
        )
        )
    return solver_config

def solve_problem(problem: Timetable, constraint_version: str, logger: logging.Logger) -> Timetable:
    logger.info("=== Starting to Solve the proble ===")
    # Create the solver configuration
    solver_config  = create_solver_config(constraint_version)
    # Create the solver factory
    solver_factory = SolverFactory.create(solver_config)
    
    # Solve the problem
    solution_manager = SolutionManager.create(solver_factory=solver_factory)
    solver   = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    logger.info("************************** Final Timetable **************************")
    print_timetable(time_table=solution, logger=logger)

    logger.info("=======================================================")
    logger.info("calling solver.explain to analyze the constraints")
    logger.info("=======================================================")
    logger.info(solution_manager.explain(solution=solution))
    
    logger.info("=== Done Solving ===")
    return solution
