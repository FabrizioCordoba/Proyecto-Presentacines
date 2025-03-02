from extensions import db
from flask_login import UserMixin
import json

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)  # Cambio de username a email
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)

    formularios = db.relationship('FormularioBase', backref='postulante', lazy=True)

class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="cerrado")
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)

    formularios = db.relationship('FormularioBase', backref='concurso', lazy=True)

class CampoFormulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    obligatorio = db.Column(db.Boolean, nullable=False, default=True)
    opciones = db.Column(db.Text, nullable=True)  # Se almacenará como JSON
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'), nullable=False)

class FormularioBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postulante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default="borrador")

    respuestas = db.relationship('RespuestaCampoDinamico', backref='formulario', lazy=True)

    def validar_completitud(self):
        return all(respuesta.valor for respuesta in self.respuestas)

class RespuestaCampoDinamico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    formulario_id = db.Column(db.Integer, db.ForeignKey("formulario_base.id"), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey("campo_formulario.id"), nullable=False)
    valor = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<RespuestaCampoDinamico {self.id} - Formulario {self.formulario_id}>"
