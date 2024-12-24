from datetime import date, datetime, time, timedelta
from itertools import product
from enum import Enum
from random import Random
from typing import Generator
from dataclasses import dataclass, field

from .domain import *


class DemoData(Enum):
    SMALL = 'SMALL'
    LARGE = 'LARGE'
    CUSTOM = 'CUSTOM'

# MODIFIED THE FOLLOWING:
FIRST_NAMES = ("Danial", "Moein", "Shahrukh")
LAST_NAMES = ("Noori Zadeh", "Roghani", "Athar")
SHIFT_LENGTH = timedelta(hours=3)
# MORNING_SHIFT_START_TIME = time(hour=14, minute=30)
# DAY_SHIFT_START_TIME = time(hour=17, minute=30)
AFTERNOON_SHIFT_START_TIME = time(hour=14, minute=30)
NIGHT_SHIFT_START_TIME = time(hour=18, minute=30)

# SHIFT_START_TIMES_COMBOS = (
#     (MORNING_SHIFT_START_TIME, AFTERNOON_SHIFT_START_TIME),
#     (MORNING_SHIFT_START_TIME, AFTERNOON_SHIFT_START_TIME, NIGHT_SHIFT_START_TIME),
#     (MORNING_SHIFT_START_TIME, DAY_SHIFT_START_TIME, AFTERNOON_SHIFT_START_TIME, NIGHT_SHIFT_START_TIME),
# )

SHIFT_START_TIMES_COMBOS = (
    (AFTERNOON_SHIFT_START_TIME, NIGHT_SHIFT_START_TIME)
)


