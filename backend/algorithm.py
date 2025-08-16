from classes import *
from constants import *
import time

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

    for valid_schedule in valid_schedules:
        valid_schedule['score'] = score_schedule(valid_schedule, time_slots)
    
    valid_schedules.sort(key=lambda x: x['score'], reverse=True)  # Sort schedules by score
    print(valid_schedules[0].pop('score'))  # Remove the score from the final output
    return valid_schedules[0]  # Return the first valid schedule found


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


def backtrack(schedule: dict, classes: list[Class], i: int, valid_schedules: list) -> None:
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
    # Sample time slots: all slots are ideal (3) for Monday and Tuesday, unavailable (0) for other days
    time_slots = {
        MON: [3] * 30 + [0] * 20,  # First half ideal, second half unavailable
        TUE: [3] * 30 + [0] * 20,
        WED: [3] * 36 + [0] * 12,
        THU: [3] * 30 + [0] * 20,
        FRI: [3] * 30 + [0] * 20
    }

    sample_classes = [
        # MATH101
        Class(course_code="MATH101", class_type="LEC", times=[
            Time(1, MON, 8.0, 1.0, 50)
        ]),
        Class(course_code="MATH101", class_type="TUT", times=[
            Time(2, TUE, 8.0, 1.0, 40),
            Time(3, TUE, 10.0, 1.0, 45),
            Time(4, TUE, 12.0, 1.0, 50),
            Time(5, TUE, 14.0, 1.0, 55),
            Time(6, TUE, 16.0, 1.0, 60),
            Time(7, WED, 8.0, 1.0, 65),
            Time(8, WED, 10.0, 1.0, 70),
            Time(9, WED, 12.0, 1.0, 75),
            Time(10, WED, 14.0, 1.0, 80),
            Time(11, WED, 16.0, 1.0, 85)
        ]),
        Class(course_code="MATH101", class_type="LAB", times=[
            Time(12, THU, 8.0, 1.0, 30),
            Time(13, THU, 10.0, 1.0, 35),
            Time(14, THU, 12.0, 1.0, 40),
            Time(15, THU, 14.0, 1.0, 45),
            Time(16, THU, 16.0, 1.0, 50),
            Time(17, FRI, 8.0, 1.0, 55),
            Time(18, FRI, 10.0, 1.0, 60),
            Time(19, FRI, 12.0, 1.0, 65),
            Time(20, FRI, 14.0, 1.0, 70),
            Time(21, FRI, 16.0, 1.0, 75)
        ]),
        # PHYS102
        Class(course_code="PHYS102", class_type="LEC", times=[
            Time(22, TUE, 11.0, 1.0, 55)
        ]),
        Class(course_code="PHYS102", class_type="TUT", times=[
            Time(23, WED, 8.0, 1.0, 45),
            Time(24, WED, 10.0, 1.0, 50),
            Time(25, WED, 12.0, 1.0, 55),
            Time(26, WED, 14.0, 1.0, 60),
            Time(27, WED, 16.0, 1.0, 65),
            Time(28, THU, 8.0, 1.0, 70),
            Time(29, THU, 10.0, 1.0, 75),
            Time(30, THU, 12.0, 1.0, 80),
            Time(31, THU, 14.0, 1.0, 85),
            Time(32, THU, 16.0, 1.0, 90)
        ]),
        Class(course_code="PHYS102", class_type="LAB", times=[
            Time(33, FRI, 8.0, 1.0, 45),
            Time(34, FRI, 10.0, 1.0, 50),
            Time(35, FRI, 12.0, 1.0, 55),
            Time(36, FRI, 14.0, 1.0, 60),
            Time(37, FRI, 16.0, 1.0, 65),
            Time(38, FRI, 18.0, 1.0, 70),
            Time(39, FRI, 19.0, 1.0, 75),
            Time(40, FRI, 20.0, 1.0, 80),
            Time(41, FRI, 21.0, 1.0, 85),
            Time(42, FRI, 22.0, 1.0, 90)
        ]),
        # CHEM103
        Class(course_code="CHEM103", class_type="LEC", times=[
            Time(43, WED, 16.0, 1.0, 75)
        ]),
        Class(course_code="CHEM103", class_type="TUT", times=[
            Time(44, THU, 8.0, 1.0, 65),
            Time(45, THU, 10.0, 1.0, 70),
            Time(46, THU, 12.0, 1.0, 75),
            Time(47, THU, 14.0, 1.0, 80),
            Time(48, THU, 16.0, 1.0, 85),
            Time(49, FRI, 8.0, 1.0, 90),
            Time(50, FRI, 10.0, 1.0, 95),
            Time(51, FRI, 12.0, 1.0, 100),
            Time(52, FRI, 14.0, 1.0, 105),
            Time(53, FRI, 16.0, 1.0, 110)
        ]),
        Class(course_code="CHEM103", class_type="LAB", times=[
            Time(54, FRI, 8.0, 1.0, 55),
            Time(55, FRI, 10.0, 1.0, 60),
            Time(56, FRI, 12.0, 1.0, 65),
            Time(57, FRI, 14.0, 1.0, 70),
            Time(58, FRI, 16.0, 1.0, 75),
            Time(59, FRI, 18.0, 1.0, 80),
            Time(60, FRI, 19.0, 1.0, 85),
            Time(61, FRI, 20.0, 1.0, 90),
            Time(62, FRI, 21.0, 1.0, 95),
            Time(63, FRI, 22.0, 1.0, 100)
        ]),
        # CS104
        Class(course_code="CS104", class_type="LEC", times=[
            Time(64, THU, 13.0, 1.0, 80)
        ]),
        Class(course_code="CS104", class_type="TUT", times=[
            Time(65, FRI, 8.0, 1.0, 90),
            Time(66, FRI, 9.0, 1.0, 92),
            Time(67, FRI, 10.0, 1.0, 94),
            Time(68, FRI, 11.0, 1.0, 96),
            Time(69, FRI, 12.0, 1.0, 98),
            Time(70, FRI, 13.0, 1.0, 100),
            Time(71, FRI, 14.0, 1.0, 102),
            Time(72, FRI, 15.0, 1.0, 104),
            Time(73, FRI, 16.0, 1.0, 106),
            Time(74, FRI, 17.0, 1.0, 108)
        ]),
        Class(course_code="CS104", class_type="LAB", times=[
            Time(75, FRI, 8.0, 1.0, 65),
            Time(76, FRI, 9.0, 1.0, 67),
            Time(77, FRI, 10.0, 1.0, 69),
            Time(78, FRI, 11.0, 1.0, 71),
            Time(79, FRI, 12.0, 1.0, 73),
            Time(80, FRI, 13.0, 1.0, 75),
            Time(81, FRI, 14.0, 1.0, 77),
            Time(82, FRI, 15.0, 1.0, 79),
            Time(83, FRI, 16.0, 1.0, 81),
            Time(84, FRI, 17.0, 1.0, 83)
        ])
    ]
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