import requests
import sys
import json

url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

def getBestNote(url_base, token, userid, quizid):
    function = "mod_quiz_get_user_best_grade"
    
    params = f"&userid={userid}&quizid={quizid}"

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = r.json()

    return result

def userCompletQuiz(db, id_course, id_quiz, id_user, url_moodle):

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
            
            for item in all_data:
                if 'source' in item and item['source'] == id_transiction:
                    target_id = item['target']

            for item in all_data:
                if 'id' in item and item['id'] == target_id:
                    target_activity = item

            result = db.run(f"MATCH (network:Network{{url:'{url_moodle}'}})-[r2]-(cond:Condition{{id_activity:'{id_activity}'}}) return cond").data()

            if len(result) == 0:
                return
            result = json.loads( result[0]['cond']['data'] )['default']

            best_grade = getBestNote(url_moodle, network['token'], id_user, id_quiz)

            """if len(result) == 0:
                instance = getInstance(db, target_activity, url_moodle, id_course, item )
                addUserToGroup(url_moodle, network['token'], id_user,instance['id_group'])"""

            print(result,file=sys.stderr)
            print(best_grade,file=sys.stderr)
            if result['propriedade'].lower() == "number;Nota recebida".lower() and best_grade['hasgrade']:

                if result['operacao'] == "=":
                    if( best_grade['grade'] == int(result['valor'])):
                        if( 'suggestion_uuid' in target_activity ):
                            instance = getInstance(db, target_activity, url_moodle, id_course, item )
                            addUserToGroup(url_moodle, network['token'],id_user,instance['id_group'])

                elif result['operacao'] == ">":
                    if( best_grade['grade'] > int(result['valor'])):
                        if( 'suggestion_uuid' in target_activity ):
                            instance = getInstance(db, target_activity, url_moodle, id_course, item )
                            addUserToGroup(url_moodle, network['token'],id_user,instance['id_group'])

                elif result['operacao'] == "<":
                    if( best_grade['grade'] < int(result['valor'])):
                        if( 'suggestion_uuid' in target_activity ):
                            instance = getInstance(db, target_activity, url_moodle, id_course, item )
                            addUserToGroup(url_moodle, network['token'],id_user,instance['id_group'])

def getInstance(db, target_activity, url_moodle, id_course, item ):
    type_item = target_activity['suggestion_type']
    item = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(item:{type_item}{{uuid:'{target_activity['suggestion_uuid']}'}}) return item").data()[0]['item']
    instance = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{type_item}Instance{{id_{type_item.lower()}:'{item['uuid']}'}}) return instance").data()[0]['instance']
    return instance

def addUserToGroup(url_base, token, id_user, id_group):
    function = "core_group_add_group_members"
    
    params = f"&members[0][userid]={id_user}&members[0][groupid]={id_group}"

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = r.json()

    print(final_url, file=sys.stderr)
    print(result, file=sys.stderr)

    return result