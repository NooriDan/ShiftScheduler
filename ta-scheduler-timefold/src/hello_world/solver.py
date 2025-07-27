import argparse
import logging
import sys, os
import uuid
import time
from datetime import datetime

from typing     import List, Dict, Callable, Any
from pathlib    import Path
from tqdm       import tqdm
from abc        import ABC, abstractmethod

from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory, SolutionManager, Solver, SolverManager, SolverStatus, SolverJob

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
        self.default_term_time_budget           : Duration =  Duration(minutes=1, seconds=30)
        self.default_term_unimproved_early_term : Duration =  Duration(seconds=10)

        # Private attributes to hold the solver configuration and factory
        self._solver_config     : SolverConfig
        self._solver_factory    : SolverFactory

        # Validate the inputs
        self._validate_inputs()
    
    # User-facing methods
    def set_random_seed(self, seed: int):
        """Sets the random seed for the solver."""
        self.random_seed = seed
        if self._solver_config:
            self._solver_config.random_seed = seed
        
    def create_solver_config(self) -> SolverConfig:
        """ Create the solver configuration based on the constraint version """
        self._validate_inputs()
        if self.use_config_xml:
            self._solver_config =  self._create_solver_conffig_from_xml(path_to_solver_config=self.path_to_solver_config)
        else:
            self._solver_config =  self._create_solver_config_default()

        return self._solver_config

    def solve_problem(self, problem: Timetable) -> Timetable:
        """Wrapper for the solve methods"""
        self._validate_inputs()
        logger = self.logger

        logger.info("\n🚀 === Starting to Solve the Problem ===")
        
        # 1) Build SolverConfig and SolverFactory
        logger.info("\t⚙️  Creating SolverConfig and SolverFactory...")
        self.create_solver_config()
        self._solver_factory = SolverFactory.create(self._solver_config)
        
        # 2) Solve the problem based on the solving method (extended in child classes)
        logger.info("\n🧠 === Solving the Problem Body ===")
        solution = self._solve_problem_body(problem=problem)
        logger.info("✅ === Solver Finished Successfully ===")

        # 3) Visualize the final solution
        logger.info("\n🗓️ === Final Timetable ===")
        print_timetable(time_table=solution, logger=logger)
        logger.info("🗓️ === /End of Final Timetable ===")
        
        # 4) Post-process (justification, analysis, etc.)
        logger.info("\n📊 === Post-processing the Solution ===")
        solution_manager = self.post_process_solution(solution=solution)
        logger.info("🏁 === Post-processing Complete ===")
        
        return solution
    
    # Post-processing Methods
    def post_process_solution(self, solution: Timetable) -> SolutionManager:
        logger = self.logger
        solution_manager = SolutionManager.create(solver_factory=self._solver_factory)

        # logger.info("=======================================================")
        # logger.info("calling solver.explain to explain the constraints")
        # logger.info("=======================================================")
        # score_explanation = solution_manager.explain(solution=solution)
        # logger.info(score_explanation.summary)

        logger.info("=======================================================")
        logger.info("calling solver.analyze to explain the constraints")
        logger.info("=======================================================")
        score_analysis = solution_manager.analyze(solution=solution)
        logger.info(score_analysis.summary)

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

    def visualize_hot_planning_vars(self, solution: Timetable):
        solution_manager = SolutionManager.create(self._solver_factory)
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
        self._solver_config =  SolverConfig(
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
        return self._solver_config
    
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
        self._solver_config = solver_config
        return self._solver_config
    
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

class TimetableSolverBlocking(TimetableSolverBase):
    # Absteract methods    
    def _solve_problem_body(self, problem: Timetable) -> Timetable:
        logger = self.logger
        logger.info("Solving with blocking solver...")
        if not self._solver_config:
            self.create_solver_config()
        self._solver_factory = SolverFactory.create(self._solver_config)
        solver      = self._solver_factory.build_solver()
        solution    = solver.solve(problem)
        return solution

class TimetableSolverWithSolverManager(TimetableSolverBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Members only relevant for this subclass
        self._solver_manager    : SolverManager
        self._job_id_list       : List[SolverJob]  = []
        self.latest_solutions_by_job_id_dict   : Dict[str, List[Timetable]] = {}

    # Abstract methods
    def _solve_problem_body(self, problem: Timetable) -> Timetable:
        logger = self.logger
        logger.info("=== Creating the SolverManager ===")

        if not self._solver_factory:
            raise ValueError("SolverFactory is not initialized. Call create_solver_config() first.")
        
        # 1) Create the solver manager
        self._solver_manager = SolverManager.create(self._solver_factory)
        
        # 2) Choose a unique problem ID
        problem_id = str(uuid.uuid4())
        
        # 3) Run the solver asynchronously and retrieve the best solution
        self.latest_solutions_by_job_id_dict[problem_id] = []
        def on_best_solution_changed(sol: Timetable):
            """Callback triggered when a new best solution is found."""
            # This is invoked on every new best solution
            self.latest_solutions_by_job_id_dict[problem_id].append(sol)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"\n💡 New best solution found! {timestamp} 🧠")
            logger.info(f"\t📈 Updated score: {sol.score}\n")

        solver_job = self._solver_manager.solve_builder() \
            .with_problem_id(problem_id) \
            .with_problem(problem) \
            .with_best_solution_consumer(on_best_solution_changed) \
            .run()   # <- Run is required here!
            # more optional setting:
            # .with_first_initialized_solution_consumer(on_first_solution_changed) \
            # .with_final_best_solution_consumer(on_final_solution_changed) \
            # .with_exception_handler(on_exception_handler) \
            # .with_config_override(config_override) \
        self._job_id_list.append(solver_job)

        # while solver_job.get_solver_status != SolverStatus.<name-of-status>
        self.blocking_show_job_status(job=solver_job)
        
        # 4) Retrieve the final solution (blocks only if it isn't done yet)
        logger.info("Retrieving the final solution...")
        solution: Timetable = solver_job.get_final_best_solution()
        logger.info("Solver finished: status=%s, score=%s",
                    solver_job.get_solver_status().name, solution.score)
                
        return solution
    
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

        self.logger.info(f"\n✅ Blocking finished. Final job status: {status.name}")
        self.logger.info("==========================================")
