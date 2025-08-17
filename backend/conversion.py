from classes import *
from main import *
from constants import *

import requests

def convertForAlgorithmCourses(courses_activities: list, retrieveLectures = True) -> list[Class]:
    """
    Converts a list of course activity dictionaries into a list of Class objects for algorithmic processing.

    Each activity dictionary should contain keys such as 'course_code', 'activity_code', 'day', 'start', 'duration', and 'class_type'.
    Activities are grouped by course and class type. For each group, a Class instance is created, containing one or more Time instances
    representing the scheduled times for that activity.

    If retrieveLectures is False, activities with a class type of 'LEC' (lecture) are excluded from the output.

    Args:
        courses_activities (list): List of dictionaries, each representing a course activity with required keys:
            - 'course_code': str, course identifier
            - 'activity_code': str, unique activity code
            - 'day': str, day of the week
            - 'start': str, start time in "HH:MM" format
            - 'duration': str or int, duration in minutes
            - 'class_type': str, type of class (e.g., 'LEC', 'TUT', etc.)
        retrieveLectures (bool, optional): If False, lecture activities are excluded. Defaults to True.

    Returns:
        list[Class]: List of Class objects, each containing associated Time objects for grouped activities.

    Notes:
        - Activities are grouped by course_code, class_type, and subclass_type.
        - Time objects are created for each activity and added to the corresponding Class.
        - If no existing Class matches the activity, a new Class is instantiated.
        - The function prints each activity_code during processing for debugging.
    """
    
    classes = []

    # Creates the Class instances, with the Time instances inside
    for course in courses_activities:
        # Create time class
        time = Time(
            convertActivityNumber(course["activity_code"]),
            JSON_TO_DAY[course["day"]],
            convertTime(course["start"]),
            convertMinToHours(course["duration"]),
            50)
        
        # prevent lectures from being instantiated if retrieveLectures is false. Below code for dealing with class instances
        # are ignored 
        if retrieveLectures == False and getClassType(course["class_type"]) == "LEC":
            continue

        # if existing class exists, add time to it
        foundClassInstance = False
        for classInstance in classes:
            if (classInstance.course_code == course["course_code"] 
                and classInstance.class_type == getClassType(course["class_type"])
                and classInstance.subclass_type == course["class_type"]
            ):
                classInstance.add_time(time)
                foundClassInstance = True
                break
        
        # if not, create new class and append to classes
        if (foundClassInstance == False):
            times = [time]
            classes.append(Class(course["course_code"], getClassType(course["class_type"]), course["class_type"], times))
            
    return classes 

def convertForAlgorithmTimeSlots(preferences: dict) -> dict[list[int]]:
    """
    Converts user time slot preferences into a structured dictionary for algorithmic processing.

    The function creates a dictionary mapping each weekday to a list of time slot values. Each value represents the user's
    preference or rank for that time slot, based on the input preferences.

    Args:
        preferences (dict): Dictionary where keys are date strings (e.g., "MON-9:00") and values are dictionaries with:
            - "preference": str, either "preferred" or another preference type
            - "rank": int, rank value if preference is "preferred"

    Returns:
        dict[list[int]]: Dictionary with weekdays as keys (MON, TUE, WED, THU, FRI) and lists of integers representing
                         preference or rank for each time slot.

    Notes:
        - Uses JSON_TO_RANK for "preferred" slots and JSON_TO_PREFERENCE for others.
        - Time slots are indexed using getDay and getTimeIndex helpers.
        - The length of each time slot list is NUMBER_OF_TIME_SLOTS + 1.
    """

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
    """
    Converts a time string in "HH:MM" format to a float representing hours.

    Args:
        time (str): Time string in "HH:MM" format.

    Returns:
        float: Time as a float, where minutes are represented as a fraction of an hour. For example, "13:30" becomes 13.5.
    """
    hours, minutes = time.split(":")
    return int(hours) + (int(minutes) / 60)

def convertActivityNumber(activityNum: str) -> int:
    """
    Extracts and converts the first two characters of an activity code to an integer.

    Args:
        activityNum (str): Activity code string.

    Returns:
        int: Integer representation of the activity number.
    """
    return int(activityNum[:2])

def convertMinToHours(duration: str) -> float:
    """
    Converts a duration in minutes to hours as a float.

    Args:
        duration (str): Duration in minutes.

    Returns:
        float: Duration in hours.
    """
    return int(duration) / 60

def getClassType(subclass_type: str) -> str:
    """
    Extracts the general class type from a subclass type string.

    This function returns the first three characters of the subclass type string,
    which typically represent the main class type (e.g., 'LEC' for lecture, 'TUT' for tutorial).

    Args:
        subclass_type (str): Subclass type string (e.g., 'LEC1', 'TUT2').

    Returns:
        str: General class type (first three characters of the input).
    """
    return subclass_type[0:3]


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
    
    # Initialize 28x5 grid (11 time slots, 5 weekdays)
    grid = []

    # bug: its the whole day

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
    """
    Extracts the weekday from a date string and maps it to the internal weekday representation.

    Args:
        date (str): Date string in the format "DAY-HH:MM" (e.g., "MON-9:00").

    Returns:
        str: Internal weekday representation as defined in JSON_TO_DAY2.
    """

    return JSON_TO_DAY2.get(date.split("-")[0])

def getTimeIndex(date: str) -> int:
    """
    Calculates the time slot index from a date string.

    Args:
        date (str): Date string in the format "DAY-HH:MM" (e.g., "MON-9:00").

    Returns:
        int: Index of the time slot for the given time.
    """

    time = date.split("-")[1]
    index = convertTime(time) * 2
    return int(index)


