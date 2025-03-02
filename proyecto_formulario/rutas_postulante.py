from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Concurso, FormularioBase, CampoFormulario, RespuestaCampoDinamico
import json
import pdfkit
import os
from decoradores import rol_requerido


postulante_bp = Blueprint("postulante", __name__)

# ----------------- PANEL DEL POSTULANTE -----------------
@postulante_bp.route("/panel_postulante", methods=["GET"])
@login_required
def panel_postulante():
    if current_user.role != "postulante":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    postulaciones_borrador = FormularioBase.query.filter_by(postulante_id=current_user.id, estado="borrador").all()
    postulaciones_finalizadas = FormularioBase.query.filter_by(postulante_id=current_user.id, estado="finalizado").all()
    concursos_abiertos = Concurso.query.filter(Concurso.estado == "abierto").all()

    return render_template(
        "panel_postulante.html",
        postulaciones_borrador=postulaciones_borrador,
        postulaciones_finalizadas=postulaciones_finalizadas,
        concursos_abiertos=concursos_abiertos
    )

# ----------------- INICIAR POSTULACIÓN -----------------
@postulante_bp.route("/iniciar_postulacion/<int:concurso_id>", methods=["GET"])
@login_required
def iniciar_postulacion(concurso_id):
    if current_user.role != "postulante":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    # Verificar si ya existe un formulario para este concurso
    formulario = FormularioBase.query.filter_by(postulante_id=current_user.id, concurso_id=concurso_id).first()
    if not formulario:
        formulario = FormularioBase(postulante_id=current_user.id, concurso_id=concurso_id, estado="borrador")
        db.session.add(formulario)
        db.session.commit()

    return redirect(url_for("postulante.completar_formulario", formulario_id=formulario.id))

# ----------------- COMPLETAR FORMULARIO -----------------
@postulante_bp.route("/completar_formulario/<int:formulario_id>", methods=["GET", "POST"])
@login_required
def completar_formulario(formulario_id):
    formulario = FormularioBase.query.get_or_404(formulario_id)
    
    if current_user.role != "postulante" or formulario.postulante_id != current_user.id:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    concurso = Concurso.query.get_or_404(formulario.concurso_id)
    campos = CampoFormulario.query.filter_by(concurso_id=formulario.concurso_id).all()
    
    if request.method == "POST":
        respuestas = {campo.id: request.form.get(str(campo.id)) for campo in campos}
        
        for campo_id, valor in respuestas.items():
            respuesta = RespuestaCampoDinamico.query.filter_by(formulario_id=formulario.id, campo_id=campo_id).first()
            if respuesta:
                respuesta.valor = valor
            else:
                nueva_respuesta = RespuestaCampoDinamico(formulario_id=formulario.id, campo_id=campo_id, valor=valor)
                db.session.add(nueva_respuesta)

        db.session.commit()
        flash("Formulario guardado correctamente.", "success")
        return redirect(url_for("postulante.panel_postulante"))

    return render_template("formulario_dinamico.html", formulario=formulario, concurso=concurso, campos=campos)

# ----------------- FINALIZAR FORMULARIO -----------------
@postulante_bp.route("/finalizar_formulario/<int:formulario_id>", methods=["POST"])
@login_required
def finalizar_formulario(formulario_id):
    formulario = FormularioBase.query.get_or_404(formulario_id)

    if current_user.role != "postulante" or formulario.postulante_id != current_user.id:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    formulario.estado = "finalizado"
    db.session.commit()

    flash("Formulario enviado correctamente.", "success")
    return redirect(url_for("postulante.panel_postulante"))

# ----------------- GENERAR PDF -----------------
@postulante_bp.route("/generar_pdf/<int:formulario_id>", methods=["GET"])
@login_required
def generar_pdf(formulario_id):
    formulario = FormularioBase.query.get_or_404(formulario_id)

    if current_user.role != "postulante" or formulario.postulante_id != current_user.id:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    concurso = Concurso.query.get_or_404(formulario.concurso_id)
    respuestas = RespuestaCampoDinamico.query.filter_by(formulario_id=formulario.id).all()
    
    datos = {respuesta.campo_id: respuesta.valor for respuesta in respuestas}
    
    html = render_template("formulario_pdf.html", concurso=concurso, datos=datos)
    
    pdf_path = f"postulacion_{formulario_id}.pdf"
    pdfkit.from_string(html, pdf_path, options={"enable-local-file-access": ""})
    
    return send_file(pdf_path, as_attachment=True)

# ----------------- VER POSTULACIONES -----------------
@postulante_bp.route("/ver_postulaciones", methods=["GET"])
@login_required
def ver_postulaciones():
    if current_user.role != "postulante":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("auth.login"))

    postulaciones = FormularioBase.query.filter_by(postulante_id=current_user.id).all()
    
    return render_template("ver_postulaciones.html", postulaciones=postulaciones)
