from extensions import db

# Tabla para los usuarios
from flask_login import UserMixin
from extensions import db

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    formularios_datos_generales = db.relationship('FormularioDatosGenerales', backref='postulante', lazy=True)
    formularios_plan_trabajo = db.relationship('FormularioPlanTrabajo', backref='postulante', lazy=True)

    # Métodos requeridos por Flask-Login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True  # Esto indica que el usuario está activo

    def is_anonymous(self):
        return False  # No hay usuarios anónimos

    def get_id(self):
        return str(self.id)



# Tabla para los concursos
class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)#Ejemplo, BEDOC, BENTRE, ETC	
    estado = db.Column(db.String(20), nullable=False, default="cerrado")
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    formularios_datos_generales = db.relationship('FormularioDatosGenerales', backref='concurso', lazy=True)
    formularios_plan_trabajo = db.relationship('FormularioPlanTrabajo', backref='concurso', lazy=True)

# Tabla para los campos de los formularios
class CampoFormulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del campo (ej: "Apellidos")
    tipo = db.Column(db.String(50), nullable=False)  # Tipo de campo (ej: "text", "date", "select")
    obligatorio = db.Column(db.Boolean, nullable=False, default=True)
    opciones = db.Column(db.Text, nullable=True)  # Opciones para campos tipo "select"
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'), nullable=False)
    formulario_tipo = db.Column(db.String(50), nullable=False, default="Datos Generales")  # Evita valores NULL

# Tabla para los datos de los formularios completados
class FormularioDatosGenerales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postulante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'), nullable=False)
    datos = db.Column(db.Text, nullable=False)  # Almacena los datos en formato JSON
    estado = db.Column(db.String(20), nullable=False, default="borrador")  # Agregar este campo

class FormularioPlanTrabajo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postulante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'), nullable=False)
    datos = db.Column(db.Text, nullable=False)  # Almacena los datos en formato JSON


class FormularioBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postulante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'), nullable=False)
    datos_generales = db.Column(db.JSON, nullable=False)  # Almacena los datos comunes del formulario
    estado = db.Column(db.String(20), nullable=False, default="borrador")

    # Relación con el concurso
    concurso = db.relationship('Concurso', backref=db.backref('formularios', lazy=True))


class RespuestaCampoDinamico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    formulario_id = db.Column(db.Integer, db.ForeignKey('formulario_base.id'), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey('campo_formulario.id'), nullable=False)
    valor = db.Column(db.Text, nullable=False)  # Respuesta del postulante
