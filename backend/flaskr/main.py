import datetime
import os
from datetime import datetime

from assessments import assessment_api
from course import course_api
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from timetable import timetable_api

app = Flask(__name__, static_folder="build")
cors = CORS(
    app,
    origins=[
        "https://uqcoursecraft.onrender.com/",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger_path = os.path.join(BASE_DIR, "logger.json")

app.register_blueprint(course_api, url_prefix="/course")
app.register_blueprint(timetable_api, url_prefix="/timetable")
app.register_blueprint(assessment_api, url_prefix="/assessment")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print(e)
