from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime, time, timedelta
from enum import Enum

@dataclass(frozen=True)
class AvailabilityStatus:
    DESIRED: int = 1
    UNDESIRED: int = 0
    UNAVAILABLE: int = -1


@dataclass
class TA:
    id: int
    macid: str
    name: str
    req_shift_per_week: int
    availability_as_dict: Dict[str, str] = field(default_factory=dict)
    availability_as_array_int: List[int] = field(default_factory=list)
    # to be planned
    assigned_shifts: List[int] = field(default_factory=list)

@dataclass
class Shift:
    id: int
    name: str
    req_ta_per_shift: int
    series: str
    day_of_week: str
    date: datetime
    start_time: time
    duration: timedelta = timedelta(hours=3, minutes=0)
    # to be planned
    assigned_tas: List[TA] = field(default_factory=list)

    def __post_init__(self):
        # Combine date and start_time to create a datetime object
        start_datetime = datetime.combine(self.date, self.start_time)
        # Calculate end_datetime by adding duration
        end_datetime = start_datetime + self.duration
        # Extract the time component from end_datetime
        self.end_time = end_datetime.time()

@dataclass
class Schedule:
    tas: List[TA] = field(default_factory=list)
    shifts: List[Shift] = field(default_factory=list)