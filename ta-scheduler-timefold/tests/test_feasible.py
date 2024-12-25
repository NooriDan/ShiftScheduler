
from timefold.solver import SolverFactory
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration, TerminationCompositionStyle)

from hello_world.domain import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import define_constraints
from hello_world.main import generate_demo_data


def test_feasible():
    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=Timetable,
            entity_class_list=[ShiftAssignment],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            ),
            termination_config=TerminationConfig(
                termination_config_list=[
                    TerminationConfig(best_score_feasible=True),
                    TerminationConfig(spent_limit=Duration(seconds=30)),
                ],
                termination_composition_style=TerminationCompositionStyle.OR
            )
        ))
    solver = solver_factory.build_solver()
    solution = solver.solve(generate_demo_data())
    assert solution.score.is_feasible


if __name__ == '__main__':
    test_feasible()