from timefold.solver        import SolverManager, SolverFactory, SolutionManager
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver.score  import ConstraintFactory, Constraint

from .domain        import Timetable, ShiftAssignment
from .constraints   import (basic_ta_scheduling_constraints, grad_undergrad_constraints, favourite_partners_constraints, all_constraints)
from typing import Callable


class Solver:
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
        return self.solution_manager.solve(timetable)
    
    def terminate(self):
        self.solver_manager.terminate_early()
    
    def is_terminated(self) -> bool:
        return self.solver_manager.is_termination_imminent()

basic_ta_scheduling_solver = Solver(basic_ta_scheduling_constraints)
grad_undergrad_solver = Solver(grad_undergrad_constraints)
favourite_partners_solver = Solver(favourite_partners_constraints)
all_constraints_solver = Solver(all_constraints)