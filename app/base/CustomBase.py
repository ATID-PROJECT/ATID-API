from app.database import sqlite_db
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

def obterDataComHora():
    try:
        now_utc = datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('America/Recife'))
        return now_pacific.strftime('%Y-%m-%d %H:%M:%S')

    except Exception as e:
        return ""

class CustomBase(sqlite_db.Model):
    __abstract__ = True

    __table_args__ = {'mysql_engine': 'InnoDB'}

    created_on = sqlite_db.Column(sqlite_db.DateTime, default=datetime.utcnow)
    updated_on = sqlite_db.Column(sqlite_db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
