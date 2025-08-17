from enum import StrEnum
"""
The file containing all constants used in the UQCourseCraft backend.
"""

MON = "Monday"
TUE = "Tuesday"
WED = "Wednesday"
THU = "Thursday"
FRI = "Friday"

DAYS = [MON, TUE, WED, THU, FRI]

JSON_TO_DAY = {
    "Mon": MON,
    "Tue": TUE,
    "Wed": WED,
    "Thu": THU,
    "Fri": FRI
}

JSON_TO_DAY2 = {
    "MON": MON,
    "TUE": TUE,
    "WED": WED,
    "THU": THU,
    "FRI": FRI
}

NUMBER_OF_TIME_SLOTS = 48  # 24 hours * 2 (half-hour increments)

IDEAL = 4
OKAY = 3
BAD = 2
UNAVAILABLE = 1

STANDARD_LEVELS = [UNAVAILABLE, OKAY, BAD, IDEAL]

ALWAYS_AVAILABLE = {
    day: [IDEAL] * NUMBER_OF_TIME_SLOTS for day in DAYS
}

RETURN_FIRST_MATCH = False

JSON_TO_PREFERENCE = {
    "preferred": IDEAL,
    "default": UNAVAILABLE,
    "unavailable": UNAVAILABLE
}

JSON_TO_RANK = {
    1: IDEAL,
    2: OKAY,
    3: BAD,
    4: UNAVAILABLE
}
