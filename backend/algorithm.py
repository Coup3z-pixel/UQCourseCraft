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

def solve_timetable(time_slots: dict[list[int]], classes: list[Class]) -> list[dict]:
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
    invalid_classes = [class_.course_code + class_.subclass_type for class_ in classes if not class_.times]
    if invalid_classes:
        message = f"Cannot allocate: {', '.join(invalid_classes)}. No fitting time slots available."
        raise ValueError(message)

    # Prune search space: order classes by number of available times (most constrained first)
    classes.sort(key=lambda c: len(c.times))

    # Initialize the schedule with empty strings for each time slot
    schedule = {day: [''] * NUMBER_OF_TIME_SLOTS for day in DAYS}
    schedule_heap = ScheduleHeap(5)

    def backtrack(i: int, score: int, hours_remaining: int) -> bool:
        """
        Recursively attempts to assign class times to the schedule using backtracking.
        Tries to find a valid arrangement of all classes without conflicts.
        If a valid arrangement is found, it is added to the valid_schedules list.

        Args:
            i (int): The index of the class currently being considered.
        """
        if i == len(classes):
            copy = {}  # Calculate the score of the current schedule
            copy['score'] = score
            for day in DAYS:
                copy[day] = schedule[day].copy()  # Copy the current schedule to output
            schedule_heap.newEntry(score, copy)  # Add the current schedule to the heap
            return True
        
        # IF the current schedule cannot make it onto the top 5 schedules, return False
        if len(schedule_heap.heap) == schedule_heap.capacity and score + (hours_remaining) * 2 * IDEAL < schedule_heap.heap[0].score:
            return False
        
        class_ = classes[i]
        for time in class_.times:
            score_added = allocate_class(schedule, time_slots, class_, time)
            if score_added:
                if backtrack(i+1, score+score_added, hours_remaining-time.duration) and RETURN_FIRST_MATCH:
                    return True
                deallocate_class(schedule, class_, time)  # Backtrack by removing the class from the schedule

        return False

    backtrack(0, 0, total_time(classes))
    if not schedule_heap.heap:
        raise ValueError("No valid timetable found.")
    print(total_time(classes))
    return schedule_heap.getBestSchedules()

def total_time(classes: list[Class]) -> int:
    """Calculate the total time required for all classes."""
    return sum([class_.times[0].duration for class_ in classes])

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

def allocate_class(schedule: dict,time_slots:dict[list[int]], class_: Class, time: Time) -> int:
    """"
    Attempt to allocate a class to the schedule. Returns the increase in score if successful, otherwise returns 0.

    Args:
        schedule (dict): The current schedule to which the class is being allocated.
        class_ (Class): The class to be allocated.
        time (Time): The time slot for the class.
    """
    day = time.day
    start_time = int(time.start_time) * 2  # Convert to half-hour increments
    end_time = int((time.start_time + time.duration) * 2)  # Convert to half-hour increments
    score = 0
    
    for slot in range(start_time, end_time):
        if schedule[day][slot] != "":
            return 0
        
    # If all slots are available, allocate the class
    for slot in range(start_time, end_time):
        schedule[day][slot] = f"{class_.course_code} {class_.subclass_type} {time.activity_code}"
        score += time_slots[day][slot]  # Add the score of the time slot to the total score
        
    return score  # Successfully allocated the class


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
