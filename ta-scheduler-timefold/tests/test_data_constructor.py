import pytest
from collections import Counter

# Custom imports
from hello_world.utils import DataConstructor

def test_data_constructor():
    data_constructor = DataConstructor(
        ta_csv_path='test_data/1/ta_list.csv',
        shift_csv_path='test_data/1/shift_list.csv',
        availability_folder='test_data/1/availability',
        load= False
    )

    # Test no loading happened
    assert data_constructor.timetable is None
    assert data_constructor.ta_dataframe is None
    assert data_constructor.shift_dataframe is None

    data_constructor.create()

    # Correct number of TAs created
    macids_constructor = [ta.id for ta in data_constructor.timetable.tas]
    macids_actual  = ["noorizad", "roghanim", "roghania", "baratia", "ebi", "saram"]
    assert Counter(macids_constructor) == Counter(macids_actual)

    # Correct number of shifts created
    shifts_constructor = [shift.series for shift in data_constructor.timetable.shifts]
    shifts_actual = ["L01", "L02", "L03", "L04", "L05", "L06", "L07", "L08", "L09", "L10"]
    assert Counter(shifts_constructor) == Counter(shifts_actual)

    # Correct number of shift assignments created
    assert len(data_constructor.timetable.shift_assignments) == sum([shifts.required_tas for shifts in data_constructor.timetable.shifts])

    # Correct imported for each TA


if __name__ == '__main__':
    test_data_constructor()


