from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from extensions import db
from config import Config  # ✅ Importamos configuración centralizada

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Configurar LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Manejo de errores global
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

# Importar y registrar Blueprints
from rutas_auth import auth_bp
from rutas_postulante import postulante_bp
from rutas_admin import admin_bp
from rutas_formularios import formulario_bp

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(postulante_bp, url_prefix="/postulante")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(formulario_bp, url_prefix="/formulario")

# Redirección global
@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "administrador":
            return redirect(url_for("admin.panel_admin"))
        elif current_user.role == "postulante":
            return redirect(url_for("postulante.panel_postulante"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)
