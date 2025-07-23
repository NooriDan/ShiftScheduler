import argparse
import logging
import sys, os
import uuid

from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory, SolutionManager, Solver, SolverManager, SolverStatus

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
    """Wrapper for the solve methods"""
    # solution = solve_problem_blocking(problem=problem, constraint_version=constraint_version, logger=logger)
    solution = solve_problem_with_manager(problem=problem, constraint_version=constraint_version, logger=logger)
    return solution

def solve_problem_with_manager(problem: Timetable, constraint_version: str, logger: logging.Logger) -> Timetable:
    logger.info("=== Starting to Solve the problem (SolverManager) ===")
    
    # 1) Build SolverConfig and SolverFactory
    solver_config = create_solver_config(constraint_version)
    solver_factory = SolverFactory.create(solver_config)
    solver_manager = SolverManager.create(solver_factory)
    
    # 2) Choose a unique problem ID
    problem_id = str(uuid.uuid4())
    
    # 3) Run the solver asynchronously and retrieve the best solution
    solver_job = solver_manager.solve_builder() \
        .with_problem_id(problem_id) \
        .with_problem(problem) \
        .run()   # <- Run is required here!
        # more optional setting:
        # .with_first_initialized_solution_consumer(on_first_solution_changed) \
        # .with_best_solution_consumer(on_best_solution_changed) \
        # .with_final_best_solution_consumer(on_final_solution_changed) \
        # .with_exception_handler(on_exception_handler) \
        # .with_config_override(config_override) \

    # while solver_job.get_solver_status != SolverStatus.<name-of-status>

    solution: Timetable = solver_job.get_final_best_solution()

     
    # 4) Visualize final solution
    logger.info("=== Final timetable ===")
    print_timetable(time_table=solution, logger=logger)
    
    # 5) Post-process
    solution = post_process_solution(solution=solution, solver_factory=solver_factory, logger=logger)
    
    logger.info("=== Done Solving ===")
    return solution

def solve_problem_blocking(problem: Timetable, constraint_version: str, logger: logging.Logger) -> Timetable:
    logger.info("=== Starting to Solve the proble ===")
    # Create the solver configuration
    solver_config  = create_solver_config(constraint_version)
    # Create the solver factory
    solver_factory = SolverFactory.create(solver_config)
    
    # Solve the problem
    solver   = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    logger.info("************************** Final Timetable **************************")
    print_timetable(time_table=solution, logger=logger)

    solution_manager = post_process_solution(solution=solution, solver_factory=solver_factory, logger=logger)

    logger.info("=== Done Solving ===")
    return solution

def post_process_solution(solution: Timetable, solver_factory: SolverFactory, logger: logging.Logger) -> SolutionManager:
    solution_manager = SolutionManager.create(solver_factory=solver_factory)
    logger.info("=======================================================")
    logger.info("calling solver.explain to explain the constraints")
    logger.info("=======================================================")
    score_explanation = solution_manager.explain(solution=solution)
    print(score_explanation.summary)

    logger.info("=======================================================")
    logger.info("calling solver.analyze to explain the constraints")
    logger.info("=======================================================")
    score_analysis = solution_manager.analyze(solution=solution)
    print(score_analysis.summary)

    # When you have the ScoreAnalysis instance, you can find out which constraints are broken:
    for constraint_ref, constraint_analysis in score_analysis.constraint_map.items():
        constraint_id           = constraint_ref.constraint_id
        score_per_constraint    = constraint_analysis.score

        match_count = constraint_analysis.match_count
        # If you wish to go further and find out which planning entities and problem facts are responsible for breaking the constraint, 
        # you can further explore the ConstraintAnalysis instance you received from ScoreAnalysis.constraintMap():
        for match_analysis in constraint_analysis.matches:
            score_per_match = match_analysis.score
            justification = match_analysis.justification
            
   
    # logger.info(solution_manager.analyze(solution=solution))

    return solution_manager

def visualize_hot_planning_vars(solution: Timetable, solver_factory: SolverFactory, logger: logging.Logger):
    solution_manager = SolutionManager.create(solver_factory)
    score_explanation = solution_manager.explain(solution)
    indictment_map = score_explanation.indictment_map
    for assignment in solution.shift_assignments:
        indictment = indictment_map.get(assignment)
        if indictment is None:
            continue
        # The score impact of that planning entity
        total_score = indictment.score

        for constraint_match in indictment.constraint_match_set:
            # constraint_name = constraint_match.constraint_name
            score = constraint_match.score
            
