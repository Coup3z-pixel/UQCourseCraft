from flask import Flask, jsonify, request
from flask_cors import CORS

import requests

app = Flask(__name__)
cors = CORS(app)

@app.route("/course/<course_code>", methods = ['GET'])
def course(course_code):
    print(request.args.get('semester'))
    print(request.args.get('location'))

    timetable_url = "https://timetable.my.uq.edu.au/odd/rest/timetable/subjects"
    course_body = {
        "search-term": course_code,
        "semester": request.args.get('semester'),
        "campus": request.args.get('location'),
        "faculty": "ALL",
        "type": "ALL",
        "days": ["0", "1", "2", "3", "4", "5", "6"],
        "start-time": "00:00",
        "end-time": "23:00"
    }

    timetable_response = requests.post(timetable_url, data=course_body)
    
    print(timetable_response.json())

    return timetable_response.json()


@app.route("/timetable", methods = ['POST'])
def recommend_timetable():
    '''
    data: {
        
    }
    '''

    data = request.data
    print(data)

    return "<p>Hello, World!</p>"
