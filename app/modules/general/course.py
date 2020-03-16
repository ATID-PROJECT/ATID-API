from dynaconf import settings
import requests
import sys

def getCourses( url_base, token ):
    function = "core_course_get_courses"

    params = f""
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getCourseByName( url_base, token, course_name ):
    function = "core_course_get_courses_by_field"

    params = f"&field=shortname&value={course_name}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getUsersByCourse( url_base, token, courseid ):
    function = "get_users_by_course"

    params = f"&courseid={courseid}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def get_enrolled(db, current_user, network_id, course_id):
    network = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net" %
        (current_user, network_id)).data()[0]['net']

    url_base = network['url']
    token = network['token']

    function = "core_enrol_get_enrolled_users"
    params = f"&courseid={course_id}"
    final_url = str(url_base + "/" +
                    (settings.URL_MOODLE.format(token, function + params)))

    r = requests.post(final_url, data={})
    result = r.json()

    return result