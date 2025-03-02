from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from extensions import db
from models import CampoFormulario
import json
from decoradores import rol_requerido


formulario_bp = Blueprint("formulario", __name__)

# ----------------- GESTIONAR FORMULARIOS -----------------
@formulario_bp.route("/gestionar_formularios/<int:concurso_id>", methods=["GET"])
@login_required
@rol_requerido("administrador")
def gestionar_formularios(concurso_id):
    concurso = Concurso.query.get_or_404(concurso_id)
    campos = CampoFormulario.query.filter_by(concurso_id=concurso_id).all()
    return render_template("gestionar_formularios.html", concurso=concurso, campos=campos)

# ----------------- AGREGAR CAMPOS AL FORMULARIO -----------------
@formulario_bp.route("/agregar_campo", methods=["POST"])
@login_required
def agregar_campo():
    nombre = request.form.get("nombre")
    tipo = request.form.get("tipo")
    obligatorio = request.form.get("obligatorio") == "true"
    opciones = request.form.get("opciones")
    
    if tipo == "select":
        opciones = json.dumps(opciones.split(","))  # Guardar como JSON

    nuevo_campo = CampoFormulario(
        nombre=nombre,
        tipo=tipo,
        obligatorio=obligatorio,
        opciones=opciones
    )

    db.session.add(nuevo_campo)
    db.session.commit()

    flash("Campo agregado correctamente.", "success")
    return redirect(url_for("formulario.agregar_campo"))


# ----------------- EDITAR CAMPOS DEL FORMULARIO -----------------
@formulario_bp.route("/editar_campo/<int:campo_id>", methods=["POST"])
@login_required
@rol_requerido("administrador")
def editar_campo(campo_id):
    campo = CampoFormulario.query.get_or_404(campo_id)
    
    campo.nombre = request.form.get("nombre_campo")
    campo.tipo = request.form.get("tipo_campo")
    campo.obligatorio = request.form.get("obligatorio") == "1"
    campo.opciones = request.form.get("opciones", None) if campo.tipo == "select" else None

    db.session.commit()
    flash("Campo actualizado correctamente.", "success")
    return redirect(url_for("formulario.gestionar_formularios", concurso_id=campo.concurso_id))

# ----------------- ELIMINAR CAMPOS DEL FORMULARIO -----------------
@formulario_bp.route("/eliminar_campo/<int:campo_id>", methods=["POST"])
@login_required
@rol_requerido("administrador")
def eliminar_campo(campo_id):
    campo = CampoFormulario.query.get_or_404(campo_id)
    concurso_id = campo.concurso_id

    db.session.delete(campo)
    db.session.commit()

    flash("Campo eliminado correctamente.", "success")
    return redirect(url_for("formulario.gestionar_formularios", concurso_id=concurso_id))

# ----------------- OBTENER CAMPOS DINÁMICAMENTE (AJAX) -----------------
@formulario_bp.route("/obtener_campos/<int:concurso_id>", methods=["GET"])
@login_required
def obtener_campos(concurso_id):
    campos = CampoFormulario.query.filter_by(concurso_id=concurso_id).all()
    campos_json = [{"id": c.id, "nombre": c.nombre, "tipo": c.tipo, "obligatorio": c.obligatorio, "opciones": c.opciones} for c in campos]
    return jsonify(campos_json)
