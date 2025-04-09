from flask import Flask, render_template
from datetime import datetime, timedelta
import os

# Importar extensiones sin inicializar
from app.extensions import db, login_manager, socketio, mail, migrate, cache

def create_app(config_name='development'):
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    # Cargar configuración (mover importación aquí para evitar circulares)
    from app.config.config import config
    app.config.from_object(config[config_name])
    
    # Configurar carpetas de archivos
    configure_upload_folders(app)
    
    # Inicializar extensiones
    initialize_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar autenticación
    configure_auth(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Configurar contexto global y filtros
    configure_template_context(app)
    
    return app

def configure_upload_folders(app):
    """Configurar carpetas para archivos subidos"""
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def initialize_extensions(app):
    """Inicializar extensiones Flask"""
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    cache.init_app(app)

def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    from app.controllers.auth.routes import auth_bp
    from app.controllers.dashboard.routes import dashboard_bp
    from app.controllers.empresas.routes import empresas_bp
    from app.controllers.main.routes import main_bp
    from app.controllers.tareas.routes import tareas_bp
    from app.controllers.formacion.routes import formacion_bp
    from app.controllers.kmy.routes import kmy_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(empresas_bp, url_prefix='/empresas')
    app.register_blueprint(main_bp)
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    app.register_blueprint(formacion_bp, url_prefix='/formacion')
    app.register_blueprint(kmy_bp, url_prefix='/api/kmy')

def configure_auth(app):
    """Configurar autenticación y login manager"""
    from app.models.user import User  # Mover importación aquí
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    login_manager.remember_cookie_duration = timedelta(days=30)

def register_error_handlers(app):
    """Registrar manejadores de errores HTTP"""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

def configure_template_context(app):
    """Configurar contexto global y filtros de templates"""
    @app.context_processor
    def utility_processor():
        return dict(
            app_name='StrateKaz',
            current_year=datetime.now().year
        )
        
    @app.template_filter('from_json')
    def parse_json(value):
        import json
        try:
            return json.loads(value)
        except:
            return []

# Crear la aplicación cuando se importa el módulo
app = create_app()