from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Concurso, FormularioBase, CampoFormulario

formulario_bp = Blueprint("formulario", __name__)

# ----------------- SELECCIONAR CONCURSO PARA GESTIONAR FORMULARIO -----------------
@formulario_bp.route("/seleccionar_concurso", methods=["GET", "POST"])
@login_required
def seleccionar_concurso():
    if current_user.role != "administrador":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_admin"))

    if request.method == "POST":
        concurso_id = request.form.get("concurso_id")
        return redirect(url_for("formulario.gestionar_formulario", concurso_id=concurso_id))

    concursos = Concurso.query.all()
    return render_template("seleccionar_concurso.html", concursos=concursos)

# ----------------- GESTIONAR FORMULARIO -----------------
@formulario_bp.route("/gestionar_formulario/<int:concurso_id>", methods=["GET", "POST"])
@login_required
def gestionar_formulario(concurso_id):
    if current_user.role != "administrador":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_admin"))

    concurso = Concurso.query.get_or_404(concurso_id)

    # Crear un formulario base si no existe
    formulario = FormularioBase.query.filter_by(concurso_id=concurso.id).first()
    if not formulario:
        formulario = FormularioBase(
            nombre=f"Formulario {concurso.tipo}",
            concurso_id=concurso.id,
            tipo_concurso=concurso.tipo,
            datos_fijos="{}",
            campos_dinamicos="[]"
        )
        db.session.add(formulario)
        db.session.commit()

    # Obtener campos dinámicos asociados al formulario
    campos = CampoFormulario.query.filter_by(formulario_id=formulario.id).all()

    return render_template("gestionar_formularios.html", concurso=concurso, formulario=formulario, campos=campos)

# ----------------- AGREGAR CAMPO A FORMULARIO -----------------
@formulario_bp.route("/agregar_campo/<int:formulario_id>", methods=["POST"])
@login_required
def agregar_campo(formulario_id):
    if current_user.role != "administrador":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_admin"))

    nombre_campo = request.form.get("nombre_campo")
    tipo_campo = request.form.get("tipo_campo")
    obligatorio = request.form.get("obligatorio") == "1"
    opciones = request.form.get("opciones", None) if tipo_campo == "select" else None

    if not nombre_campo or not tipo_campo:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("formulario.gestionar_formulario", formulario_id=formulario_id))

    nuevo_campo = CampoFormulario(
        formulario_id=formulario_id,
        nombre=nombre_campo,
        tipo=tipo_campo,
        obligatorio=obligatorio,
        opciones=opciones
    )
    db.session.add(nuevo_campo)
    db.session.commit()

    flash("Campo agregado correctamente.", "success")
    return redirect(url_for("formulario.gestionar_formulario", concurso_id=formulario_id))

# ----------------- ELIMINAR CAMPO DE FORMULARIO -----------------
@formulario_bp.route("/eliminar_campo/<int:campo_id>", methods=["GET"])
@login_required
def eliminar_campo(campo_id):
    if current_user.role != "administrador":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_admin"))

    campo = CampoFormulario.query.get_or_404(campo_id)
    formulario_id = campo.formulario_id

    db.session.delete(campo)
    db.session.commit()
    flash("Campo eliminado correctamente.", "success")
    
    return redirect(url_for("formulario.gestionar_formulario", concurso_id=formulario_id))
