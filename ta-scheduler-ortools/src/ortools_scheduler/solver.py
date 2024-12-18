from typing import List
import os
from ortools.sat.python import cp_model

# Custom Imports
from .domain import TA, Shift

class Scheduler:
    def __init__(self, schedule, enable_logs: bool = False):
        self.schedule = schedule
        # Solver configuration
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.linearization_level = 0
        self.solver.parameters.num_search_workers  = os.cpu_count()//2 + 1
        self.solver.parameters.max_time_in_seconds = 5.0   # Limit to 5 seconds
        self.solver.parameters.log_search_progress = enable_logs  # Enable logs
        self.solver_status = None
        # Properties to be computed
        self.assigment_matrix = {}

    def add_ta(self, ta: TA):
        self.schedule.tas.append(ta)

    def add_shift(self, shift: Shift):
        self.schedule.shifts.append(shift)

    def update_availability(self, ta_id: str, availability_as_array_int: List[int]):
        ta: TA = next((ta for ta in self.schedule.tas if ta.id == ta_id), None)
        if ta:
            total_available_count = sum( 1 for x in availability_as_array_int if x!= -1 )
            if ta.req_shift_per_week > total_available_count:
                print(f"TA_{ta_id} {ta.name} is not available enough to meet their requirement\n{ta.req_shift_per_week} required\n{total_available_count} was given")
                return False
            ta.availability_as_array_int = availability_as_array_int
        else:
            print(f"TA with ID {ta_id} not found.")
            return False
        return True

    def update_shift_requirements(self, shift_id: str, req_ta_per_shift: int):
        shift = next((shift for shift in self.schedule.shifts if shift.id == shift_id), None)
        if shift:
            shift.req_ta_per_shift = req_ta_per_shift
        else:
            print(f"Shift with ID {shift_id} not found.")

    def update_ta_requirements(self, ta_id: str, req_shift_per_week: int):
        ta = next((ta for ta in self.schedule.tas if ta.id == ta_id), None)
        if ta:
            ta.req_shift_per_week = req_shift_per_week
        else:
            print(f"TA with ID {ta_id} not found.")

    # 1 - Create Desicion Variables
    def create_decision_variables(self):
        for ta in self.schedule.tas:
            for shift in self.schedule.shifts:
                self.assigment_matrix[(ta.id, shift.id)] = self.model.NewBoolVar(f'availability_{ta.id}_{shift.id}')

    # 2 - Constraint Definitions
    # (2.1) TAs must meet their shift requirements
    def tas_meet_shift_requirements(self):
        for ta in self.schedule.tas:
            self.model.Add(sum(self.assigment_matrix[(ta.id, shift.id)] for shift in self.schedule.shifts) >= ta.req_shift_per_week)

    # (2.2) Shifts must meet staffing requirements
    def shifts_meet_staffing_requirements(self):
        for shift in self.schedule.shifts:
            self.model.Add(sum(self.assigment_matrix[(ta.id, shift.id)] for ta in self.schedule.tas) == shift.req_ta_per_shift)

    # (2.3) Respect TA availability
    def respect_ta_availability(self):
      for ta in self.schedule.tas:
        for shift in self.schedule.shifts:
          if ta.availability_as_array_int[shift.id] == -1:  # Unavailable
            self.model.Add(self.assigment_matrix[(ta.id, shift.id)] == 0)

    # 3 - Define Objective function
    def objective_function(self):
        objective_terms = []
        for ta in self.schedule.tas:
            for shift in self.schedule.shifts:
                if ta.availability_as_array_int[shift.id] == 1:
                    objective_terms.append(10 * self.assigment_matrix[(ta.id, shift.id)])
                elif ta.availability_as_array_int[shift.id] == 0:
                    objective_terms.append(-1 * self.assigment_matrix[(ta.id, shift.id)])
        self.model.Maximize(sum(objective_terms))

    # Put everything together
    def solve(self):
        self.create_decision_variables()
        # Apply constraints
        self.tas_meet_shift_requirements()
        self.shifts_meet_staffing_requirements()
        self.respect_ta_availability()
        # Optional Objective function
        self.objective_function()

        self.status = self.solver.Solve(self.model)

        if self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE:
            print("\nFound Feasible Solutions")
            for ta in self.schedule.tas:
                ta_shifts_str = [f"{shift.series}_{shift.id}" for shift in self.schedule.shifts if self.solver.Value(self.assigment_matrix[(ta.id, shift.id)]) == 1]
                print(f"TA {ta.id} requires {ta.req_shift_per_week} given {len(ta_shifts_str)}: {ta_shifts_str}")
                # Update TA and Shift objects
                for shift in self.schedule.shifts:
                    if self.solver.Value(self.assigment_matrix[(ta.id, shift.id)]) == 1:
                        ta.assigned_shifts.append(shift)
                        shift.assigned_tas.append(ta)
        else:
            print("\nNo feasible solution found. Possible reasons:")
            print("- Check if total TA shift requirements match total shift needs.")
            print("- Ensure there are enough available TAs for each shift.")
            print("- Check if constraints are overly strict.")

        return self.status
