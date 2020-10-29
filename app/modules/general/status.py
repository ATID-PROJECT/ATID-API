from dynaconf import settings
import requests
import sys

def getStatus( url_base, token, course_id, user_list, date_list ):
    function = "get_status"

    params = f"&user_list={user_list}&date_list={date_list}&courseid={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    print("...........", file=sys.stderr)
    print(final_url, file=sys.stderr)

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getGradeStatus( url_base, token, course_id, param ):
    function = "get_grades_status"

    params = f"&user_list={param}&courseid={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result
