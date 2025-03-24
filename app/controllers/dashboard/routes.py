from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.empresa import Empresa
from app.services.dashboard_service import DashboardService
from app.config.database import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Obtener datos básicos según el tipo de usuario
    stats = DashboardService.get_stats_for_user(current_user.id)
    
    # Si es usuario de tipo empresa, obtener sus empresas
    empresas = []
    if current_user.user_type == 'company':
        empresas = Empresa.get_by_user(current_user.id)
        
    # Renderizar template según tipo de usuario
    if current_user.user_type == 'professional':
        return render_template(
            'dashboard/profesional.html', 
            stats=stats,
            empresas=empresas
        )
    else:
        return render_template(
            'dashboard/company.html', 
            stats=stats, 
            empresas=empresas,
            company_type=current_user.company_type
        )

@dashboard_bp.route('/perfil')
@login_required
def perfil():
    # Obtener estadísticas del usuario
    stats = DashboardService.get_stats_for_user(current_user.id)
    return render_template('dashboard/perfil.html', stats=stats)

@dashboard_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def actualizar_perfil():
    if request.method == 'POST':
        print("Datos recibidos:", request.form)  # Para debuggear
        username = request.form.get('username')
        # Validar username
        username = request.form.get('username')
        if username:  # Solo actualizar si hay un valor
            current_user.username = username

        # Actualizar información según tipo de usuario
        if current_user.user_type == 'professional':
            current_user.first_name = request.form.get('first_name')
            current_user.last_name = request.form.get('last_name')
        else:
            current_user.company_name = request.form.get('company_name')
            current_user.nit = request.form.get('nit')
        
        try:
            db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil', 'danger')
            
    return redirect(url_for('dashboard.perfil'))

@dashboard_bp.route('/modulos')
@login_required
def modulos():
    """Vista para mostrar los módulos disponibles."""
    modulos = [
        {
            'id': 'sg',
            'name': 'Sistema de Gestión',
            'icon': 'clipboard-check',
            'description': 'Diseñe e implemente cualquier sistema de gestión',
            'available': True
        },
        {
            'id': 'sgsst',
            'name': 'SG-SST',
            'icon': 'hard-hat',
            'description': 'Gestione la seguridad y salud en el trabajo',
            'available': True
        },
        {
            'id': 'pesv',
            'name': 'PESV',
            'icon': 'car',
            'description': 'Plan estratégico de seguridad vial',
            'available': True
        },
        {
            'id': 'ambiental',
            'name': 'Gestión Ambiental',
            'icon': 'leaf',
            'description': 'Sistema de gestión ambiental',
            'available': False
        },
        {
            'id': 'asistencia',
            'name': 'Lista de Asistencia',
            'icon': 'clipboard-list',
            'description': 'Gestione la asistencia a capacitaciones y eventos',
            'available': True,
            'url': '/formacion'  # Ruta al módulo de formación
        }
    ]
    
    return render_template('dashboard/modulos.html', modulos=modulos)