from classes import Class, Time
from constants import DAYS, NUMBER_OF_TIME_SLOTS
from algorithm import solve_timetable, print_schedule
import time

def test_fully_fledged_case():
    # All slots are ideal for all days
    time_slots = {day: [3] * NUMBER_OF_TIME_SLOTS for day in DAYS}

    # Generate 10 classes, each with 10 timeslots, all between 8am and 10pm
    classes = []
    course_codes = [f"COURSE{i+1:02d}" for i in range(4)]
    class_types = ["LEC", "TUT", "LAB"]
    for idx, code in enumerate(course_codes):
        # Each class gets a unique subclass_type
        subclass_type = f"{class_types[idx%len(class_types)]}_{idx+1:02d}"
        times = []
        for t in range(30):
            day = DAYS[t % len(DAYS)]
            # Start times: 8.0, 9.5, 11.0, ..., up to 21.5 (all end before 22.0)
            start_time = 8.0 + (t * 0.5)
            if start_time + 1.0 > 22.0:
                start_time = 20.0 + (t % 2) # fallback to keep within bounds
            duration = 1.0
            percent_booked = 10 * (t+1)
            activity_code = f"{code}_{subclass_type}_{t+1:02d}"
            times.append(Time(activity_code, day, start_time, duration, percent_booked))
        classes.append(Class(code, class_types[idx%len(class_types)], subclass_type, times))
    print(len(classes))
    before = time.time()
    result = solve_timetable(time_slots, classes)
    after = time.time()
    print(f"Time taken: {after - before:.2f} seconds")
    print_schedule(result)

if __name__ == "__main__":
    test_fully_fledged_case()
