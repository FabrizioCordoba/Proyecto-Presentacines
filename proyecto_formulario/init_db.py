import logging

try:
    from app import app
    from extensions import db
    from models import db, Usuario, Concurso, FormularioBase  


    with app.app_context():
        db.create_all()
        logging.info("Base de datos y tablas creadas correctamente.")

except Exception as e:
    logging.error(f"Error: {e}")
finally:
    # Cerrar la conexión a la base de datos si es necesario
    pass