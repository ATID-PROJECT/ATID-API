from dynaconf import settings
import requests

def createQuiz(url_base, token, course_id, name, description, timeopen, timeclose):
    
    function = "local_wstemplate_handle_quiz"
    params = f"&course_id={course_id}&name={name}&description={description}&timeopen={timeopen}&timeclose={timeclose}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateQuiz(url_base, token, quiz_id, name, description, timeopen, timeclose):
    
    function = "update_quiz"
    params = f"&quiz_id={quiz_id}&name={name}&description={description}&timeopen={timeopen}&timeclose={timeclose}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result