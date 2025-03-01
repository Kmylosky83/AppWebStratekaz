from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.empresa import Empresa

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
    return render_template('dashboard/estadisticas.html')