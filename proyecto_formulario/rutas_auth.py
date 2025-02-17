from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import Usuario
import time

auth_bp = Blueprint("auth", __name__)

# Diccionario para almacenar intentos fallidos por usuario
intentos_fallidos = {}

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form.get("role")

        # Control de intentos fallidos
        if username in intentos_fallidos and intentos_fallidos[username]['intentos'] >= 5:
            tiempo_bloqueo = intentos_fallidos[username]['tiempo']
            if time.time() - tiempo_bloqueo < 300:
                flash("Cuenta bloqueada temporalmente por intentos fallidos.", "danger")
                return redirect(url_for("auth.login"))
            else:
                intentos_fallidos[username]['intentos'] = 0

        usuario = Usuario.query.filter_by(username=username, role=role).first()

        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            session['role'] = role  # Guardar rol en sesión
            intentos_fallidos.pop(username, None)  # Reset intentos fallidos
            return redirect(url_for(f"{role}.panel_{role}"))

        else:
            flash("Credenciales incorrectas o rol no válido.", "danger")
            if username not in intentos_fallidos:
                intentos_fallidos[username] = {'intentos': 1, 'tiempo': time.time()}
            else:
                intentos_fallidos[username]['intentos'] += 1
                intentos_fallidos[username]['tiempo'] = time.time()

    return render_template("login_unificado.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('role', None)
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("auth.login"))
