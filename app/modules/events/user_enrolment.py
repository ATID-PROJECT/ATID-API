from flask import abort
import requests
import sys
import json
import os
from dynaconf import settings

from .util import *

def UserToStart(db, url_host, id_course, id_user):
    
    try:

        network = db.run( f"MATCH (network:Network{{url:'{url_host}'}})-[r2]-(c:Course{{id:{id_course}}}) return network").data()[0]['network']
        all_data = json.loads( network['all_data'])

        for item in all_data:
            
            if( 'id' in item and item['type'].lower() == "custom:start"):
                
                target_transictions,target_modules = getNextActivity(db, url_host, id_course, item['id'])

                for tmodule in target_modules:
                    target_item = getNetworkByID(db, url_host, id_course, tmodule)
                    
                    if not('suggestion_uuid' in target_item):
                        continue
                    
                    target_uuid = target_item['suggestion_uuid']

                    target_activity = db.run(f"MATCH (network:Network{{url:'{url_host}'}})-[:HAS_QUESTIONS]->(target{{uuid:'{target_uuid}'}}) return target").data()[0]['target']
                    id_group = getInstanceOfActivityUUID(db, url_host, id_course, target_uuid, target_activity['label'])[0]["instance"]["id_group"]
                    
                    addUserToGroup(url_host, network['token'], str(id_user), str(id_group))

        return "ok"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
        return 400


    