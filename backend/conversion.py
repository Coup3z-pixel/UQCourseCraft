from classes import *
from constants import *

def convertForAlgorithmCourses(courses_activities: list) -> list[Class]:
    """
    Converts a list of course activity dictionaries into a list of Class objects for algorithmic processing.

    Each activity dictionary should contain keys such as 'course_code', 'activity_code', 'day', 'start', 'duration', and 'class_type'.
    The function groups activities by course and class type, creating Class instances and adding Time instances for each activity.

    Args:
        courses_activities (list): List of dictionaries representing course activities.

    Returns:
        list[Class]: List of Class objects, each containing associated Time objects.
    """
    
    classes = []

    # Creates the Class instances, with the Time instances inside
    for course in courses_activities:
        # Create time class
        time = Time(
            convertActivityNumber(course["activity_code"]),
            JSON_TO_DAY.get(course["day"]),
            convertTime(course["start"]),
            convertMinToHours(course["duration"]),
            0)
        
        # if existing class exists, add time to it
        foundClassInstance = False
        for classInstance in classes:
            if classInstance.course_code == course["course_code"] and classInstance.subclass_type == course["class_type"]:
                classInstance.add_time(time)
                foundClassInstance = True
                break
        
        # if not, create new class and append to classes
        if (foundClassInstance == False):
            times = [time]
            classes.append(Class(course["course_code"], getClassType(course["class_type"]), course["class_type"], times))
            
    return classes 

def convertForAlgorithmTimeSlots(preferences: dict) -> dict[list[int]]:
    timeslots = {MON: [0 for _ in range(NUMBER_OF_TIME_SLOTS + 1)],
                 TUE: [0 for _ in range(NUMBER_OF_TIME_SLOTS + 1)],
                 WED: [0 for _ in range(NUMBER_OF_TIME_SLOTS + 1)],
                 THU: [0 for _ in range(NUMBER_OF_TIME_SLOTS + 1)],
                 FRI: [0 for _ in range(NUMBER_OF_TIME_SLOTS + 1)]}
    
    for date, preference in preferences.items():
        if (preference["preference"] == "preferred"):
            timeslots[getDay(date)][getTimeIndex(date)] = JSON_TO_RANK.get(preference["rank"])
        else:
            timeslots[getDay(date)][getTimeIndex(date)] = JSON_TO_PREFERENCE.get(preference["preference"])
        
    return timeslots


def convertTime(time: str) -> float:
    hours, minutes = time.split(":")
    return int(hours) + (int(minutes) / 60)

def convertActivityNumber(activityNum: str) -> int: 
    return int(activityNum[:2])

def convertMinToHours(duration: str) -> float:
    return int(duration) / 60

def getClassType(subclass_type: str) -> str:
    return subclass_type[0:len(subclass_type) - 1]


# For time slots
def getDay(date: str) -> str:
    # date = MON-9:00 for example
    return JSON_TO_DAY2.get(date.split("-")[0])

def getTimeIndex(date: str) -> int:
    # data = MON-9:00 for example
    time = date.split("-")[1]
    index = convertTime(time) * 2
    return int(index)


