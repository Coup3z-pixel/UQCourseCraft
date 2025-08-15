from flask import Flask, jsonify, request
from flask_cors import CORS

import requests

app = Flask(__name__)
cors = CORS(app)

def course_details(course_code, options):
    timetable_url = "https://timetable.my.uq.edu.au/odd/rest/timetable/subjects"
    course_body = {
        "search-term": course_code,
        "semester": options['semester'],
        "campus": options['location'],
        "faculty": "ALL",
        "type": "ALL",
        "days": ["0", "1", "2", "3", "4", "5", "6"],
        "start-time": "00:00",
        "end-time": "23:00"
    }

    timetable_response = requests.post(timetable_url, data=course_body)
    
    print(timetable_response.json())

    return timetable_response.json()


@app.route("/course/<course_code>", methods = ['GET'])
def course(course_code):
    course_timetable = course_details(course_code, options={
        "semester": request.args.get('semester'),
        "location": request.args.get('location')
    })

    return course_timetable


@app.route("/timetable", methods = ['POST'])
def recommend_timetable():
    '''
    data: {
        semester: semester,
		location: location,
		courses: courses,
		timetablePreferences: convertTimetableForAPI()
    }
    '''

    data = request.get_json()
    print(data)

    populated_timetable = [
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
    ]

    for course in data.get('courses'):
        course_timetable = course_details(course, options={
            "semester": data.get('semester'),
            "location": data.get('location')
        })

        print(course_timetable)


    # for each courses get the times
    """
        course_code: string | null
        preference: "default" | "preferred" | "unavailable"
        rank: number // 1-5 ranking system, 1 being highest preference
    """

    return [
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
        [[], [], [], [], [{ "course_code": "SCIE1200", "preferences": "preferred", "rank": 1}]],
    ]
