from dynaconf import settings
import requests
from .util import *
import sys

def createExterntool(url_base, token, course_id, name, description, showdescription, showtitlelaunch, showdescriptionlaunch,
 typeid,toolurl, securetoolurl, launchcontainer, resourcekey, password, instructorcustomparameters):
    function = "local_wstemplate_handle_lti"
    params = f"&name={name}&description={description}&course_id={course_id}&showdescription={getValueFromCheckbox(showdescription)}&showtitlelaunch={getValueFromCheckbox(showtitlelaunch)}&\
        showdescriptionlaunch={getValueFromCheckbox(showdescriptionlaunch)}&typeid={typeid}&toolurl={str(toolurl)}&securetoolurl={str(securetoolurl)}&launchcontainer={getValueFromCheckbox(launchcontainer)}&resourcekey={resourcekey}&\
            password={password}&instructorcustomparameters={instructorcustomparameters}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()


    return result

def updateExterntool(url_base, token, lti_id, name, description, showdescription, showtitlelaunch, showdescriptionlaunch,
 typeid,toolurl, securetoolurl, launchcontainer, resourcekey, password, instructorcustomparameters):
    function = "update_extern_tool"
    
    params = f"&name={name}&description={description}&lti_id={lti_id}&showdescription={getValueFromCheckbox(showdescription)}&showtitlelaunch={getValueFromCheckbox(showtitlelaunch)}&"+\
        f"showdescriptionlaunch={getValueFromCheckbox(showdescriptionlaunch)}&typeid={typeid}&toolurl={str(toolurl)}&securetoolurl={str(securetoolurl)}&launchcontainer={getValueFromCheckbox(launchcontainer)}&resourcekey={resourcekey}&"+\
            f"password={password}&instructorcustomparameters={instructorcustomparameters}"
    
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    print(final_url, file=sys.stderr)
    r = requests.post( final_url, data={} )
    result = r.json()

    return result
    