from classes import *
from constants import *

def convertForAlgorithm(courses_activities: list) -> list[Class]:
    classes = []
    time_slots = dict()

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
            

def convertTime(time: str) -> float:
    hours, minutes = time.split(":")
    return int(hours) + (int(minutes) / 60)

def convertActivityNumber(activityNum: str) -> int: 
    return int(activityNum[:2])

def convertMinToHours(duration: str) -> float:
    return int(duration) / 60

def getClassType(subclass_type: str) -> str:
    return subclass_type[0:len(subclass_type) - 1]

def convertTimetableToGrid(timetable: dict):
    pass
