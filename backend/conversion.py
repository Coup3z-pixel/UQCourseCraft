from classes import *
from main import *
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
        print(course["activity_code"])
        # Create time class
        time = Time(
            convertActivityNumber(course["activity_code"]),
            course["day"],
            convertTime(course["start"]),
            convertMinToHours(course["duration"]),
            50)
        
        # if existing class exists, add time to it
        foundClassInstance = False
        for classInstance in classes:
            if classInstance.course_code == course["course_code"] and classInstance.class_type == course["class_type"]:
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


def convertTimetableToGrid(timetable_dict):
    """
    Convert a timetable dictionary to an 11x5 2D array.
    
    Args:
        timetable_dict (dict): Dictionary with days as keys ('Monday', 'Tuesday', etc.)
                              and lists of time slots as values
    
    Returns:
        list: 11x5 2D array where rows represent time slots and columns represent weekdays
              [Monday, Tuesday, Wednesday, Thursday, Friday]
    """
    # Define the order of weekdays
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Initialize 11x5 grid (11 time slots, 5 weekdays)
    grid = []

    for timeIndex, _ in enumerate(timetable_dict['Monday']):
        row = []
        for _, day in enumerate(weekdays): 

            if timetable_dict[day][timeIndex] != "":
                row.append([{
                    "course_code": timetable_dict[day][timeIndex],
                    "preferences": "preferred",
                    "rank": 1
                  }])
            else:
                row.append([])

        grid.append(row)
    
    return grid


# For time slots
def getDay(date: str) -> str:
    # date = MON-9:00 for example
    return JSON_TO_DAY2.get(date.split("-")[0])

def getTimeIndex(date: str) -> int:
    # data = MON-9:00 for example
    time = date.split("-")[1]
    index = convertTime(time) * 2
    return int(index)


