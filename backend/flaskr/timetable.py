import time

from conversion import (
    convertForAlgorithmCourses,
    convertForAlgorithmTimeSlots,
    convertTimetableToGrid,
)
from course_interface import course_details
from flask import Blueprint, request
from recommendation.algorithm import solve_timetable

timetable_api = Blueprint("timetable", __name__)


def parse_course_timetable(course_json, course_code):
    course_key = next(iter(course_json))
    course_information = course_json[course_key]

    course_activities = []

    # Iterate over the activities
    for key, activity in course_information["activities"].items():
        course_activities.append(
            {
                "course_code": course_code,
                "class_type": key.split("|")[1],
                "activity_code": activity["activity_code"],
                "day": activity["day_of_week"],
                "start": activity["start_time"],
                "duration": activity["duration"],
                "availability:": activity["availability"],
            }
        )

    return course_activities


@timetable_api.route("/recommend", methods=["POST"])
def recommend_timetable():
    """
    data: {
        semester: semester,
                location: location,
                courses: courses,
                timetablePreferences: convertTimetableForAPI()
    }
    """
    body = request.get_json()
    courses_activities = []
    attend_lectures = body.get("attendLectures")

    for course in body.get("courses"):
        course_timetable = course_details(
            course,
            options={
                "semester": body.get("semester"),
                "location": body.get("location"),
            },
        )

        course_info = parse_course_timetable(course_timetable, course)
        algo_course_compatible = convertForAlgorithmCourses(
            course_info, retrieveLectures=attend_lectures
        )
        courses_activities += algo_course_compatible

    preferences = body.get("timetablePreferences")
    timeslots = convertForAlgorithmTimeSlots(preferences)
    before = time.time()
    best_timetables = solve_timetable(timeslots, courses_activities)
    after = (
        time.time()
    )  # This line was missing in the original code, added for completeness

    timetable_recommendation_response = {"recommendations": []}

    for index, timetable in enumerate(best_timetables):
        process_timetable = {
            "Monday": timetable["Monday"][16:44],
            "Tuesday": timetable["Tuesday"][16:44],
            "Wednesday": timetable["Wednesday"][16:44],
            "Thursday": timetable["Thursday"][16:44],
            "Friday": timetable["Friday"][16:44],
        }

        timetable_recommendation_response["recommendations"].append(
            {
                "id": "rec_{id}".format(id=index + 1),
                "name": "Recommendation {no}".format(no=index + 1),
                "score": timetable["score"],
                "conflicts": 0,
                "grid": convertTimetableToGrid(process_timetable),
            }
        )

    return timetable_recommendation_response
