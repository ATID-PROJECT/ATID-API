from dynaconf import settings
import requests
import sys

def getChat( url_base, token, course_id, chat_id ):
    function = "get_chat"

    params = f"&chat_id={chat_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result


def createChat(url_base, token, course_id, name, description, group_id):
    
    function = "local_wstemplate_handle_chat"
    params = f"&name={name}&description={description}&course_id={course_id}&group_id={group_id}"
    
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateChat(url_base, token, chat_id, name, description):
    
    function = "update_chat"
    params = f"&name={name}&description={description}&chat_id={chat_id}"
    
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result