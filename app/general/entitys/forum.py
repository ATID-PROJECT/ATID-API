from dynaconf import settings
import requests
import sys

def createForum(url_base, token, course_id, name, description, type_forum, maxbytes, maxattachments, displaywordcount, forcesubscribe, trackingtype):
    
    function = "local_wstemplate_handle_forum"
    
    params = f"&name={name}&description={description}&course_id={course_id}&type={type_forum}&maxbytes={maxbytes}&\
        maxattachments={maxattachments}&displaywordcount={displaywordcount}&forcesubscribe={forcesubscribe}&trackingtype={trackingtype}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result
    
def updateForum(url_base, token, forum_id, name, description, type_forum, maxbytes, maxattachments, displaywordcount, forcesubscribe, trackingtype):
    
    function = "update_forum"
    params = f"&name={name}&description={description}&forum_id={forum_id}&type={type_forum}&maxbytes={maxbytes}&\
        maxattachments={maxattachments}&displaywordcount={displaywordcount}&forcesubscribe={forcesubscribe}&trackingtype={trackingtype}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result
