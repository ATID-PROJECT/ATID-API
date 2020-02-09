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

def getChatByCourse( url_base, token, course_id):
    function = "mod_chat_get_chats_by_courses"

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result


def createChat(url_base, token, course_id, name, description, group_id):
    
    function = "create_chat"
    params = f"&name={name}&description={description}&course_id={course_id}&group_id={group_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateChat(url_base, token, chat_id, name, description):
    
    function = "update_chat"
    params = f"&name={name}&description={description}&chat_id={chat_id}"
    
    final_url = str( str(url_base) + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def setChatGroup(url_base, token, chat_id, course_id, group_id):
    
    function = "group_chat"
    
    params = f"&group_id={group_id}&course_id={course_id}&chat_id={chat_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result