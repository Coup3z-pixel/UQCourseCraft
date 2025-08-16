"""
The file containing all helper classes for the algorithm file.
"""
from constants import *

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
        """
        Adds a Time object to the class's times list.

        Args:
            time (Time): The Time object to add.
        """
        self.times.append(time)