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
    trim_classes(time_slots, classes)

    invalid_classes = [class_.course_code + class_.class_type for class_ in classes if not class_.times]
    if invalid_classes:
        message = f"Cannot allocate: {', '.join(invalid_classes)}. No fitting time slots available."
        raise ValueError(message)
    
    schedule = {day: [''] * NUMBER_OF_TIME_SLOTS for day in DAYS} 
    valid_schedules = []  # List to store all valid schedules found

    backtrack(schedule, classes, 0, valid_schedules)
    if not valid_schedules:
        raise ValueError("No valid timetable found.")

    score_heap = []
    heapify(score_heap)

    for valid_schedule in valid_schedules:
        valid_schedule['score'] = score_schedule(valid_schedule, time_slots)

        if len(score_heap) == 5:
            heappop(score_heap)

        heappush(score_heap, (valid_schedule['score'], id(valid_schedule), valid_schedule))

    best_schedules = []

    for _ in range(5):
        schedule_tuple = heappop(score_heap)  
        best_schedules.append(schedule_tuple[2])
     
    return best_schedules  # Return the first valid schedule found


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


def backtrack(schedule: dict, classes: list[Class], i: int, valid_schedules: list) -> bool:
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
        valid_schedules.append({})
        for day in DAYS:
            valid_schedules[-1][day] = schedule[day].copy()  # Copy the current schedule to output
        return True
    
    class_ = classes[i]
    for time in class_.times:
        if allocate_class(schedule, class_, time):
            if backtrack(schedule, classes, i + 1, valid_schedules):
                # Don't return early
                pass # If a valid arrangement is found, return immediately

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


"""
Area below is for testing purposes only.
"""
def test_solve_timetable_sample():    
    before = time.time()
    result = solve_timetable(time_slots, sample_classes)
    after = time.time()
    print(f"Time taken: {after - before:.2f} seconds")
    print_schedule(result)


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

if __name__ == "__main__":
    test_solve_timetable_sample()
