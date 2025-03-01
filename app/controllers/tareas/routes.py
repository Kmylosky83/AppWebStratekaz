from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.tarea import Tarea
from app.services.tarea_service import TareaService
from datetime import datetime

tareas_bp = Blueprint('tareas', __name__, url_prefix='/tareas')

@tareas_bp.route('/')
@login_required
def index():
    """Vista principal para la gestión de tareas."""
    tareas = Tarea.get_by_user(current_user.id, 'all')
    return render_template('dashboard/tareas.html', tareas=tareas)

@tareas_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crea una nueva tarea."""
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description', ''),
            'due_date': request.form.get('due_date'),
            'priority': request.form.get('priority', 'medium'),
            'status': request.form.get('status', 'pending'),
            'assigned_to_id': request.form.get('assigned_to_id', current_user.id),
            'empresa_id': request.form.get('empresa_id')
        }
        
        tarea = TareaService.crear_tarea(data, current_user.id)
        
        if tarea:
            flash('Tarea creada exitosamente', 'success')
        else:
            flash('Error al crear la tarea', 'danger')
            
        return redirect(url_for('tareas.index'))

@tareas_bp.route('/<int:tarea_id>/actualizar', methods=['POST'])
@login_required
def actualizar(tarea_id):
    """Actualiza una tarea existente."""
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'due_date': request.form.get('due_date'),
            'priority': request.form.get('priority'),
            'status': request.form.get('status'),
            'assigned_to_id': request.form.get('assigned_to_id')
        }
        
        # Eliminar campos None o vacíos
        data = {k: v for k, v in data.items() if v is not None and v != ''}
        
        tarea = TareaService.actualizar_tarea(tarea_id, data)
        
        if tarea:
            flash('Tarea actualizada exitosamente', 'success')
        else:
            flash('Error al actualizar la tarea', 'danger')
            
        return redirect(url_for('tareas.index'))

@tareas_bp.route('/<int:tarea_id>/eliminar', methods=['POST'])
@login_required
def eliminar(tarea_id):
    """Elimina una tarea."""
    if request.method == 'POST':
        resultado = TareaService.eliminar_tarea(tarea_id)
        
        if resultado:
            flash('Tarea eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la tarea', 'danger')
            
        return redirect(url_for('tareas.index'))

@tareas_bp.route('/<int:tarea_id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado(tarea_id):
    """Cambia el estado de una tarea."""
    if request.method == 'POST':
        nuevo_estado = request.form.get('status')
        
        if not nuevo_estado:
            return jsonify({'success': False, 'error': 'Estado no proporcionado'}), 400
            
        tarea = TareaService.cambiar_estado(tarea_id, nuevo_estado)
        
        if tarea:
            return jsonify({
                'success': True,
                'task': tarea.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Error al cambiar el estado'}), 400

@tareas_bp.route('/<int:tarea_id>/asignar', methods=['POST'])
@login_required
def asignar(tarea_id):
    """Asigna una tarea a un usuario."""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Usuario no proporcionado'}), 400
            
        tarea = TareaService.asignar_tarea(tarea_id, user_id)
        
        if tarea:
            return jsonify({
                'success': True,
                'task': tarea.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Error al asignar la tarea'}), 400

@tareas_bp.route('/filtrar', methods=['GET'])
@login_required
def filtrar():
    """Filtra tareas según parámetros."""
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    if status:
        tareas = Tarea.get_by_status(status, current_user.id)
    elif priority:
        tareas = Tarea.get_by_priority(priority, current_user.id)
    else:
        tareas = Tarea.get_by_user(current_user.id, 'all')
        
    return render_template('dashboard/tareas.html', tareas=tareas)

@tareas_bp.route('/buscar', methods=['GET'])
@login_required
def buscar():
    """Busca tareas por texto."""
    texto = request.args.get('q', '')
    
    if texto:
        tareas = TareaService.buscar_tareas(texto, user_id=current_user.id)
    else:
        tareas = Tarea.get_by_user(current_user.id, 'all')
        
    return render_template('dashboard/tareas.html', tareas=tareas, busqueda=texto)

@tareas_bp.route('/estadisticas', methods=['GET'])
@login_required
def estadisticas():
    """Obtiene estadísticas de tareas para el usuario actual."""
    stats = TareaService.get_estadisticas_usuario(current_user.id)
    return jsonify(stats)