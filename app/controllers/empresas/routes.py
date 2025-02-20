from flask import Blueprint, render_template
from flask_login import login_required

empresas_bp = Blueprint('empresas', __name__, url_prefix='/empresas')

@empresas_bp.route('/')
@login_required
def index():
    return render_template('empresas/index.html')

@empresas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_empresa():
    return render_template('empresas/nueva.html')