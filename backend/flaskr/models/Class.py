from models.constants import *
from models.Time import Time


class Class:
    """
    Represents a university course class, such as a lecture or tutorial, with associated times.

    Attributes:
        course_code (str): The code of the course (e.g., 'MATH1051').
        class_type (str): The general type of the class (e.g., 'LEC', 'TUT').
        subclass_type (str): The specific subclass type (e.g., 'LEC1', 'LEC2', 'LEC3').
        times (list[Time]): A list of Time objects representing when the class occurs.
    """

    def __init__(
        self, course_code: str, class_type: str, subclass_type: str, times: list[Time]
    ) -> None:
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
            self.course_code == other.course_code
            and self.class_type == other.class_type
            and self.subclass_type == other.subclass_type
        )
