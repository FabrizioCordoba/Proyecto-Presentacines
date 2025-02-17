# rutas_postulante.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Concurso, FormularioBase, CampoFormulario, RespuestaCampoDinamico
import json
import pdfkit
import os

postulante_bp = Blueprint('postulante', __name__)

# ----------------- TABLERO POSTULANTE -----------------
@postulante_bp.route("/panel_postulante", methods=["GET"])
@login_required
def panel_postulante():
    if current_user.role != "postulante":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_postulante"))

    postulaciones_borrador = FormularioBase.query.filter_by(postulante_id=current_user.id, estado="borrador").all()
    postulaciones_finalizadas = FormularioBase.query.filter_by(postulante_id=current_user.id, estado="finalizado").all()

    concursos_abiertos = Concurso.query.filter(Concurso.estado == "abierto").all()

    return render_template(
        "panel_postulante.html",
        postulaciones_borrador=postulaciones_borrador,
        postulaciones_finalizadas=postulaciones_finalizadas,
        concursos_abiertos=concursos_abiertos
    )


# ----------------- LISTAR CONCURSOS ACTIVOS -----------------
@postulante_bp.route("/concursos_activos", methods=["GET"])
@login_required
def concursos_activos():
    if current_user.role != "postulante":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_postulante"))
    
    concursos = Concurso.query.filter_by(estado="abierto").all()
    return render_template("concursos_activos.html", concursos=concursos)

# ----------------- INICIAR FORMULARIO -----------------
@postulante_bp.route("/completar_formulario/<int:concurso_id>", methods=["GET", "POST"])
@login_required
def completar_formulario(concurso_id):
    if current_user.role != "postulante":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login_postulante"))

    concurso = Concurso.query.get_or_404(concurso_id)
    formulario = FormularioBase.query.filter_by(postulante_id=current_user.id, concurso_id=concurso_id).first()
    campos = CampoFormulario.query.filter_by(concurso_id=concurso_id).all()

    if formulario:
        if formulario.estado == "finalizado":
            flash("Ya has completado este formulario. No puedes postularte dos veces.", "warning")
            return redirect(url_for("postulante.panel_postulante"))

    if not campos:
        flash("No hay campos definidos para este concurso. Contacte al administrador.", "warning")
        return redirect(url_for("postulante.panel_postulante"))

    if request.method == "POST":
        datos_formulario = json.dumps(request.form.to_dict())

        if formulario:
            formulario.datos_generales = datos_formulario
        else:
            formulario = FormularioBase(
                postulante_id=current_user.id,
                concurso_id=concurso_id,
                datos_generales=datos_formulario,
                estado="borrador"
            )
            db.session.add(formulario)

        db.session.commit()
        flash("Formulario guardado correctamente.", "success")
        return redirect(url_for("postulante.panel_postulante"))

    return render_template("formulario_dinamico.html", concurso=concurso, campos=campos)



# ----------------- FINALIZAR FORMULARIO -----------------
@postulante_bp.route("/finalizar_formulario/<int:concurso_id>", methods=["POST"])
@login_required
def finalizar_formulario(concurso_id):
    formulario = FormularioBase.query.filter_by(postulante_id=current_user.id, concurso_id=concurso_id).first()
    
    if not formulario:
        flash("No hay un formulario guardado para este concurso.", "danger")
        return redirect(url_for("postulante.completar_formulario", concurso_id=concurso_id))
    
    formulario.estado = "finalizado"
    db.session.commit()
    flash("Formulario enviado correctamente.", "success")
    return redirect(url_for("postulaciones_enviadas"))

# ----------------- LISTAR FORMULARIOS ENVIADOS -----------------
@postulante_bp.route("/postulaciones_enviadas", methods=["GET"])
@login_required
def postulaciones_enviadas():
    postulaciones = FormularioBase.query.filter_by(postulante_id=current_user.id, estado="finalizado").all()
    return render_template("postulaciones_enviadas.html", postulaciones=postulaciones)

# ----------------- GENERAR PDF -----------------
@postulante_bp.route("/generar_pdf/<int:formulario_id>", methods=["GET"])
@login_required
def generar_pdf(formulario_id):
    formulario = FormularioBase.query.get_or_404(formulario_id)
    datos_generales = json.loads(formulario.datos_generales)
    
    html = render_template("postulacion_pdf.html", datos_generales=datos_generales)
    pdf_path = f"postulacion_{formulario_id}.pdf"
    pdfkit.from_string(html, pdf_path)
    
    response = send_file(pdf_path, as_attachment=True)
    os.remove(pdf_path)
    return response
