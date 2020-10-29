from dynaconf import settings
import requests
import sys

def createWiki(url_base, token, course_id, name, description, group_id ):
    
    function = "create_wiki"
    params = f"&name={name}&description={description}&course_id={course_id}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result
    
def updateWiki(url_base, token, wiki_id, name, description):
    
    function = "update_wiki"
    
    params = f"&name={name}&description={description}&wiki_id={wiki_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def setWikiGroup(url_base, token, wiki_id, course_id, group_id):
    
    function = "group_wiki"

    params = f"&group_id={group_id}&course_id={course_id}&wiki_id={wiki_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getWikisByCourse( url_base, token, course_id):
    function = "mod_wiki_get_wikis_by_courses"

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result