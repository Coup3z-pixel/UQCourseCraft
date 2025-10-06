import os
from algorithm import solve_timetable
from conversion import convertForAlgorithmCourses, convertForAlgorithmTimeSlots, convertTimetableToGrid
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from constants import *
import time
import datetime
from bs4 import BeautifulSoup
import re
from datetime import datetime

import requests

app = Flask(__name__, static_folder='build')
cors = CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger_path = os.path.join(BASE_DIR, "logger.json")

timetable_count = 0

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

    return timetable_response.json()

def parse_course_timetable(course_json, course_code):
    course_key = next(iter(course_json))
    course_information = course_json[course_key]

    course_activities = []

    # Iterate over the activities
    for key, activity in course_information["activities"].items(): 
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
    print(request.args.get('semester'))
    print(request.args.get('location'))

    if len(course_code) != 8:
        return "Course not found", 400

    course_timetable = course_details(course_code, options={
        "semester": request.args.get('semester'),
        "location": request.args.get('location')
    })

    if course_timetable == {}:
        return "Course not found", 400

    return course_timetable

def parse_and_format_date(date_str):
    # Check for weekly recurring format
    if 'week' in date_str.lower() and ('due' in date_str.lower() or 'submission' in date_str.lower()):
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', date_str, re.IGNORECASE)
        day_match = re.search(r'(\w+day)', date_str, re.IGNORECASE)
        
        time_str = time_match.group(1) if time_match else ''
        day_str = day_match.group(1) if day_match else ''

        if day_str:
            return f"Weekly, {day_str.capitalize()} {time_str}".strip()
        
        # Fallback for weekly
        return "Weekly Assessment"

    # If not weekly, try to find specific dates
    dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', date_str)
    if dates:
        last_date_str = dates[-1]
        try:
            dt = datetime.strptime(last_date_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # As a last resort, return the cleaned original string
    return date_str.split('\n')[0]

def parse_weight(weight_str):
    if '%' in weight_str:
        try:
            return int(weight_str.replace('%', '').strip())
        except ValueError:
            return 0
    elif weight_str.lower() == 'pass/fail':
        return 0
    else:
        try:
            return int(weight_str)
        except ValueError:
            return 0

def map_assessment_type(category_str):
    category_lower = category_str.lower()
    if 'exam' in category_lower:
        return 'exam'
    if 'assignment' in category_lower:
        return 'assignment'
    if 'quiz' in category_lower:
        return 'quiz'
    if 'project' in category_lower:
        return 'project'
    if 'practical' in category_lower:
        return 'project'
    if 'tutorial' in category_lower or 'problem set' in category_lower:
        return 'assignment'
    return 'assignment'

@app.route("/assessment/<course_code>", methods = ['GET'])
def assessment_for_course(course_code):
    semester = request.args.get('semester') # e.g., S1
    location = request.args.get('location') # e.g., STLUC

    semester_map = {'S1': 'Semester 1', 'S2': 'Semester 2'}
    location_map = {'STLUC': 'St Lucia', 'GATTN': 'Gatton', 'HERST': 'Herston'}
    target_semester_str = semester_map.get(semester)
    target_location_str = location_map.get(location)

    if not target_semester_str or not target_location_str:
        return "Invalid or missing semester/location parameter.", 400

    try:
        course_offering_url = f"https://programs-courses.uq.edu.au/course.html?course_code={course_code}"
        response = requests.get(course_offering_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching course page: {e}", 500

    soup = BeautifulSoup(response.text, 'html.parser')
    
    ecp_url = None
    
    def find_ecp_in_table(table):
        if not table or not table.find('tbody'):
            return None
        
        for row in table.find('tbody').find_all('tr'):
            semester_cell = row.find('a', class_='course-offering-year')
            location_cell = row.find('td', class_='course-offering-location')

            if semester_cell and location_cell:
                semester_text = semester_cell.get_text()
                location_text = location_cell.get_text(strip=True)

                if target_semester_str in semester_text and target_location_str == location_text:
                    profile_cell = row.find('td', class_='course-offering-profile')
                    if profile_cell:
                        link = profile_cell.find('a', class_='profile-available')
                        if link and 'href' in link.attrs:
                            return link['href']
        return None

    current_offerings_table = soup.find('table', id='course-current-offerings')
    ecp_url = find_ecp_in_table(current_offerings_table)

    if not ecp_url:
        archived_offerings_table = soup.find('table', id='course-archived-offerings')
        ecp_url = find_ecp_in_table(archived_offerings_table)

    if not ecp_url:
        return "ECP link not found for specified semester and location.", 404

    try:
        ecp_response = requests.get(ecp_url)
        ecp_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching ECP page: {e}", 500

    ecp_soup = BeautifulSoup(ecp_response.text, 'html.parser')
    
    course_name = ''
    h1 = ecp_soup.find('h1')
    if h1:
        full_title = h1.get_text(strip=True)
        if '(' in full_title:
            course_name = full_title.split('(')[0].strip()
        else:
            course_name = full_title

    assessment_section = ecp_soup.find('section', id='assessment--section')
    assessments = []

    if assessment_section:
        summary_table = assessment_section.find('table')
        if summary_table and summary_table.find('tbody'):
            for index, row in enumerate(summary_table.find('tbody').find_all('tr')):
                cells = row.find_all('td')
                if len(cells) == 4:
                    category = cells[0].get_text(strip=True)
                    task_cell = cells[1]
                    task_name = task_cell.get_text(strip=True)
                    
                    task_link = task_cell.find('a')
                    if task_link:
                        task_name = task_link.get_text(strip=True)

                    weight_str = cells[2].get_text(strip=True)
                    due_date_str = cells[3].get_text(separator=' ', strip=True)

                    assessments.append({
                        'id': str(index + 1),
                        'courseCode': course_code.upper(),
                        'courseName': course_name,
                        'assessmentName': task_name,
                        'dueDate': parse_and_format_date(due_date_str),
                        'weighting': parse_weight(weight_str),
                        'notes': '',
                        'type': map_assessment_type(category)
                    })

    return assessments

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
    global timetable_count
    body = request.get_json()
    courses_activities = []
    attend_lectures = body.get('attendLectures')
    
    for course in body.get('courses'):
        course_timetable = course_details(course, options={
            "semester": body.get('semester'),
            "location": body.get('location')
        })

        course_info = parse_course_timetable(course_timetable, course)
        algo_course_compatible = convertForAlgorithmCourses(course_info, retrieveLectures=attend_lectures)
        courses_activities += algo_course_compatible

    preferences = body.get('timetablePreferences')
    timeslots = convertForAlgorithmTimeSlots(preferences)
    before = time.time()
    best_timetables = solve_timetable(timeslots, courses_activities)
    after = time.time() # This line was missing in the original code, added for completeness

    timetable_recommendation_response = {
            "recommendations": []
    }

    for index, timetable in enumerate(best_timetables):
        process_timetable = {
                "Monday": timetable["Monday"][16:44],
                "Tuesday": timetable["Tuesday"][16:44],
                "Wednesday": timetable["Wednesday"][16:44],
                "Thursday": timetable["Thursday"][16:44],
                "Friday": timetable["Friday"][16:44],
        }

        timetable_recommendation_response["recommendations"].append({
            "id": "rec_{id}".format(id=index+1),
            "name": "Recommendation {no}".format(no=index+1),
            "score": timetable["score"],
            "conflicts": 0,
            "grid": convertTimetableToGrid(process_timetable)
        })

    app.logger.info(f"Time taken: {after - before:.2f} seconds")
    timetable_count += 1
    app.logger.info(f"Timetables Generated: {timetable_count}")

    with open(logger_path, 'w') as f:
        f.write(str(timetable_count))

    return timetable_recommendation_response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    print(logger_path)

    if os.path.exists(logger_path):
        with open(logger_path, "r") as f:
            timetable_count = int(f.read())
    else:
        with open(logger_path, 'w+') as f:
            f.write(str(timetable_count))

    try:
        app.run(host='0.0.0.0', port=5000)
    except:
        with open(logger_path, 'w+') as f:
            f.write(f"{timetable_count}")
