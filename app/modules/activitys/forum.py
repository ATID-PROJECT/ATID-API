from dynaconf import settings
import requests
import sys

def getForum( url_base, token, course_id, forum_id ):
    function = "get_forum"

    params = f"&forum_id={forum_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createForum(url_base, token, course_id, name, description, group_id):
    
    function = "create_forum"
    
    params = f"&name={name}&description={description}&course_id={course_id}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    
    result = r.json()

    return result
    
def updateForum(url_base, token, forum_id, name, description):
    
    function = "update_forum"
    params = f"&name={name}&description={description}&forum_id={forum_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def setForumGroup(url_base, token, forum_id, course_id, group_id):
    
    function = "group_forum"

    params = f"&group_id={group_id}&course_id={course_id}&forum_id={forum_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getForumsByCourse( url_base, token, course_id):
    function = "mod_forum_get_forums_by_courses "

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result