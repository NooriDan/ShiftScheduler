import argparse
import logging
import sys, os
import uuid
import time
from datetime import datetime

from typing     import List, Dict, Callable, Any, Tuple, Optional
from pathlib    import Path
from tqdm       import tqdm
from abc        import ABC, abstractmethod
from functools import partial


from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver        import SolverFactory, SolutionManager, Solver, SolverManager, SolverStatus, SolverJob
from timefold.solver.score  import ScoreAnalysis

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import constraints_provider_dict               # a dictionary mapping constraint versions to their provider functions
from hello_world.utils       import print_timetable

LOOP_WAIT_SECONDS           = 5     # seconds to wait between checking the solver job status
SUPPORTED_SOLVING_METHODS   = ["solver_manager", "blocking", "tqdm"]

class TimetableSolverBase(ABC):
    def __init__(self, 
                 constraint_version: str, 
                 logger: logging.Logger, 
                 random_seed: int | None = None,
                 path_to_config_xml: Path | str | None = None,
                 use_config_xml: bool = False):
        """ Initializes the TimetableSolver with the given parameters."""
        # Store the parameters
        self.constraint_version = constraint_version
        self.random_seed        = random_seed
        self.logger             = logger
        self.path_to_config_xml = Path(path_to_config_xml) if path_to_config_xml else None
        self.use_config_xml     = use_config_xml

        # class constants
        self.default_term_time_budget           : Duration =  Duration(minutes=2, seconds=30)
        self.default_term_unimproved_early_term : Duration =  Duration(seconds=10)

        # attributes to hold the solver configuration and factory
        self.solver_config     : Optional[SolverConfig]  = None
        self.solver_factory    : Optional[SolverFactory] = None

        # Validate the inputs
        self._validate_inputs()
    
    # User-facing methods
    def set_random_seed(self, seed: int):
        """Sets the random seed for the solver."""
        self.random_seed = seed
        if self.solver_config is not None:
            self.solver_config.random_seed = seed
        

    def solve_problem(self, problem: Timetable, log_solution: bool = True) -> Timetable:
        """Wrapper for the solve methods"""
        self._validate_inputs()
        logger = self.logger

        logger.info("\n🚀 === Starting to Solve the Problem ===")
        
        # Solve the problem based on the solving method (extended in child classes)
        solution = self._solve_problem_body(problem=problem)
        logger.info("✅ === Solver Finished Successfully ===")

        # Visualize the final solution
        if log_solution:
            logger.info("\n🗓️ === Final Timetable ===")
            print_timetable(time_table=solution, logger=logger)
            logger.info("🗓️ === /End of Final Timetable ===")
                
        return solution
    
    # Post-processing Methods
    def post_process_solution(self, solution: Timetable, log_analysis: bool = True) -> ScoreAnalysis:
        # Post-process (justification, analysis, etc.)
        logger = self.logger
        logger.info("\n📊 === Post-processing the Solution ===")
        solution_manager = SolutionManager.create(solver_factory=self.solver_factory)

        # logger.info("=======================================================")
        # logger.info("calling solver.explain to explain the constraints")
        # logger.info("=======================================================")
        # score_explanation = solution_manager.explain(solution=solution)
        # logger.info(score_explanation.summary)
        if log_analysis:
            logger.info("=======================================================")
            logger.info("calling solver.analyze to explain the constraints")
            logger.info("=======================================================")
        score_analysis = solution_manager.analyze(solution=solution)

        if log_analysis:
            logger.info(score_analysis.summary)
            
        logger.info("🏁 === Post-processing Complete ===")
        return score_analysis

    def visualize_hot_planning_vars(self, solution: Timetable):
        solution_manager = SolutionManager.create(self.solver_factory)
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
        
    # Solver Configuration Methods
    def _create_solver_config_default(self) -> SolverConfig:
        """ Create the solver configuration based on the constraint version """
        
        # Get the appropriate constraints provider function
        constraints_provider_function = constraints_provider_dict[self.constraint_version]
        
        # Create the solver configuration
        self.solver_config =  SolverConfig(
            random_seed=self.random_seed,
            solution_class=Timetable,
            entity_class_list=[ShiftAssignment],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=constraints_provider_function
            ),
            termination_config=TerminationConfig(
                # The solver runs only for 5 seconds on this small dataset.
                # It's recommended to run for at least 5 minutes ("5m") otherwise.
                spent_limit=self.default_term_time_budget,
                unimproved_spent_limit=self.default_term_unimproved_early_term
            )
        )
        return self.solver_config
    
    def _create_solver_conffig_from_xml(self, path_to_solver_config: Path | str) -> SolverConfig:
        # Valudation
        if path_to_solver_config is not None:
            self.path_to_solver_config = Path(path_to_solver_config)
            self._validate_inputs()
        else:
            raise ValueError("Path to solver config XML must be provided.")
        # Get the appropriate constraints provider function
        constraints_provider_function = constraints_provider_dict[self.constraint_version]
        # Create the solver configuration
        solver_config = SolverConfig.create_from_xml_resource(path=self.path_to_solver_config)
        # specify the domain's classes/functions
        solver_config.solution_class = Timetable
        solver_config.entity_class_list = [ShiftAssignment]
        solver_config.score_director_factory_config = ScoreDirectorFactoryConfig(
                constraint_provider_function= constraints_provider_function
            )
        if self.random_seed is not None:
            solver_config.random_seed = self.random_seed

        # update local attributes
        self.solver_config = solver_config
        return self.solver_config
    
    # Abstract Methods
    @abstractmethod
    def _solve_problem_body(self, problem: Timetable) -> Timetable:
        """Abstract method. Must be implemented in child classes."""
        pass
    
    # Optional Override
    def _validate_inputs(self):
        """ Validates the inputs provided to the solver."""
        # validate constraint_version
        if self.constraint_version not in constraints_provider_dict:
            raise ValueError(f"Invalid constraint version: {self.constraint_version}. "
                             f"Available versions: {list(constraints_provider_dict.keys())}")
        # validate path_to_config
        if (self.path_to_config_xml and not Path(self.path_to_config_xml).exists()):
            raise FileNotFoundError(f"The specified path to the solver config does not exist: {self.path_to_config_xml}")
        if self.use_config_xml and not self.path_to_config_xml:
            raise ValueError("When use_config_xml is True, path_to_config must be provided.")
        
    def create_solver(self):
        """ Create the solver configuration based on the constraint version """
        self._validate_inputs()

        # Build SolverConfig and SolverFactory
        self.logger.info("\t⚙️  Creating SolverConfig and SolverFactory...")
        if self.use_config_xml:
            self.solver_config =  self._create_solver_conffig_from_xml(path_to_solver_config=self.path_to_config_xml)
        else:
            self.solver_config =  self._create_solver_config_default()

        self.solver_factory = SolverFactory.create(self.solver_config)

        self.logger.info("✅ === SolverConfig and SolverFactory Created Successfully ===")

class TimetableSolverBlocking(TimetableSolverBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Members only relevant for this subclass
        self.solver: Solver

    # ----------------------------
    # Abstract methods
    # ----------------------------
    def create_solver(self):
        super().create_solver()
        self.solver      = self.solver_factory.build_solver()
       
    def _solve_problem_body(self, problem: Timetable) -> Timetable:
        if self.solver_config is None or self.solver_factory is None or self.solver is None:
            self.logger.info("calling create_solver() method")
            self.create_solver()

        self.logger.info("Solving with blocking solver...")
        solver : Solver = self.solver
        solution    = solver.solve(problem=problem)
        return solution

class TimetableSolverWithSolverManager(TimetableSolverBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Members only relevant for this subclass
        self._solver_manager    : SolverManager
        self._job_id_list       : List[SolverJob]  = []
        self.latest_solutions_by_job_id_dict   : Dict[str, List[Timetable]] = {}

    # ----------------------------
    # Abstract methods
    # ----------------------------
    def create_solver(self) -> None:
        """Creates a solver manager to handle solve requests"""
        super().create_solver()
        # 1) Create the solver manager
        self.logger.info("=== Creating the SolverManager ===")
        self._solver_manager = SolverManager.create(self.solver_factory)

    def _solve_problem_body(self, problem: Timetable) -> Timetable:
        logger = self.logger

        if self.solver_config is None or self.solver_factory is None or self._solver_manager is None:
            self.logger.info("calling create_solver() method")
            self.create_solver()

        # 1) Create a unique problem ID
        problem_id = str(uuid.uuid4())
        
        # 2) Run the solver asynchronously and retrieve the best solution
        callback = partial(self._on_best_solution_changed, problem_id)      # this converts _on_best_solution_changed(self, problem_id: str, sol: Timetable) -> callback(sol: Timetable), pre-filling some fields in the original method
        logger.info("Requesting the SolverManager to create a SolverJob...")
        solver_job = self._solver_manager.solve_builder() \
            .with_problem_id(problem_id) \
            .with_problem(problem) \
            .with_best_solution_consumer(callback) \
            .run()   # <- Run is required here!
            # more optional setting:
            # .with_first_initialized_solution_consumer(on_first_solution_changed) \
            # .with_final_best_solution_consumer(on_final_solution_changed) \
            # .with_exception_handler(on_exception_handler) \
            # .with_config_override(config_override) \
        logger.info(f"\t✅ SolverJob created {solver_job.get_problem_id()} id\n")
        
        self._job_id_list.append(solver_job)

        # while solver_job.get_solver_status != SolverStatus.<name-of-status>
        self.blocking_show_job_status(job=solver_job)
        
        # 3) Retrieve the final solution (blocks only if it isn't done yet)
        logger.info("Retrieving the final solution...")
        solution: Timetable = solver_job.get_final_best_solution()
        logger.info(f"Solver finished: status={solver_job.get_solver_status().name}, score={solution.score}")
                
        return solution

    # ----------------------------
    # New Children Methods
    # ----------------------------
    def blocking_show_job_status(self, job: SolverJob):
        """Blocks until the job with the given ID is finished and shows its status."""

        self.logger.info("\n==========================================")
        self.logger.info("🛑 Starting blocking: waiting for solver job to finish")
        self.logger.info("-------------------------------------------")
        self.logger.info(f"Job ID: {job.get_problem_id()}")
        start_time = time.time()

        while True:
            time.sleep(LOOP_WAIT_SECONDS)
            status  = job.get_solver_status()
            sol     = self.latest_solutions_by_job_id_dict[job.get_problem_id()][-1] if self.latest_solutions_by_job_id_dict[job.get_problem_id()] else None
            score   = sol.score if sol is not None else "–"
            elapsed = time.time() - start_time

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")



            # Break once the solver is no longer running
            if not (status in [SolverStatus.SOLVING_ACTIVE, SolverStatus.SOLVING_SCHEDULED]):
                self.logger.info(f"⏱️ {now_str} - job has finished... Elapsed time: {elapsed:.1f} seconds")
                break
            
            self.logger.info(f"⏱️ {now_str} - Elapsed time: {elapsed:.1f} seconds")
            self.logger.info(f"\t⏳ Job status: {status.name} | Best score: {score}\n")

        self.logger.info(f"\n✅ Blocking finished. Final job status: {status.name} - total time spent: {job.get_solving_duration()}")
        self.logger.info("==========================================")

    def _on_best_solution_changed(self, problem_id: str, sol: Timetable):
        """Callback triggered when a new best solution is found."""
        logger = self.logger
        # Create an empty list for the best solutions
        self.latest_solutions_by_job_id_dict[problem_id] = []
        # This is invoked on every new best solution
        self.latest_solutions_by_job_id_dict[problem_id].append(sol)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"\n💡 New best solution found! {timestamp} 🧠")
        logger.info(f"\t📈 Updated score: {sol.score}\n")

    def get_solver_job(self, index: int = -1) -> SolverJob:
        if len(self._job_id_list) == 0:
            raise IndexError("no job was run with this solver")
        
        return self._job_id_list[index]

        
