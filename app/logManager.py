
from app.database import sqlite_db
import os
import sys
from .modules import *

def createLog(current_user, network_id, description):

    try:
        log = NetworkUserLog(
            user_id=current_user,
            network_id=network_id,
            description=description)
        sqlite_db.session.add(log)
        sqlite_db.session.commit()
    except Exception as e:
        print('*************------------------++++++++++++', file=sys.stderr)
        print(str(e), file=sys.stderr)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)