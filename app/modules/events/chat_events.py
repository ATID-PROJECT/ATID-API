import requests
import sys
import json
import os
from dynaconf import settings

from .util import *

url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

def getNumMessages(url_base, token, id_user, chat_id):
    
    function = "count_messages_by_user"
    
    params = f"&user_id={id_user}&chat_id={chat_id}"
    
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={})
    result = r.json()

    return result['count']

def userCompletChat( db, id_course, id_chat, id_user, url_moodle ):
    try:
        token, target_transictions, transictions, instances = getTransictionsByAny( db, id_course, id_chat, url_moodle, 'chat')

        for instance in instances:
            if 'id_group' in instance:
                if userHasGroup(url_moodle, token, id_user, instance['id_group']):
                    #user has already passed the fork
                    return
                    
        for index, transiction in enumerate(transictions):

            if not 'conditions' in transiction:
                break

            conditions = transiction['conditions']
            num_messages = getNumMessages(url_moodle, token, id_user, id_chat)

            for condition in conditions:
                if not condition:
                    continue

                if isValid( condition, num_messages ):
     
                    for instance in instances:
        
                        if checkNextActivity(instance, target_transictions[index]):

                            addUserToGroup(url_moodle, token,id_user,instance['id_group'])
                            return

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)

def isValid( conditions, num_messages ):
    try:
        if not 'type' in conditions:
            return True
        
        type_condition = str(conditions['type']).lower()
        for index, condition in enumerate(conditions['children']):
            if 'condition_type' in condition:
                condition_type = str(condition['condition_type']).lower()
                if condition_type == 'min_msgs':

                    isValid = num_messages >= int( condition['min_msgs'] )
                    
                    if isValid and type_condition=='or':
                        break
                    elif not isValid and index == len(conditions['children'])-1 and type_condition=='or':
                        return False
                    elif not isValid and type_condition=='and':
                        return False
                
            elif 'type' in condition:
                valid = isValid( condition, num_messages )
                if valid and type_condition=='or':
                    break
                elif not valid and index == len(conditions['children'])-1 and type_condition=='or':
                    return False
                if not valid and type_condition=='and':
                    return False
                    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
        return 400

    return True

def validGrade( type_grade, grade, best_grade ):
    type_grade = str(type_grade).lower()
    grade = int( grade )
    result = False

    if type_grade == 'max':
        result = best_grade <= grade
    elif type_grade == 'min':
        result = best_grade >= grade
    else:
        result = best_grade == grade

    return result