from dynaconf import settings
import requests
import sys

def createWiki(url_base, token, course_id, name, description, group_id ):
    
    function = "local_wstemplate_handle_wiki"
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
