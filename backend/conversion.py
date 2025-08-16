from classes import *
from main import *
from constants import *

def convertForAlgorithm(courses_activities: list):
    classes = []
    time_slots = dict()

    """
    for course in courses_activities:
        course[]
    """

def convertTime(time: str) -> float:
    hours, minutes = time.split(":")
    return int(hours) + (int(minutes) / 60)

print(convertTime("14:00"))
print(convertTime("14:30"))
print(convertTime("11:00"))
print(convertTime("11:45"))