from enum import StrEnum
"""
The file containing all constants used in the UQCourseCraft backend.
"""

MON = "Monday"
TUE = "Tuesday"
WED = "Wednesday"
THU = "Thursday"
FRI = "Friday"
SAT = "Saturday"
SUN = "Sunday"

DAYS = [MON, TUE, WED, THU, FRI, SAT, SUN]

JSON_TO_DAY = {
    "Mon": MON,
    "Tue": TUE,
    "Wed": WED,
    "Thu": THU,
    "Fri": FRI,
    "Sat": SAT,
    "Sun": SUN
}

NUMBER_OF_TIME_SLOTS = 48  # 24 hours * 2 (half-hour increments)