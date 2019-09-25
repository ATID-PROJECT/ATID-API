from dynaconf import settings
import requests
import sys
from .util import *

def getDatabase( url_base, token, course_id, data_id ):
    function = "get_data"

    params = f"&data_id={data_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createDatabase(url_base, token, course_id, name, description, group_id):
    
    function = "local_wstemplate_handle_data"
    params = f"&name={name}&description={description}&course_id={course_id}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateDatabase(url_base, token, database_id, name, description):
    
    function = "update_database"
    params = f"&name={name}&description={description}&database_id={database_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result