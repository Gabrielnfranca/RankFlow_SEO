from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    clientes = db.relationship('Cliente', backref='usuario', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    website = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    tarefas = db.relationship('Tarefa', backref='cliente', lazy=True)

    def __init__(self, nome, website=None, descricao=None, usuario_id=None):
        self.nome = nome
        self.website = website
        self.descricao = descricao
        self.usuario_id = usuario_id

class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')
    prioridade = db.Column(db.String(20), default='medium')
    checklist = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    etapa_seo_id = db.Column(db.Integer, db.ForeignKey('etapa_seo.id'), nullable=True)

class EtapaSEO(db.Model):
    __tablename__ = 'etapa_seo'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer)
    tarefas = db.relationship('Tarefa', backref='etapa_seo', lazy=True)
    progressos = db.relationship('ProgressoSEO', backref='etapa_seo', lazy=True)

class ProgressoSEO(db.Model):
    __tablename__ = 'progresso_seo'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    etapa_id = db.Column(db.Integer, db.ForeignKey('etapa_seo.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')
    data_conclusao = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
