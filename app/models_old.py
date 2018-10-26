import sys
from sqlalchemy import Column, Float, ForeignKey, Boolean, DateTime, String, Integer, Text, Numeric, Date, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from models.base import Model

#usado para serializar datatime
def dump_datetime(value):
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Visita(Model):
    __tablename__ = "visita"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    horario = Column(DateTime)
    nome_cliente = Column(String(200))
    nome_responsavel = Column(String(200))
    cpf_cliente = Column(String(11))
    valor_proposto = Column(Numeric(12,0))
    comentario =  Column(Text)
    criado_em = Column(DateTime)
    ativo = Column(Boolean)

    def __init__(self, horario,nome_cliente,nome_responsavel,cpf_cliente,valor_proposto,comentario,criado_em,ativo):
        self.horario = horario
        self.nome_cliente =nome_cliente
        self.nome_responsavel = nome_responsavel
        self.cpf_cliente =cpf_cliente
        self.valor_proposto = valor_proposto
        self.comentario = comentario
        self.criado_em =criado_em
        self.ativo = ativo

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'horario': dump_datetime(self.horario),
           # This is an example how to deal with Many2Many relations
           'nome_cliente': self.nome_cliente,
           'nome_responsavel': self.nome_responsavel,
           'cpf_cliente': self.cpf_cliente,
           'valor_proposto': str(self.valor_proposto),
           'comentario': self.comentario,
           'criado_em': dump_datetime(self.criado_em),
           'ativo': self.ativo,
       }

    def __repr__(self):
        return '<visita %r>' % (self.id)

class VisitaSugestaoCarteira(Model):
    __tablename__ = "visita_sugestao_carteira"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_visita =  Column(Integer,ForeignKey('visita.id'),primary_key=True)
    id_pim =  Column(Integer,ForeignKey('pim.id'),primary_key=True)
    id_carteira = Column(Integer,ForeignKey('carteira.id'),primary_key=True)

    def __repr__(self):
        return '<visita_sugestao_carteira %r>' % (self.id_visita)

class VisitaSugestaoImovel(Model):
    __tablename__ = "visita_sugestao_imovel"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_visita =  Column(Integer,ForeignKey('visita.id'),primary_key=True)
    id_pim =  Column(Integer,ForeignKey('pim.id'),primary_key=True)
    id_imovel = Column(Integer,ForeignKey('imovel.id'),primary_key=True)

    def __repr__(self):
        return '<visita_sugestao_imovel %r>' % (self.id_visita)

class Endereco_Imovel(Model):
    __tablename__ = "endereco_imovel"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_imovel = Column(Integer,ForeignKey('imovel.id'),primary_key=True)
    id_endereco = Column(Integer,ForeignKey('endereco.id'),primary_key=True)

    def __init__(self, id_imovel,id_endereco):
        self.id_imovel = id_imovel
        self.id_endereco = id_endereco

    def save(self, db):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Endereco_Imovel.query.all()

    def delete(self, db):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Endereco_Imovel {}>'.format(self.id_imovel)

class EnderecoPIM(Model):
    __tablename__ = "endereco_pim"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_pim = Column(Integer,ForeignKey('pim.id'),primary_key=True)
    id_endereco = Column(Integer,ForeignKey('endereco.id'),primary_key=True)

    def __repr__(self):
        return '<endereco_pim %r>' % (self.id_pim)

class EnderecoClientePIM(Model):
    __tablename__ = "endereco_cliente_pim"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_cliente = Column(Integer,ForeignKey('cliente_pim.id'),primary_key=True)
    id_endereco = Column(Integer,ForeignKey('endereco.id'),primary_key=True)

    def __repr__(self):
        return '<endereco_pim %r>' % (self.id_pim)

class Endereco_Proprietario(Model):
    __tablename__ = "endereco_proprietario"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_proprietario = Column(Integer,ForeignKey('proprietario.id'),primary_key=True)
    id_endereco = Column(Integer,ForeignKey('endereco.id'),primary_key=True)

    def __repr__(self):
        return '<endereco_proprietario %r>' % (self.id_proprietario)

class PIM(Model):
    __tablename__= "pim"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    finalidade = Column(Integer)
    tipo_imovel = Column(Integer)
    area_total = Column(Numeric(9,3))
    area_util = Column(Numeric(9,3))
    quartos = Column(Integer)
    suites = Column(Integer)
    banheiros = Column(Integer)
    vagas = Column(Integer)
    valor_venda = Column(Numeric(12,0))
    valor_locacao = Column(Numeric(12,0))
    comentarios = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    id_anunciante = Column(Integer,ForeignKey('anunciante.id'),primary_key=True)
    id_corretor = Column(Integer,ForeignKey('corretor.id'),primary_key=True) 
    id_cliente = Column(Integer,ForeignKey('cliente_pim.id'),primary_key=True)

    def setIdAnunciante(self,anunciante_id):
        id_anunciante=anunciante_id

    def setIdCorretor(self,corretor_id):
        id_corretor=corretor_id

    def __repr__(self):
        return '<pim %r>' % (self.id)

class ClientePIM(Model):
    __tablename__= "cliente_pim"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    nome = Column(String(200))
    cpf = Column(String(50))
    cnpj = Column(String(50))
    profissao = Column(String(80))
    data_nascimento = Column(DateTime)
    estado_civil = Column(String(80))
    email = Column(String(120))
    comentarios = Column(Text)

    def __repr__(self):
        return '<cliente_pim %r>' % (self.id)

class SugestaoCarteira(Model):
    __tablename__ = "sugestao_carteira"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_pim = Column(Integer,ForeignKey('pim.id'),primary_key=True)
    id_carteira = Column(Integer,ForeignKey('carteira.id'),primary_key=True)
    ativo = Column(Boolean)
    data = Column(Date,primary_key=True)

class SugestaoImovel(Model):
    __tablename__ = "sugestao_imovel"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_pim = Column(Integer,ForeignKey('pim.id'),primary_key=True)
    id_imovel = Column(Integer,ForeignKey('imovel.id'),primary_key=True)
    ativo = Column(Boolean)
    data = Column(Date,primary_key=True)

class Endereco(Model):
    __tablename__ = "endereco"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    cep = Column(String(500),nullable=False)
    logradouro = Column(String(500))
    numero = Column(Integer)
    complemento = Column(String(500))
    bairro = Column(String(500))
    uf = Column(String(500))
    nome_condominio = Column(String(500))
    numero_apto = Column(Integer)
    municipio = Column(String(500))
    latitude = Column(Float(Precision=64))
    longitude = Column(Float(Precision=64))
    visivel = Column(Integer)
    
    def __repr__(self):
        return '<endereco>'
        
class Anunciante(Model):
    __tablename__ = "anunciante"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    token = Column(String(500))
    tipo = Column(Integer)
    nome = Column(String(500))
    cpf= Column(String(500))
    cnpj = Column(String(500))
    apelido = Column(String(500))
    email = Column(String(500))
    cidade = Column(String(500))
    genero = Column(Integer)
    identidade = Column(String(500))
    uf_emissao = Column(String(500))
    orgao_emissor = Column(String(500))
    data_expedicao = Column(Date)
    data_nascimento = Column(Date)
    nome_mae = Column(String(500))
    naturalidade = Column(String(500))
    nacionalidade = Column(String(500))
    senha = Column(String(500))
    id_endereco = Column(Integer,ForeignKey('endereco.id'))
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
        return '<Anunciante %r>' % (self.apelido)

class FimCarteira(Model):
    __tablename__ = "fim_carteira"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_carteira = Column(Integer,primary_key=True)
    id_anunciante = Column(Integer)
    id_mantenedor = Column(Integer)
    motivo = Column(Integer)
    data = Column(Date)
    valor = Column(Numeric(12,0))
    observacao = Column(String(500))

    def __repr__(self):
        return '<fim_carteira>'

class Proprietario(Model):
    __tablename__ = 'proprietario'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    cpf= Column(String(500))
    cnpj = Column(String(500))
    nome = Column(String(500),nullable=False)
    apelido = Column(String(500))
    genero = Column(Integer)
    data_nascimento = Column(Date)
    profissao = Column(String(500))
    identidade = Column(Integer)
    uf_emissao = Column(String(500))
    orgao_emissor = Column(String(500))
    naturalidade = Column(String(500))
    nacionalidade = Column(String(500))
    email = Column(String(500))
    estado_civil = Column(Integer)
    passaporte = Column(String(500))
    contato = Column(String(500))
    observacao = Column(String(500))
    data_expedicao = Column(Date)
    nome_mae = Column(String(500),nullable=False)
    ativo = Column(Boolean)
    id_dados = Column(Integer,ForeignKey('dados_bancarios.id'))
    id_anunciante = Column(Integer,ForeignKey(Anunciante.id))
    foto_url = Column(String(500))

    def __repr__(self):
        return '<proprietario>'

class Corretor(Model):
    __tablename__ = "corretor"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    token = Column(String(500))
    sigla = Column(String(500))
    data_inicio = Column(Date)
    data_fim = Column(Date)
    observacao = Column(String(500))
    senha = Column(String(500))
    ativo = Column(Boolean)
    id_proprietario = Column(Integer,ForeignKey(Proprietario.id),nullable=False)

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
        return '<Corretor>'

class PermissoesCorretor(Model):
    __tablename__ = "permissoes_corretor"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id_corretor = Column(Integer,ForeignKey('corretor.id'),primary_key=True)
    cadastro_carteira = Column(Integer)
    cadastro_imovel = Column(Integer)
    cadastro_pim = Column(Integer)

    def __repr__(self):
        return '<permissoes_corretor %r>' % (self.id_corretor)

class Observacao(Model):
    __tablename__ = "observacao"
    __table_args__ = (
        PrimaryKeyConstraint("id", "id_anuncio","data"),
    )
    id = Column(Integer,autoincrement=True)
    id_anuncio = Column(Integer)
    data = Column(DateTime)
    observacao = Column(String(500))

    def __repr__(self):
        return '<observacao>'

class AnuncianteObservacao(Model):
    __tablename__ = "anuncianteobservacao"
    __table_args__ = (
        PrimaryKeyConstraint("id_anunciante", "id_observacao"),
    )
    id_anunciante = Column(Integer,ForeignKey('anunciante.id'))
    id_observacao = Column(Integer,ForeignKey('observacao.id'))

    def __repr__(self):
        return '<anuncianteobservacao>'

class CorretorObservacao(Model):
    __tablename__ = "corretor_observacao"

    id_corretor = Column(Integer,ForeignKey('corretor.id'),primary_key=True)
    id_observacao = Column(Integer,ForeignKey('observacao.id'),primary_key=True)
    
    def __repr__(self):
        return '<corretor_observacao>'

class HistoricoAnunciante(Model):
    __tablename__ = "historico_anunciante"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True)
    id_anunciante = Column(Integer)
    autor = Column(Integer)
    tipo = Column(Integer)
    observacao = Column(String(500))
    data = Column(Date)

class HistoricoImovel(Model):
    __tablename__ = "historico_edicao_imovel"

    id_anunciante = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint("id_anunciante", "data","id_imovel"),
    )
    id_imovel = Column(Integer)
    id_proprietario = Column(Integer)
    data = Column(Date)

    def __repr__(self):
        return '<historico_edicao_imovel %r>' % (self.id_anunciante)

class HistoricoCorretorImovel(Model):
    __tablename__ = "historico_edicao_corretor_imovel"

    id_corretor = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint("id_corretor", "data","id_imovel"),
    )
    id_imovel = Column(Integer)
    id_proprietario = Column(Integer)
    data = Column(Date)

    def __repr__(self):
        return '<historico_edicao_corretor_imovel %r>' % (self.id_corretor)

class HistoricoCorretorPIM(Model):
    __tablename__ = "historico_edicao_corretor_pim"

    id_corretor = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint("id_corretor", "data","id_pim"),
    )
    id_pim = Column(Integer)
    data = Column(Date)

    def __repr__(self):
        return '<historico_edicao_corretor_pim %r>' % (self.id_corretor)

class HistoricoPIM(Model):
    __tablename__ = "historico_edicao_pim"

    id_anunciante = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint("id_anunciante", "data","id_pim"),
    )
    id_pim = Column(Integer)
    data = Column(Date)

    def __repr__(self):
        return '<historico_edicao_pim %r>' % (self.id_anunciante)

class HistoricoCorretorCarteira(Model):
    __tablename__ = "historico_edicao_corretor_carteira"
    __table_args__ = (
        PrimaryKeyConstraint("id_corretor", "data","id_carteira"),
    )
    id_corretor = Column(Integer)
    id_carteira = Column(Integer)
    valor = Column(Numeric(12,0))
    data = Column(DateTime)
    negocio = Column(Integer)
    internet = Column(Integer)
    id_mantenedor = Column(Integer,nullable=True)
    tipo = Column(Integer)


    def __repr__(self):
        return '<historico_edicao_corretor_carteira %r>' % (self.id_anunciante)

class HistoricoCarteira(Model):
    __tablename__ = "historico_edicao_carteira"

    id_anunciante = Column(Integer)
    id_carteira = Column(Integer)
    valor = Column(Numeric(12,0))
    data = Column(DateTime)
    negocio = Column(Integer)
    internet = Column(Integer)
    id_mantenedor = Column(Integer,nullable=True)
    tipo = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint(id_anunciante,data,id_carteira),
    )
    def __repr__(self):
        return '<historico_edicao_carteira %r>' % (self.id_anunciante)

class HistoricoProprietario(Model):
    __tablename__ = "historico_edicao_proprietario"
    __table_args__ = (
        PrimaryKeyConstraint("id_anunciante", "id_proprietario"),
    )

    id_anunciante = Column(Integer)
    id_proprietario = Column(Integer)
    data = Column(Date,primary_key=True)

    def __repr__(self):
        return '<historico_edicao_proprietario %r>' % (self.id_anunciante)

class Imovel(Model):
    __tablename__ = "imovel"
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer,primary_key=True,autoincrement=True)
    tipo = Column(Integer)
    criado_em = Column(DateTime) #real date
    sub_tipo = Column(Integer)
    quartos = Column(Integer)
    salas = Column(Integer)
    suites = Column(Integer)
    banheiros = Column(Integer)
    vagas = Column(Integer)
    iptu = Column(Numeric(12,0))
    valor_condominio = Column(Numeric(12,0))
    id_proprietario = Column(Integer,ForeignKey(Proprietario.id),nullable=False)
    id_corretor = Column(Integer,ForeignKey(Corretor.id),nullable=False)
    arcondicionados = Column(Integer)
    pavimentos_predio = Column(Integer)
    pavimentos_apto = Column(Integer)
    distancia_mar = Column(Numeric(9,3))
    ano_construcao = Column(Integer)
    data_criacao = Column(Date)
    area_util = Column(Numeric(9,3))
    area_total = Column(Numeric(9,3))
    largura = Column(Numeric(9,3))
    comprimento = Column(Numeric(9,3))
    AC = Column(Numeric(9,3))
    codigo = Column(String(500),unique=True)
    ativo = Column(Boolean)
    observacao = Column(String(500))

    def __repr__(self):
        return '<imovel %r>' % (self.nome)

class Carteira(Model):
    __tablename__ = "carteira"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    valor_venda = Column(Numeric(12,0))
    valor_mensal = Column(Numeric(12,0))
    internet = Column(Boolean)
    data = Column(DateTime)
    chave = Column(String(500))
    placa = Column(String(500))
    codigo = Column(String(500),unique=True)
    tipo = Column(Integer)
    exclusividade = Column(Integer)
    observacao = Column(String(500))
    comissao = Column(Numeric(12))
    id_imovel = Column(Integer,ForeignKey(Imovel.id),nullable=False)
    ativo = Column(Boolean)
    IVI = Column(Numeric(12,0))
    id_mantenedor = Column(Integer,ForeignKey(Corretor.id),nullable=False)
    id_corretor = Column(Integer,ForeignKey(Corretor.id),nullable=False)
    titulo = Column(String(500))
    descricao = Column(String(500))
    destaque = Column(Boolean)
    iptu_incluso = Column(Boolean)
    tipo_imovel_adicional = Column(Integer)
    subtipo_imovel_adicional = Column(Integer)
    condominio_incluso = Column(Boolean)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'titulo'   : self.titulo,
       }

    def __repr__(self):
        return '<carteira %r>' % self.codigo

class Regras(Model):
    __tablename__ = "regras"

    id = Column(Integer,primary_key=True,autoincrement=True)
    color = Column(String(8))
    anunciante_id = Column(Integer,ForeignKey(Anunciante.id),nullable=False)

    def __repr__(self):
        return '< regras %r>' % self.codigo

class PeriodoTemporada(Model):
    __tablename__ = "periodo_temporada"
    __table_args__ = (
        PrimaryKeyConstraint("regras_id", "carteira_id"),
    )

    inicio = Column(DateTime)
    fim = Column(DateTime) 
    criado_em = Column(DateTime)
    valor = Column(Numeric(12,0))
    regras_id = Column(Integer,ForeignKey(Regras.id),nullable=False)
    carteira_id = Column(Integer,ForeignKey(Carteira.id),nullable=False)

    def __repr__(self):
        return '< PeriodoTemporada %r>' % self.criado_em

class Telefone(Model):
    __tablename__ = "telefone"
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    id_proprietario = Column(Integer,ForeignKey(Proprietario.id),nullable=False)
    id_anunciante = Column(Integer,ForeignKey(Anunciante.id),nullable=False)
    telefone = Column(String(500),nullable=False)
    tipo = Column(Integer,nullable=False)

    def __repr__(self):
        return '<telefone %r>' % (self.id)

class TelefoneCliente(Model):
    __tablename__ = "telefone_cliente"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    id_cliente = Column(Integer,ForeignKey(Proprietario.id),nullable=False)
    telefone = Column(String(500),nullable=False)
    tipo = Column(Integer,nullable=False)

    def __repr__(self):
        return '<TelefoneCliente %r>' % (self.id)

class Beneficio(Model):
    __tablename__ = "beneficio"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    nome = Column(String(500))
    id_imovel = Column(Integer,ForeignKey(Imovel.id))

    def __repr__(self):
        return '<Beneficio %r>' % (self.nome)

class Anuncio(Model):
    __tablename__ = "anuncio"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    video = Column(String(500))
    data = Column(Date)
    id_imovel = Column(Integer,ForeignKey(Imovel.id))
    id_anunciante = Column(Integer,ForeignKey('anunciante.id'))
    id_corretor = Column(Integer,ForeignKey('corretor.id'))
    foto_id = Column(Integer,ForeignKey('foto.id'))

    def setIdCorretor(self,corretor_id):
        self.id_corretor=corretor_id

    def setIdAnunciante(self,anunciante_id):
        self.id_anunciante=anunciante_id

    def __repr__(self):
        return '<Anuncio %r>' % (self.id)

class DadosBancarios(Model):
    __tablename__ = "dados_bancarios"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    banco = Column(String(500))
    agencia = Column(String(500))
    conta_corrente = Column(String(500))

    def __repr__(self):
        return '<DadosBancarios %r>' % (self.banco)

class Carteira_Historico(Model):
    __tablename__ = "carteira_historico"
    __table_args__ = (
        PrimaryKeyConstraint("id_carteira", "data_historico"),
    )

    data_historico = Column(DateTime)
    venda = Column(Integer)
    aluguel = Column(Integer)
    temporada = Column(Integer)
    id_mantenedor = Column(Integer,nullable=True)
    id_carteira = Column(Integer,autoincrement=False)
    tipo = Column(Integer)
    observacao=Column(Text)

    def __repr__(self):
        return '<carteira_historico>'

class Mobilia(Model):
    __tablename__ = "mobilia"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    nome =  Column(String(500))

class Mobilia_Imovel(Model):
    __tablename__ = "mobilia_imovel"
    __table_args__ = (
        PrimaryKeyConstraint("id_imovel", "id_mobilia"),
    )

    id_imovel = Column(Integer,primary_key=True)
    id_mobilia = Column(Integer,primary_key=True)

class Foto(Model):
    __tablename__ = "foto"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer,primary_key=True,autoincrement=True)
    #codigo = Column(BLOB)
    foto_url = Column(String(250))
    id_anuncio = Column(Integer,ForeignKey(Anuncio.id))

    def __repr__(self):
        return '<Foto %r>' % (self.id_anuncio)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'foto_url'   : self.foto_url,
       }

class Newsletter(Model):
    __tablename__ = "newsletter"
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    nome = Column(String(200))
    email = Column(String(200))
    numero = Column(String(12))
