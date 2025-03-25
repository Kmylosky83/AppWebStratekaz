from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.empresa import Empresa
from app.config.database import db
from flask import jsonify

empresas_bp = Blueprint('empresas', __name__, url_prefix='/empresas')

@empresas_bp.route('/')
@login_required
def index():
    empresas = Empresa.get_by_user(current_user.id)
    return render_template('empresas/index.html', empresas=empresas)

@empresas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_empresa():
    if request.method == 'POST':
        empresa = Empresa(
            nombre=request.form.get('nombre'),
            ruc=request.form.get('ruc'),
            direccion=request.form.get('direccion'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            user_id=current_user.id
        )
        try:
            empresa.save()
            flash('Empresa registrada exitosamente.', 'success')
            return redirect(url_for('empresas.index'))
        except Exception as e:
            flash('Error al registrar la empresa.', 'danger')
            print(f"Error: {str(e)}")
            
    return render_template('empresas/nueva.html')

# En app/controllers/empresas/routes.py
@empresas_bp.route('/api/empresas')
@login_required
def api_empresas():
    empresas = Empresa.get_by_user(current_user.id)
    empresas_data = [{
        'id': empresa.id,
        'nombre': empresa.nombre,
        'ruc': empresa.ruc,
        'created_at': empresa.created_at.strftime('%d/%m/%Y')
    } for empresa in empresas]
    return jsonify(empresas_data)