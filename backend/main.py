from algorithm import solve_timetable
from conversion import convertForAlgorithmCourses, convertForAlgorithmTimeSlots
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

def parse_course_timetable(course_json, course_code):
    course_key = next(iter(course_json))
    course_information = course_json[course_key]

    print(course_key) 

    course_activities = []

    # Iterate over the activities
    for key, activity in course_information["activities"].items():
        print("Key:", key)
        print("Course type: ", key.split("|")[1])
        print("Day:", activity["day_of_week"])
        print("Start:", activity["start_time"])
        print("Duration:", activity["duration"])
        print("Availability:", activity["availability"])
        print("---")

        course_activities.append({
            "course_code": course_code,
            "class_type": key.split("|")[1],
            "activity_code": activity["activity_code"],
            "day": activity["day_of_week"],
            "start": activity["start_time"],
            "duration": activity["duration"],
            "availability:": activity["availability"]
        })

    return course_activities    

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

    body = request.get_json()
    print(body)

    courses_activities = []
    
    for course in body.get('courses'):
        course_timetable = course_details(course, options={
            "semester": body.get('semester'),
            "location": body.get('location')
        })

        print(course_timetable)

        course_info = parse_course_timetable(course_timetable, course)
        algo_course_compatible = convertForAlgorithmCourses(course_info)
        courses_activities.append(algo_course_compatible)

    # Retrieve timeslot preferences, and convert them to algorithm format
    preferences = body.get('timetablePreferences')
    timeslots = convertForAlgorithmTimeSlots(preferences)

    print(courses_activities)

    best_timetables = solve_timetable(timeslots, courses_activities)

    # solve timetable

    timetable_recommendation_response = {
            "recommendations": []
    }

    for timetable in best_timetables:
        pass
    
    return {
        "recommendations": [
    {
      "id": "rec_001",
      "name": "Best Overall",
      "score": 95,
      "conflicts": 0,
      "grid": [
        [
          [],
          [],
          [
            {
              "course_code": "COMP3506 LEC 01",
              "preferences": "preferred",
              "rank": 1
            }
          ],
          [],
          []
        ],
        [
          [],
          [],
          [],
          [
            {
              "course_code": "MATH2001",
              "preferences": "preferred",
              "rank": 2
            }
          ],
          []
        ]
      ]
    },
    {
      "id": "rec_001",
      "name": "Best Overall",
      "score": 95,
      "conflicts": 0,
      "grid": [
        [
          [],
          [],
          [
            {
              "course_code": "COMP3506 LEC 01",
              "preferences": "preferred",
              "rank": 1
            }
          ],
          [],
          []
        ],
        [
          [],
          [],
          [],
          [
            {
              "course_code": "MATH2001",
              "preferences": "preferred",
              "rank": 2
            }
          ],
          []
        ]
      ]
    }
  ]
}

