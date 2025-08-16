from classes import *
from main import *
from constants import *

def convertForAlgorithm(courses_activities: list) -> list[Class]:
    classes = []
    time_slots = dict()

    # Creates the Class instances, with the Time instances inside
    for course in courses_activities:
        # Create time class
        time = Time(
            convertActivityNumber(course["activity_code"]),
            course["day"].upper(),
            convertTime(course["start"]),
            convertMinToHours(course["duration"]),
            50)
        
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
    if "-" in activityNum: 
        num, _ = activityNum.split("-")
    elif "_" in activityNum:
        num, _ = activityNum.split("_")
    else:
        num = activityNum

    return int(num)

def convertMinToHours(duration: str) -> float:
    return int(duration) / 60

def getClassType(subclass_type: str) -> str:
    return subclass_type[0:len(subclass_type) - 1]

def testing():
    timetable_url = "https://timetable.my.uq.edu.au/odd/rest/timetable/subjects"
    course_body = {
            "search-term": "MATH1051",
            "semester": "S2",
            "campus": "ALL",
            "faculty": "ALL",
            "type": "ALL",
            "days": ["0", "1", "2", "3", "4", "5", "6"],
            "start-time": "00:00",
            "end-time": "23:00"
        }
    timetable_response = requests.post(timetable_url, data=course_body)
    courses = parse_course_timetable(timetable_response.json(), "MATH1051")
    classes = convertForAlgorithm(courses)

    for newClass in classes:
        print(newClass)

testing()
