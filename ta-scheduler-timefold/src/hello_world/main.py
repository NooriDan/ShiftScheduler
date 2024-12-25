from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from timefold.solver import SolverFactory

from hello_world.domain      import Timetable, ShiftAssignment, Shift, TA
from hello_world.constraints import define_constraints
from hello_world.demo_data   import generate_demo_data
from hello_world.utils       import print_timetable


def main():

    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=Timetable,
            entity_class_list=[ShiftAssignment],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            ),
            termination_config=TerminationConfig(
                # The solver runs only for 5 seconds on this small dataset.
                # It's recommended to run for at least 5 minutes ("5m") otherwise.
                spent_limit=Duration(seconds=5)
            )
        ))

    # Load the problem
    problem = generate_demo_data()

    # Solve the problem
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    # Visualize the solution
    print_timetable(solution)

if __name__ == '__main__':
    main()
