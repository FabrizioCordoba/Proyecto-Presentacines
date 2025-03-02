from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from extensions import db
from models import Concurso, FormularioBase, RespuestaCampoDinamico, CampoFormulario
from decoradores import rol_requerido
import json
import csv
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

# ----------------- PANEL DE ADMINISTRACIÓN -----------------
@admin_bp.route("/panel_admin")
@login_required
@rol_requerido("administrador")
def panel_admin():
    concursos = Concurso.query.all()
    formularios = FormularioBase.query.all()

    # Verificar si hay concursos para evitar errores en tojson
    concursos_labels = [concurso.nombre for concurso in concursos] if concursos else ["Sin datos"]
    postulaciones_finalizadas = [FormularioBase.query.filter_by(concurso_id=concurso.id, estado="finalizado").count() for concurso in concursos] if concursos else [0]
    postulaciones_borrador = [FormularioBase.query.filter_by(concurso_id=concurso.id, estado="borrador").count() for concurso in concursos] if concursos else [0]

    return render_template("panel_admin.html",
                           concursos=concursos,
                           formularios=formularios,
                           concursos_labels=concursos_labels,
                           postulaciones_finalizadas=postulaciones_finalizadas,
                           postulaciones_borrador=postulaciones_borrador)

# ----------------- CARGAR CONCURSO -----------------
@admin_bp.route("/cargar_concurso", methods=["GET", "POST"])
@login_required
@rol_requerido("administrador")
def cargar_concurso():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        tipo = request.form.get("tipo")
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")

        if not nombre or not tipo or not fecha_inicio or not fecha_fin:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("admin.cargar_concurso"))

        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        if fecha_fin < fecha_inicio:
            flash("La fecha de finalización no puede ser anterior a la fecha de inicio.", "danger")
            return redirect(url_for("admin.cargar_concurso"))

        nuevo_concurso = Concurso(
            nombre=nombre,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado="abierto"
        )
        db.session.add(nuevo_concurso)
        db.session.commit()

        flash("Concurso creado correctamente.", "success")
        return redirect(url_for("admin.cargar_concurso"))

    concursos = Concurso.query.all()
    return render_template("cargar_concurso.html", concursos=concursos)
# ----------------- VINCULAR FORMULARIO A CONCURSO -----------------
@admin_bp.route("/vincular_formulario", methods=["POST"])
@login_required
@rol_requerido("administrador")
def vincular_formulario():
    concurso_id = request.form.get("concurso_id")
    formulario_id = request.form.get("formulario_id")

    if not concurso_id or not formulario_id:
        flash("Debe seleccionar un concurso y un formulario.", "danger")
        return redirect(url_for("admin.panel_admin"))

    concurso = Concurso.query.get(concurso_id)
    formulario = FormularioBase.query.get(formulario_id)

    if not concurso or not formulario:
        flash("El concurso o el formulario seleccionado no existen.", "danger")
        return redirect(url_for("admin.panel_admin"))

    concurso.formulario_id = formulario.id
    db.session.commit()

    flash("Formulario vinculado correctamente al concurso.", "success")
    return redirect(url_for("admin.panel_admin"))

#--------------------------VER POSTULACIONES------------------------------------
@admin_bp.route("/ver_postulaciones", methods=["GET"])
@login_required
@rol_requerido("administrador")
def ver_postulaciones():
    concursos = Concurso.query.all()
    concurso_id = request.args.get("concurso_id")

    postulaciones = FormularioBase.query.filter_by(concurso_id=concurso_id, estado="finalizado").all() if concurso_id else []

    return render_template("ver_postulaciones.html", concursos=concursos, postulaciones=postulaciones)

#------------------------------------DESCARGAR EXCEL--------------------------------------
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from extensions import db
from models import Concurso, FormularioBase, RespuestaCampoDinamico, CampoFormulario
from decoradores import rol_requerido
import json
import csv
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

# ----------------- PANEL DE ADMINISTRACIÓN -----------------
@admin_bp.route("/panel_admin")
@login_required
@rol_requerido("administrador")
def panel_admin():
    concursos = Concurso.query.all()
    return render_template("panel_admin.html", concursos=concursos)

# ----------------- CARGAR CONCURSO -----------------
@admin_bp.route("/cargar_concurso", methods=["GET", "POST"])
@login_required
@rol_requerido("administrador")
def cargar_concurso():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        tipo = request.form.get("tipo")
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")

        if not nombre or not tipo or not fecha_inicio or not fecha_fin:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("admin.cargar_concurso"))

        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        if fecha_fin < fecha_inicio:
            flash("La fecha de finalización no puede ser anterior a la fecha de inicio.", "danger")
            return redirect(url_for("admin.cargar_concurso"))

        nuevo_concurso = Concurso(
            nombre=nombre,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado="abierto"
        )
        db.session.add(nuevo_concurso)
        db.session.commit()

        flash("Concurso creado correctamente.", "success")
        return redirect(url_for("admin.cargar_concurso"))

    concursos = Concurso.query.all()
    return render_template("cargar_concurso.html", concursos=concursos)

# ----------------- DESCARGAR POSTULACIONES -----------------
@admin_bp.route("/descargar_postulaciones/<int:concurso_id>")
@login_required
@rol_requerido("administrador")
def descargar_postulaciones(concurso_id):
    concurso = Concurso.query.get_or_404(concurso_id)
    postulaciones = FormularioBase.query.filter_by(concurso_id=concurso_id, estado="finalizado").all()

    if not postulaciones:
        flash("No hay postulaciones finalizadas para este concurso.", "warning")
        return redirect(url_for("admin.panel_admin"))

    csv_filename = f"postulaciones_{concurso.nombre}.csv"
    csv_data = []

    for postulacion in postulaciones:
        respuestas = RespuestaCampoDinamico.query.filter_by(formulario_id=postulacion.id).all()
        datos = {respuesta.campo_id: respuesta.valor for respuesta in respuestas}
        csv_data.append(datos)

    def generate():
        if csv_data:
            header = csv_data[0].keys()
            yield ",".join(map(str, header)) + "\n"
            for row in csv_data:
                yield ",".join(str(row.get(col, "")) for col in header) + "\n"
        else:
            yield "No hay datos disponibles.\n"

    response = Response(generate(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={csv_filename}"
    return response
