import sys
from sqlalchemy import Column, Float, ForeignKey, Boolean, DateTime, String, Integer, Text, Numeric, Date, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from models.base import Model

#usado para serializar datatime
def dump_datetime(value):
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Usuario(Model):
    __tablename__ = "usuario"

    id = Column(Integer,primary_key=True,autoincrement=True)
    token = Column(String(500))
    tipo = Column(Integer)
    nome = Column(String(500))
    email = Column(String(500))
    genero = Column(Integer)
    foto_url = Column(String(500))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<Usuario %r>' % (self.apelido)