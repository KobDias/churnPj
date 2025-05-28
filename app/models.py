from sqlalchemy import DateTime, Integer, String, Column
from flask_login import UserMixin
from db import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    nome = Column(String(80), unique=True, nullable=False)
    senha = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    docs = db.relationship('Documentos', backref='user')

class Documentos(db.Model):
    __tablename__ = 'documentos'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    caminho_origem = Column(String(120), nullable=False)
    caminho_pred = Column(String(120), nullable=True)
    caminho_grupos = Column(String(120), nullable=True)
    nome_documento = Column(String(120), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    graph = db.relationship('Graficos', backref='documentos')

class Graficos(db.Model):
    __tablename__ = 'graficos'
    id = Column(Integer, primary_key=True)
    documentos_id = Column(Integer, db.ForeignKey('documentos.id'), nullable=False)
    caminho_graph_importance = Column(String(120), nullable=False)
    caminho_graph_risco = Column(String(120), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())