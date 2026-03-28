import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request

assessment_api = Blueprint("assessment", __name__)


def parse_and_format_date(date_str):
    # Check for weekly recurring format
    if "week" in date_str.lower() and (
        "due" in date_str.lower() or "submission" in date_str.lower()
    ):
        time_match = re.search(
            r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))", date_str, re.IGNORECASE
        )
        day_match = re.search(r"(\w+day)", date_str, re.IGNORECASE)

        time_str = time_match.group(1) if time_match else ""
        day_str = day_match.group(1) if day_match else ""

        if day_str:
            return f"Weekly, {day_str.capitalize()} {time_str}".strip()

        # Fallback for weekly
        return "Weekly Assessment"

    # If not weekly, try to find specific dates
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", date_str)
    if dates:
        last_date_str = dates[-1]
        try:
            dt = datetime.strptime(last_date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # As a last resort, return the cleaned original string
    return date_str.split("\n")[0]


def parse_weight(weight_str):
    if "%" in weight_str:
        try:
            return int(weight_str.replace("%", "").strip())
        except ValueError:
            return 0
    elif weight_str.lower() == "pass/fail":
        return 0
    else:
        try:
            return int(weight_str)
        except ValueError:
            return 0


def map_assessment_type(category_str):
    category_lower = category_str.lower()
    if "exam" in category_lower:
        return "exam"
    if "assignment" in category_lower:
        return "assignment"
    if "quiz" in category_lower:
        return "quiz"
    if "project" in category_lower:
        return "project"
    if "practical" in category_lower:
        return "project"
    if "tutorial" in category_lower or "problem set" in category_lower:
        return "assignment"
    return "assignment"


@assessment_api.route("/assessment/<course_code>", methods=["GET"])
def assessment_for_course(course_code):
    semester = request.args.get("semester")  # e.g., S1
    location = request.args.get("location")  # e.g., STLUC

    semester_map = {"S1": "Semester 1", "S2": "Semester 2"}
    location_map = {"STLUC": "St Lucia", "GATTN": "Gatton", "HERST": "Herston"}
    target_semester_str = semester_map.get(semester)
    target_location_str = location_map.get(location)

    if not target_semester_str or not target_location_str:
        return "Invalid or missing semester/location parameter.", 400

    try:
        course_offering_url = (
            f"https://programs-courses.uq.edu.au/course.html?course_code={course_code}"
        )
        response = requests.get(course_offering_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching course page: {e}", 500

    soup = BeautifulSoup(response.text, "html.parser")

    ecp_url = None

    def find_ecp_in_table(table):
        if not table or not table.find("tbody"):
            return None

        for row in table.find("tbody").find_all("tr"):
            semester_cell = row.find("a", class_="course-offering-year")
            location_cell = row.find("td", class_="course-offering-location")

            if semester_cell and location_cell:
                semester_text = semester_cell.get_text()
                location_text = location_cell.get_text(strip=True)

                if (
                    target_semester_str in semester_text
                    and target_location_str == location_text
                ):
                    profile_cell = row.find("td", class_="course-offering-profile")
                    if profile_cell:
                        link = profile_cell.find("a", class_="profile-available")
                        if link and "href" in link.attrs:
                            return link["href"]
        return None

    current_offerings_table = soup.find("table", id="course-current-offerings")
    ecp_url = find_ecp_in_table(current_offerings_table)

    if not ecp_url:
        archived_offerings_table = soup.find("table", id="course-archived-offerings")
        ecp_url = find_ecp_in_table(archived_offerings_table)

    if not ecp_url:
        return "ECP link not found for specified semester and location.", 404

    try:
        ecp_response = requests.get(ecp_url)
        ecp_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching ECP page: {e}", 500

    ecp_soup = BeautifulSoup(ecp_response.text, "html.parser")

    course_name = ""
    h1 = ecp_soup.find("h1")
    if h1:
        full_title = h1.get_text(strip=True)
        if "(" in full_title:
            course_name = full_title.split("(")[0].strip()
        else:
            course_name = full_title

    assessment_section = ecp_soup.find("section", id="assessment--section")
    assessments = []

    if assessment_section:
        summary_table = assessment_section.find("table")
        if summary_table and summary_table.find("tbody"):
            for index, row in enumerate(summary_table.find("tbody").find_all("tr")):
                cells = row.find_all("td")
                if len(cells) == 4:
                    category = cells[0].get_text(strip=True)
                    task_cell = cells[1]
                    task_name = task_cell.get_text(strip=True)

                    task_link = task_cell.find("a")
                    if task_link:
                        task_name = task_link.get_text(strip=True)

                    weight_str = cells[2].get_text(strip=True)
                    due_date_str = cells[3].get_text(separator=" ", strip=True)

                    assessments.append(
                        {
                            "id": str(index + 1),
                            "courseCode": course_code.upper(),
                            "courseName": course_name,
                            "assessmentName": task_name,
                            "dueDate": parse_and_format_date(due_date_str),
                            "weighting": parse_weight(weight_str),
                            "notes": "",
                            "type": map_assessment_type(category),
                        }
                    )

    return assessments
