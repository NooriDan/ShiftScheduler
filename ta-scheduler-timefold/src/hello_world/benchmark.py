import random
import logging
import pickle
import argparse
import datetime
import sys, os
import json

from dataclasses    import dataclass, asdict
from pathlib        import Path
from copy           import deepcopy
from typing         import List, Dict, Any, Tuple, Optional, Type
from abc            import ABC, abstractmethod
from datetime       import timedelta
from io             import TextIOWrapper

from timefold.solver.score  import ScoreAnalysis

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA, ConstraintParameters
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

@dataclass
class BenchmarkConfig:
    num_of_runs         : int
    random_seed         : int
    use_config_xml      : bool
    path_to_config_xml  : str | Path

class BenchmarkRunnerBase(ABC):
    def __init__(self, path_to_benchmark_config: str | Path = "configs/benchmark_config.json"):
        self.path_to_benchmark_config = path_to_benchmark_config
        self.args   = get_args()
        self.logger = initialize_logger(self.args)
        self.config_data = self._load_config()

        # Create objects with the config data
        self.benchmark_config  = BenchmarkConfig( 
            **self.config_data["BenchmarkConfig"]
        )

        self.solver = TimetableSolverWithSolverManager(
            logger=self.logger,
            **self.config_data["TimetableSolver"]
        )

        self.generator = RandomTimetableGenerator(
            name=self.args.demo_data_select,
            logger=self.logger,
            randomization_params=ProblemRandomizationParameters(**self.config_data["randomization_params"]),
            **self.config_data["RandomTimetableGenerator"]
        )

        # Benchmark Obserbations
        self.iterations:        List[Dict[str, Any]]    = []
        self.solutions:         List[Timetable]         = []

        # Save Path
        self.timestamp          = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.results_base_dir   = Path(f"results/{self.config_data['TimetableSolver']['constraint_version']}/{self.timestamp}")
        self.results_base_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        with open(self.path_to_benchmark_config, "r") as f:
            return json.load(f)
    
    def run(self):
        seed = self.benchmark_config.random_seed
        self.logger.info(f"Running the TA Rostering Program with seed: {seed}")

        for iteration_index in range(self.benchmark_config.num_of_runs):
            self.logger.info(f"Iteration {iteration_index + 1} / {self.benchmark_config.num_of_runs}")
            self.logger.info("=================================================================")

            solution, score_analysis, metadata = self._run_iteration()
            self._add_iteration(iteration_index=iteration_index, solution=solution, score_analysis=score_analysis, metadata=metadata)

            self.logger.info("=================================================================")
            self.logger.info(f"End of iteration {iteration_index + 1} / {self.benchmark_config.num_of_runs}\n")

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
                    "seed": self.benchmark_config.random_seed,
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

        solutions_pkl_path  = self.dump_objects_to_pickle()
        benchmark_json_path = self.dump_benchmark_results_to_json()

        self.logger.info("📦 Benchmark results saved to:")
        self.logger.info(f"\t📄 JSON: {benchmark_json_path}")
        self.logger.info(f"\t🧪 PKL : {solutions_pkl_path}")

    # The following is extended in the parent class
    def dump_objects_to_pickle(self) -> Path:
        solutions_pkl_path = self.results_base_dir / "solutions.pkl"
        with open(solutions_pkl_path, "wb") as f:
            pickle.dump(self.solutions, f)
        return solutions_pkl_path
    
    def dump_benchmark_results_to_json(self) -> Path:
        benchmark_results = {
            "timestamp"             : self.timestamp,
            "logger"                : create_logger_info(self.logger.parent),
            "benchmark_config"      : self.benchmark_config.__dict__,
            "generator"             : {
                "name"                      : self.generator.name,
                "constraint_params"         : self.generator.constraint_params.__dict__,
                "ta_names"                  : self.generator.ta_names,
                "config"                    : self.generator.randomization_params.__dict__,
                "num_of_weeks"              : self.generator.num_of_weeks,
                "num_shifts_per_week"       : self.generator.num_shifts_per_week,
                "ta_demands"                : self.generator.ta_demands,
                "ta_demands_weekly"         : self.generator.ta_demands_weekly,
                "allow_different_weekly_availability": self.generator.allow_different_weekly_availability,
                } ,
            "iterations"            : self.iterations, # this is where the timetable is and solver results are stored.
        }

        benchmark_json_path = self.results_base_dir / "benchmark_results.json"
        with open(benchmark_json_path, "w") as f:
            json.dump(benchmark_results, f, indent=4)
        
        return benchmark_json_path


class BenchmarkRunnerWithDatabase(BenchmarkRunnerBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Members only relevant for this subclass
        self.problem_database:  Optional[SchedulingProblemDatabase] = None  # Init empty

    def run(self):
        "run_with_problem_database"
        seed = self.benchmark_config.random_seed
        self.logger.info(f"Running the TA Rostering Program with seed: {seed}")

        num_runs = self.benchmark_config.num_of_runs

        # Generate and solve all problems upfront
        self.problem_database = SchedulingProblemDatabase.generate_and_solve_problems(
            generator=self.generator,
            solver=self.solver,
            constraint_params=self.generator.constraint_params,
            num_problems=num_runs,
            logger=self.logger
        )

        for iteration_index, scheduling_problem in enumerate(self.problem_database.problem_sets):
            self.logger.info(f"adding the Iteration {iteration_index + 1} / {num_runs}")
            self.logger.info("=================================================================")

            if self.problem_database.solutions is None:
                self.logger.info(f"!!! skipping {iteration_index} because the solution is None type")
                continue

            metadata        = {key : val for key, val in asdict(scheduling_problem).items() if key != "problem"}  # Add metadata if you want to track from generator or elsewhere
            solution        = self.problem_database.solutions[iteration_index]
            score_analysis  = self.solver.post_process_solution(solution=solution, log_analysis=False)

            self._add_iteration(
                iteration_index=iteration_index,
                solution=solution,
                score_analysis=score_analysis,
                metadata=metadata
            )

            self.logger.info("=================================================================")
            self.logger.info(f"End of iteration {iteration_index + 1} / {num_runs}\n")

        self.problem_database.sort_problems_by_difficulty(increasing=True)
        self._save_results()
        self.logger.info("🏁 Benchmark completed successfully!")

    # Overwrites the parent's method
    def dump_objects_to_pickle(self):
        if self.problem_database is None:
            raise ValueError("need to create a problem_database by calling run() or load() method")  
        solutions_pkl_path = self.results_base_dir / "baseline.pkl"
        with open(solutions_pkl_path, "wb") as f:
            pickle.dump({
            "problem_database"  : self.problem_database.problem_sets,
            "solutions"         : self.solutions
            }, f)
        return solutions_pkl_path        

@dataclass
class SchedulingProblem:
    problem: Timetable

    best_score_hard:    int
    best_score_medium:  int
    best_score_soft:    int

    num_of_tas:         int
    num_of_shifts:      int
    num_of_weeks:       int

    num_of_desired_shifts:              int
    num_of_unique_desired_shifts:       int

    num_of_undesired_shifts:            int
    num_of_unique_undesired_shifts:     int

    num_of_unavailable_shifts:          int
    num_of_unique_unavailable_shifts:   int

    avg_desired_shifts_per_ta:  float = 0.0
    ta_to_shift_ratio:          float = 0.0
    solve_time_seconds:         int = 0
    difficulty_label:           str = "unknown"

    @classmethod
    def from_timetable(
        cls:        Type["SchedulingProblem"],
        timetable:  Timetable,
        score:      Tuple[int, int, int] = (0, 0, 0),
        solve_time_seconds: int = 0,
        difficulty_label:   Optional[str] = None,
    ) -> "SchedulingProblem":
        tas = timetable.tas
        shifts = timetable.shifts

        num_tas = len(tas)
        num_shifts = len(shifts)
        num_weeks = len(set(shift.week_id for shift in shifts))

        all_desired     = [shift.id for ta in tas for shift in ta.desired]
        all_undesired   = [shift.id for ta in tas for shift in ta.undesired]
        all_unavailable = [shift.id for ta in tas for shift in ta.unavailable]

        unique_desired      = set(all_desired)
        unique_undesired    = set(all_undesired)
        unique_unavailable  = set(all_unavailable)

        avg_desired_per_ta = len(all_desired) / num_tas if num_tas > 0 else 0.0
        avg_desired_per_ta = round(avg_desired_per_ta, 2)

        ta_to_shift_ratio = num_tas / num_shifts if num_shifts > 0 else 0.0
        ta_to_shift_ratio = round(ta_to_shift_ratio, 2)

        # Auto-assign difficulty label if not provided
        hard, medium, soft = score
        if difficulty_label is None:
            if hard < 0:
                difficulty = "hard"
            elif medium < 0:
                difficulty = "medium"
            elif soft < 0:
                difficulty = "soft"
            else:
                difficulty = "easy"
        else:
            difficulty = difficulty_label

        return cls(
            problem=timetable,
            best_score_hard=hard,
            best_score_medium=medium,
            best_score_soft=soft,

            num_of_tas=num_tas,
            num_of_shifts=num_shifts,
            num_of_weeks=num_weeks,

            num_of_desired_shifts=len(all_desired),
            num_of_unique_desired_shifts=len(unique_desired),
            num_of_undesired_shifts=len(all_undesired),
            num_of_unique_undesired_shifts=len(unique_undesired),
            num_of_unavailable_shifts=len(all_unavailable),
            num_of_unique_unavailable_shifts=len(unique_unavailable),

            avg_desired_shifts_per_ta=avg_desired_per_ta,
            ta_to_shift_ratio=ta_to_shift_ratio,
            solve_time_seconds=solve_time_seconds,
            difficulty_label=difficulty
        )

@dataclass
class SchedulingProblemDatabase:
    problem_sets        : List[SchedulingProblem]
    constraint_params   : ConstraintParameters
    logger              : logging.Logger
    solutions           : Optional[List[Timetable]] = None

    def sort_problems_by_difficulty(self, increasing: bool = True):
        """Performs in-place sorting on the problem sets by increasing difficulty:
        First by hard score (lowest first), then medium, then soft.
        """
        self.problem_sets.sort(
            key=lambda p: (
                p.best_score_hard,     # Most critical
                p.best_score_medium,
                p.best_score_soft      # Least critical
            ),
            reverse=increasing
        )

    @classmethod
    def generate_random_problems(
        cls,
        generator: "RandomTimetableGenerator",
        constraint_params: ConstraintParameters,
        num_problems: int,
        logger: logging.Logger,
        ) -> "SchedulingProblemDatabase":

        problems : List[SchedulingProblem] = []

        for i in range(num_problems):
            logger.info(f"Generating random problem {i + 1} / {num_problems}")
            timetable, generation_metadata = generator.gen_demo_data()
            scheduling_problem = SchedulingProblem.from_timetable(timetable)
            problems.append(scheduling_problem)

        return cls(problem_sets=problems, constraint_params=constraint_params, logger=logger)
    
    @classmethod
    def generate_and_solve_problems(
        cls,
        generator: "RandomTimetableGenerator",
        solver: "TimetableSolverWithSolverManager",
        constraint_params: ConstraintParameters,
        num_problems: int,
        logger: logging.Logger,
    ) -> "SchedulingProblemDatabase":
        
        problems           : List[SchedulingProblem] = []
        solutions          : List[Timetable]         = []
        for i in range(num_problems):
            logger.info(f"Generating and solving problem {i + 1} / {num_problems}")

            timetable, generation_metadata = generator.gen_demo_data()

            # Solve the problem to get solution and score
            solution       = solver.solve_problem(problem=timetable)
            score_analysis = solver.post_process_solution(solution=solution)

            # Extract scores as integers (adapt as needed)
            hard_score      = int(solution.score.hard_score)
            medium_score    = int(solution.score.medium_score)
            soft_score      = int(solution.score.soft_score)

            # Create SchedulingProblem with score and solve time (if available)
            scheduling_problem = SchedulingProblem.from_timetable(
                timetable=timetable,
                score=(hard_score, medium_score, soft_score),
                solve_time_seconds=solver.get_solver_job(index=-1).get_solving_duration().seconds,
                difficulty_label=None
            )

            problems.append(scheduling_problem)
            solutions.append(solution)

        return cls(
            problem_sets=problems, 
            solutions=solutions,
            constraint_params=constraint_params, 
            logger=logger
            )

    def save_as_pickle(self, path: Path):
        """
        Save the full SchedulingProblemDatabase as a pickle file.

        Args:
            path (Path): The full path to save the pickle file to (e.g., Path("data/problems.pkl"))
        """
        path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        with open(path, "wb") as f:
            pickle.dump(self, f)

        print(f"✅ SchedulingProblemDatabase saved to: {path}")

    @classmethod
    def load_from_pickle(cls, path: Path) -> "SchedulingProblemDatabase":
        with open(path, "rb") as f:
            return pickle.load(f)

        
def run_benchmark() -> None:
    # BenchmarkRunnerBase().run()
    BenchmarkRunnerWithDatabase().run()

if __name__ == "__main__":
    # Run the benchmark
    run_benchmark()
    
    # Exit the program
    sys.exit(0)