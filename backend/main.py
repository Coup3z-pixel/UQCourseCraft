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

def parse_course_timetable(course_json):
    from datetime import datetime, timedelta
    # Days mapping
    days_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}

    # Create empty timetable
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("18:00", "%H:%M")
    time_slots = []
    while start_time < end_time:
        time_slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=30)

    # Initialize timetable dict
    timetable = {slot: [[] for _ in range(5)] for slot in time_slots}

    # Fill timetable
    subject_data = next(iter(course_json.values()))  # first subject
    for activity in subject_data["activities"].values():
        day = activity["day_of_week"]
        if day not in days_map:
            continue

        day_idx = days_map[day]
        start = datetime.strptime(activity["start_time"], "%H:%M")
        duration = int(activity["duration"])
        end = start + timedelta(minutes=duration)

        # Add activity to relevant time slots
        for slot in time_slots:
            slot_time = datetime.strptime(slot, "%H:%M")
            if start <= slot_time < end:
                timetable[slot][day_idx].append(activity["description"])

    # Example: print timetable
    for slot, days in timetable.items():
        print(slot, days)

    return timetable.items()


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

    for course in body.get('courses'):
        course_timetable = course_details(course, options={
            "semester": body.get('semester'),
            "location": body.get('location')
        })

        print(course_timetable)
    
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
    }
  ]
}
