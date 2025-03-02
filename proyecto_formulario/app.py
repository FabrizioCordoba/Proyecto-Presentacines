import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user
from extensions import db
from models import Usuario
from rutas_admin import admin_bp
from rutas_auth import auth_bp
from rutas_postulante import postulante_bp
from rutas_formularios import formulario_bp
from decoradores import rol_requerido


app = Flask(__name__)

# Configuración segura con variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///your_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')

# Inicialización de extensiones
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "administrador":
            return redirect(url_for("admin.panel_admin"))
        return redirect(url_for("postulante.panel_postulante"))
    return redirect(url_for("auth.login"))

# Registrar los Blueprints
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(postulante_bp, url_prefix="/postulante")
app.register_blueprint(formulario_bp, url_prefix="/formulario")

if __name__ == "__main__":
    app.run(debug=True)
