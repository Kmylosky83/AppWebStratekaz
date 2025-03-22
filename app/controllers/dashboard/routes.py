from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.empresa import Empresa
from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Obtener datos básicos según el tipo de usuario
    stats = {
        'total_visits': 0,
        'pending_tasks': 0,
        'upcoming_events': [],
        'recent_activity': []
    }
    
    # Si es usuario de tipo empresa, obtener sus empresas
    empresas = []
    if current_user.user_type == 'company':
        empresas = Empresa.get_by_user(current_user.id)
        
    # Renderizar template según tipo de usuario
    if current_user.user_type == 'professional':
        return render_template(
            'dashboard/professional.html', 
            stats=stats
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
    return render_template('dashboard/perfil.html')

@dashboard_bp.route('/estadisticas')
@login_required
def estadisticas():
    """Vista para mostrar estadísticas y análisis."""
    stats = DashboardService.get_user_stats(current_user.id)
    return render_template('dashboard/estadisticas.html', stats=stats)

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

