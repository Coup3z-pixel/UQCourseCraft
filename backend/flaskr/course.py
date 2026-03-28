import requests
from course_interface import course_details
from flask import Blueprint, request

course_api = Blueprint("course", __name__)


@course_api.route("/<course_code>", methods=["GET"])
def course(course_code):
    print(request.args.get("semester"))
    print(request.args.get("location"))

    if len(course_code) != 8:
        return "Course not found", 400

    course_timetable = course_details(
        course_code,
        options={
            "semester": request.args.get("semester"),
            "location": request.args.get("location"),
        },
    )

    if course_timetable == {}:
        return "Course not found", 400

    return course_timetable
