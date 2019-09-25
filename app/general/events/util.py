import sys
import json
import requests
from dynaconf import settings

def getNextActivity(db, url_host, id_course, current_id):
    
    target_activitys = []
    target_transictions = []

    network = db.run( f"MATCH (network:Network{{url:'{url_host}'}})-[r2]-(c:Course{{id:{id_course}}}) return network").data()[0]['network']
    
    all_data = json.loads( network['all_data'] )

    for item in all_data:
        
        if 'source' in item and item['source'] == current_id:
            
            target_transictions.append( item['target'] )

    for transiction in target_transictions:
        for item in all_data:
            if 'source' in item and item['source'] == transiction:
                target_activitys.append( item['target'] )
    
    return [target_transictions,target_activitys]

def getInstanceOfActivityUUID(db, url_base, id_course, uuid_activity, type_activity):
    print(f"MATCH (a:Network{{url:'{url_base}'}})-[r2]-(c:Course{{id:{id_course}}})-[r3]-(instance:{type_activity.capitalize()}Instance{{id_{type_activity.lower()}:'{uuid_activity}'}}) return instance", file=sys.stderr)
    print("000000000000000", file=sys.stderr)
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
 


    