from classes import *
from main import *
from constants import *

def convertForAlgorithm(courses_activities: list):
    classes = []
    time_slots = dict()
    
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
            classes.append(Class(
                course["course_code"], 
                course["class_type"]))

    return classes
        

def convertTime(time: str) -> float:
    hours, minutes = time.split(":")
    return int(hours) + (int(minutes) / 60)

def convertActivityNumber(activityNum: str) -> int:
    if "-" in activityNum: 
        num, _ = activityNum.split("-")
    else:
        num = activityNum

    return int(num)

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