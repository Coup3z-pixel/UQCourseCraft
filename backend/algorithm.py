from classes import *
from constants import *
from pytest import *

"""
In this file, we are implementing the timetabling algorithm for UQCourseCraft.

Inputs to algorithm:
User Data: A dictionary mapping days of the week to a list of time slots, indexable by military time (arr[0] represents 00:00-00:59).
Course Data: A dictionary mapping course codes to a list of class types, each containing a list of time slots.

Output: A dictionary mapping the course code and class type to the ideal preferences.

Current algorithm: recursive backtracking to find the first valid timetable. Only takes into account the time slots.
"""

def solve_timetable(time_slots: dict[list[int]], classes: list[Class]) -> dict:
    """
    Solve the timetabling problem by finding the best fit for course classes into user preferences.
    
    Args:
        time_slots (dict): A dictionary mapping days of the week to a list of time slots. Each time slot is given a number between 0 and 3 inclusive.
        0 represents unavailable, 1 represents poor time, 2 represents good time, and 3 represents ideal time. The index of the list is
        the 30 minute increment of the day, starting from 00:00.
        classes (list[Class]): A list of Class objects representing each class the student must take.

    Returns:
        dict: A dictionary mapping a tuple of course code and class type to the ideal preferences (list of activity numbers).
    """
    trim_classes(time_slots, classes)

    invalid_classes = [class_.course_code + class_.class_type for class_ in classes if not class_.times]
    if invalid_classes:
        raise ValueError(f"Cannot allocate: {', '.join(invalid_classes)}")
    
    schedule = {}
    for day in DAYS:
        schedule[day] = [""] * 48  # Initialize each day with 48 half-hour slots (24 hours)
        # Each slot will be marked with course code and class type if allocated, or empty string if not allocated.
    output = {}

    backtrack(schedule, classes, 0, output)

    return output


def trim_classes(time_slots: dict[list[int]], classes: list[Class]) -> None:
    """
    Remove all classes at times that the useer marked as unavailable.
    """
    for class_ in classes:
        working_times = []
        for time in class_.times:
            start_time = int(time.start_time) * 2  # Convert to half-hour increments
            end_time = int((time.start_time + time.duration) * 2)  # Convert to half-hour increments

            if sum(time_slots[time.day][start_time:end_time]) > 0:
                working_times.append(time)
        class_.times = working_times


def backtrack(schedule: dict, classes: list[Class], i: int, output: dict) -> None:
    """
    Recursively attempts to assign class times to the schedule using backtracking.
    Tries to find a valid arrangement of all classes without conflicts.

    Args:
        schedule (dict): The current timetable, mapping days to lists of time slots.
        classes (list[Class]): List of Class objects to be scheduled.
        i (int): The index of the class currently being considered.
    """
    if i == len(classes):
        output = schedule.copy()
    
    if allocate_class(schedule, classes[i]):
        backtrack(schedule, classes, i + 1)
    else:
        return  # If we cannot allocate the class, we stop the recursion here.

def allocate_class(schedule: dict, class_: Class) -> bool:
    """"
    Attempt to allocate a class to the schedule. Returns True if successful, False otherwise.
    """
    for time in class_.times:
        day = time.day
        start_time = int(time.start_time) * 2  # Convert to half-hour increments
        end_time = int((time.start_time + time.duration) * 2)  # Convert to half-hour increments
        unavailable = False
    
        for slot in range(start_time, end_time):
            if schedule[day][slot] != "":
                unavailable = True
                break
        
        if unavailable:
            continue  # Skip this time if any slot is already occupied

        # If all slots are available, allocate the class
        for slot in range(start_time, end_time):
            schedule[day][slot] = f"{class_.course_code} {class_.class_type}"
        
        return True  # Successfully allocated the class
    return False


