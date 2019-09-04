from dynaconf import settings
import requests
from .util import *
import sys


def getLTI( url_base, token, course_id, lti_id ):
    function = "get_lti"

    params = f"&lti_id={lti_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createExterntool(url_base, token, course_id, name, description):
    function = "local_wstemplate_handle_lti"
    params = f"&name={name}&description={description}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()


    return result

def updateExterntool(url_base, token, lti_id, name, description):
    function = "update_extern_tool"
    
    params = f"&name={name}&description={description}&lti_id={lti_id}"
    
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result
    