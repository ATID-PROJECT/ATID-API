from dynaconf import settings
import requests
import sys

def getQuiz( url_base, token, course_id, quiz_id ):
    function = "get_quiz"

    params = f"&quiz_id={quiz_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createQuiz(url_base, token, course_id, name, description, group_id):
    
    function = "create_quiz"
    params = f"&course_id={course_id}&name={name}&description={description}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )

    result = r.json()

    return result

def updateQuiz(url_base, token, quiz_id, name, description, open_date='', end_date=''):
    
    function = "update_quiz"
    params = f"&quiz_id={quiz_id}&name={name}&description={description}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def setQuizGroup(url_base, token, quiz_id, course_id, group_id):
    
    function = "group_quiz"

    params = f"&group_id={group_id}&course_id={course_id}&quiz_id={quiz_id}"

    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def getQuizzestByCourse( url_base, token, course_id):
    function = "mod_quiz_get_quizzes_by_courses"

    params = f"&courseids[0]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result