from dynaconf import settings
import requests

def getChoice( url_base, token, course_id, choice_id ):
    function = "get_choice"

    params = f"&choice_id={choice_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createChoiceOption(url_base, token, choiceid, text, maxanswers):
    
    function = "local_wstemplate_handle_choice_option"
    params = f"&choiceid={int(choiceid)}&text={text}&maxanswers={int(maxanswers)}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createChoice(url_base, token, course_id, name, description, allowupdate, allowmultiple, limitanswers, choice_questions, group_id):
    
    function = "local_wstemplate_handle_choice"

    params = f"&name={name}&description={description}&course_id={course_id}&allowupdate={getValueFromCheckbox(allowupdate)}&\
        allowmultiple={getValueFromCheckbox(allowmultiple)}&limitanswers={getValueFromCheckbox(limitanswers)}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    for c in choice_questions:
        createChoiceOption(url_base, token, result['id'], c, 0)
        
    return result

def updateChoice(url_base, token, choice_id, name, description, allowupdate, allowmultiple, limitanswers, choice_questions):
    
    function = "update_choice"

    params = f"&name={name}&description={description}&choice_id={choice_id}&allowupdate={getValueFromCheckbox(allowupdate)}&allowmultiple={getValueFromCheckbox(allowmultiple)}&limitanswers={getValueFromCheckbox(limitanswers)}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    for c in choice_questions:
        createChoiceOption(url_base, token, result['id'], c, 0)
        
    return result

def setChoiceGroup(url_base, token, choice_id, course_id, group_id):
    
    function = "group_choice"

    params = f"&group_id={group_id}&course_id={course_id}&choice_id={choice_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getChoicesByCourse( url_base, token, course_id):
    function = "mod_choice_get_choices_by_courses"

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result