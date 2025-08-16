from classes import *
from constants import *
import time

from heapq import heapify, heappush, heappop

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
        dict: A dictionary of lists where the key is the day of the week and the value is a list of strings representing the 
        allocated classes in each half-hour slot, empty classes are represented by an empty string.
    
    Raises:
        ValueError: If no valid timetable can be found or if there are classes that cannot be allocated before running the algorithm.
    """
    # Check if there are any classes that cannot be allocated
    trim_classes(time_slots, classes)
    invalid_classes = [class_.course_code + class_.class_type for class_ in classes if not class_.times]
    if invalid_classes:
        message = f"Cannot allocate: {', '.join(invalid_classes)}. No fitting time slots available."
        raise ValueError(message)
    
    # Initialize the schedule with empty strings for each time slot
    # Each day has 48 half-hour slots (24 hours * 2)
    schedule = {day: [''] * NUMBER_OF_TIME_SLOTS for day in DAYS} 
    schedule_heap = ScheduleHeap(5)  # Min-heap to store the best schedules based on their scores

    backtrack(schedule, classes, time_slots, 0, schedule_heap)
    if not schedule_heap:
        raise ValueError("No valid timetable found.")

    return schedule_heap.getBestSchedules()[0]  # Return the best schedule from the heap


def score_schedule(schedule: dict, time_slots: dict) -> int:
    """
    Calculate the score of a schedule based on the number of ideal time slots allocated.
    """
    score = 0

    for day in schedule:
        for slot in range(NUMBER_OF_TIME_SLOTS):
            if schedule[day][slot]:
                score += time_slots[day][slot]  # Add the score of the time slot to the total score
    
    return score

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


def backtrack(schedule: dict, classes: list[Class], time_slots: dict[list[int]], i: int, schedule_heap: ScheduleHeap) -> bool:
    """
    Recursively attempts to assign class times to the schedule using backtracking.
    Tries to find a valid arrangement of all classes without conflicts.
    If a valid arrangement is found, it is added to the valid_schedules list.

    Args:
        schedule (dict): The current timetable, mapping days to lists of time slots.
        classes (list[Class]): List of Class objects to be scheduled.
        i (int): The index of the class currently being considered.
    """
    if i == len(classes):
        copy = {}
        for day in DAYS:
            copy[day] = schedule[day].copy()  # Copy the current schedule to output
        score = score_schedule(copy, time_slots)
        schedule_heap.newEntry(score, copy)  # Add the current schedule to the heap
        return True
    
    class_ = classes[i]
    for time in class_.times:
        if allocate_class(schedule, class_, time):
            if backtrack(schedule, classes, time_slots, i + 1, schedule_heap):
                # Don't return early
                return True# If a valid arrangement is found, return immediately

            deallocate_class(schedule, class_, time)  # Backtrack by removing the class from the schedule
    return False

def allocate_class(schedule: dict, class_: Class, time: Time) -> bool:
    """"
    Attempt to allocate a class to the schedule. Returns True if successful, False otherwise.
    """
    day = time.day
    start_time = int(time.start_time) * 2  # Convert to half-hour increments
    end_time = int((time.start_time + time.duration) * 2)  # Convert to half-hour increments
    
    for slot in range(start_time, end_time):
        if schedule[day][slot] != "":
            return False
        
    # If all slots are available, allocate the class
    for slot in range(start_time, end_time):
        schedule[day][slot] = f"{class_.course_code} {class_.class_type}"
        
    return True  # Successfully allocated the class


def deallocate_class(schedule: dict, class_: Class, time: Time) -> None:
    """    Deallocate a class from the schedule.
    """
    day = time.day
    start_time = int(time.start_time) * 2
    end_time = int((time.start_time + time.duration) * 2)  # Convert to half-hour increments

    for slot in range(start_time, end_time):
        schedule[day][slot] = ""  # Remove the class from the schedule


def print_schedule(schedule: dict) -> None:
    """
    Print the schedule in a readable format.
    """
    rows = []
    for i in range(48):
        row = [str(i/2).center(6)]
        for day in DAYS:
            slot = schedule[day][i]
            row.append(slot.center(15) if slot else '-'.center(15))  # Center the slot text in a 30-character wide cell
        rows.append(" | ".join(row))
    print("\n".join(rows[16:44]))