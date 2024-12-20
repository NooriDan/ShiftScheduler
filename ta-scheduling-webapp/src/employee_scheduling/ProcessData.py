import pandas as pd
from datetime import date, datetime, time, timedelta
from random import Random
from dataclasses import dataclass, field
# Custom Imports
from src.employee_scheduling.domain import Shift, Employee, EmployeeSchedule


def readEmployeeData(filename: str):
    pass

def generate_data() -> EmployeeSchedule:
    
    start_date = date.today()
    random = Random(2024)
    shift_template_index = 0

    random.shuffle()

    employees = []

    shifts: list[Shift] = []

    def id_generator():
        current_id = 0
        while True:
            yield str(current_id)
            current_id += 1

    ids = id_generator()

    shift_count = 0
    for shift in shifts:
        shift.id = str(shift_count)
        shift_count += 1

    return EmployeeSchedule(
        employees=employees,
        shifts=shifts
    )

