from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistroForm

auth_bp = Blueprint("auth", __name__)

# ----------------- LOGIN -----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and check_password_hash(usuario.password, form.password.data):
            login_user(usuario)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("admin.panel_admin") if usuario.role == "administrador" else url_for("postulante.panel_postulante"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html", form=form)

# ----------------- REGISTRO DE POSTULANTE -----------------
@auth_bp.route("/register_postulante", methods=["GET", "POST"])
def register_postulante():
    form = RegistroForm()
    if form.validate_on_submit():
        existing_user = Usuario.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("El correo ya está registrado.", "warning")
            return redirect(url_for("auth.register_postulante"))

        nuevo_postulante = Usuario(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role="postulante",
            nombres=form.nombres.data,
            apellidos=form.apellidos.data,
            dni=form.dni.data
        )

        db.session.add(nuevo_postulante)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_postulante.html", form=form)


# ----------------- REGISTRO DE ADMINISTRADOR (Solo accesible para administradores) -----------------
@auth_bp.route("/register_admin", methods=["GET", "POST"])
@login_required
def register_admin():
    if not hasattr(request, "current_user") or request.current_user.role != "administrador":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        nombres = request.form.get("nombres")
        apellidos = request.form.get("apellidos")
        dni = request.form.get("dni")

        if not email or not password or not nombres or not apellidos or not dni:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("auth.register_admin"))

        existing_user = Usuario.query.filter_by(username=email).first()
        if existing_user:
            flash("El correo ya está registrado.", "warning")
            return redirect(url_for("auth.register_admin"))

        nuevo_admin = Usuario(
            username=email,
            password=generate_password_hash(password),
            role="administrador",
            nombres=nombres,
            apellidos=apellidos,
            dni=dni
        )

        db.session.add(nuevo_admin)
        db.session.commit()

        flash("Administrador creado con éxito.", "success")
        return redirect(url_for("admin.panel_admin"))

    return render_template("register_admin.html")
