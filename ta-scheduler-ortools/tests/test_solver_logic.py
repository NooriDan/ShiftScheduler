
from ortools_scheduler.domain import TA, Shift, Schedule
from ortools_scheduler.solver import Scheduler
from ortools_scheduler.utils  import DataConstructor, Schedule_Utils
from datetime import datetime, time
from ortools.sat.python import cp_model
from pytest import fail


def test_solver():
    # Testing the class definitions above
    shift1 = Shift(id= 0, name='Morning Shift',    series='L01', day_of_week='Monday',    date=datetime(2024, 12, 12), start_time=time(14, 30), req_ta_per_shift = 2)
    shift2 = Shift(id= 1, name='Afternoon Shift',  series='L02', day_of_week='Tuesday',   date=datetime(2024, 12, 13), start_time=time(14, 30), req_ta_per_shift = 1)
    shift3 = Shift(id= 2, name='Evening Shift',    series='L03', day_of_week='Wednesday', date=datetime(2024, 12, 14), start_time=time(18, 30), req_ta_per_shift = 2)
    shift4 = Shift(id= 3, name='Night Shift',      series='L04', day_of_week='Thursday',  date=datetime(2024, 12, 15), start_time=time(18, 30), req_ta_per_shift = 1)
    shift5 = Shift(id= 4, name='Late Night Shift', series='L05', day_of_week='Friday',    date=datetime(2024, 12, 16), start_time=time(18, 30), req_ta_per_shift = 2)

    ta1 = TA(id= 0, macid = "aaa", name='A Doe',       req_shift_per_week=1)
    ta2 = TA(id= 1, macid = "bbb", name='B Smith',     req_shift_per_week=2)
    ta3 = TA(id= 2, macid = "ccc", name='C Smith', req_shift_per_week=1)
    ta4 = TA(id= 3, macid = "ddd", name='D Brown',      req_shift_per_week=2)

    schedule = Schedule()
    schedule.tas = [ta1, ta2, ta3, ta4]
    schedule.shifts = [shift1, shift2, shift3, shift4, shift5]


    ta_scheduling = Scheduler(schedule)

    ta_scheduling.update_availability(ta_id= 0, availability_as_array_int=[1, 1, 0, 1,  -1])
    ta_scheduling.update_availability(ta_id= 1, availability_as_array_int=[1, 0, 0, 0,  1])
    ta_scheduling.update_availability(ta_id= 2, availability_as_array_int=[1, 0, 0, 0,  1])
    ta_scheduling.update_availability(ta_id= 3, availability_as_array_int=[1, 0, 0, 1, -1])


    status = ta_scheduling.solve()

    assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE

def test_read_csv():
    try: 
        constructor = DataConstructor(ta_csv_path="../data/ta_list.csv",
                    shift_csv_path="../data/shift_list.csv",
                    availability_folder="../data/availability")
    except Exception as e:
        fail(F"REAFING FROM CSV FAILED")
        