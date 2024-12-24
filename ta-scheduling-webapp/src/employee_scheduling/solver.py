from timefold.solver        import SolverManager, SolverFactory, SolutionManager
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver.score  import ConstraintFactory, Constraint

from .domain        import Timetable, ShiftAssignment
from .constraints   import define_constraints
from typing import Callable


class Solver:
    solver_manager: SolverManager
    solution_manager: SolutionManager
    
    def __init__(self, define_constraints: Callable[[ConstraintFactory], list[Constraint]]):
        self.solver_config   = SolverConfig(
            solution_class    = Timetable,
            entity_class_list = [ShiftAssignment],
            score_director_factory_config    = ScoreDirectorFactoryConfig(
                constraint_provider_function = define_constraints
            ),
            termination_config=TerminationConfig(
                spent_limit=Duration(seconds=30)
            )
        )

        self.solver_manager   = SolverManager.create(SolverFactory.create(self.solver_config))
        self.solution_manager = SolutionManager.create(self.solver_manager)

    def solve(self, timetable: Timetable) -> Timetable:
        return self.solver_manager.solve(timetable)
    
    def solve_and_listen(self, job_id: str, timetable: Timetable, listener: Callable[[Timetable], None]):
        self.solver_manager.solve_and_listen(job_id, timetable, listener)
    
    def terminate_early(self):
        self.solver_manager.terminate_early()
        
    def get_solver_status(self, job_id: str) -> str:
        return self.solver_manager.get_solver_status(job_id)

solver_manager = Solver(define_constraints)