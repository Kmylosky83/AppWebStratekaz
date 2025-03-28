from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.formacion import FichaFormacion, ListaAsistencia, Asistente, PreguntaFormacion, RespuestaFormacion
from app.models.empresa import Empresa
from app.config.database import db
from datetime import datetime
import json
import uuid
import base64
import os

formacion_bp = Blueprint('formacion', __name__, url_prefix='/formacion')

@formacion_bp.route('/')
@login_required
def index():
    """Vista principal para gestión de fichas de formación"""
    fichas = FichaFormacion.query.filter_by(user_id=current_user.id).all()
    return render_template('formacion/index.html', fichas=fichas)

@formacion_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_ficha():
    """Crear una nueva ficha de formación"""
    if request.method == 'POST':
        # Datos básicos de la ficha
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%dT%H:%M')
        lugar = request.form.get('lugar')
        duracion = request.form.get('duracion')
        responsable = request.form.get('responsable')
        objetivos = request.form.get('objetivos')
        empresa_id = request.form.get('empresa_id') or None
        
        # Generar código único para la ficha
        codigo = f"FORM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Crear la ficha
        ficha = FichaFormacion(
            titulo=titulo,
            descripcion=descripcion,
            fecha=fecha,
            lugar=lugar,
            duracion=duracion,
            responsable=responsable,
            objetivos=objetivos,
            codigo=codigo,
            user_id=current_user.id,
            empresa_id=empresa_id
        )
        
        # Guardar preguntas
        preguntas_json = request.form.get('preguntas', '[]')
        preguntas_data = json.loads(preguntas_json)
        
        db.session.add(ficha)
        db.session.flush()  # Para obtener el ID de la ficha
        
        for pregunta_data in preguntas_data:
            pregunta = PreguntaFormacion(
                texto=pregunta_data['texto'],
                tipo=pregunta_data['tipo'],
                opciones=json.dumps(pregunta_data.get('opciones', [])),
                ficha_id=ficha.id
            )
            db.session.add(pregunta)
        
        # Crear lista de asistencia asociada
        lista = ListaAsistencia(
            ficha_id=ficha.id,
            enlace_compartible=str(uuid.uuid4())
        )
        db.session.add(lista)
        
        try:
            db.session.commit()
            flash('Ficha de formación creada exitosamente', 'success')
            return redirect(url_for('formacion.ver_ficha', ficha_id=ficha.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la ficha: {str(e)}', 'danger')
            return redirect(url_for('formacion.index'))
    
    # GET: Mostrar formulario
    empresas = []
    if current_user.user_type == 'company' and current_user.company_type == 'consultant':
        empresas = Empresa.query.filter_by(user_id=current_user.id).all()
    
    return render_template('formacion/crear_ficha.html', empresas=empresas)

@formacion_bp.route('/<int:ficha_id>')
@login_required
def ver_ficha(ficha_id):
    """Ver detalles de una ficha de formación"""
    ficha = FichaFormacion.query.get_or_404(ficha_id)
    
    # Verificar permiso
    if ficha.user_id != current_user.id:
        flash('No tienes permiso para ver esta ficha', 'danger')
        return redirect(url_for('formacion.index'))
    
    lista = ListaAsistencia.query.filter_by(ficha_id=ficha.id).first()
    
    return render_template('formacion/ver_ficha.html', ficha=ficha, lista=lista)

@formacion_bp.route('/asistencia/<string:enlace>')
def lista_asistencia(enlace):
    """Formulario público para registrar asistencia"""
    lista = ListaAsistencia.query.filter_by(enlace_compartible=enlace).first_or_404()
    ficha = lista.ficha
    preguntas = PreguntaFormacion.query.filter_by(ficha_id=ficha.id).all()
    
    return render_template('formacion/asistencia.html', lista=lista, ficha=ficha, preguntas=preguntas)

@formacion_bp.route('/registrar-asistente', methods=['POST'])
def registrar_asistente():
    """Registrar un nuevo asistente en la lista"""
    lista_id = request.form.get('lista_id')
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    documento = request.form.get('documento')
    cargo = request.form.get('cargo')
    telefono = request.form.get('telefono')
    firma_data = request.form.get('firma_data')
    
    # Crear asistente
    asistente = Asistente(
        nombre=nombre,
        email=email,
        documento=documento,
        cargo=cargo,
        telefono=telefono,
        firma_data=firma_data,
        lista_id=lista_id
    )
    
    db.session.add(asistente)
    db.session.flush()  # Para obtener el ID del asistente
    
    # Guardar respuestas
    for key, value in request.form.items():
        if key.startswith('pregunta_'):
            pregunta_id = int(key.split('_')[1])
            respuesta = RespuestaFormacion(
                respuesta=value,
                pregunta_id=pregunta_id,
                asistente_id=asistente.id
            )
            db.session.add(respuesta)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Asistencia registrada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al registrar asistencia: {str(e)}'})

@formacion_bp.route('/<int:ficha_id>/generar-acta')
@login_required
def generar_acta(ficha_id):
    """Generar acta de formación en PDF"""
    ficha = FichaFormacion.query.get_or_404(ficha_id)
    
    # Verificar permiso
    if ficha.user_id != current_user.id:
        flash('No tienes permiso para generar esta acta', 'danger')
        return redirect(url_for('formacion.index'))
    
    lista = ListaAsistencia.query.filter_by(ficha_id=ficha.id).first()
    
    if not lista or not lista.asistentes:
        flash('No se puede generar el acta sin asistentes registrados', 'warning')
        return redirect(url_for('formacion.ver_ficha', ficha_id=ficha.id))
    
    # Aquí iría la lógica para generar el PDF
    # Por ahora solo mostraremos una vista previa
    return render_template('formacion/vista_previa_acta.html', ficha=ficha, lista=lista)

@formacion_bp.route('/<int:ficha_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_ficha(ficha_id):
    """Editar una ficha de formación existente"""
    ficha = FichaFormacion.query.get_or_404(ficha_id)
    
    # Verificar permiso
    if ficha.user_id != current_user.id:
        flash('No tienes permiso para editar esta ficha', 'danger')
        return redirect(url_for('formacion.index'))
    
    if request.method == 'POST':
        # Actualizar datos básicos
        ficha.titulo = request.form.get('titulo')
        ficha.descripcion = request.form.get('descripcion')
        ficha.fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%dT%H:%M')
        ficha.lugar = request.form.get('lugar')
        ficha.duracion = request.form.get('duracion')
        ficha.responsable = request.form.get('responsable')
        ficha.objetivos = request.form.get('objetivos')
        
        try:
            db.session.commit()
            flash('Ficha de formación actualizada exitosamente', 'success')
            return redirect(url_for('formacion.ver_ficha', ficha_id=ficha.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la ficha: {str(e)}', 'danger')
    
    # GET: Mostrar formulario
    return render_template('formacion/editar_ficha.html', ficha=ficha)