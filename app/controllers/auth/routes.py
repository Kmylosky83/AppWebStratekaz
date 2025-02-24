from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user
from app.models.user import User
from app.config.database import db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Usuario no encontrado', 'danger')
            return render_template('auth/login.html')
        
        # Verificar si el usuario está bloqueado
        if user.is_locked:
            if (user.last_attempt_time and 
                datetime.utcnow() - user.last_attempt_time > timedelta(minutes=15)):
                user.reset_login_attempts()
            else:
                flash('Cuenta temporalmente bloqueada. Intenta más tarde.', 'danger')
                return render_template('auth/login.html')
        
        # Validar contraseña
        if user.check_password(password):
            user.reset_login_attempts()
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            user.increment_login_attempts()
            flash('Contraseña incorrecta', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template('auth/registro.html')
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error en el registro.', 'danger')
            print(f"Error: {str(e)}")
    
    return render_template('auth/registro.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))