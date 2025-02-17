from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import Usuario

auth_bp = Blueprint("auth", __name__)

# ----------------- LOGIN UNIFICADO -----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form.get("role")

        usuario = Usuario.query.filter_by(username=username, role=role).first()

        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            flash(f"Inicio de sesión exitoso como {role.capitalize()}.", "success")
            return redirect(url_for(f"{role}.panel_{role}"))
        else:
            flash("Credenciales incorrectas o rol no válido.", "danger")

    return render_template("login_unificado.html")  # ✅ Nuevo template con selección de rol

# ----------------- CIERRE DE SESIÓN -----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("auth.login"))
