import random
import logging
import pickle
import argparse
import datetime
import sys, os
import json

from pathlib import Path
from copy import deepcopy
from typing import List, Dict, Any, Tuple
from dataclasses import asdict

from timefold.solver.score  import ScoreAnalysis


from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.demo_data   import RandomTimetableGenerator, ProblemRandomizationParameters
from hello_world.utils       import print_ta_availability, initialize_logger, create_logger_info
from hello_world.solver      import TimetableSolverBlocking, TimetableSolverWithSolverManager


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the TA Rostering Program in Terminal')
    
    parser.add_argument('--constraint_version',
                        type=str,
                        choices=['default', 'tabriz'],
                        help='Choose the constraint version to use',
                        default='default')
    
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='enable overwrite [not implemented yet]',
                        default=False)
    
    parser.add_argument('--demo_data_select',
                    type=str,
                    choices=list(['benchmark-weekly', 'benchmark-semester']),
                    help='Select the demo data to use',
                    default='benchmark-weekly')

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

def process_score_analysis(score_analysis: ScoreAnalysis) -> Any:

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


def run_benchmark():
    # standard library
    # Parse command line arguments
    args = get_args()
    # Initialize the logger
    logger = initialize_logger(args)

    # 1. Load config JSON file
    with open("configs/benchmark_config.json", "r") as f:
        config_data = json.load(f)

    benchmark_config    = config_data["BenchmarkConfig"]
    global_seed         = benchmark_config["random_seed"]
    
    logger.info(f"Running the TA Rostering Program with seed: {global_seed}")

    # create the solver
    solver = TimetableSolverWithSolverManager(logger=logger, **config_data["TimetableSolver"])

    # Create random data generator
    randomization_params = ProblemRandomizationParameters(**config_data["ProblemRandomizationParameters"])
    print(f"Randomization Parameters: {randomization_params}")

    generator = RandomTimetableGenerator(
        name=args.demo_data_select,
        randomization_params=randomization_params,
        logger=logger,
        **config_data["RandomTimetableGenerator"]
    )

    iterations : List[Dict[str, Any]] = []
    solutions:   List[Timetable] = []
    # Create the planning problem
    for i in range(config_data["BenchmarkConfig"]["num_of_runs"]):
        logger.info(f"iteration {i+1} / {config_data['BenchmarkConfig']['num_of_runs']}")
        logger.info("=================================================================")

        logger.info("Creating the planning problem...")
        problem, metadata = generator.gen_demo_data()

        logger.info("************************** Initial Timetable **************************")
        print_ta_availability(time_table=deepcopy(problem), logger=logger)
        logger.info("************************** /Initial Timetable **************************")

        solution = solver.solve_problem(problem=problem)

        score_analysis = solver.post_process_solution(solution=solution)

        iterations.append({
            "iteration" : {
                "id"        : i,
                "seed"      : global_seed,
                "problem_metadata": metadata,
                "score"     : str(solution.score),
                "score_analysis": {
                    "summary"       : score_analysis.summary,
                    "constraint_map": {
                        constraint_ref.constraint_id: {
                            "score"         : str(constraint_analysis.score),
                            "match_count"   : constraint_analysis.match_count,
                            # "matches": [
                            #     {
                            #         "score": str(match_analysis.score),
                            #         "justification": str(match_analysis.justification)
                            #     } for match_analysis in constraint_analysis.matches
                            # ]
                        } for constraint_ref, constraint_analysis in score_analysis.constraint_map.items()
                    }
                }
            }
        })

        solutions.append(solution)

        logger.info("=================================================================")
        logger.info(f"end of iteration ... {i+1} / {config_data['BenchmarkConfig']['num_of_runs']}\n")

    # Generate timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    constraint_version = config_data["TimetableSolver"]["constraint_version"]

    # Base directory for this run
    base_results_dir = Path(f"results/{constraint_version}/{timestamp}")
    base_results_dir.mkdir(parents=True, exist_ok=True)

    # Define result file paths
    solutions_pkl_path = base_results_dir / "solutions.pkl"
    benchmark_results_json_path = base_results_dir / "benchmark_results.json"

    # Build results dict
    benchmark_results : Dict[str, Any] = {
        "timestamp": timestamp,
        "logger": create_logger_info(logger.parent),
        "benchmark_config": benchmark_config,
        "randomization_params": asdict(randomization_params),
        "iterations": iterations,
    }

    # Save solutions (Pickle)
    with open(solutions_pkl_path, "wb") as f:
        pickle.dump(solutions, f)

    # Save metadata/results (JSON)
    with open(benchmark_results_json_path, "w") as f:
        json.dump(benchmark_results, f, indent=4)

    # Log final message
    logger.info("📦 Benchmark results saved to:")
    logger.info(f"\t📄 JSON: {benchmark_results_json_path}")
    logger.info(f"\t🧪 PKL : {solutions_pkl_path}")

    logger.info("🏁 Benchmark completed successfully!")

if __name__ == "__main__":
    # Run the benchmark
    run_benchmark()
    
    # Exit the program
    sys.exit(0)