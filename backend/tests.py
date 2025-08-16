from algorithm import *
from constants import *
from classes import *
import pytest


class TestTrimClasses:
    def test_trims_unavailable_classes(self):
        time_slots = {
            MON: [4] * NUMBER_OF_TIME_SLOTS,
            TUE: [4] * NUMBER_OF_TIME_SLOTS,
            WED: [0] * NUMBER_OF_TIME_SLOTS,
            THU: [0] * NUMBER_OF_TIME_SLOTS,
            FRI: [0] * NUMBER_OF_TIME_SLOTS
        }

        sample_classes = [
            Class(course_code="MATH101", class_type="LEC", times=[Time(1, MON, 9.0, 1.0, 50)]),
            Class(course_code="PHYS102", class_type="TUT", times=[Time(2, TUE, 11.0, 1.5, 30)]),
            Class(course_code="CHEM103", class_type="LEC", times=[Time(3, WED, 14.0, 2.0, 70)]),
            Class(course_code="CS104", class_type="LAB", times=[Time(4, THU, 16.0, 1.0, 90)])
        ]

        trim_classes(time_slots, sample_classes)
        assert (
            sample_classes[0].times == [Time(1, MON, 9.0, 1.0, 50)] and
            sample_classes[1].times == [Time(2, TUE, 11.0, 1.5, 30)] and
            sample_classes[2].times == [] and
            sample_classes[3].times == []
        )
 
    def test_trims_all_classes_when_fully_unavailable(self):
        time_slots = {
            MON: [0] * 48,
            TUE: [0] * 48,
            WED: [0] * 48,
            THU: [0] * 48,
            FRI: [0] * 48
        }

        sample_classes = [
            Class(course_code="MATH101", class_type="LEC", times=[Time(1, MON, 9.0, 1.0, 50)]),
            Class(course_code="PHYS102", class_type="TUT", times=[Time(2, TUE, 11.0, 1.5, 30)]),
            Class(course_code="CHEM103", class_type="LEC", times=[Time(3, WED, 14.0, 2.0, 70)]),
            Class(course_code="CS104", class_type="LAB", times=[Time(4, THU, 16.0, 1.0, 90)])
        ]

        trim_classes(time_slots, sample_classes)
        assert all(class_.times == [] for class_ in sample_classes)
