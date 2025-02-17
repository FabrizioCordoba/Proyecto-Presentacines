from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash
from app import app

with app.app_context():
    username = "admin@cic.gob.ar"
    password = "admin123"
    apellidos = "Admin"
    nombres = "Principal"
    dni = "00000000"

    # Verificar si ya existe un administrador
    if not Usuario.query.filter_by(username=username).first():
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
        nuevo_admin = Usuario(
            username=username, 
            password=hashed_password, 
            role="administrador",
            apellidos=apellidos,
            nombres=nombres,
            dni=dni
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print("Administrador creado con éxito.")
    else:
        print("El usuario administrador ya existe.")
