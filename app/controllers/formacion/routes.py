from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.formacion import FichaFormacion, ListaAsistencia, Asistente, PreguntaFormacion, RespuestaFormacion
from app.models.empresa import Empresa
from app.config.database import db
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
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
        objetivos_json = request.form.get('objetivos', '[]')
        objetivos_data = json.loads(objetivos_json)
        objetivos_texto = '\n• '.join([obj['texto'] for obj in objetivos_data if obj['texto']])
        objetivos = '• ' + objetivos_texto if objetivos_texto else ''
        empresa_id = request.form.get('empresa_id') or None
        metodologia = request.form.get('metodologia')  # Ahora es un solo valor
        recursos = request.form.getlist('recursos')    # Esto sigue siendo una lista
        
        # Generar código único para la ficha
        codigo = f"FORM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
              
        # Convertir a JSON para guardar en la base de datos
        metodologia_valor = metodologia if metodologia else None
        recursos_json = json.dumps(recursos) if recursos else None
        
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
            empresa_id=empresa_id,
            metodologias=metodologia,  # Ya no es JSON, solo un string
            recursos=json.dumps(recursos) if recursos else None
        )
        
        # Guardar preguntas
        preguntas_json = request.form.get('preguntas', '[]')
        preguntas_data = json.loads(preguntas_json)
        
        try:
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
            metodo_diligenciamiento = request.form.get('metodo_diligenciamiento', 'directo')
            es_externo = metodo_diligenciamiento == 'externo'
            email_externo = request.form.get('email_externo') if es_externo else None

            lista = ListaAsistencia(
                ficha_id=ficha.id,
                enlace_compartible=str(uuid.uuid4()),
                es_externo=es_externo,
                email_externo=email_externo
            )
            db.session.add(lista)
            db.session.commit()
            
            # Enviar correo si es externo
            if es_externo and email_externo:
                try:
                    # Importar función de envío de correo
                    from app.utils.email_utils import send_email
                    
                    enlace_completo = request.host_url.rstrip('/') + url_for('formacion.lista_asistencia', enlace=lista.enlace_compartible)
                    
                    asunto = f"Invitación para diligenciar Ficha de Formación: {ficha.titulo}"
                    cuerpo = f"""
                    Hola,
                    
                    Has sido invitado a diligenciar una ficha de formación en la plataforma StrateKaz.
                    
                    Título: {ficha.titulo}
                    Responsable: {ficha.responsable}
                    
                    Por favor accede al siguiente enlace para completar la información:
                    {enlace_completo}
                    
                    Saludos,
                    Equipo StrateKaz
                    """
                    
                    send_email(email_externo, asunto, cuerpo)
                    flash('Se ha enviado un correo al profesional externo con el enlace para diligenciar la ficha', 'info')
                except Exception as e:
                    flash(f'La ficha se creó correctamente, pero hubo un error al enviar el correo: {str(e)}', 'warning')
            
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

@formacion_bp.route('/enviar-enlace-creacion', methods=['POST'])
@login_required
def enviar_enlace_creacion():
    """Enviar enlace para creación externa de ficha"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email requerido'})
    
    try:
        # Generar token único para este enlace
        token = str(uuid.uuid4())
        
        # Guardar token en sesión o base de datos para validarlo después
        # Por simplicidad usamos sesión, pero en producción debería guardarse en BD
        if 'enlaces_creacion' not in session:
            session['enlaces_creacion'] = {}
        
        session['enlaces_creacion'][token] = {
            'email': email,
            'user_id': current_user.id,
            'created_at': datetime.now().isoformat()
        }
        
        # Importar función de envío de correo
        from app.utils.email_utils import send_email
        
        enlace_completo = request.host_url.rstrip('/') + url_for('formacion.crear_ficha_externa', token=token)
        
        asunto = "Invitación para crear Ficha de Formación en StrateKaz"
        cuerpo = f"""
        Hola,
        
        Has sido invitado a crear una ficha de formación en la plataforma StrateKaz.
        
        Por favor accede al siguiente enlace para completar la información:
        {enlace_completo}
        
        Saludos,
        Equipo StrateKaz
        """
        
        send_email(email, asunto, cuerpo)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@formacion_bp.route('/crear-externa/<token>')
def crear_ficha_externa(token):
    """Formulario para crear ficha por un externo"""
    # Verificar token
    enlaces = session.get('enlaces_creacion', {})
    if token not in enlaces:
        flash('Enlace inválido o expirado', 'danger')
        return redirect(url_for('main.index'))
    
    # Usar datos del token
    data = enlaces[token]
    user_id = data['user_id']
    
    # Obtener usuario
    from app.models.user import User
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.index'))
    
    # Mostrar formulario adaptado para externos
    return render_template('formacion/crear_ficha.html', 
                          token=token, 
                          email=data['email'],
                          es_externo=True)

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