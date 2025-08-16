from classes import *
from constants import *

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
    output = {}# Initialize output with empty lists for each day
    backtrack(schedule, classes, 0, output)
    if not output:
        raise ValueError("No valid timetable found.")
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
        for day in DAYS:
            output[day] = schedule[day].copy()  # Copy the current schedule to output
        return
    
    class_ = classes[i]
    for time in class_.times:
        if allocate_class(schedule, class_, time):
            backtrack(schedule, classes, i + 1, output)
            deallocate_class(schedule, class_, time)  # Backtrack by removing the class from the schedule
        

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


#space to run sketches
def test_solve_timetable_sample():
    # Sample time slots: all slots are ideal (3) for Monday and Tuesday, unavailable (0) for other days
    time_slots = {
        MON: [3] * 48,
        TUE: [3] * 48,
        WED: [3] * 48,
        THU: [3] * 48,
        FRI: [3] * 48
    }

    sample_classes = [
        # MATH101
        Class(course_code="MATH101", class_type="LEC", times=[
            Time(1, MON, 8.0, 1.0, 50)
        ]),
        Class(course_code="MATH101", class_type="TUT", times=[
            Time(9, MON, 13.0, 1.0, 40), Time(10, TUE, 14.0, 1.0, 50), Time(11, WED, 13.0, 1.0, 60)
        ]),
        Class(course_code="MATH101", class_type="LAB", times=[
            Time(12, MON, 17.0, 1.0, 30), Time(13, TUE, 17.0, 1.0, 40), Time(14, WED, 17.0, 1.0, 50)
        ]),
        # PHYS102
        Class(course_code="PHYS102", class_type="LEC", times=[
            Time(15, TUE, 9.0, 1.0, 55)
        ]),
        Class(course_code="PHYS102", class_type="TUT", times=[
            Time(16, TUE, 13.0, 1.0, 45), Time(17, WED, 14.0, 1.0, 55), Time(18, THU, 14.0, 1.0, 70)
        ]),
        Class(course_code="PHYS102", class_type="LAB", times=[
            Time(19, TUE, 18.0, 1.0, 45), Time(20, WED, 18.0, 1.0, 55), Time(21, THU, 17.0, 1.0, 60)
        ]),
        # CHEM103
        Class(course_code="CHEM103", class_type="LEC", times=[
            Time(22, WED, 10.0, 1.0, 75)
        ]),
        Class(course_code="CHEM103", class_type="TUT", times=[
            Time(23, WED, 15.0, 1.0, 65), Time(24, THU, 13.0, 1.0, 70), Time(25, FRI, 13.0, 1.0, 75)
        ]),
        Class(course_code="CHEM103", class_type="LAB", times=[
            Time(26, WED, 18.0, 1.0, 55), Time(27, THU, 18.0, 1.0, 60), Time(28, FRI, 17.0, 1.0, 65)
        ]),
        # CS104
        Class(course_code="CS104", class_type="LEC", times=[
            Time(29, THU, 9.0, 1.0, 80)
        ]),
        Class(course_code="CS104", class_type="TUT", times=[
            Time(30, THU, 14.0, 1.0, 70), Time(31, FRI, 10.0, 1.0, 90), Time(32, FRI, 13.0, 1.0, 75)
        ]),
        Class(course_code="CS104", class_type="LAB", times=[
            Time(33, THU, 17.0, 1.0, 60), Time(34, FRI, 15.0, 1.0, 65), Time(35, FRI, 17.0, 1.0, 65)
        ])
    ]

    result = solve_timetable(time_slots, sample_classes)
    print_schedule(result)


def print_schedule(schedule: dict) -> None:
    """
    Print the schedule in a readable format.
    """
    rows = []
    for i in range(48):
        row = []
        for day in DAYS:
            slot = schedule[day][i]
            row.append(slot.center(15) if slot else '-'.center(15))  # Center the slot text in a 30-character wide cell
        rows.append(" | ".join(row))
    print("\n".join(rows[16:44]))

if __name__ == "__main__":
    test_solve_timetable_sample()