from dynaconf import settings
import requests
import sys
from .util import *

def createDatabase(url_base, token, course_id, name, description, approval, manageapproved, comments, requiredentriestoview, maxentries,
timeavailablefrom,timeavailableto, timeviewfrom, timeviewto):
    print("===================", file=sys.stderr)
    function = "local_wstemplate_handle_data"
    params = f"&name={name}&description={description}&course_id={course_id}&approval={getValueFromCheckbox(approval)}&manageapproved={getValueFromCheckbox(manageapproved)}&comments={getValueFromCheckbox(comments)}&\
    requiredentriestoview={getValueFromCheckbox(requiredentriestoview)}&maxentries={getValueFromCheckbox(maxentries)}&timeavailablefrom={timeavailablefrom}&timeavailableto={timeavailableto}&\
    timeviewfrom={timeviewfrom}&timeviewto={timeviewto}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateDatabase(url_base, token, database_id, name, description, approval, manageapproved, comments, requiredentriestoview, maxentries,
timeavailablefrom,timeavailableto, timeviewfrom, timeviewto):
    
    function = "update_database"
    params = f"&name={name}&description={description}&database_id={database_id}&approval={getValueFromCheckbox(approval)}&manageapproved={getValueFromCheckbox(manageapproved)}&comments={getValueFromCheckbox(comments)}&\
    requiredentriestoview={getValueFromCheckbox(requiredentriestoview)}&maxentries={getValueFromCheckbox(maxentries)}&timeavailablefrom={timeavailablefrom}&timeavailableto={timeavailableto}&\
    timeviewfrom={timeviewfrom}&timeviewto={timeviewto}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result