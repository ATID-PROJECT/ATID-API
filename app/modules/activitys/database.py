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
    
    function = "create_data"
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

def setDatabaseGroup(url_base, token, data_id, course_id, group_id):
    
    function = "group_data"

    params = f"&group_id={group_id}&course_id={course_id}&data_id={data_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getDatabaseByCourse( url_base, token, course_id):
    function = "mod_data_get_databases_by_courses"

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result