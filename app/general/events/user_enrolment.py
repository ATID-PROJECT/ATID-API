from flask import abort
import requests
import sys
import json
import os
from dynaconf import settings

from .util import *

def UserToStart(db, url_host, id_course, id_user):
    
    network = db.run( f"MATCH (network:Network{{url:'{url_host}'}})-[r2]-(c:Course{{id:{id_course}}}) return network").data()[0]['network']
    all_data = json.loads( network['all_data'])

    for item in all_data:
        if( 'id' in item and item['type'].lower() == "custom:start"):
            
            target_transictions,target_activitys = getNextActivity(db, url_host, id_course, item['id'])

            target_item = getNetworkByID(db, url_host, id_course, target_activitys[0])
            
            if not('suggestion_uuid' in target_item):
                abort(400, {'message': 'A rede possuí erros estruturais.'})

            
            target_uuid = target_item['suggestion_uuid']
            
            target_activity = db.run(f"MATCH (network:Network{{url:'{url_host}'}})-[:HAS_QUESTIONS]->(target{{uuid:'{target_uuid}'}}) return target").data()[0]['target']
            id_group = getInstanceOfActivityUUID(db, url_host, id_course, target_uuid, target_activity['label'])[0]["instance"]["id_group"]
             
            addUserToGroup(url_host, network['token'], str(id_user), str(id_group))

            return



    