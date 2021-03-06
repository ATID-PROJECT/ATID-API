from dynaconf import settings
import requests
import sys

def getGlossary( url_base, token, course_id, glossary_id ):
    function = "get_glossary"

    params = f"&glossary_id={glossary_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createGlossario(url_base, token, course_id, name, description, group_id):
    
    function = "create_glossary"
    params = f"&name={name}&description={description}&course_id={course_id}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateGlossario(url_base, token, glossario_id, name, description):

    function = "update_glossario"
    
    params = f"&name={name}&description={description}&glossario_id={glossario_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def setGlossaryGroup(url_base, token, glossary_id, course_id, group_id):
    
    function = "group_glossary"

    params = f"&group_id={group_id}&course_id={course_id}&glossary_id={glossary_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getGlossariesByCourse( url_base, token, course_id):
    function = "mod_glossary_get_glossaries_by_courses "

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result