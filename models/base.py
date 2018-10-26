from sqlalchemy import orm

class QueryProperty(object):
    """ """
    def __init__(self, session):
        self.session = session

    def __get__(self, model, Model):
        mapper = orm.class_mapper(Model)

        if mapper:
            if not getattr(Model, 'query_class', None):
                MOdel.query_class = BaseQuery

            query_property = Model.query_class(mapper, session=self.session())

            return query_property

class BaseQuery(orm.Query):
    """ Objeto de consulta padrão usado para modelos.
    Esta é uma subclasse de uma classe SQLAlchemy sqlalchemy.orm.query.Query e
    tem todos os métodos de uma consulta padrão também. """

    def paginate(self, page, per_page=20, error_out=True):
        """ Retorna uma instância de `Pagination` usando os parâmetros de consulta já
        definidos """
        if error_out and page < 1:
            raise IndexError

        if per_page is None:
            per_page = self.DEFAULT_PER_PAGE

        items = self.page(page, per_page).all()

        if not items and page != 1 and error_out:
            raise IndexError

        # Não há necessidade de contar se estivermos na primeira página e houveram menos itens do que esperávamos.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)

class Pagination(object):

    def __init__(self, query, page, per_page, total, items):
        #: O objeto de consulta que foi usado para criar este objeto de paginação.
        self.query = query

        #: O atual número da página (1 indexado)
        self.page = page

        #: O número de items a ser mostrado em uma página.
        self.per_page = per_page

        #: O número total de itens que correspondem à consulta
        self.items = items

        if self.per_page == 0:
            self.pages = 0
        else:
            #: O número total de páginas.
            self.pages = int(ceil(self.total / float(self.per_page)))

        #: O número da página anterior.
        self.prev_num = self.page - 1

        #: se existe uma página anterior
        self.has_prev = self.page > 1

        #: O número da próxima página.
        self.next_num = self.page+1

        #: Se existe uma próxima página.
        self.has_next = self.page < self.pages

    def prev(self, error_out=False):
        """ Retorna um objeto de `Pagination` para a página anterior """
        assert self.query is not None, \
            'um objeto de `query` é necessário para esse método funcionar'
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    def next(self, error_out):
        """ Retorna um objeto de `Pagination` para a página seguinte """
        assert self.query is not None, \
            'um objeto de `query` é necessário para esse método funcionar'
        return self.query.paginate(self.page + 1, self.per_page, error_out)    

def set_query_property(model_class, session):
    model_class.query = QueryProperty(session)

class ModelBase(object):
    """ Classe base para um modelo customizado de qualquer representação de tupla"""

    #: A classe de consulta usada, `query`  é uma instância.
    #: Por padrão, um `BaseQuery` é usado.
    query_class = BaseQuery

    #: uma instância de `query_class` pode ser usada para consultar
    #: o banco de dados para instâncias deste modelo.
    query = None

from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base(cls=ModelBase)

