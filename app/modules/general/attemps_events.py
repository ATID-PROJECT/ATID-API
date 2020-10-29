from dynaconf import settings
import requests
import sys

def getAttempsStatus( url_base, token, courseid, quizid ):
    
    function = "user_attemps_external"

    params = f"&courseid={courseid}&quizid={quizid}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result