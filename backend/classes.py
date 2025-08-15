"""
The file containing all helper classes for the algorithm file.
"""

class Time:
    def __init__(self, day: str, start_time: float, duration: float, percent_booked: int) -> None:
        """
        Initialize a class with a day, start time, and duration.
        
        Args:
            day (str): The day of the week the class is scheduled.
            start_time (float): The start time of the class in military format (e.g., 13.5 for 1:30 PM).
            duration (int): The duration of the class in hours.
        """
        self.day = day
        self.start_time = start_time
        self.duration = duration
        self.percent_booked = percent_booked
    
    def __repr__(self):
        return f"Time(day={self.day}, start_time={self.start_time}, duration={self.duration}, percent_booked={self.percent_booked})"


class Class:
    def __init__(self, class_type: str, times: list[Time]):
        """
        Initialize a class with a type and a list of times.

        Args:
            type (str): The type of class (e.g., lecture, tutorial).
            times (list[Time]): A list of Time objects representing when the class occurs.
        """
        self.class_type = class_type
        self.times = times
    
    def __repr__(self):
        return f"Class(class_type={self.class_type}, times={self.times})"


class Course:
    def __init__(self, code: str, classes: list[Class]):
        """
        Initialize a course with a code and a list of classes.

        Args:
            code (str): The course code (e.g., "COMP1000").
            classes (list[Class]): A list of Class objects representing the different types of classes for the course.
        """
        self.code = code
        self.classes = classes
    
    def __repr__(self):
        return f"Course(code={self.code}, classes={self.classes})"
    