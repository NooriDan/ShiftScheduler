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

class BenchmarkRunner:
    def __init__(self):
        self.args   = get_args()
        self.logger = initialize_logger(self.args)
        self.config_data = self._load_config()
        self.benchmark_config = self.config_data["BenchmarkConfig"]

        self.randomization_params = ProblemRandomizationParameters(
            **self.config_data["ProblemRandomizationParameters"]
        )

        self.solver = TimetableSolverWithSolverManager(
            logger=self.logger,
            **self.config_data["TimetableSolver"]
        )

        self.generator = RandomTimetableGenerator(
            name=self.args.demo_data_select,
            randomization_params=self.randomization_params,
            logger=self.logger,
            **self.config_data["RandomTimetableGenerator"]
        )
        self.iterations: List[Dict[str, Any]] = []
        self.solutions: List[Timetable] = []
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.results_base_dir = Path(f"results/{self.config_data['TimetableSolver']['constraint_version']}/{self.timestamp}")
        self.results_base_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        with open("configs/benchmark_config.json", "r") as f:
            return json.load(f)
    
    def run(self):
        seed = self.benchmark_config["random_seed"]
        self.logger.info(f"Running the TA Rostering Program with seed: {seed}")

        for iteration_index in range(self.benchmark_config["num_of_runs"]):
            self.logger.info(f"Iteration {iteration_index + 1} / {self.benchmark_config['num_of_runs']}")
            self.logger.info("=================================================================")

            solution, score_analysis, metadata = self._run_iteration()
            self._add_iteration(iteration_index=iteration_index, solution=solution, score_analysis=score_analysis, metadata=metadata)

            self.logger.info("=================================================================")
            self.logger.info(f"End of iteration {iteration_index + 1} / {self.benchmark_config['num_of_runs']}\n")

        self._save_results()
        self.logger.info("🏁 Benchmark completed successfully!")

    def _run_iteration(self) -> Tuple[Timetable, ScoreAnalysis, Dict[str, Any]]:
        self.logger.info("Creating the planning problem...")
        problem, metadata = self.generator.gen_demo_data()

        self.logger.info("************************** Initial Timetable **************************")
        print_ta_availability(time_table=deepcopy(problem), logger=self.logger)
        self.logger.info("************************** /Initial Timetable **************************")

        solution        = self.solver.solve_problem(problem=problem)
        score_analysis  = self.solver.post_process_solution(solution=solution)

        return solution, score_analysis, metadata
        
    def _add_iteration(self, iteration_index: int, solution: Timetable, score_analysis: ScoreAnalysis, metadata: Dict[str, Any]):
        self.iterations.append({
            "iteration": {
                "id": iteration_index,
                "score": str(solution.score),
                "iteration_metadata": {
                    "seed": self.benchmark_config["random_seed"],
                    "metadata" : metadata,
                    "score_analysis": {
                        "summary": score_analysis.summary,
                        "constraint_map": {
                            constraint_ref.constraint_id: {
                                "score": str(analysis.score),
                                "match_count": analysis.match_count
                            } for constraint_ref, analysis in score_analysis.constraint_map.items()
                        }
                    }
                }
            }
        })

        self.solutions.append(solution)

    def _save_results(self):
        solutions_pkl_path = self.results_base_dir / "solutions.pkl"
        benchmark_json_path = self.results_base_dir / "benchmark_results.json"

        benchmark_results = {
            "timestamp": self.timestamp,
            "logger": create_logger_info(self.logger.parent),
            "benchmark_config": self.benchmark_config,
            "randomization_params": self.randomization_params.__dict__,
            "iterations": self.iterations,
        }

        with open(solutions_pkl_path, "wb") as f:
            pickle.dump(self.solutions, f)

        with open(benchmark_json_path, "w") as f:
            json.dump(benchmark_results, f, indent=4)

        self.logger.info("📦 Benchmark results saved to:")
        self.logger.info(f"\t📄 JSON: {benchmark_json_path}")
        self.logger.info(f"\t🧪 PKL : {solutions_pkl_path}")

def run_benchmark() -> None:
    BenchmarkRunner().run()

if __name__ == "__main__":
    # Run the benchmark
    run_benchmark()
    
    # Exit the program
    sys.exit(0)