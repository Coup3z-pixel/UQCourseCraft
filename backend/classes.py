"""
The file containing all helper classes for the algorithm file.
"""
from constants import *
import heapq

class Time:
    def __init__(self, activity_code: str, day: str, start_time: float, duration: float, percent_booked: int) -> None:
        """
        Initialize a class with the activity number, day, start time, duration, and percentage booked.
        
        Args:
            activity_number (int): The index of the activity in the schedule.
            day (str): The day of the week the class is scheduled.
            start_time (float): The start time of the class in military format (e.g., 13.5 for 1:30 PM).
            duration (int): The duration of the class in hours.
            percent_booked (int): The percentage of people that booked into the class compared to its capacity.
        """
        self.activity_code = activity_code
        self.day = day
        self.start_time = start_time
        self.duration = duration
        self.percent_booked = percent_booked
    
    def __repr__(self) -> str:
        return f"""Time(activity_number={self.activity_code}, 
            day={self.day}, 
            start_time={self.start_time}, 
            duration={self.duration}, 
            percent_booked={self.percent_booked})
        """
    
    def __eq__(self, other) -> bool:
        return (
            self.activity_number == other.activity_number and
            self.day == other.day and
            self.start_time == other.start_time and
            self.duration == other.duration and
            self.percent_booked == other.percent_booked
        )


class Class:
    """
    Represents a university course class, such as a lecture or tutorial, with associated times.

    Attributes:
        course_code (str): The code of the course (e.g., 'MATH1051').
        class_type (str): The general type of the class (e.g., 'LEC', 'TUT').
        subclass_type (str): The specific subclass type (e.g., 'LEC1', 'LEC2', 'LEC3').
        times (list[Time]): A list of Time objects representing when the class occurs.
    """

    def __init__(self, course_code: str, class_type: str, subclass_type: str, times: list[Time]) -> None:
        """
        Initializes a Class instance.

        Args:
            course_code (str): The code of the course.
            class_type (str): The general type of the class (e.g., 'LEC', 'TUT').
            subclass_type (str): The specific subclass type (e.g., 'LEC1', 'LEC2', 'LEC3').
            times (list[Time]): A list of Time objects representing when the class occurs.
        """
        self.course_code = course_code
        self.class_type = class_type
        self.subclass_type = subclass_type
        self.times = times
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Class instance.

        Returns:
            str: String representation of the Class.
        """
        return f"""Class(course_code={self.course_code}, class_type={self.class_type}, subclass_type={self.subclass_type}, times={self.times})"""
    
    def add_time(self, time: Time) -> None:
        self.times.append(time)
    
    def __eq__(self, other) -> bool:
        """
        Checks if two Class instances are equal based on their attributes.
        """
        return (
            self.course_code == other.course_code and
            self.class_type == other.class_type and
            self.subclass_type == other.subclass_type
        )


class ComparableSchedule:
    def __init__(self, score: int, schedule: dict):
        self.score = score
        self.schedule = schedule
    def __lt__(self, other):
            return self.score < other.score
    

class ScheduleHeap:
    def __init__(self, capacity: int) -> None:
        """
        Initialize a min-heap with a given capacity.
        """
        self.capacity = capacity
        self.heap = []
    
    def newEntry(self, score: int, schedule: dict) -> None:
        """
        Add a new entry to the heap with a given score and schedule. If the heap is not full or the 
        new entry has a higher score than the smallest entry, it is added to the heap.
        """
        if len(self.heap) < self.capacity or score > self.heap[0].score:
            heapq.heappush(self.heap, ComparableSchedule(score, schedule))

            if len(self.heap) > self.capacity:
                heapq.heappop(self.heap)
    
    def getBestSchedules(self) -> list[dict]:
        """
        Get the best schedules from the heap, sorted by score in descending order.
        """
        output = self.heap.copy()
        output.sort(reverse=True, key=lambda x: x.score)  # Sort by score in descending order
        return [comparable_schedule.schedule for comparable_schedule in output]  # Return in descending order of score
    
    def getBestSchedule(self) -> dict:
        """
        Get the best schedule from the heap.
        """
        print(self.heap)
        return self.heap[0].schedule if self.heap else None
