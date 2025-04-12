from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user
from app.models.user import User
from app.models.role import Role
from app.config.database import db
from datetime import datetime, timedelta
from werkzeug.urls import url_parse

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Variables para el template
    error = None
    email = None
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            error = 'Usuario no encontrado. Por favor verifica tu correo.'
            return render_template('auth/login.html', error=error, email=email)
        
        # Verificar si el usuario está bloqueado
        #if user.is_locked:
        #    if (user.last_attempt_time and 
        #        datetime.utcnow() - user.last_attempt_time > timedelta(minutes=15)):
        #        user.reset_login_attempts()
        #    else:
        #        error = 'Cuenta temporalmente bloqueada. Intenta de nuevo después de 15 minutos.'
        #        return render_template('auth/login.html', error=error, email=email)
        
        # Validar contraseña
        if user.check_password(password):
            #user.reset_login_attempts()
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            
            # Redireccionar a la página que intentaba visitar
            next_page = request.args.get('next')
            if next_page and url_parse(next_page).netloc == '':
                flash('Inicio de sesión exitoso', 'success')
                return redirect(next_page)
            
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            #user.increment_login_attempts()
            error = 'Contraseña incorrecta. Por favor intenta de nuevo.'
    
    return render_template('auth/login.html', error=error, email=email)

# Agregar nueva ruta para recuperar contraseña
@auth_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generar token para resetear contraseña
            from app.utils.email_utils import generate_verification_token, send_verification_email
            token = generate_verification_token(user.email)
            
            # En producción, enviaríamos un email
            # Por ahora, mostramos el link en la consola
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print(f"URL de restablecimiento de contraseña: {reset_url}")
            
            flash('Se ha enviado un enlace para restablecer tu contraseña al correo proporcionado.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('No se encontró ninguna cuenta con ese correo electrónico.', 'warning')
    
    return render_template('auth/recuperar_contrasena.html')

# Agregar nueva ruta para restablecer contraseña
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    from app.utils.email_utils import verify_token
    email = verify_token(token)
    
    if not email:
        flash('El enlace de restablecimiento no es válido o ha expirado.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('No se encontró la cuenta de usuario.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'danger')
        elif not User.validate_password_strength(password):
            flash('La contraseña no cumple con los requisitos de seguridad.', 'danger')
        else:
            user.set_password(password)
            db.session.commit()
            flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        user_type = request.form.get('user_type')
        
        # Verificar si el email ya está registrado
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template('auth/registro.html')
            
        # Crear el nuevo usuario
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Establecer tipo de usuario
        user.user_type = user_type
        
        # Asignar rol según el tipo de usuario
        if user_type == 'professional':
            # Asignar rol de profesional independiente
            role = Role.query.filter_by(name='professional').first()
            if role:
                user.role_id = role.id
        elif user_type == 'company':
            company_type = request.form.get('company_type')
            user.company_type = company_type
            
            if company_type == 'direct':
                # Asignar rol de administrador de empresa directa
                role = Role.query.filter_by(name='direct_company_admin').first()
            else:  # 'consultant'
                # Asignar rol de empresa consultora
                role = Role.query.filter_by(name='consultant_company').first()
                
            if role:
                user.role_id = role.id
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error en el registro: {str(e)}', 'danger')
            print(f"Error en registro: {str(e)}")
    
    return render_template('auth/registro.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/admin/roles', methods=['GET'])
def admin_roles():
    """
    Vista de administración de roles (solo visible para administradores)
    """
    if not current_user.is_authenticated or not current_user.has_permission('admin_users'):
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('dashboard.index'))
    
    roles = Role.query.all()
    return render_template('auth/admin_roles.html', roles=roles)


@auth_bp.route('/admin/usuarios', methods=['GET'])
def admin_users():
    """
    Vista de administración de usuarios (solo visible para administradores)
    """
    if not current_user.is_authenticated or not current_user.has_permission('admin_users'):
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('dashboard.index'))
    
    users = User.query.all()
    roles = Role.query.all()
    
    return render_template('auth/admin_users.html', users=users, roles=roles)


@auth_bp.route('/admin/usuario/<int:user_id>/rol', methods=['POST'])
def update_user_role(user_id):
    """
    Actualiza el rol de un usuario
    """
    if not current_user.is_authenticated or not current_user.has_permission('admin_users'):
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get_or_404(user_id)
    role_id = request.form.get('role_id')
    
    if role_id:
        user.role_id = int(role_id)
        db.session.commit()
        flash(f'Rol actualizado para el usuario {user.username}', 'success')
    else:
        flash('Debe seleccionar un rol válido', 'warning')
    
    return redirect(url_for('auth.admin_users'))