from sqlalchemy import Numeric,PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Boolean, Text
from app.base.CustomBase import CustomBase

from app.database import sqlite_db

class NetworkUserLog(sqlite_db.Model):
    __tablename__ = 'user_log'

    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(sqlite_db.Integer)
    network_id = Column(sqlite_db.Text)
    description = Column(sqlite_db.Text)
    created_on = Column(sqlite_db.DateTime)
    updated_on = Column(sqlite_db.DateTime)

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id'         : self.id,
           'user_id': self.user_id,
           'network_id': self.network_id,
           'description'  : self.description,
       }
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]