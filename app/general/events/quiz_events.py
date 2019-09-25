import requests
import sys
import json
import os
from dynaconf import settings

from .util import *

url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

def userHasGroup(url_base, token, userid, groupid):
    function = "core_group_get_group_members"
    
    params = f"&groupids[0]={groupid}"
    
    final_url = str( url_base + "/" + str(url_moodle.format(token, function+params)))
    print(str(final_url), file=sys.stderr)
    r = requests.post( final_url, data={})
    result = r.json()

    for userid_group in result[0]['userids']:
        if userid_group == userid:
            return True

    return False

def getBestNote(url_base, token, userid, quizid):
    function = "mod_quiz_get_user_best_grade"
    
    params = f"&userid={userid}&quizid={quizid}"

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    
    r = requests.post( final_url, data={})
    result = r.json()

    return result

def getTransictionsByAny(db, id_course, id_quiz, url_moodle, type_table):
    table = str(type_table).capitalize()

    target_transiction_list = []
    target_activity_list = []
    target_connection_list = []

    all_instances = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{table}Instance{{id_instance:{id_quiz}}}) return instance").data()
    result = all_instances[0]['instance']
    uuid = result["id_quiz"]
    
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(quiz:{table}{{uuid:'{uuid}'}}) return network").data()[0]['network']

    all_data = json.loads( network['all_data'])

    for item in all_data:
        if 'suggestion_uuid' in item and item['suggestion_uuid'] == uuid:
            target_activity_list.append( item['id'] )

    for item in all_data:
        if 'source' in item and item['source'] in target_activity_list:
            target_connection_list.append( item['target'] )

    for item in all_data:
        if 'id' in item and item['id'] in target_connection_list:
            target_transiction_list.append( item )

    #secound step (instances)
    transiction_connection_list = []
    target_transiction_ids = []
            
    target_transiction_list_id = [item['id'] for item in target_transiction_list ]
    for item in all_data:
        if 'source' in item and item['source'] in target_transiction_list_id:
            transiction_connection_list.append( item['target'] )

    for item in all_data:
        if ('id' in item) and item['id'] in transiction_connection_list:
            if 'suggestion_uuid' in item:
                target_transiction_ids.append( item['suggestion_uuid'] )
            else:
                target_transiction_ids.append("not_found")
                
    all_instances = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance) \
                    WHERE any(prop in ['id_quiz','id_chat'] where instance[prop] in {str(target_transiction_ids)} )\
                    return distinct instance" ).data()
    target_instances = [instance['instance'] for instance in all_instances]

    return network['token'],target_transiction_ids, target_transiction_list, target_instances

def userCompletQuiz(db, id_course, id_quiz, id_user, url_moodle):
    try:
        token, target_transictions, transictions, instances = getTransictionsByAny( db, id_course, id_quiz, url_moodle, 'quiz')

        for instance in instances:
            if 'id_group' in instance:
                if userHasGroup(url_moodle, token, id_user, instance['id_group']):
                    #user has already passed the fork
                    return
        for index, transiction in enumerate(transictions):

            print(transiction, file=sys.stderr)
            print('========================', file=sys.stderr)
            if not 'conditions' in transiction:
                break

            conditions = transiction['conditions']
            best_grade = getBestGrade(url_moodle, token, id_user, id_quiz)

            for condition in conditions:
                if not condition:
                    continue

                if not condition or isValid( condition, best_grade ):
     
                    for instance in instances:
                        print(target_transictions, file=sys.stderr)
                        print(index, file=sys.stderr)
                        print(target_transictions[index], file=sys.stderr)
                        if checkNextActivity(instance, target_transictions[index]):

                            addUserToGroup(url_moodle, token,id_user,instance['id_group'])
                            return

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
        return 400

def checkNextActivity(instance, target_uuid):
    result = False

    for id_name in ['id_quiz', 'id_chat']:
        if id_name in instance:
            result = ( instance[ id_name ] == target_uuid )

    return result

def getBestGrade(url_moodle, token, id_user, id_quiz):
    
    best_grade = getBestNote(url_moodle, token, id_user, id_quiz)

    if not best_grade['hasgrade']:
        return -1

    best_grade = best_grade['grade']
    return int( best_grade )

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

def isValid( conditions, best_grade ):
    try:
        if not 'type' in conditions:
            return True
        
        type_condition = str(conditions['type']).lower()
        for index, condition in enumerate(conditions['children']):
            if 'condition_type' in condition:
                condition_type = str(condition['condition_type']).lower()
                if condition_type == 'compare_note':

                    isValid = validGrade( condition['type_grade'],condition['grade_percentage'], best_grade )
                    if isValid and type_condition=='or':
                        break
                    elif not isValid and index == len(conditions['children'])-1 and type_condition=='or':
                        return False
                    elif not isValid and type_condition=='and':
                        return False
                
            elif 'type' in condition:
                valid = isValid( condition, best_grade )
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

def getInstance(db, target_activity, url_moodle, id_course ):
    instance = []
    if( 'suggestion_uuid' in target_activity ):
        type_item = target_activity['suggestion_type']
        item = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(item:{type_item}{{uuid:'{target_activity['suggestion_uuid']}'}}) return item").data()[0]['item']
        instance = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{type_item}Instance{{id_{type_item.lower()}:'{item['uuid']}'}}) return instance").data()[0]['instance']
        
    return instance
