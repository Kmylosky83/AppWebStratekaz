# Agregar estas importaciones al inicio del archivo
from flask import (
    Blueprint, 
    render_template, 
    redirect, 
    url_for, 
    request, 
    flash, 
    jsonify, 
    session,
    current_app,
    send_file
)
from flask_login import login_required, current_user
from flask_socketio import emit, join_room
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from typing import Dict, Optional, Any
import logging
import json
import uuid
import os
import time

# Configuración de logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importaciones locales
from app.models.formacion import (
    FichaFormacion, 
    ListaAsistencia, 
    Asistente, 
    PreguntaFormacion, 
    RespuestaFormacion, 
    EvaluacionCapacitador
)
from app.models.user import User
from app.models.empresa import Empresa
from app.config.database import db
from app.utils.email_utils import send_email
from app import socketio, cache

# Crear Blueprint
formacion_bp = Blueprint('formacion', __name__, url_prefix='/formacion')

def allowed_file(filename: str, allowed_extensions: list) -> bool:
    """Validar tipos de archivo permitidos"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def procesar_objetivos(objetivos_json: str) -> str:
    """Procesar objetivos desde JSON a texto formateado"""
    try:
        objetivos_data = json.loads(objetivos_json)
        objetivos_texto = '\n• '.join([obj['texto'] for obj in objetivos_data if obj['texto']])
        return '• ' + objetivos_texto if objetivos_texto else ''
    except Exception as e:
        print(f"Error procesando objetivos: {str(e)}")
        return ''

def verificar_permiso_ficha(ficha: FichaFormacion) -> bool:
    """Verificar si el usuario actual tiene permiso para la ficha"""
    return ficha.user_id == current_user.id

def get_ficha_con_permiso(ficha_id: int) -> FichaFormacion:
    """Obtener ficha y verificar permisos"""
    ficha = FichaFormacion.query.get_or_404(ficha_id)
    if not verificar_permiso_ficha(ficha):
        raise ValueError("No tienes permiso para esta ficha")
    return ficha

# Rutas principales
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
        try:
            # Obtener y validar datos básicos
            datos = {
                'titulo': request.form.get('titulo'),
                'descripcion': request.form.get('descripcion'),
                'fecha': datetime.strptime(request.form.get('fecha'), '%Y-%m-%dT%H:%M'),
                'lugar': request.form.get('lugar'),
                'duracion': request.form.get('duracion'),
                'responsable': request.form.get('responsable'),
                'objetivos': procesar_objetivos(request.form.get('objetivos', '[]')),
                'empresa_id': request.form.get('empresa_id') or None,
                'metodologia': request.form.get('metodologia'),
                'recursos': json.dumps(request.form.getlist('recursos')) if request.form.getlist('recursos') else None
            }

            # Crear ficha
            ficha = FichaFormacion(
                **datos,
                codigo=f"FORM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                user_id=current_user.id
            )
            
            db.session.add(ficha)
            db.session.flush()

            # Procesar preguntas
            preguntas_data = json.loads(request.form.get('preguntas', '[]'))
            for pregunta_data in preguntas_data:
                pregunta = PreguntaFormacion(
                    texto=pregunta_data['texto'],
                    tipo=pregunta_data['tipo'],
                    opciones=json.dumps(pregunta_data.get('opciones', [])),
                    respuesta_correcta=pregunta_data.get('respuestaCorrecta'),
                    ficha_id=ficha.id
                )
                db.session.add(pregunta)

            # Crear lista de asistencia
            lista = ListaAsistencia(
                ficha_id=ficha.id,
                enlace_compartible=str(uuid.uuid4()),
                es_externo=request.form.get('metodo_diligenciamiento') == 'externo',
                email_externo=request.form.get('email_externo')
            )
            db.session.add(lista)
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
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        lista = ListaAsistencia.query.filter_by(ficha_id=ficha_id).first_or_404()
        
        return render_template(
            'formacion/ver_ficha.html',
            ficha=ficha,
            lista=lista,
            preguntas=PreguntaFormacion.query.filter_by(ficha_id=ficha_id).all()
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('formacion.index'))

@formacion_bp.route('/<int:ficha_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_ficha(ficha_id):
    """Editar una ficha de formación existente"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        
        if request.method == 'POST':
            try:
                # Actualizar datos básicos
                ficha.titulo = request.form.get('titulo')
                ficha.descripcion = request.form.get('descripcion')
                ficha.fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%dT%H:%M')
                ficha.lugar = request.form.get('lugar')
                ficha.duracion = request.form.get('duracion')
                ficha.responsable = request.form.get('responsable')
                ficha.objetivos = procesar_objetivos(request.form.get('objetivos', '[]'))
                ficha.metodologia = request.form.get('metodologia')
                ficha.recursos = json.dumps(request.form.getlist('recursos')) if request.form.getlist('recursos') else None
                
                # Procesar imágenes si se subieron nuevas
                for imagen_num in [1, 2]:
                    imagen = request.files.get(f'imagen_evento{imagen_num}')
                    if imagen and allowed_file(imagen.filename, ['jpg', 'jpeg', 'png']):
                        filename = secure_filename(f"evento{imagen_num}_{ficha_id}_{int(time.time())}.{imagen.filename.rsplit('.', 1)[1].lower()}")
                        imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        imagen.save(imagen_path)
                        
                        # Eliminar imagen anterior si existe
                        old_imagen = getattr(ficha, f'imagen_evento{imagen_num}')
                        if old_imagen:
                            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_imagen)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        setattr(ficha, f'imagen_evento{imagen_num}', filename)

                db.session.commit()
                flash('Ficha actualizada exitosamente', 'success')
                return redirect(url_for('formacion.ver_ficha', ficha_id=ficha_id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error actualizando la ficha: {str(e)}', 'danger')
                return redirect(url_for('formacion.editar_ficha', ficha_id=ficha_id))
        
        # GET: Mostrar formulario de edición
        empresas = []
        if current_user.user_type == 'company' and current_user.company_type == 'consultant':
            empresas = Empresa.query.filter_by(user_id=current_user.id).all()
            
        return render_template('formacion/editar_ficha.html', ficha=ficha, empresas=empresas)
        
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('formacion.index'))

@formacion_bp.route('/<int:ficha_id>/eliminar', methods=['POST'])
@login_required
def eliminar_ficha(ficha_id):
    """Eliminar una ficha de formación"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        
        # Eliminar imágenes asociadas
        for imagen_num in [1, 2]:
            imagen = getattr(ficha, f'imagen_evento{imagen_num}')
            if imagen:
                imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imagen)
                if os.path.exists(imagen_path):
                    os.remove(imagen_path)
        
        # Eliminar ficha y datos relacionados
        db.session.delete(ficha)
        db.session.commit()
        
        flash('Ficha eliminada exitosamente', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    
# Rutas de Asistencia
@formacion_bp.route('/<int:ficha_id>/asistencia', methods=['GET', 'POST'])
@login_required
def gestionar_asistencia(ficha_id):
    """Gestionar la lista de asistencia de una ficha"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        lista = ListaAsistencia.query.filter_by(ficha_id=ficha_id).first_or_404()

        if request.method == 'POST':
            # Actualizar método de diligenciamiento
            lista.es_externo = request.form.get('metodo_diligenciamiento') == 'externo'
            lista.email_externo = request.form.get('email_externo')
            
            if lista.es_externo and lista.email_externo:
                # Enviar correo con enlace
                enlace = url_for('formacion.registro_asistencia_externo', 
                               token=lista.enlace_compartible, 
                               _external=True)
                try:
                    send_email(
                        lista.email_externo,
                        'Registro de Asistencia - Formación',
                        'email/registro_asistencia.html',
                        ficha=ficha,
                        enlace=enlace
                    )
                    flash('Correo enviado exitosamente', 'success')
                except Exception as e:
                    flash(f'Error enviando correo: {str(e)}', 'danger')

            db.session.commit()
            return redirect(url_for('formacion.ver_ficha', ficha_id=ficha_id))

        return render_template(
            'formacion/gestionar_asistencia.html',
            ficha=ficha,
            lista=lista
        )

    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('formacion.index'))

@formacion_bp.route('/registro-asistencia/<string:token>', methods=['GET', 'POST'])
def registro_asistencia_externo(token):
    """Registro de asistencia mediante enlace externo"""
    lista = ListaAsistencia.query.filter_by(enlace_compartible=token).first_or_404()
    ficha = lista.ficha

    if request.method == 'POST':
        try:
            # Validar datos
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            cargo = request.form.get('cargo')
            firma_data = request.form.get('firma')

            if not all([nombre, email, firma_data]):
                raise ValueError("Todos los campos son requeridos")

            # Crear asistente
            asistente = Asistente(
                nombre=nombre,
                email=email,
                cargo=cargo,
                firma_data=firma_data,
                lista_id=lista.id
            )
            db.session.add(asistente)
            db.session.commit()

            # Emitir evento WebSocket
            socketio.emit('nuevo_asistente', {
                'nombre': asistente.nombre,
                'lista_id': lista.id
            })

            flash('Registro completado exitosamente', 'success')
            return jsonify({'success': True})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

    return render_template(
        'formacion/registro_asistencia.html',
        ficha=ficha,
        lista=lista
    )

# Rutas de manejo de imágenes
@formacion_bp.route('/<int:ficha_id>/subir-imagen', methods=['POST'])
@login_required
def subir_imagen(ficha_id):
    """Subir imagen de evento"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        
        if 'imagen' not in request.files:
            raise ValueError("No se envió ninguna imagen")
            
        imagen = request.files['imagen']
        tipo = request.form.get('tipo')  # 'evento1' o 'evento2'
        
        if imagen and allowed_file(imagen.filename, ['jpg', 'jpeg', 'png']):
            # Generar nombre único
            filename = secure_filename(
                f"{tipo}_{ficha_id}_{int(time.time())}.{imagen.filename.rsplit('.', 1)[1].lower()}"
            )
            
            # Guardar imagen
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            imagen.save(imagen_path)
            
            # Actualizar ficha
            old_imagen = getattr(ficha, f'imagen_{tipo}')
            if old_imagen:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_imagen)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    
            setattr(ficha, f'imagen_{tipo}', filename)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'filename': filename,
                'url': url_for('static', filename=f'uploads/{filename}')
            })
            
        raise ValueError("Tipo de archivo no permitido")
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@formacion_bp.route('/<int:ficha_id>/eliminar-imagen', methods=['POST'])
@login_required
def eliminar_imagen(ficha_id):
    """Eliminar imagen de evento"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        tipo = request.form.get('tipo')  # 'evento1' o 'evento2'
        
        imagen = getattr(ficha, f'imagen_{tipo}')
        if imagen:
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imagen)
            if os.path.exists(imagen_path):
                os.remove(imagen_path)
            
            setattr(ficha, f'imagen_{tipo}', None)
            db.session.commit()
            
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    # Rutas para PDF y Actas
@formacion_bp.route('/<int:ficha_id>/vista-previa-acta')
@login_required
def vista_previa_acta(ficha_id):
    """Vista previa del acta de formación"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        lista = ListaAsistencia.query.filter_by(ficha_id=ficha_id).first_or_404()
        
        if not lista.asistentes:
            flash('No se puede generar el acta sin asistentes registrados', 'warning')
            return redirect(url_for('formacion.ver_ficha', ficha_id=ficha_id))
            
        return render_template(
            'formacion/vista_previa_acta.html',
            ficha=ficha,
            lista=lista
        )
        
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('formacion.index'))

@formacion_bp.route('/<int:ficha_id>/descargar-acta-pdf')
@login_required
def descargar_acta_pdf(ficha_id):
    """Generar y descargar acta de formación en PDF"""
    temp_file = None
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        lista = ListaAsistencia.query.filter_by(ficha_id=ficha_id).first_or_404()
        
        if not lista.asistentes:
            flash('No se puede generar el acta sin asistentes registrados', 'warning')
            return redirect(url_for('formacion.ver_ficha', ficha_id=ficha_id))

        # Generar PDF usando el servicio
        from app.services.formacion_service import FormacionService
        pdf_service = FormacionService()
        temp_file = pdf_service.generar_pdf_acta(ficha, lista)
        
        if not temp_file or not os.path.exists(temp_file):
            raise ValueError("Error generando el archivo PDF")
            
        return send_file(
            temp_file,
            download_name=f"Acta_{ficha.codigo}.pdf",
            as_attachment=True,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except OSError:
                pass
        flash(f'Error generando PDF: {str(e)}', 'danger')
        return redirect(url_for('formacion.ver_ficha', ficha_id=ficha_id))

@formacion_bp.route('/<int:ficha_id>/actualizar-conclusiones', methods=['POST'])
@login_required
def actualizar_conclusiones(ficha_id):
    """Actualizar conclusiones y observaciones del acta"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        
        ficha.conclusiones = request.form.get('conclusiones')
        ficha.observaciones = request.form.get('observaciones')
        ficha.indicadores = json.dumps(request.form.getlist('indicadores')) if request.form.getlist('indicadores') else None
        
        db.session.commit()
        flash('Conclusiones actualizadas exitosamente', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@formacion_bp.route('/<int:ficha_id>/firmar-acta', methods=['POST'])
@login_required
def firmar_acta(ficha_id):
    """Registrar firma del responsable en el acta"""
    try:
        ficha = get_ficha_con_permiso(ficha_id)
        firma_data = request.form.get('firma')
        
        if not firma_data:
            raise ValueError("No se proporcionó la firma")
            
        ficha.firma_responsable = firma_data
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Manejo de errores
@formacion_bp.errorhandler(404)
def not_found_error(error):
    flash('El recurso solicitado no existe', 'danger')
    return redirect(url_for('formacion.index'))

@formacion_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Error interno del servidor', 'danger')
    return redirect(url_for('formacion.index'))

# Utilidades para manejo de sesión y caché
def get_cached_ficha(ficha_id: int) -> Optional[FichaFormacion]:
    """Obtener ficha desde caché o base de datos"""
    cache_key = f'ficha_{ficha_id}'
    ficha = cache.get(cache_key)
    if not ficha:
        ficha = FichaFormacion.query.get(ficha_id)
        if ficha:
            cache.set(cache_key, ficha, timeout=300)  # 5 minutos
    return ficha

def clear_ficha_cache(ficha_id: int) -> None:
    """Limpiar caché de una ficha"""
    cache.delete(f'ficha_{ficha_id}')

# Decoradores personalizados
def validate_ficha_access(f):
    """Decorador para validar acceso a ficha"""
    @wraps(f)
    def decorated_function(ficha_id, *args, **kwargs):
        try:
            ficha = get_ficha_con_permiso(ficha_id)
            return f(ficha, *args, **kwargs)
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('formacion.index'))
    return decorated_function

# WebSocket events
@socketio.on('connect', namespace='/formacion')
def handle_connect():
    """Manejar conexión WebSocket"""
    if not current_user.is_authenticated:
        return False
    join_room(f'user_{current_user.id}')
    return True

@socketio.on('asistente_registrado', namespace='/formacion')
def handle_nuevo_asistente(data):
    """Manejar registro de nuevo asistente"""
    try:
        lista_id = data.get('lista_id')
        if lista_id:
            lista = ListaAsistencia.query.get(lista_id)
            if lista:
                room = f'ficha_{lista.ficha_id}'
                emit('actualizar_asistentes', {
                    'count': len(lista.asistentes),
                    'last': data.get('nombre')
                }, room=room)
    except Exception as e:
        logger.error(f"Error en WebSocket: {str(e)}")

# Mejoras en rutas existentes
@formacion_bp.route('/<int:ficha_id>/estadisticas')
@login_required
@validate_ficha_access
def estadisticas_ficha(ficha: FichaFormacion):
    """Ver estadísticas de la ficha de formación"""
    try:
        lista = ListaAsistencia.query.filter_by(ficha_id=ficha.id).first_or_404()
        stats = {
            'total_asistentes': len(lista.asistentes),
            'promedio_evaluacion': calcular_promedio_evaluacion(ficha),
            'indicadores_cumplidos': contar_indicadores_cumplidos(ficha)
        }
        
        return render_template(
            'formacion/estadisticas.html',
            ficha=ficha,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        flash('Error obteniendo estadísticas', 'danger')
        return redirect(url_for('formacion.ver_ficha', ficha_id=ficha.id))

def calcular_promedio_evaluacion(ficha: FichaFormacion) -> float:
    """Calcular promedio de evaluaciones"""
    evaluaciones = EvaluacionCapacitador.query.filter_by(ficha_id=ficha.id).all()
    if not evaluaciones:
        return 0.0
    total = sum(e.puntaje for e in evaluaciones)
    return round(total / len(evaluaciones), 2)

def contar_indicadores_cumplidos(ficha: FichaFormacion) -> Dict[str, int]:
    """Contar indicadores cumplidos"""
    if not ficha.indicadores:
        return {}
    
    try:
        indicadores = json.loads(ficha.indicadores)
        conteo = {
            'asistencia': 0,
            'conocimiento': 0,
            'participacion': 0,
            'aplicabilidad': 0
        }
        for ind in indicadores:
            if ind in conteo:
                conteo[ind] += 1
        return conteo
    except:
        return {}
    
