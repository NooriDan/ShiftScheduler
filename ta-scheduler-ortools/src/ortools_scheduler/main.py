import os
import argparse
from pprint import pprint

# Custom Imports 
from ortools_scheduler.solver import Scheduler
from ortools_scheduler.domain import TA, Shift, Schedule
from ortools_scheduler.utils  import DataConstructor, Schedule_Utils


def main():
    print("Running the main with constructor")
    constructor = DataConstructor(ta_csv_path="ta_list.csv",
                shift_csv_path="shift_list.csv",
                availability_folder="availability")
    
    scheduler = Scheduler(constructor.schedule)

    scheduler.solve()

    util = Schedule_Utils(output_dir="schedules")
    util.report_timeseries(scheduler)


if __name__ == "__main__":
    main()