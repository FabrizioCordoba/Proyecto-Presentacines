from werkzeug.security import generate_password_hash
from extensions import db
from models import Usuario
from app import app

# Configurar el entorno Flask
with app.app_context():
    # Verificar si ya existe un administrador
    if not Usuario.query.filter_by(role="administrador").first():
        nuevo_admin = Usuario(
            username="admin@example.com",
            password=generate_password_hash("admin123"),  # ✅ Cambia la contraseña si lo deseas
            role="administrador",
            apellidos="Admin",
            nombres="Administrador",
            dni="00000000"
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print("✅ Administrador creado exitosamente.")
    else:
        print("⚠️ Ya existe un administrador en el sistema.")
