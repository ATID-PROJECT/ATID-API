import requests
import sys
import json
import os
from dynaconf import settings

from .util import *

def userHasGroup(url_base, token, userid, groupid):
    function = "core_group_get_group_members"
    
    params = f"&groupids[0]={groupid}"
    
    final_url = str( url_base + "/" +(settings.url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = r.json()

    for userid_group in result[0]['userids']:
        if userid_group == userid:
            return True

    return False

def getBestNote(url_base, token, userid, quizid):
    function = "mod_quiz_get_user_best_grade"
    
    params = f"&userid={userid}&quizid={quizid}"

    final_url = str( url_base + "/" +(settings.url_moodle.format(token, function+params)))
    
    r = requests.post( final_url, data={})
    result = r.json()

    return result

def getActivityInstance(db, id_course, id_quiz, url_moodle):
    target_activity_list = []
    all_instances_list = []
    id_transiction_list = []
    
    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:QuizInstance{id_instance:%s}) return instance" % (url_moodle, id_course, id_quiz)).data()
    result = all_instances[0]['instance']
    uuid = result["id_quiz"]
    
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) return network").data()[0]['network']

    all_data = json.loads( network['all_data'])

    for item in all_data:
        if 'suggestion_uuid' in item and item['suggestion_uuid'] == uuid:
            id_activity = item['id']

    for item in all_data:
        if 'source' in item and item['source'] == id_activity:
            id_transiction = item['target']
            id_transiction_list.append( item['target'] )
            
            for item in all_data:
                if 'source' in item and item['source'] == id_transiction:
                    target_id = item['target']

            for item in all_data:
                if 'id' in item and item['id'] == target_id:
                    #pick up next activity on bpmn
                    target_activity_list.append( item )

    for target_activity in target_activity_list:
        #get activity list saved to database
        instance = getInstance(db, target_activity, url_moodle, id_course )
        all_instances_list.append( instance )

    return [id_transiction_list, network['token'], all_instances_list]

def userCompletQuiz(db, id_course, id_quiz, id_user, url_moodle):
    id_transiction_list, token, all_instances = getActivityInstance( db, id_course, id_quiz, url_moodle )
   
    for instance in all_instances:
        if userHasGroup(url_moodle, token, id_user, instance['id_group']):
            #user has already passed the fork
            return
    for index, instance in enumerate(all_instances):
        id_transiction = id_transiction_list[index]

        best_grade = getBestNote(url_moodle, token, id_user, id_quiz)
        result = db.run(f"MATCH (network:Network{{url:'{url_moodle}'}})-[r2]-(cond:Condition{{id_transiction:'{id_transiction}'}}) return cond").data()

        if len(result) == 0:
            return

        result = json.loads( result[0]['cond']['data'] )['default']

        if result['propriedade'].lower() == "number;Nota recebida".lower() and best_grade['hasgrade']:
            
            grade = best_grade['grade']
            current_note = int( result['valor'] )

            if result['operacao'] == "=" and grade == current_note:
                addUserToGroup(url_moodle, token,id_user,instance['id_group'])
                return

            elif result['operacao'] == ">" and current_note > grade:
                addUserToGroup(url_moodle, token,id_user,instance['id_group'])
                return

            elif result['operacao'] == "<" and current_note < grade:
                addUserToGroup(url_moodle, token,id_user,instance['id_group'])
                return

def getInstance(db, target_activity, url_moodle, id_course ):
    instance = []
    if( 'suggestion_uuid' in target_activity ):
        type_item = target_activity['suggestion_type']
        item = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(item:{type_item}{{uuid:'{target_activity['suggestion_uuid']}'}}) return item").data()[0]['item']
        instance = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{type_item}Instance{{id_{type_item.lower()}:'{item['uuid']}'}}) return instance").data()[0]['instance']
        
    return instance
