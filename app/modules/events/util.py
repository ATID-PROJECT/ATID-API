import sys
import json
import requests
from dynaconf import settings

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

def getNextActivity(db, url_host, id_course, current_id):
    
    target_modules = []
    target_transictions = []

    network = db.run( f"MATCH (network:Network{{url:'{url_host}'}})-[r2]-(c:Course{{id:{id_course}}}) return network").data()[0]['network']
    
    all_data = json.loads( network['all_data'] )

    for item in all_data:
        
        if 'source' in item and item['source'] == current_id:
            
            target_transictions.append( item['target'] )

    for transiction in target_transictions:
        for item in all_data:
            if 'source' in item and item['source'] == transiction:
                target_modules.append( item['target'] )
    
    return [target_transictions,target_modules]

def getInstanceOfActivityUUID(db, url_base, id_course, uuid_activity, type_activity):

    all_instances = db.run(f"MATCH (a:Network{{url:'{url_base}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{type_activity.capitalize()}Instance{{id_{type_activity.lower()}:'{uuid_activity}'}}) return instance").data()
    return all_instances

def getNetworkByID(db, url_host, id_course, id_item ):

    network = db.run( f"MATCH (network:Network{{url:'{url_host}'}})-[r2]-(c:Course{{id:{id_course}}}) return network").data()[0]['network']
    all_data = json.loads( network['all_data'])

    for item in all_data:
        if( 'id' in item and item['id'] == id_item):
            return item

def addUserToGroup(url_base, token, id_user, id_group):

    function = "core_group_add_group_members"
    
    params = f"&members[0][userid]={id_user}&members[0][groupid]={id_group}"

    final_url = str( url_base + "/" +(str(settings.URL_MOODLE).format(str(token), function+params)))

   
    r = requests.post( final_url, data={}, verify=False)

    result = r.json()
    return result

def checkNextActivity(instance, target_uuid):
    result = False

    for id_name in ['id_quiz', 'id_chat']:
        if id_name in instance:
            result = ( instance[ id_name ] == target_uuid )

    return result


def getTransictionsByAny(db, id_course, id_quiz, url_moodle, type_table):
    table = str(type_table).capitalize()

    target_transiction_list = []
    target_activity_list = []
    target_connection_list = []

    all_instances = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{table}Instance{{id_instance:{id_quiz}}}) return instance").data()
    result = all_instances[0]['instance']
    uuid = result[f"id_{table.lower()}"]
    
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